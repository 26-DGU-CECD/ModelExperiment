"""Evaluate checkpoints/<exp>/best.pt on val and test.

usage: python src/evaluate.py --config configs/<exp>.yaml
Writes results/<exp>/predictions_{val,test}.csv, results/<exp>/metrics.json; appends summary to logs/<exp>.summary.md.
Schema: docs/metrics_schema.md.
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
import torch  # noqa: E402
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from src.data import NOISY_MANIFEST, OTHER, build_noisy_test, build_split, load_labels  # noqa: E402
from src.models import build_model  # noqa: E402
from src.opoint import apply_all, fit_all  # noqa: E402
from src.train import append_md, load_config, predict  # noqa: E402


def vs_generalist(df, probs, classes, split, init_from):
    """Specialist vs the generalist it was warm-started from, remapped into the specialist label space (own classes + other)."""
    parts = [x for x in Path(str(init_from)).parts]
    if "checkpoints" not in parts or parts.index("checkpoints") + 1 >= len(parts):
        return None
    gen_name = parts[parts.index("checkpoints") + 1]
    gp = ROOT / "results" / gen_name / f"predictions_{split}.csv"
    if not gp.exists():
        return None
    g = pd.read_csv(gp, low_memory=False)
    if len(g) != len(df) or not (g["filepath"].values == df["filepath"].values).all():
        return None
    own = [c for c in classes if c != OTHER]
    y = df["label_fine"].map({c: i for i, c in enumerate(classes)}).to_numpy()
    gpred = g["pred"].where(g["pred"].isin(own), OTHER).map({c: i for i, c in enumerate(classes)}).to_numpy()
    spred = probs.argmax(1)
    fg, fs = per_class(y, gpred, classes), per_class(y, spred, classes)
    rows = {c: {"generalist_remapped_f1": fg[c]["f1"], "specialist_f1": fs[c]["f1"], "delta": fs[c]["f1"] - fg[c]["f1"]} for c in classes}
    return {"generalist": gen_name, "per_class": rows, "mean_delta_own": float(np.mean([rows[c]["delta"] for c in own]))}


BG_STRICT = ROOT / "data" / "splits" / "bg_strict.csv"


def strict_mask(df):
    """Boolean mask: background clips whose peak-segment RMS < -40 dBFS (src/bg_strict.py). Noisy rows map via clean_filepath."""
    if not BG_STRICT.exists():
        return None
    st = pd.read_csv(BG_STRICT)
    strict = set(st.loc[st["strict"], "filepath"])
    key = df["clean_filepath"].str.replace("data/miimo/", "", regex=False) if "clean_filepath" in df else df["filepath"]
    return key.isin(strict).to_numpy()


def per_class(y, pred, classes):
    p, r, f, s = precision_recall_fscore_support(y, pred, labels=range(len(classes)), zero_division=0)
    return {c: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(s[i])} for i, c in enumerate(classes)}


GROUPS = {"emergency": ["alarm", "fire_alarm", "scream", "cry", "glass_break", "gunshot", "car_horn", "siren"],
          "caution": ["dog_bark", "cat_meow", "bicycle"], "daily": ["water", "knock", "baby_cry"], "background": ["background"]}


def group_metrics(y, pred, classes):
    """Keyring view: a prediction counts as correct when it lands in the true label's group (emergency/caution/daily/background)."""
    gid = {}
    for g, labs in GROUPS.items():
        for l in labs:
            if l in classes:
                gid[classes.index(l)] = g
    yg = np.array([gid.get(i, "other") for i in y]); pg = np.array([gid.get(i, "other") for i in pred])
    out = {"group_accuracy": float((yg == pg).mean())}
    for g in GROUPS:
        t, p_ = yg == g, pg == g
        out[f"{g}_group_recall"] = float((pg[t] == g).mean()) if t.any() else None
        out[f"{g}_group_precision"] = float((yg[p_] == g).mean()) if p_.any() else None
    return out


