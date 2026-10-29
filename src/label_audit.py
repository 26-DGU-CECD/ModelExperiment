"""Label audit for AI Hub sources: per (label, scenario code) source counts and E0 per-scenario recall / F1 on test.

usage: python src/label_audit.py [--exp E0_efficientat_generalist] [--manifest data/splits/manifest_v1.csv] [--flag 0.6]
Scenario code = `<letter>_<digits>` after the date in `S-YYMMDD_<code>_...`. Uses the manifest's label_fine (v1 by default,
so the audit reflects the labels the model was trained on). Writes docs/label_audit.md.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import pandas as pd  # noqa: E402

SCEN = re.compile(r"^S-\d+_([A-Z]_\d+)")


def scen(s):
    m = SCEN.match(str(s))
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", default="E0_efficientat_generalist")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--flag", type=float, default=0.6)
    a = ap.parse_args()
    mpath = Path(a.manifest) if a.manifest else (ROOT / "data" / "splits" / ("manifest_v1.csv" if (ROOT / "data" / "splits" / "manifest_v1.csv").exists() else "manifest.csv"))
    m = pd.read_csv(mpath, low_memory=False)
    m = m[m["source_origin"] == "aihub"].copy()
    m["scen"] = m["source_file"].map(scen)
    pred = pd.read_csv(ROOT / "results" / a.exp / "predictions_test.csv", low_memory=False)
    pred = pred.merge(m[["filepath", "scen"]], on="filepath", how="inner")  # aihub test clips only; label_fine from predictions = model's label set
    rows, flagged = [], []
    for (lab, sc), g in m.drop_duplicates("source_file").groupby(["label_fine", "scen"]):
        t = pred[(pred["label_fine"] == lab) & (pred["scen"] == sc)]
        if len(t):
            tp = int((t["pred"] == lab).sum())
            fp = int(((pred["label_fine"] != lab) & (pred["pred"] == lab)).sum())
            rec = tp / len(t)
            prec = tp / max(tp + fp, 1)
            f1 = 2 * prec * rec / max(prec + rec, 1e-9)
            top = ", ".join(f"{k} {v}" for k, v in t.loc[t["pred"] != lab, "pred"].value_counts().head(2).items()) or "-"
        else:
            rec = f1 = None
            top = "-"
        n_test_src = m[(m["label_fine"] == lab) & (m["scen"] == sc) & (m["split"] == "test")]["source_file"].nunique()
        rows.append((lab, sc, len(g), n_test_src, len(t), rec, f1, top))
        if f1 is not None and f1 < a.flag:
            flagged.append((lab, sc, f1, len(t)))
    md = [f"# 라벨 감사 (AI Hub 소스, 시나리오 코드별) — 모델 {a.exp}, 라벨 {mpath.name}", "",
          "시나리오 코드 = 파일명 `S-YYMMDD_<코드>_...`. recall = 해당 (라벨, 코드) test 클립 중 정답 예측 비율. "
          "F1* = 라벨 전체 FP를 모든 코드에 공통 적용. F1* < %.1f → 플래그." % a.flag, "",
          "| label | scenario | sources (all) | test sources | test clips | recall | F1* | top wrong preds |", "|---|---|---|---|---|---|---|---|"]
    for lab, sc, ns, nts, nt, rec, f1, top in rows:
        md.append(f"| {lab} | {sc} | {ns} | {nts} | {nt} | {'-' if rec is None else f'{rec:.3f}'} | {'-' if f1 is None else f'{f1:.3f}'} | {top} |")
    md += ["", "## 플래그 (F1* < %.1f)" % a.flag, ""]
    md += [f"- **{lab} / {sc}**: F1* {f1:.3f} (test clips {nt})" for lab, sc, f1, nt in flagged] or ["- 없음"]
    (ROOT / "docs" / "label_audit.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
