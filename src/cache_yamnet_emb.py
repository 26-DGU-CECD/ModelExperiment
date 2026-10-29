"""Cache TF-Hub YAMNet embeddings (1024-d, mean over the 2 s clip's frames) for every manifest clip.

usage: python src/cache_yamnet_emb.py [--splits train val test]
writes data/cache/yamnet_emb/<split>.npy (float32 [N,1024]) + <split>.csv (filepath order). CPU, ~100 clips/s.
Used by model `yamnet_frozen` via data.py `features: yamnet_emb`.
"""
import argparse
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402

from src.data import DATA, N_SAMPLES, load_manifest, resolve  # noqa: E402

OUT = ROOT / "data" / "cache" / "yamnet_emb"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", nargs="+", default=["train", "val", "test"])
    a = ap.parse_args()
    import tensorflow_hub as hub
    model = hub.load("https://tfhub.dev/google/yamnet/1")
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_manifest()
    for split in a.splits:
        d = df[df["split"] == split].reset_index(drop=True)
        embs = np.zeros((len(d), 1024), np.float32)
        t0 = time.time()
        for i, p in enumerate(d["filepath"]):
            x, sr = sf.read(str(resolve(DATA, p)), dtype="float32")
            x = x[:N_SAMPLES] if x.ndim == 1 else x[:N_SAMPLES, 0]
            _, emb, _ = model(x)
            embs[i] = emb.numpy().mean(0)
            if (i + 1) % 2000 == 0:
                print(f"{split} {i + 1}/{len(d)} {(i + 1) / (time.time() - t0):.0f} clips/s", flush=True)
        np.save(OUT / f"{split}.npy", embs)
        d[["filepath"]].to_csv(OUT / f"{split}.csv", index=False, encoding="utf-8")
        print(f"{split}: {embs.shape} -> {OUT / (split + '.npy')} in {(time.time() - t0) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