def generalist_metrics(y, probs, classes, emergency, strict=None, pred=None):
    pred = probs.argmax(1) if pred is None else pred
    pc = per_class(y, pred, classes)
    idx = {c: i for i, c in enumerate(classes)}
    em = np.isin(y, [idx[c] for c in emergency if c in idx])
    bg = y == idx["background"]
    m = {"accuracy": float((pred == y).mean()), "macro_f1": float(np.mean([v["f1"] for v in pc.values()])),
         "macro_f1_no_carhorn": float(np.mean([v["f1"] for c, v in pc.items() if c != "car_horn"])),
         "emergency_recall": float((pred[em] == y[em]).mean()) if em.any() else None,
         "background_fa_rate": float((pred[bg] != idx["background"]).mean()) if bg.any() else None,
         "bg_fa_strict": float((pred[bg & strict] != idx["background"]).mean()) if strict is not None and (bg & strict).any() else None,
         "n_bg_strict": int((bg & strict).sum()) if strict is not None else None,
         "group": group_metrics(y, pred, classes),
         "per_class": pc, "confusion_matrix": confusion_matrix(y, pred, labels=range(len(classes))).tolist()}
    if "cry" in idx and "baby_cry" in idx:
        m["cry_babycry_confusion"] = {"cry_as_baby_cry": int(((y == idx["cry"]) & (pred == idx["baby_cry"])).sum()),
                                      "baby_cry_as_cry": int(((y == idx["baby_cry"]) & (pred == idx["cry"])).sum()),
                                      "cry_support": int((y == idx["cry"]).sum()), "baby_cry_support": int((y == idx["baby_cry"]).sum())}
    return m


def specialist_metrics(y, probs, classes, orig):
    """y in k+1 space (last = other). orig = original 14-class label names for reject-rate breakdown."""
    pred = probs.argmax(1)
    o = classes.index(OTHER)
    pc = per_class(y, pred, classes)
    own = {c: pc[c] for c in classes if c != OTHER}
    non_target_event = (y == o) & (orig != "background")
    bg = (y == o) & (orig == "background")
    return {"accuracy": float((pred == y).mean()), "macro_f1": float(np.mean([v["f1"] for v in own.values()])),
            "macro_f1_no_carhorn": float(np.mean([v["f1"] for c, v in own.items() if c != "car_horn"])) if any(c != "car_horn" for c in own) else None,
            "own_class": own, "other": pc[OTHER],
            "reject_rate_non_target_events": float((pred[non_target_event] == o).mean()) if non_target_event.any() else None,
            "reject_rate_background": float((pred[bg] == o).mean()) if bg.any() else None,
            "reject_rate_by_origin": {lab: float((pred[(y == o) & (orig == lab)] == o).mean()) for lab in sorted(set(orig[y == o]))},
            "confusion_matrix": confusion_matrix(y, pred, labels=range(len(classes))).tolist()}


