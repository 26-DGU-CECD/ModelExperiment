"""Peak-segment RMS (dBFS) of every val/test background clip -> data/splits/bg_strict.csv.
"strict silence" = peak 100 ms-segment RMS < -40 dBFS (dataset's background rule is < -30 dBFS).
Used for bg_fa_strict in evaluate.py / fuse.py. usage: python src/bg_strict.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import soundfile as sf  # noqa: E402

from src.data import DATA, load_manifest, resolve  # noqa: E402

OUT = ROOT / "data" / "splits" / "bg_strict.csv"
STRICT_DBFS = -40.0


def peak_rms_dbfs(x, seg=1600):
    n = len(x) // seg
    segs = x[: n * seg].reshape(n, seg)
    return float(20 * np.log10(np.sqrt((segs ** 2).mean(1)).max() + 1e-9))


def main():
    df = load_manifest()
    df = df[(df["label_fine"] == "background") & (df["split"].isin(["val", "test"]))]
    rows = []
    for p in df["filepath"]:
        x, _ = sf.read(str(resolve(DATA, p)), dtype="float32")
        rows.append({"filepath": p, "peak_rms_dbfs": peak_rms_dbfs(x if x.ndim == 1 else x[:, 0])})
    out = pd.DataFrame(rows)
    out["strict"] = out["peak_rms_dbfs"] < STRICT_DBFS
    out.to_csv(OUT, index=False, encoding="utf-8")
    m = df.merge(out, on="filepath")
    print(m.groupby("split")["strict"].agg(["sum", "size"]).rename(columns={"sum": "strict", "size": "all_bg"}).to_string())
    print("->", OUT)


if __name__ == "__main__":
    main()
