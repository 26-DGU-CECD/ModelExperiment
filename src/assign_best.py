"""Per-class best-model assignment from generalist val per-class F1 -> configs/groups.yaml `best` + docs/assignment_best.md.

usage: python src/assign_best.py --exps E0m_efficientat_generalist_musan E1k_yamnet_kd E2k_mnv4_kd [--min-classes 1]
Model key = experiment's `model` base name (yamnet_ft -> yamnet). A model with 0 assigned classes is dropped (2-model best set).
background is never assigned (every specialist models it inside "other").
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import yaml  # noqa: E402

from src.data import load_labels  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exps", nargs="+", required=True)
    ap.add_argument("--split", default="val")
    a = ap.parse_args()
    labels = [l for l in load_labels()["labels"] if l != "background"]
    ms = {e: json.loads((ROOT / "results" / e / "metrics.json").read_text(encoding="utf-8")) for e in a.exps}
    key = {e: m["model"].split("_")[0] for e, m in ms.items()}
    f1 = {e: {c: m[a.split]["per_class"][c]["f1"] for c in labels} for e, m in ms.items()}
    assign = {c: max(a.exps, key=lambda e: f1[e][c]) for c in labels}
    groups = {}
    for e in a.exps:
        own = [c for c in labels if assign[c] == e]
        if own:
            groups[key[e]] = {"name": f"best_{key[e]}", "labels": own, "confusers": [], "from": e}
    dropped = [e for e in a.exps if key[e] not in groups]
    gpath = ROOT / "configs" / "groups.yaml"
    g = yaml.safe_load(open(gpath, encoding="utf-8"))
    g["best"] = groups
    gpath.write_text(yaml.safe_dump(g, allow_unicode=True, sort_keys=False), encoding="utf-8")
    md = [f"# best 배정 ({a.split} per-class F1 argmax)", "", f"입력: {', '.join(a.exps)}", "",
          "| class | " + " | ".join(a.exps) + " | assigned |", "|---|" + "---|" * (len(a.exps) + 1)]
    for c in labels:
        md.append(f"| {c} | " + " | ".join(("**%.4f**" if assign[c] == e else "%.4f") % f1[e][c] for e in a.exps) + f" | {key[assign[c]]} |")
    md += ["", "## 결과 그룹", ""] + [f"- **{k}** ({v['from']}): {', '.join(v['labels'])}" for k, v in groups.items()]
    if dropped:
        md += ["", f"담당 클래스 0개로 제외된 모델: {', '.join(dropped)} → {len(groups)}-모델 구성."]
    md += ["", "background는 배정하지 않는다(모든 스페셜리스트가 other 안에서 모델링)."]
    (ROOT / "docs" / "assignment_best.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[-(len(groups) + 4):]))
    print("->", gpath, "and docs/assignment_best.md")


if __name__ == "__main__":
    main()
