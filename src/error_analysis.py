"""val -> test generalisation gap per class for generalist experiments -> docs/error_analysis_v2.md.
usage: python src/error_analysis.py --exps E0m_v2 E1k_v2 E2k_v2"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import pandas as pd  # noqa: E402

from src.data import load_labels  # noqa: E402

LABELS = load_labels()["labels"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exps", nargs="+", default=["E0m_v2", "E1k_v2", "E2k_v2"])
    ap.add_argument("--out", default="docs/error_analysis_v2.md")
    a = ap.parse_args()
    md = ["# val -> test gap (v2 generalists)", "", "F1 per class on val vs test; support in parentheses. Large negative gaps on small-support "
          "classes (car_horn: val 59 / test 26 clips) are mostly sampling noise; gaps on large classes point at val-selection bias "
          "(early stopping picks the epoch that fits val) or a val/test source mismatch.", ""]
    for e in a.exps:
        m = json.loads((ROOT / "results" / e / "metrics.json").read_text(encoding="utf-8"))
        v, t = m["val"]["per_class"], m["test"]["per_class"]
        md += [f"## {e}: val macro-F1 {m['val']['macro_f1']:.4f} -> test {m['test']['macro_f1']:.4f} (gap {m['test']['macro_f1'] - m['val']['macro_f1']:+.4f}); "
               f"w/o car_horn: {m['val'].get('macro_f1_no_carhorn', float('nan')):.4f} -> {m['test'].get('macro_f1_no_carhorn', float('nan')):.4f}", "",
               "| class | val F1 (n) | test F1 (n) | gap | test recall | test precision |", "|---|---|---|---|---|---|"]
        rows = sorted(LABELS, key=lambda c: t[c]["f1"] - v[c]["f1"])
        for c in rows:
            md.append(f"| {c} | {v[c]['f1']:.3f} ({v[c]['support']}) | {t[c]['f1']:.3f} ({t[c]['support']}) | {t[c]['f1'] - v[c]['f1']:+.3f} | {t[c]['recall']:.3f} | {t[c]['precision']:.3f} |")
        worst = rows[:3]
        md += ["", f"largest drops: {', '.join(f'{c} ({t[c][chr(102)+chr(49)] - v[c][chr(102)+chr(49)]:+.3f})' for c in worst)}", ""]
        # test confusion of the worst class
        cm, cl = m["test"]["confusion_matrix"], m["classes"]
        for c in worst[:2]:
            i = cl.index(c)
            conf = sorted(((cm[i][j], cl[j]) for j in range(len(cl)) if j != i and cm[i][j] > 0), reverse=True)[:3]
            md.append(f"- {c} test confusions (true -> pred): " + (", ".join(f"{l} {n}" for n, l in conf) or "none"))
        md.append("")
    (ROOT / a.out).write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(l for l in md if l.startswith(("## ", "largest"))))


if __name__ == "__main__":
    main()
