"""Common operating point + threshold-free group metrics (table D). Shared by evaluate.py (generalists) and fuse.py (fusions).

Procedure (identical for every system, fitted on val, applied to test/noisy):
  1. per-class thresholds tau_c on val: emergency classes -> highest tau with recall >= 0.95; daily -> lowest tau with precision >= 0.90;
     others -> argmax F1.
  2. greedy: raise the tau of the class causing the most strict-background false alarms on val, one grid step at a time, until
     strict bg FA on val <= STRICT_FA_TARGET (0.005) (global scale only as a fallback). Decision: argmax_c p_c/tau_c if >= 1 else background.
  3. report at that point: emergency recall, daily precision, caution F1, macro-F1 (+ without car_horn), bg FA, strict FA, cost score,
     group recall/precision. Plus threshold-free PR-AUC per group (score = max prob over the group's classes).
Cost score per clip: emergency FN x5, daily FP x2, any other error x1 (normalised by N).
"""
import numpy as np
from sklearn.metrics import average_precision_score

from src.data import load_labels

LAB = load_labels()
LABELS, EMERG = LAB["labels"], LAB["emergency"]
DAILY = ["water", "knock", "baby_cry"]
CAUTION = [c for c in LABELS if c not in EMERG and c not in DAILY and c != "background"]
IDX = {c: i for i, c in enumerate(LABELS)}
BG = IDX["background"]
STRICT_FA_TARGET = 0.005
GRID = np.linspace(0.02, 0.98, 49)
SCALES = np.concatenate([[1.0], np.geomspace(1.05, 20.0, 40)])


def macro_f1(y, pred, classes=None):
    classes = range(len(LABELS)) if classes is None else classes
    f = []
    for c in classes:
        tp = ((pred == c) & (y == c)).sum()
        fp = ((pred == c) & (y != c)).sum()
        fn = ((pred != c) & (y == c)).sum()
        f.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return float(np.mean(f)) if f else None


def fit_thresholds(P, y):
    taus = {}
    for c in LABELS:
        if c == "background":
            continue
        i = IDX[c]
        pos = y == i
        if not pos.any():
            taus[c] = 0.5
            continue
        rec = np.array([(P[pos, i] >= t).mean() for t in GRID])
        prec = np.array([((P[:, i] >= t) & pos).sum() / max((P[:, i] >= t).sum(), 1) for t in GRID])
        f1 = 2 * prec * rec / np.maximum(prec + rec, 1e-9)
        if c in EMERG:
            ok = GRID[rec >= 0.95]
            taus[c] = float(ok.max()) if len(ok) else float(GRID[0])
        elif c in DAILY:
            ok = GRID[prec >= 0.90]
            taus[c] = float(ok.min()) if len(ok) else float(GRID[-1])
        else:
            taus[c] = float(GRID[int(np.argmax(f1))])
    return taus


def decide(P, taus, scale=1.0):
    ratio = np.zeros_like(P)
    for c, t in taus.items():
        ratio[:, IDX[c]] = P[:, IDX[c]] / (scale * t)
    pred = ratio.argmax(1)
    pred[ratio.max(1) < 1.0] = BG
    return pred


def strict_fa(pred, y, strict):
    bg = y == BG
    m = bg & strict if strict is not None else bg
    return float((pred[m] != BG).mean()) if m.any() else None


def fit_scale(P, y, taus, strict, target=STRICT_FA_TARGET, max_iter=400):
    """Greedy per-class threshold raise until strict bg FA on val <= target: at each step raise tau of the class that
    produces the most strict false alarms (one grid step), so emergency thresholds are only touched when they cause FAs.
    Falls back to a global scale if every offending tau has hit the ceiling. Mutates `taus`; returns (scale, val_fa)."""
    step = float(GRID[1] - GRID[0])
    for _ in range(max_iter):
        pred = decide(P, taus, 1.0)
        fa = strict_fa(pred, y, strict)
        if fa is None or fa <= target:
            return 1.0, fa
        mask = (y == BG) & (strict if strict is not None else True) & (pred != BG)
        offenders = [LABELS[i] for i in pred[mask] if LABELS[i] in taus and taus[LABELS[i]] < 0.98]
        if not offenders:
            break
        worst = max(set(offenders), key=offenders.count)
        taus[worst] = min(0.98, taus[worst] + step)
    for s in SCALES:  # fallback
        fa = strict_fa(decide(P, taus, s), y, strict)
        if fa is None or fa <= target:
            return float(s), fa
    return float(SCALES[-1]), strict_fa(decide(P, taus, SCALES[-1]), y, strict)


