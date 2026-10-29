"""Error-overlap matrix and oracle_any upper bound for a member set (test split).

usage: python src/error_overlap.py --name overlap_seed --exps E0m_v2 G_mn10_seed1 G_mn10_seed2
Members may be generalists (prob_<14>) or specialist fusions (results/<F>/predictions_test.csv). A member is "wrong" on a clip
when its argmax != label_fine. Writes results/<name>/metrics.json (condition=analysis) + docs/<name>.md:
- matrix[i][j] = clips where both i and j are wrong; diagonal = wrong count; also Jaccard of error sets
- oracle_any: fraction of clips where at least one member is right; macro-F1 of "pick a correct member if any, else member 0"
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

from src.data import load_labels  # noqa: E402
from src.evaluate import generalist_metrics, strict_mask  # noqa: E402

LAB = load_labels()
LABELS, EMERG = LAB["labels"], LAB["emergency"]
IDX = {c: i for i, c in enumerate(LABELS)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--exps", nargs="+", required=True)
    ap.add_argument("--split", default="test")
    a = ap.parse_args()
    preds = {}
    for e in a.exps:
        p = ROOT / "results" / e / f"predictions_{a.split}.csv"
        if not p.exists():
            sys.exit(f"missing {p}")
        preds[e] = pd.read_csv(p, low_memory=False)
    ref = preds[a.exps[0]]
    y = ref["label_fine"].map(IDX).to_numpy()
    for e, d in preds.items():
        assert (d["filepath"].values == ref["filepath"].values).all(), f"row order differs: {e}"
    P = {e: d[[f"prob_{c}" for c in LABELS]].to_numpy(dtype=float) for e, d in preds.items()}
    pred = {e: np.nan_to_num(P[e], nan=-1.0).argmax(1) for e in a.exps}
    wrong = {e: pred[e] != y for e in a.exps}
    n = len(a.exps)
    both = [[int((wrong[a.exps[i]] & wrong[a.exps[j]]).sum()) for j in range(n)] for i in range(n)]
    jacc = [[float((wrong[a.exps[i]] & wrong[a.exps[j]]).sum() / max((wrong[a.exps[i]] | wrong[a.exps[j]]).sum(), 1)) for j in range(n)] for i in range(n)]
    all_wrong = np.logical_and.reduce([wrong[e] for e in a.exps])
    any_right = ~all_wrong
    # oracle_any prediction: first member that is right, else member 0
    oracle = pred[a.exps[0]].copy()
    for e in a.exps[::-1]:
        oracle[~wrong[e]] = y[~wrong[e]]
    Po = np.zeros((len(y), len(LABELS)))
    Po[np.arange(len(y)), oracle] = 1.0
    m = generalist_metrics(y, Po, LABELS, EMERG, strict_mask(ref))
    out = {"experiment": a.name, "condition": "analysis", "mode": "error_overlap", "members": a.exps, "split": a.split, "label_version": LAB.get("version", "v1"),
           "date": dt.date.today().isoformat(), "n": int(len(y)), "wrong": {e: int(wrong[e].sum()) for e in a.exps},
           "both_wrong_matrix": both, "error_jaccard": jacc, "all_wrong": int(all_wrong.sum()), "oracle_any_accuracy": float(any_right.mean()),
           "oracle_any": m, "macro_f1": m["macro_f1"], "accuracy": m["accuracy"], "danger_recall": m["emergency_recall"],
           "background_fa_rate": m["background_fa_rate"], "bg_fa_strict": m["bg_fa_strict"], "emergency_group_recall": m["group"]["emergency_group_recall"]}
    res = ROOT / "results" / a.name
    res.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(res / "metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    md = [f"# {a.name}: error overlap ({a.split}, n={len(y)})", "", "members: " + ", ".join(a.exps), "",
          "## both-wrong counts (diagonal = wrong count)", "", "| | " + " | ".join(a.exps) + " |", "|---|" + "---|" * n]
    md += [f"| {a.exps[i]} | " + " | ".join(str(both[i][j]) for j in range(n)) + " |" for i in range(n)]
    md += ["", "## error-set Jaccard", "", "| | " + " | ".join(a.exps) + " |", "|---|" + "---|" * n]
    md += [f"| {a.exps[i]} | " + " | ".join(f"{jacc[i][j]:.3f}" for j in range(n)) + " |" for i in range(n)]
    md += ["", f"all members wrong: {int(all_wrong.sum())} clips ({all_wrong.mean():.3%}). **oracle_any accuracy {any_right.mean():.4f}, macro-F1 {m['macro_f1']:.4f}** "
           f"(upper bound: pick any correct member). emergency group recall {m['group']['emergency_group_recall']:.4f}."]
    (ROOT / "docs" / f"{a.name}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"name": a.name, "wrong": out["wrong"], "all_wrong": out["all_wrong"], "oracle_any_acc": round(out["oracle_any_accuracy"], 4), "oracle_any_macro_f1": round(m["macro_f1"], 4)}))


if __name__ == "__main__":
    main()
