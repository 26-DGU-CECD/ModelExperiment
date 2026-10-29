"""Generate SB_<model>_best specialist configs for the `best` assignment (configs/groups.yaml, from src/assign_best.py),
only for models whose best label set differs from their semantic set. Writes configs/SB_<model>_best.yaml and prints the list.
Models whose sets are identical reuse the S* result (no config, queue step skipped as optional)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import yaml  # noqa: E402

TEMPLATE = {"efficientat": "configs/S1_efficientat_caution.yaml", "yamnet": "configs/S2_yamnet_emergency.yaml", "mnv4": "configs/S3_mnv4_daily.yaml"}


def main():
    g = yaml.safe_load(open(ROOT / "configs" / "groups.yaml", encoding="utf-8"))
    best, sem = g.get("best") or {}, g["semantic"]
    made = []
    for model, spec in best.items():
        if model in sem and sorted(spec["labels"]) == sorted(sem[model]["labels"]):
            print(f"{model}: best == semantic ({spec['labels']}) -> reuse S* result")
            continue
        base = yaml.safe_load(open(ROOT / TEMPLATE[model], encoding="utf-8"))
        base["exp_name"] = f"SB_{model}_best"
        base["group_set"] = "best"
        out = ROOT / "configs" / f"SB_{model}_best.yaml"
        out.write_text(yaml.safe_dump(base, allow_unicode=True, sort_keys=False), encoding="utf-8")
        made.append(out.name)
        print(f"{model}: best {spec['labels']} != semantic {sem.get(model, {}).get('labels')} -> {out.name}")
    (ROOT / "configs" / "sb_generated.txt").write_text("\n".join(made), encoding="utf-8")


if __name__ == "__main__":
    main()
