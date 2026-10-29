"""Ablation A2: random 3-group assignment of the 13 event labels (seed 42) -> configs/groups.yaml `random`.
Group sizes match the semantic assignment (5/4/4) and are given to efficientat / yamnet / mnv4 in that order."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import numpy as np  # noqa: E402
import yaml  # noqa: E402

from src.data import load_labels  # noqa: E402


def main(seed=42):
    labels = [l for l in load_labels()["labels"] if l != "background"]
    rng = np.random.default_rng(seed)
    perm = [labels[i] for i in rng.permutation(len(labels))]
    sizes = {"efficientat": 5, "yamnet": 4, "mnv4": 4}
    groups, i = {}, 0
    for model, n in sizes.items():
        groups[model] = {"name": f"random_{model}", "labels": perm[i:i + n], "confusers": []}
        i += n
    gpath = ROOT / "configs" / "groups.yaml"
    g = yaml.safe_load(open(gpath, encoding="utf-8"))
    g["random"] = groups
    gpath.write_text(yaml.safe_dump(g, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for k, v in groups.items():
        print(k, v["labels"])
    print("->", gpath)


if __name__ == "__main__":
    main()
