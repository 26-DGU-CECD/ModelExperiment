"""MACs / params of each wrapper at our input (2 s @16 kHz) via torch.utils.flop_counter (FLOPs/2 = MACs).
usage: python src/macs.py  -> prints a markdown table (paste into docs/experiment_protocol.md)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import torch  # noqa: E402
from torch.utils.flop_counter import FlopCounterMode  # noqa: E402

from src.models import build_model  # noqa: E402

VARIANTS = [("efficientat", {"pretrained_name": "mn04_as"}, "mn04_as"), ("efficientat", {"pretrained_name": "mn10_as"}, "mn10_as"),
            ("efficientat", {"pretrained_name": "dymn10_as"}, "dymn10_as"), ("mnv4", {}, "mobilenetv4_conv_small"), ("yamnet_ft", {}, "yamnet (torch port)")]


def main():
    x = torch.zeros(1, 32000)
    rows = ["| model | params (M) | MACs per 2 s clip (G) | MACs/s (G) |", "|---|---|---|---|"]
    for name, args, label in VARIANTS:
        m = build_model(name, 14, {"model_args": args}).eval()
        fc = FlopCounterMode(display=False)
        with fc, torch.no_grad():
            m(x)
        macs = fc.get_total_flops() / 2
        rows.append(f"| {label} | {sum(p.numel() for p in m.parameters()) / 1e6:.2f} | {macs / 1e9:.3f} | {macs / 2 / 1e9:.3f} |")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
