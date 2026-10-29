"""Specialist fusions for the `best` assignment: members = SB_<model>_best where generated, else the semantic S* model
(identical label set). Runs rule / gated / stacked / oracle and writes results/F_best_fusions.done."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEMANTIC = {"efficientat": "S1_efficientat_caution", "yamnet": "S2_yamnet_emergency", "mnv4": "S3_mnv4_daily"}


def main():
    members = []
    for model, sem in SEMANTIC.items():
        sb = f"SB_{model}_best"
        if (ROOT / "results" / sb / "metrics.json").exists():
            members.append(sb)
        elif (ROOT / "results" / sem / "metrics.json").exists():
            members.append(sem)
        else:
            print(f"missing specialist for {model} ({sb} / {sem})")
    if len(members) < 2:
        sys.exit("not enough specialist results for best fusion")
    print("best members:", members)
    rc = 0
    for name, method in [("F_best_rule", "rule"), ("F_best_gated", "gated"), ("F_best_stacked", "stacked"), ("oracle_best", "oracle")]:
        cmd = [sys.executable, "-u", "-W", "ignore", str(ROOT / "src" / "fuse.py"), "--name", name, "--method", method, "--exps", *members]
        rc |= subprocess.call(cmd, cwd=str(ROOT))
    if rc == 0:
        (ROOT / "results" / "F_best_fusions.done").write_text("\n".join(members) + "\n", encoding="utf-8")
    sys.exit(rc)


if __name__ == "__main__":
    main()
