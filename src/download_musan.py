"""Download MUSAN noise/** (HF FluidInference/musan) to data/musan/noise and split files 80/20 (seed 42) into
data/musan_train/noise and data/musan_test/noise via hard links. Writes data/musan/noise_split.csv."""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parent.parent
MUSAN = ROOT / "data" / "musan"


def main():
    snapshot_download("FluidInference/musan", repo_type="dataset", local_dir=str(MUSAN), allow_patterns=["noise/**"], max_workers=16)
    files = sorted(p.relative_to(MUSAN).as_posix() for p in (MUSAN / "noise").rglob("*.wav"))
    rng = np.random.default_rng(42)
    is_test = np.zeros(len(files), bool)
    is_test[rng.choice(len(files), int(round(0.2 * len(files))), replace=False)] = True
    df = pd.DataFrame({"file": files, "split": np.where(is_test, "test", "train"), "size": [(MUSAN / f).stat().st_size for f in files]})
    df.to_csv(MUSAN / "noise_split.csv", index=False)
    for split in ("train", "test"):
        for f in df.loc[df.split == split, "file"]:
            dst = ROOT / "data" / f"musan_{split}" / f
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                os.link(MUSAN / f, dst)
    print(df.groupby("split").agg(n=("file", "size"), MB=("size", lambda s: round(s.sum() / 1e6, 1))).to_string())
    print(f"-> {MUSAN / 'noise_split.csv'}")


if __name__ == "__main__":
    main()