def cm_md(cm, classes):
    head = "| true \ pred | " + " | ".join(classes) + " |\n|" + "---|" * (len(classes) + 1) + "\n"
    return head + "".join(f"| {c} | " + " | ".join(str(v) for v in row) + " |\n" for c, row in zip(classes, cm))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--eval-set", choices=["clean", "noisy", "all"], default="clean",
                    help="clean: val+test; noisy: test x SNR from data/test_noisy (updates metrics.json in place); all: both")
    ap.add_argument("--snrs", nargs="+", type=int, default=[20, 15, 10])
    args = ap.parse_args()
    cfg = load_config(args.config)
    exp = cfg["exp_name"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt = torch.load(ROOT / "checkpoints" / exp / "best.pt", map_location="cpu", weights_only=False)
    classes, tcfg = ckpt["classes"], ckpt["config"]
    model = build_model(tcfg["model"], len(classes), tcfg).to(device)
    model.load_state_dict(ckpt["model_state_dict"])
    labels_cfg = load_labels()
    all14, emergency = labels_cfg["labels"], labels_cfg["emergency"]
    specialist = cfg["mode"] == "specialist"
    res_dir = ROOT / "results" / exp
    res_dir.mkdir(parents=True, exist_ok=True)
    mpath = res_dir / "metrics.json"
    out = json.loads(mpath.read_text(encoding="utf-8")) if (args.eval_set == "noisy" and mpath.exists()) else {}
    out.update({"experiment": exp, "model": tcfg["model"], "condition": cfg["mode"], "mode": cfg["mode"], "label_version": labels_cfg.get("version", "v1"),
                "recipe": cfg.get("recipe", "ft-v2" if (specialist and cfg.get("init_from")) else ("naive" if specialist else None)),
                "group": cfg.get("group_set") if specialist else None, "classes": classes, "date": dt.date.today().isoformat(),
                "best_epoch": ckpt["epoch"], "best_val_macro_f1": ckpt["val_macro_f1"], "config": tcfg})
    op_fit = None
    sets = []
    if args.eval_set in ("clean", "all"):
        sets += [("val", None), ("test", None)]
    if args.eval_set in ("noisy", "all"):
        assert NOISY_MANIFEST.exists(), f"{NOISY_MANIFEST} missing: run src/musan_mix.py first"
        sets += [(f"noisy_snr{s}", s) for s in args.snrs]
    md = f"\n## evaluate ({out['date']}) best epoch {ckpt['epoch']}\n\n"
    for split, snr in sets:
        df, _, ds = build_noisy_test(cfg, classes, snr) if snr is not None else build_split(cfg, split, classes)
        probs, y = predict(model, DataLoader(ds, batch_size=cfg["batch_size"], num_workers=cfg["num_workers"]), device, cfg["amp"] and device.type == "cuda")
        pred = df.assign(pred=[classes[i] for i in probs.argmax(1)])[["filepath", "label_fine", "split", "pred"]]
        if specialist:
            pred["label_fine"] = df["_orig"].values  # original 14-class label; group label kept separately
            pred.insert(2, "label_group", df["label_fine"].values)
            for c in all14:  # project onto the 14-class space: own classes keep their prob, the rest NaN
                pred[f"prob_{c}"] = probs[:, classes.index(c)] if c in classes else np.nan
            pred["prob_other"] = probs[:, classes.index(OTHER)]
            m = specialist_metrics(y, probs, classes, df["_orig"].to_numpy())
            vg = vs_generalist(df, probs, classes, split, tcfg.get("init_from")) if tcfg.get("init_from") else None
            if vg:
                m["vs_generalist"] = vg
                md += (f"#### vs generalist {vg['generalist']} (remapped to own+other), {split}: mean delta own {vg['mean_delta_own']:+.4f}" + chr(10) + chr(10) +
                       "| class | generalist F1 | specialist F1 | delta |" + chr(10) + "|---|---|---|---|" + chr(10) +
                       chr(10).join(f"| {c} | {r['generalist_remapped_f1']:.4f} | {r['specialist_f1']:.4f} | {r['delta']:+.4f} |" for c, r in vg["per_class"].items()) + chr(10) + chr(10))
        else:
            for i, c in enumerate(classes):
                pred[f"prob_{c}"] = probs[:, i]
            m = generalist_metrics(y, probs, classes, emergency, strict_mask(df))
            if split == "val":
                op_fit = fit_all(probs, y, strict_mask(df))
            if op_fit is not None:
                m.update(apply_all(op_fit, probs, y, strict_mask(df)))
        pred.to_csv(res_dir / f"predictions_{split}.csv", index=False, encoding="utf-8")
        out[split] = m
        md += f"### {split}: acc {m['accuracy']:.4f} macro-F1 {m['macro_f1']:.4f}"
        md += (f" reject(non-target events) {m['reject_rate_non_target_events']} reject(bg) {m['reject_rate_background']}\n\n" if specialist
               else f" emergency recall {m['emergency_recall']} bg FA {m['background_fa_rate']} bg FA strict {m.get('bg_fa_strict')}\n\n")
        md += cm_md(m["confusion_matrix"], classes) + "\n"
    if "test" in out:  # leaderboard-compatible top-level keys (clean test split)
        t = out["test"]
        for k in ("operating_point", "operating_point_001"):
            if t.get(k):
                out[k] = t[k]
        out.update({"accuracy": t["accuracy"], "macro_f1": t["macro_f1"], "danger_recall": t.get("emergency_recall"),
                    "background_fa_rate": t.get("background_fa_rate"), "bg_fa_strict": t.get("bg_fa_strict"), "macro_f1_no_carhorn": t.get("macro_f1_no_carhorn"),
                    "emergency_group_recall": t.get("group", {}).get("emergency_group_recall"),
                    "emergency_group_precision": t.get("group", {}).get("emergency_group_precision")})
    json.dump(out, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    append_md(ROOT / "logs" / f"{exp}.summary.md", md)
    keys = ["experiment", "accuracy", "macro_f1", "danger_recall", "background_fa_rate"] + [k for k in out if k.startswith("noisy_snr")]
    print(json.dumps({k: (out[k]["macro_f1"] if isinstance(out.get(k), dict) else out.get(k)) for k in keys}), flush=True)
    print("->", res_dir / "metrics.json", flush=True)


if __name__ == "__main__":
    main()
