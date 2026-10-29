"""Two-stage cascade from saved predictions (no training).

stage 1 gate  = --gate experiment: event score = 1 - p_background; threshold tuned on val so that event recall >= --gate-recall (0.99).
stage 2       = --cls experiment (E0m_v2): clips passing the gate get its 14-class probabilities; the rest are background.
Reports table C/D metrics (both operating points), gate pass rate, and expected compute = MACs_gate + pass_rate x MACs_cls
versus the classifier alone. usage: python src/cascade.py --name F_cascade_E2k --gate E2k_v2 --cls E0m_v2
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src.evaluate import generalist_metrics, strict_mask  # noqa: E402
from src.opoint import BG, EMERG, IDX, LABELS, apply_all, fit_all  # noqa: E402
from src.train import append_md  # noqa: E402

# MACs per 2 s clip (G), measured at our input with src/macs.py (resample + mel included); see docs/experiment_protocol.md
MACS = {"efficientat": 0.128, "mnv4": 0.055, "yamnet_ft": 0.141, "yamnet_frozen": 0.141}
SPLITS = ["val", "test", "noisy_snr20", "noisy_snr15", "noisy_snr10"]


def load(exp, split):
    p = ROOT / "results" / exp / f"predictions_{split}.csv"
    return pd.read_csv(p, low_memory=False) if p.exists() else None


def probs(df):
    return df[[f"prob_{c}" for c in LABELS]].to_numpy(dtype=float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--gate", required=True)
    ap.add_argument("--cls", default="E0m_v2")
    ap.add_argument("--gate-recall", type=float, default=0.99)
    a = ap.parse_args()
    gmeta = json.loads((ROOT / "results" / a.gate / "metrics.json").read_text(encoding="utf-8"))
    cmeta = json.loads((ROOT / "results" / a.cls / "metrics.json").read_text(encoding="utf-8"))
    macs_gate, macs_cls = MACS[gmeta["model"]], MACS[cmeta["model"]]
    # gate threshold on val: event (non-background) recall >= target
    gv = load(a.gate, "val")
    y_val = gv["label_fine"].map(IDX).to_numpy()
    ev_score = 1.0 - probs(gv)[:, BG]
    is_event = y_val != BG
    cands = np.sort(ev_score[is_event])
    k = int(np.floor((1 - a.gate_recall) * is_event.sum()))  # allow this many missed events on val
    thr = float(cands[k]) if k < len(cands) else float(cands[0])
    out = {"experiment": a.name, "condition": "ensemble", "mode": "cascade", "method": "cascade", "model": f"{gmeta['model']}->{cmeta['model']}",
           "members": [a.gate, a.cls], "classes": LABELS, "label_version": cmeta.get("label_version"), "date": dt.date.today().isoformat(),
           "cascade": {"gate": a.gate, "classifier": a.cls, "gate_recall_target": a.gate_recall, "gate_threshold": thr,
                       "macs_gate_G": macs_gate, "macs_cls_G": macs_cls}}
    md = f"# {a.name}\n\ngate={a.gate} (event score = 1 - p_bg, thr {thr:.4f} for val event recall >= {a.gate_recall}), classifier={a.cls}\n\n"
    ops = None
    for split in SPLITS:
        g, c = load(a.gate, split), load(a.cls, split)
        if g is None or c is None:
            continue
        assert (g["filepath"].values == c["filepath"].values).all(), f"row order differs on {split}"
        y = g["label_fine"].map(IDX).to_numpy()
        passed = (1.0 - probs(g)[:, BG]) >= thr
        P = probs(c).copy()
        P[~passed] = 0.0
        P[~passed, BG] = 1.0
        strict = strict_mask(g)
        m = generalist_metrics(y, P, LABELS, EMERG, strict)
        if split == "val":
            ops = fit_all(P, y, strict)
        if ops is not None:
            m.update(apply_all(ops, P, y, strict))
        pass_rate = float(passed.mean())
        ev = y != BG
        bg_pass = float(passed[~ev].mean()) if (~ev).any() else None
        m["cascade"] = {"pass_rate": pass_rate, "event_recall_gate": float(passed[ev].mean()) if ev.any() else None, "bg_pass_rate": bg_pass,
                        "expected_macs_G": macs_gate + pass_rate * macs_cls, "saving_vs_cls_pct": 100 * (1 - (macs_gate + pass_rate * macs_cls) / macs_cls),
                        # keyring reality: most of the day is background -> compute on a pure-background stream
                        "expected_macs_bg_stream_G": (macs_gate + bg_pass * macs_cls) if bg_pass is not None else None,
                        "saving_bg_stream_pct": 100 * (1 - (macs_gate + bg_pass * macs_cls) / macs_cls) if bg_pass is not None else None}
        out[split] = m
        pred = c[["filepath", "label_fine", "split"]].copy()
        pred["pred"] = [LABELS[i] for i in P.argmax(1)]
        for i, lab in enumerate(LABELS):
            pred[f"prob_{lab}"] = P[:, i]
        (ROOT / "results" / a.name).mkdir(parents=True, exist_ok=True)
        pred.to_csv(ROOT / "results" / a.name / f"predictions_{split}.csv", index=False, encoding="utf-8")
        md += (f"- {split}: macro-F1 {m['macro_f1']:.4f} emerg recall {m['emergency_recall']} bg FA {m['background_fa_rate']} strict {m['bg_fa_strict']} | "
               f"gate pass {pass_rate:.3f} (events {m['cascade']['event_recall_gate']}, bg {m['cascade']['bg_pass_rate']}) expected MACs {m['cascade']['expected_macs_G']:.3f}G "
               f"({m['cascade']['saving_vs_cls_pct']:+.1f}% vs {a.cls}; pure-bg stream {m['cascade']['expected_macs_bg_stream_G']:.3f}G {m['cascade']['saving_bg_stream_pct']:+.1f}%)\n")
    t = out["test"]
    out.update({"accuracy": t["accuracy"], "macro_f1": t["macro_f1"], "macro_f1_no_carhorn": t.get("macro_f1_no_carhorn"), "danger_recall": t["emergency_recall"],
                "background_fa_rate": t["background_fa_rate"], "bg_fa_strict": t["bg_fa_strict"], "emergency_group_recall": t["group"]["emergency_group_recall"],
                "operating_point": t.get("operating_point"), "operating_point_001": t.get("operating_point_001"), "cascade_test": t["cascade"]})
    res = ROOT / "results" / a.name
    res.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(res / "metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    append_md(ROOT / "logs" / f"{a.name}.summary.md", md + "\n")
    print(json.dumps({"name": a.name, "macro_f1": round(t["macro_f1"], 4), "pass_rate": round(t["cascade"]["pass_rate"], 3), "bg_pass_rate": round(t["cascade"]["bg_pass_rate"], 3),
                      "expected_macs_G": round(t["cascade"]["expected_macs_G"], 3), "saving_pct": round(t["cascade"]["saving_vs_cls_pct"], 1),
                      "bg_stream_macs_G": round(t["cascade"]["expected_macs_bg_stream_G"], 3), "bg_stream_saving_pct": round(t["cascade"]["saving_bg_stream_pct"], 1),
                      "cost_005": round(t["operating_point"]["cost"], 3) if t.get("operating_point") else None}))


if __name__ == "__main__":
    main()
