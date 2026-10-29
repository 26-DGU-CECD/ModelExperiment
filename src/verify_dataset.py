"""Verify data/miimo against clip_metadata.csv and README counts.

usage: python src/verify_dataset.py [--root data/miimo] [--n-audio 10] [--seed 0]
writes results/dataset_verify.json, prints tables.
"""
import argparse
import json
import random
import sys
import unicodedata
from pathlib import Path

import pandas as pd
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["alarm", "fire_alarm", "water", "scream", "glass_break", "bicycle", "gunshot",
          "baby_cry", "car_horn", "cat_meow", "dog_bark", "knock", "background"]
# README "라벨별 수량" table: clips_2s, 독립 소스
README_CLIPS = {"alarm": 15810, "fire_alarm": 6150, "water": 6714, "scream": 2457, "glass_break": 12303,
                "bicycle": 3747, "gunshot": 4257, "baby_cry": 9204, "car_horn": 771, "cat_meow": 2772,
                "dog_bark": 1305, "knock": 417, "background": 14142}
README_SOURCES = {"alarm": 395, "fire_alarm": 167, "water": 195, "scream": 90, "glass_break": 255,
                  "bicycle": 78, "gunshot": 254, "baby_cry": 325, "car_horn": 57, "cat_meow": 127,
                  "dog_bark": 106, "knock": 85, "background": 1058}
SR, CH, N, DTYPE = 16000, 1, 32000, "float32"


def resolve(root, rel):
    """CSV paths and on-disk names can differ in unicode normalization (Korean filenames); try NFC/NFD."""
    for form in (None, "NFC", "NFD"):
        p = root / (unicodedata.normalize(form, rel) if form else rel)
        if p.is_file():
            return p
    return None


def table(rows, cols):
    w = [max(len(str(r[c])) for r in rows + [dict(zip(cols, cols))]) for c in cols]
    line = lambda r: "| " + " | ".join(str(r[c]).ljust(w[i]) for i, c in enumerate(cols)) + " |"
    return "\n".join([line(dict(zip(cols, cols))), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def check_audio(path):
    info = sf.info(str(path))
    data, sr = sf.read(str(path), dtype="float32")
    return {"ok": sr == SR and info.channels == CH and info.frames == N and info.subtype == "FLOAT",
            "sr": sr, "channels": info.channels, "frames": info.frames, "subtype": info.subtype,
            "peak": float(abs(data).max()) if len(data) else 0.0}


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Korean filenames on a cp949 console
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "data" / "miimo"))
    ap.add_argument("--n-audio", type=int, default=10)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    root = Path(a.root)
    df = pd.read_csv(root / "clip_metadata.csv")
    df["is_augmented"] = df["is_augmented"].astype(int)
    out = {"root": str(root), "n_rows": int(len(df))}

    # 1. file existence
    exists = df["filepath"].map(lambda p: resolve(root, p) is not None)
    missing = df.loc[~exists, "filepath"].tolist()
    out["missing_files"] = {"count": len(missing), "list": missing[:200]}
    print(f"\n[1] files: {int(exists.sum())}/{len(df)} exist, {len(missing)} missing")
    for p in missing[:20]:
        print("   MISSING", p)
    if len(missing) > 20:
        print(f"   ... +{len(missing) - 20} more (full list in json, first 200)")

    # 2. counts vs README, 3. orig/aug + unique source_file
    rows = []
    extra = sorted(set(df["label"]) - set(LABELS))
    for lab in LABELS:
        d = df[df["label"] == lab]
        n, n_orig = len(d), int((d["is_augmented"] == 0).sum())
        n_src = int(d["source_file"].nunique())
        rows.append({"label": lab, "clips": n, "readme": README_CLIPS[lab], "match": "OK" if n == README_CLIPS[lab] else "DIFF",
                     "orig": n_orig, "aug": n - n_orig, "aug_ratio": f"{(n - n_orig) / n_orig:.2f}" if n_orig else "-",
                     "sources": n_src, "readme_src": README_SOURCES[lab], "src_match": "OK" if n_src == README_SOURCES[lab] else "DIFF"})
    rows.append({"label": "TOTAL", "clips": len(df), "readme": sum(README_CLIPS.values()),
                 "match": "OK" if len(df) == sum(README_CLIPS.values()) else "DIFF",
                 "orig": int((df["is_augmented"] == 0).sum()), "aug": int((df["is_augmented"] == 1).sum()),
                 "aug_ratio": "", "sources": int(df["source_file"].nunique()), "readme_src": "", "src_match": ""})
    out["label_counts"] = rows
    out["unexpected_labels"] = extra
    print("\n[2-3] label counts vs README, orig/aug, unique source_file")
    print(table(rows, ["label", "clips", "readme", "match", "orig", "aug", "aug_ratio", "sources", "readme_src", "src_match"]))
    if extra:
        print("   UNEXPECTED labels:", extra)

    # 4. audio format on random clips per label
    rng = random.Random(a.seed)
    audio = {}
    arows = []
    print(f"\n[4] audio format: {a.n_audio} random clips/label, expect {SR}Hz/{CH}ch/{N} samples/{DTYPE}")
    for lab in LABELS:
        paths = [p for p in df.loc[df["label"] == lab, "filepath"] if resolve(root, p)]
        sample = rng.sample(paths, min(a.n_audio, len(paths)))
        res = []
        for p in sample:
            try:
                r = check_audio(resolve(root, p))
            except Exception as e:  # corrupt file
                r = {"ok": False, "error": f"{type(e).__name__}: {e}"}
            r["filepath"] = p
            res.append(r)
        bad = [r for r in res if not r["ok"]]
        audio[lab] = {"checked": len(res), "bad": len(bad), "bad_list": bad}
        arows.append({"label": lab, "checked": len(res), "bad": len(bad)})
        for r in bad:
            print("   BAD", lab, r)
    out["audio_check"] = audio
    print(table(arows, ["label", "checked", "bad"]))

    out["summary"] = {"missing_files": len(missing), "count_mismatch": [r["label"] for r in rows if r["match"] == "DIFF"],
                      "source_mismatch": [r["label"] for r in rows if r["src_match"] == "DIFF"],
                      "audio_bad": sum(v["bad"] for v in audio.values())}
    dst = ROOT / "results" / "dataset_verify.json"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nsummary:", json.dumps(out["summary"], ensure_ascii=False))
    print("->", dst)
    return 0 if not missing and not out["summary"]["count_mismatch"] and not out["summary"]["audio_bad"] else 1


if __name__ == "__main__":
    sys.exit(main())