def cost_score(pred, y):
    em = set(IDX[c] for c in EMERG)
    da = set(IDX[c] for c in DAILY)
    cost = 0.0
    for t, p in zip(y, pred):
        if t == p:
            continue
        if t in em:
            cost += 5.0
        elif p in da:
            cost += 2.0
        else:
            cost += 1.0
    return float(cost / len(y))


def group_pr_auc(P, y):
    out = {}
    for name, labs in (("emergency", EMERG), ("daily", DAILY), ("caution", CAUTION)):
        ids = [IDX[c] for c in labs if c in IDX]
        score = np.nan_to_num(P[:, ids]).max(1)
        truth = np.isin(y, ids)
        out[name] = float(average_precision_score(truth, score)) if truth.any() and (~truth).any() else None
    return out


def group_metrics_at(pred, y):
    from src.evaluate import group_metrics
    return group_metrics(y, pred, LABELS)


def point_metrics(P, y, taus, scale, strict):
    pred = decide(P, taus, scale)
    em_idx = [IDX[c] for c in EMERG]
    da_idx = [IDX[c] for c in DAILY]
    ca_idx = [IDX[c] for c in CAUTION]
    em = np.isin(y, em_idx)
    pda = np.isin(pred, da_idx)
    bg = y == BG
    return {"emergency_recall": float((pred[em] == y[em]).mean()) if em.any() else None,
            "daily_precision": float((y[pda] == pred[pda]).mean()) if pda.any() else None,
            "caution_f1": macro_f1(y, pred, ca_idx),
            "macro_f1": macro_f1(y, pred), "macro_f1_no_carhorn": macro_f1(y, pred, [i for i in range(len(LABELS)) if LABELS[i] != "car_horn"]),
            "accuracy": float((pred == y).mean()),
            "bg_fa_rate": float((pred[bg] != BG).mean()) if bg.any() else None, "bg_fa_strict": strict_fa(pred, y, strict),
            "fa_per_hour": float((pred[bg] != BG).mean() * 1800) if bg.any() else None,
            "cost": cost_score(pred, y), "group": group_metrics_at(pred, y), "pr_auc": group_pr_auc(P, y)}


def fit_operating_point(P_val, y_val, strict_val):
    taus = fit_thresholds(P_val, y_val)
    base = dict(taus)
    scale, fa = fit_scale(P_val, y_val, taus, strict_val)
    raised = {c: round(taus[c] - base[c], 2) for c in taus if taus[c] != base[c]}
    return {"rule": f"per-class tau (emergency recall>=0.95 / daily precision>=0.90 / others max F1), then greedy raise of FA-causing taus until val strict bg FA <= {STRICT_FA_TARGET}",
            "raised": raised,
            "thresholds": taus, "threshold": float(np.mean(list(taus.values()))), "scale": scale, "val_strict_fa": fa}


def apply_operating_point(op, P, y, strict):
    m = point_metrics(P, y, op["thresholds"], op["scale"], strict)
    m.update({"rule": op["rule"], "threshold": op["threshold"], "scale": op["scale"], "thresholds": op["thresholds"],
              "raised": op.get("raised"), "val_strict_fa": op.get("val_strict_fa")})
    m["precision"] = None  # legacy key
    em_idx = [IDX[c] for c in EMERG]
    pred = decide(P, op["thresholds"], op["scale"])
    pem = np.isin(pred, em_idx)
    m["precision"] = float((y[pem] == pred[pem]).mean()) if pem.any() else None
    return m
