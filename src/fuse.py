"""Fuse member predictions. Fit anything learnable on val, report on test + noisy SNR 20/15/10.

usage: python src/fuse.py --name F_generalist_soft --method soft_avg --exps E0_... E1_... E2_... [--tag premusan]
generalist methods : hard_vote | soft_avg (val temperature scaling) | weighted_soft (val macro-F1 weights) | stacking (LogReg C=1) | best_single
specialist methods : rule | gated | stacked | oracle | hier   (members = specialist experiments, 14-class projected predictions + prob_other)
                     hier = hierarchical: --router <generalist exp> picks the group (argmax class -> its group), that specialist answers
Output: results/<name>/metrics.json (+ predictions_test.csv), same schema as evaluate.py plus `method`, `members`, `operating_point`.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.optimize import minimize_scalar  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402

from src.data import load_labels  # noqa: E402
from src.evaluate import generalist_metrics, group_metrics, strict_mask  # noqa: E402
from src.train import append_md  # noqa: E402

SPLITS = ["val", "test", "noisy_snr20", "noisy_snr15", "noisy_snr10"]
LAB = load_labels()
LABELS, EMERG = LAB["labels"], LAB["emergency"]
DAILY = ["water", "knock", "baby_cry"]
IDX = {c: i for i, c in enumerate(LABELS)}
BG = IDX["background"]


def load_preds(exp, split):
    p = ROOT / "results" / exp / f"predictions_{split}.csv"
    return pd.read_csv(p, low_memory=False) if p.exists() else None


def probs_of(df):  # [N,14] in LABELS order (NaN for specialist non-own classes)
    return df[[f"prob_{c}" for c in LABELS]].to_numpy(dtype=float)


def y_of(df):
    return df["label_fine"].map(IDX).to_numpy()


def softmax(z):
    z = z - z.max(1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(1, keepdims=True)


def temperature(logp, y):
    """Scalar temperature fitted on val log-probs by NLL."""
    def nll(T):
        z = logp / T
        z = z - z.max(1, keepdims=True)
        return -(z[np.arange(len(y)), y] - np.log(np.exp(z).sum(1))).mean()
    return float(minimize_scalar(nll, bounds=(0.3, 5.0), method="bounded").x)


def macro_f1(y, pred, n=len(LABELS)):
    f = []
    for c in range(n):
        tp = ((pred == c) & (y == c)).sum()
        fp = ((pred == c) & (y != c)).sum()
        fn = ((pred != c) & (y == c)).sum()
        f.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return float(np.mean(f))


# ---------------- generalist fusions: dict split -> (ref df, probs [N,14])
def fuse_generalist(method, members):
    val = {e: load_preds(e, "val") for e in members}
    y_val = y_of(next(iter(val.values())))
    for e, d in val.items():
        assert (y_of(d) == y_val).all(), f"val row order differs for {e}"
    T = {e: temperature(np.log(probs_of(val[e]) + 1e-9), y_val) for e in members}
    f1v = {e: macro_f1(y_val, probs_of(val[e]).argmax(1)) for e in members}
    info = {"temperature": T, "val_macro_f1": f1v}

    def cal(e, d):
        return softmax(np.log(probs_of(d) + 1e-9) / T[e])

    stacker = None
    if method == "stacking":
        stacker = LogisticRegression(C=1.0, max_iter=2000).fit(np.concatenate([cal(e, val[e]) for e in members], 1), y_val)
    if method == "weighted_soft":
        w = np.array([f1v[e] for e in members])
        info["weights"] = dict(zip(members, (w / w.sum()).tolist()))
    best = max(members, key=lambda e: f1v[e])
    info["best_single"] = best
    out = {}
    for split in SPLITS:
        ds = {e: load_preds(e, split) for e in members}
        if any(d is None for d in ds.values()):
            continue
        ref = next(iter(ds.values()))
        if method == "best_single":
            P = probs_of(ds[best])
        elif method == "hard_vote":
            P = np.zeros((len(ref), len(LABELS)))
            for e in members:  # ties broken by val F1
                P[np.arange(len(ref)), probs_of(ds[e]).argmax(1)] += 1 + 1e-3 * f1v[e]
            P = P / P.sum(1, keepdims=True)
        elif method == "soft_avg":
            P = np.mean([cal(e, ds[e]) for e in members], 0)
        elif method == "weighted_soft":
            P = sum(info["weights"][e] * cal(e, ds[e]) for e in members)
        elif method == "stacking":
            P = stacker.predict_proba(np.concatenate([cal(e, ds[e]) for e in members], 1))
        else:
            raise ValueError(method)
        out[split] = (ref, P)
    return out, info


# ---------------- specialist fusions
def spec_features(d, own):
    """[N, k+1]: own-class probs + prob_other of one specialist."""
    return np.column_stack([np.nan_to_num(probs_of(d)[:, [IDX[c] for c in own]]), d["prob_other"].to_numpy()])


def fuse_specialist(method, members, router=None):
    """members: specialist experiments (predictions with prob_<own classes>, NaN elsewhere, + prob_other)."""
    val = {e: load_preds(e, "val") for e in members}
    groups = {e: [c for c in LABELS if c != "background" and val[e][f"prob_{c}"].notna().all()] for e in members}
    info = {"groups": groups}
    stacker = None
    if method == "stacked":
        X = np.concatenate([spec_features(val[e], groups[e]) for e in members], 1)
        stacker = LogisticRegression(C=1.0, max_iter=2000).fit(X, y_of(next(iter(val.values()))))
    out = {}
    for split in SPLITS:
        ds = {e: load_preds(e, split) for e in members}
        if any(d is None for d in ds.values()):
            continue
        ref = next(iter(ds.values()))
        n = len(ref)
        P = np.zeros((n, len(LABELS)))
        other = np.column_stack([ds[e]["prob_other"].to_numpy() for e in members])
        if method in ("rule", "gated"):
            for e in members:
                pe, po = probs_of(ds[e]), ds[e]["prob_other"].to_numpy()
                for c in groups[e]:
                    P[:, IDX[c]] = pe[:, IDX[c]] * ((1 - po) if method == "gated" else 1.0)
            P[:, BG] = other.min(1)
        elif method == "stacked":
            P = stacker.predict_proba(np.concatenate([spec_features(ds[e], groups[e]) for e in members], 1))
        elif method == "hier":  # router (generalist) argmax -> group -> that group's specialist decides (own probs + other as bg)
            rp = load_preds(router, split)
            assert rp is not None and len(rp) == n and (rp["filepath"].values == ref["filepath"].values).all(), f"router {router} rows differ"
            r_cls = probs_of(rp).argmax(1)
            owner = {}
            for e in members:
                for c in groups[e]:
                    owner[IDX[c]] = e
            for e in members:
                pe, po = np.nan_to_num(probs_of(ds[e])), ds[e]["prob_other"].to_numpy()
                mine = np.array([owner.get(c) == e for c in r_cls])
                P[mine] = pe[mine]
                P[mine, BG] = po[mine]
            isbg = r_cls == BG
            P[isbg] = 0.0
            P[isbg, BG] = 1.0
        elif method == "oracle":  # route by the TRUE label's specialist; true background -> bg iff every specialist says other
            y = y_of(ref)
            for e in members:
                pe, po = np.nan_to_num(probs_of(ds[e])), ds[e]["prob_other"].to_numpy()
                mine = np.isin(y, [IDX[c] for c in groups[e]])
                P[mine] = pe[mine]
                P[mine, BG] = po[mine]
            isbg = y == BG
            says_other = np.column_stack([np.nan_to_num(probs_of(ds[e])).max(1) < ds[e]["prob_other"].to_numpy() for e in members])
            all_other = says_other.all(1)
            P[isbg & all_other, BG] = 1.0
            rest = isbg & ~all_other
            P[rest] = np.nan_to_num(np.nanmax(np.stack([probs_of(ds[e]) for e in members]), 0))[rest]
        else:
            raise ValueError(method)
        out[split] = (ref, P / np.maximum(P.sum(1, keepdims=True), 1e-9))
    return out, info


# ---------------- operating point (table D)
def fit_thresholds(P, y):
    """Per-class thresholds on val: emergency recall>=0.95 (highest tau meeting it), daily precision>=0.90 (lowest tau), rest max F1."""
    taus = {}
    grid = np.linspace(0.02, 0.98, 49)
    for c in LABELS:
        if c == "background":
            continue
        i = IDX[c]
        pos = y == i
        if not pos.any():
            taus[c] = 0.5
            continue
        rec = np.array([(P[pos, i] >= t).mean() for t in grid])
        prec = np.array([((P[:, i] >= t) & pos).sum() / max((P[:, i] >= t).sum(), 1) for t in grid])
        f1 = 2 * prec * rec / np.maximum(prec + rec, 1e-9)
        if c in EMERG:
            ok = grid[rec >= 0.95]
            taus[c] = float(ok.max()) if len(ok) else float(grid[0])
        elif c in DAILY:
            ok = grid[prec >= 0.90]
            taus[c] = float(ok.min()) if len(ok) else float(grid[-1])
        else:
            taus[c] = float(grid[int(np.argmax(f1))])
    return taus


def apply_thresholds(P, taus):
    ratio = np.zeros_like(P)
    for c, t in taus.items():
        ratio[:, IDX[c]] = P[:, IDX[c]] / t
    pred = ratio.argmax(1)
    pred[ratio.max(1) < 1.0] = BG
    return pred


def op_metrics(P, y, taus, strict):
    pred = apply_thresholds(P, taus)
    em_idx = [IDX[c] for c in EMERG]
    em, pem = np.isin(y, em_idx), np.isin(pred, em_idx)
    bg = y == BG
    bg_fa = float((pred[bg] != BG).mean()) if bg.any() else None
    return {"rule": "per-class tau on val: emergency recall>=0.95 / daily precision>=0.90 / others max F1", "thresholds": taus,
            "threshold": float(np.mean(list(taus.values()))),
            "emergency_recall": float((pred[em] == y[em]).mean()) if em.any() else None,
            "precision": float((y[pem] == pred[pem]).mean()) if pem.any() else None,
            "bg_fa_rate": bg_fa,
            "bg_fa_strict": float((pred[bg & strict] != BG).mean()) if strict is not None and (bg & strict).any() else None,
            "fa_per_hour": bg_fa * 1800 if bg_fa is not None else None,  # proxy: 1800 two-second clips per hour of pure background
            "macro_f1": macro_f1(y, pred), "accuracy": float((pred == y).mean()), "group": group_metrics(y, pred, LABELS)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--method", required=True)
    ap.add_argument("--exps", nargs="+", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--router", default=None, help="generalist experiment used by method=hier")
    a = ap.parse_args()
    specialist = a.method in ("rule", "gated", "stacked", "oracle", "hier")
    if a.method == "hier":
        assert a.router, "--router required for hier"
        a.exps = list(a.exps)
    missing = [f"{e}/{s}" for e in a.exps for s in ("val", "test") if load_preds(e, s) is None]
    if missing:
        sys.exit(f"fuse: missing member predictions {missing}; refusing to write partial results")
    fused, info = fuse_specialist(a.method, a.exps, a.router) if specialist else fuse_generalist(a.method, a.exps)
    if a.router:
        info["router"] = a.router
    res = ROOT / "results" / a.name
    res.mkdir(parents=True, exist_ok=True)
    out = {"experiment": a.name, "model": "+".join(sorted({e.split("_")[1] for e in a.exps})), "condition": "ensemble",
           "mode": "specialist_fusion" if specialist else "generalist_fusion", "method": a.method, "members": a.exps, "tag": a.tag,
           "classes": LABELS, "date": dt.date.today().isoformat(), "fit_info": info, "label_version": LAB.get("version", "v1")}
    taus = None
    md = f"# {a.name}\n\nmethod={a.method} members={a.exps} tag={a.tag}\n\n"
    for split, (ref, P) in fused.items():
        y, strict = y_of(ref), strict_mask(ref)
        m = generalist_metrics(y, P, LABELS, EMERG, strict)
        if split == "val":
            taus = fit_thresholds(P, y)
        if taus is not None:
            m["operating_point"] = op_metrics(P, y, taus, strict)
        out[split] = m
        if split == "test":
            pred = ref[["filepath", "label_fine", "split"]].copy()
            pred["pred"] = [LABELS[i] for i in P.argmax(1)]
            for i, c in enumerate(LABELS):
                pred[f"prob_{c}"] = P[:, i]
            pred.to_csv(res / "predictions_test.csv", index=False, encoding="utf-8")
        md += (f"- {split}: macro-F1 {m['macro_f1']:.4f} acc {m['accuracy']:.4f} emerg recall {m['emergency_recall']} "
               f"bg FA {m['background_fa_rate']} strict {m['bg_fa_strict']}\n")
    t = out["test"]
    out.update({"accuracy": t["accuracy"], "macro_f1": t["macro_f1"], "danger_recall": t["emergency_recall"],
                "background_fa_rate": t["background_fa_rate"], "bg_fa_strict": t["bg_fa_strict"], "operating_point": t.get("operating_point"),
                "emergency_group_recall": t["group"]["emergency_group_recall"], "emergency_group_precision": t["group"]["emergency_group_precision"]})
    json.dump(out, open(res / "metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    append_md(ROOT / "logs" / f"{a.name}.summary.md", md + "\n")
    keys = ["experiment", "method", "macro_f1", "accuracy", "danger_recall", "background_fa_rate", "bg_fa_strict", "noisy_snr20", "noisy_snr15", "noisy_snr10"]
    print(json.dumps({k: (round(out[k]["macro_f1"], 4) if isinstance(out.get(k), dict) else out.get(k)) for k in keys if k in out}))


if __name__ == "__main__":
    main()
