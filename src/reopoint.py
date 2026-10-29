"""Recompute both operating points (0.005 / 0.01 val strict-FA targets) for every result from saved predictions - no model inference.
Covers generalists, fusions and specialist fusions whose predictions are in the 14-class space (predictions_val.csv has prob_<label> for
all labels). Specialist-only results (k+1 space) are skipped. usage: python src/reopoint.py [--only names...]"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.evaluate import strict_mask  # noqa: E402
from src.opoint import IDX, LABELS, apply_all, fit_all  # noqa: E402


def probs_of(df):
    cols = [f"prob_{c}" for c in LABELS]
    if not all(c in df for c in cols) or df[cols].isna().any().any():
        return None
    return df[cols].to_numpy(dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    done, skipped = [], []
    for mp in sorted(ROOT.glob("results/*/metrics.json")):
        name = mp.parent.name
        if name.startswith("smoke") or (a.only and name not in a.only):
            continue
        m = json.loads(mp.read_text(encoding="utf-8"))
        if m.get("condition") in ("specialist", "analysis"):
            skipped.append(name)
            continue
        val = mp.parent / "predictions_val.csv"
        if not val.exists():
            skipped.append(name)
            continue
        dv = pd.read_csv(val, low_memory=False)
        Pv = probs_of(dv)
        if Pv is None:
            skipped.append(name)
            continue
        yv = dv["label_fine"].map(IDX).to_numpy()
        ops = fit_all(Pv, yv, strict_mask(dv))
        for split in ("val", "test", "noisy_snr20", "noisy_snr15", "noisy_snr10"):
            pp = mp.parent / f"predictions_{split}.csv"
            if not pp.exists() or split not in m:
                continue
            d = pd.read_csv(pp, low_memory=False)
            P = probs_of(d)
            if P is None:
                continue
            m[split].update(apply_all(ops, P, d["label_fine"].map(IDX).to_numpy(), strict_mask(d)))
        for k in ("operating_point", "operating_point_001"):
            if m.get("test", {}).get(k):
                m[k] = m["test"][k]
        json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
        done.append(name)
    print(f"recomputed operating points for {len(done)}: {done}")
    print(f"skipped (specialist/analysis/no 14-class val preds): {skipped}")


if __name__ == "__main__":
    main()
