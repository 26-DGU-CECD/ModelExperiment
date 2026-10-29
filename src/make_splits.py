"""Source-level StratifiedGroupKFold splits for data/miimo/clip_metadata.csv.

group = source_file, stratify key = <source event label>_<source_origin>. fold 0 -> test, 1 -> val, 2-4 -> train.
val/test keep only is_augmented == 0. Writes data/splits/manifest.csv, results/split_summary.json, docs/split_summary.md.
"""
import json
import sys
import unicodedata
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "miimo"
LABELS = ["alarm", "fire_alarm", "water", "scream", "glass_break", "bicycle", "gunshot",
          "baby_cry", "car_horn", "cat_meow", "dog_bark", "knock", "background"]
FOLD_SPLIT = {0: "test", 1: "val", 2: "train", 3: "train", 4: "train"}
MIN_TEST_SOURCES = 10


def resolve(root, rel):
    """CSV paths are NFC, on-disk Korean names are NFD. Return the relative path that exists on disk."""
    for form in (None, "NFC", "NFD"):
        p = unicodedata.normalize(form, rel) if form else rel
        if (root / p).is_file():
            return p
    raise FileNotFoundError(rel)


def source_origin(source_file, label):
    if source_file.startswith("S-21"):
        return "aihub"
    if source_file.startswith("ESC50_"):
        return "esc50"
    if label == "baby_cry":
        return "donateacry"
    return "other"


def md_table(df):
    cols = [str(df.index.name or "label")] + [str(c) for c in df.columns]
    rows = [[str(i)] + [str(v) for v in r] for i, r in zip(df.index, df.values)]
    w = [max(len(x) for x in col) for col in zip(cols, *rows)]
    line = lambda r: "| " + " | ".join(x.ljust(w[i]) for i, x in enumerate(r)) + " |"
    return "\n".join([line(cols), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    df = pd.read_csv(DATA / "clip_metadata.csv", low_memory=False)
    df["filepath"] = df["filepath"].map(lambda p: resolve(DATA, p))
    df["is_augmented"] = df["is_augmented"].astype(int)
    # effective event label: background clips carry their origin label (same source_file as the event clips)
    df["event_label"] = df["origin_label"].where(df["label"] == "background", df["label"])

    # one row per source: stratify key from the source's event label + origin
    src = df.groupby("source_file").agg(event_label=("event_label", "first"), n=("filepath", "size")).reset_index()
    src["source_origin"] = [source_origin(s, l) for s, l in zip(src["source_file"], src["event_label"])]
    src["key"] = src["event_label"] + "_" + src["source_origin"]
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    src["fold"] = -1
    for k, (_, idx) in enumerate(sgkf.split(src, src["key"], groups=src["source_file"])):
        src.loc[idx, "fold"] = k
    assert (src["fold"] >= 0).all()
    src["split"] = src["fold"].map(FOLD_SPLIT)

    df = df.merge(src[["source_file", "source_origin", "fold", "split"]], on="source_file", how="left")
    df = df[(df["split"] == "train") | (df["is_augmented"] == 0)].reset_index(drop=True)

    # leakage checks
    assert (df.groupby("source_file")["split"].nunique() == 1).all(), "source_file spans splits"
    assert (df.loc[df["split"] != "train", "is_augmented"] == 0).all(), "augmented clip in val/test"
    bg = df[df["label"] == "background"]
    ev = df[df["label"] != "background"].drop_duplicates("source_file").set_index("source_file")["split"]
    both = bg[bg["source_file"].isin(ev.index)]
    assert (both["split"].values == ev.loc[both["source_file"]].values).all(), "background split != event split for same source"

    cols = ["filepath", "label", "source_file", "source_origin", "is_augmented", "variant", "fold", "split"]
    out = ROOT / "data" / "splits" / "manifest.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df[cols].to_csv(out, index=False, encoding="utf-8")

    # summaries
    order = ["train", "val", "test"]
    clips = df.pivot_table(index="label", columns="split", values="filepath", aggfunc="size", fill_value=0).reindex(LABELS)[order]
    clips["total"] = clips.sum(axis=1)
    clips.loc["TOTAL"] = clips.sum()
    sources = df.pivot_table(index="label", columns="split", values="source_file", aggfunc="nunique", fill_value=0).reindex(LABELS)[order]
    sources["total"] = df.groupby("label")["source_file"].nunique().reindex(LABELS)
    sources.loc["TOTAL"] = [df[df["split"] == s]["source_file"].nunique() for s in order] + [df["source_file"].nunique()]
    origin = df.pivot_table(index="label", columns="source_origin", values="source_file", aggfunc="nunique", fill_value=0).reindex(LABELS)
    warn = [l for l in LABELS if sources.loc[l, "test"] < MIN_TEST_SOURCES]

    summary = {"n_clips": int(len(df)), "n_sources": int(df["source_file"].nunique()),
               "clips_by_split_label": clips.astype(int).to_dict(orient="index"),
               "sources_by_split_label": sources.astype(int).to_dict(orient="index"),
               "sources_by_label_origin": origin.astype(int).to_dict(orient="index"),
               "warn_test_sources_lt_10": warn,
               "params": {"n_splits": 5, "random_state": 42, "group": "source_file", "stratify": "event_label_source_origin",
                          "fold_to_split": FOLD_SPLIT, "val_test_filter": "is_augmented == 0"}}
    (ROOT / "results" / "split_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Split summary", "",
          "`python src/make_splits.py`. group = `source_file`, StratifiedGroupKFold(5, shuffle, seed 42), "
          "stratify = event label + source_origin. fold 0 = test, 1 = val, 2-4 = train. val/test = orig clips only.", "",
          "## 클립 수 (split × label)", "", md_table(clips.astype(int)), "",
          "## source_file 수 (split × label)", "", md_table(sources.astype(int)), "",
          "## source_file 수 (label × source_origin)", "", md_table(origin.astype(int)), ""]
    if warn:
        md += [f"**경고**: test source 수 < {MIN_TEST_SOURCES}: {', '.join(warn)}", ""]
    (ROOT / "docs" / "split_summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    print(f"-> {out} ({len(df)} rows)")


if __name__ == "__main__":
    main()
