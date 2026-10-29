"""Label fixes for the alarm/fire_alarm boundary (implemented, run only after a decision).

usage: python src/relabel.py --mode relabel_s103 | merge_siren [--dry-run]
  relabel_s103 : alarm clips whose source scenario code is S_103 -> fire_alarm (fire_alarm sources are all S_103)
  merge_siren  : alarm + fire_alarm -> siren (13 classes)
Updates data/splits/manifest.csv `label_fine` only (split/fold untouched; `label` kept), backs up the original to
data/splits/manifest_v1.csv (never overwritten), rewrites configs/labels.yaml + configs/groups.yaml, regenerates docs/split_summary.md.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from src.data import MANIFEST  # noqa: E402

BACKUP = ROOT / "data" / "splits" / "manifest_v1.csv"
SCEN = re.compile(r"^S-\d+_([A-Z]_\d+)")


def scenario(source_file):
    m = SCEN.match(str(source_file))
    return m.group(1) if m else None


def update_yaml(path, fn):
    d = yaml.safe_load(open(path, encoding="utf-8"))
    d = fn(d)
    path.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["relabel_s103", "merge_siren"], required=True)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    df = pd.read_csv(MANIFEST, low_memory=False)
    before = df["label_fine"].value_counts()
    if a.mode == "relabel_s103":
        sel = (df["label_fine"] == "alarm") & (df["source_file"].map(scenario) == "S_103")
        df.loc[sel, "label_fine"] = "fire_alarm"
        rename = None
    else:
        sel = df["label_fine"].isin(["alarm", "fire_alarm"])
        df.loc[sel, "label_fine"] = "siren"
        rename = {"alarm": "siren", "fire_alarm": "siren"}
    print(f"mode={a.mode}: {int(sel.sum())} clips changed ({df.loc[sel, 'source_file'].nunique()} sources)")
    print("before:", before.to_dict())
    print("after: ", df["label_fine"].value_counts().to_dict())
    if a.dry_run:
        return
    if not BACKUP.exists():
        pd.read_csv(MANIFEST, low_memory=False).to_csv(BACKUP, index=False, encoding="utf-8")
        print("backup ->", BACKUP)
    df.to_csv(MANIFEST, index=False, encoding="utf-8")

    def fix_list(labels):
        out = []
        for l in labels:
            l2 = rename.get(l, l) if rename else l
            if l2 not in out:
                out.append(l2)
        return out

    update_yaml(ROOT / "configs" / "labels.yaml", lambda d: {**d, "labels": fix_list(d["labels"]), "emergency": fix_list(d["emergency"])})

    def fix_groups(d):
        for gs in d.values():
            if isinstance(gs, dict):
                for g in gs.values():
                    if isinstance(g, dict) and "labels" in g:
                        g["labels"] = fix_list(g["labels"])
        return d

    update_yaml(ROOT / "configs" / "groups.yaml", fix_groups)
    # split summary on the new label_fine (make_splits regenerates everything from clip_metadata, so rebuild tables here)
    from src.make_splits import md_table
    labels = yaml.safe_load(open(ROOT / "configs" / "labels.yaml", encoding="utf-8"))["labels"]
    order = ["train", "val", "test"]
    clips = df.pivot_table(index="label_fine", columns="split", values="filepath", aggfunc="size", fill_value=0).reindex(labels)[order]
    clips["total"] = clips.sum(axis=1)
    sources = df.pivot_table(index="label_fine", columns="split", values="source_file", aggfunc="nunique", fill_value=0).reindex(labels)[order]
    sources["total"] = df.groupby("label_fine")["source_file"].nunique().reindex(labels)
    md = [f"# Split summary (after `src/relabel.py --mode {a.mode}`)", "",
          "split/fold unchanged from manifest_v1.csv; only `label_fine` changed. Tables use `label_fine`.", "",
          "## 클립 수 (split × label_fine)", "", md_table(clips.astype(int)), "",
          "## source_file 수 (split × label_fine)", "", md_table(sources.astype(int)), ""]
    (ROOT / "docs" / "split_summary.md").write_text("\n".join(md), encoding="utf-8")
    print("updated manifest, configs/labels.yaml, configs/groups.yaml, docs/split_summary.md")
    print("NOTE: existing results/ were produced with the old labels; re-run evaluate/fuse (predictions carry label_fine) or retrain.")


if __name__ == "__main__":
    main()
