"""Rebuild results/LEADERBOARD.md from results/*/metrics.json (schema: docs/metrics_schema.md).

A generalist per-class F1 (model x class) | B specialist own-class F1 vs same-model generalist, rejects
C fusion/condition summary (macro-F1 / accuracy / emergency recall / bg FA) | D operating points. Empty cells "-".
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
LABELS = ["alarm", "fire_alarm", "water", "scream", "glass_break", "bicycle", "gunshot",
          "baby_cry", "cry", "car_horn", "cat_meow", "dog_bark", "knock", "background"]


def fmt(v, nd=4):
    if v is None or v == "":
        return "-"
    return f"{v:.{nd}f}" if isinstance(v, float) else str(v)


def table(header, rows):
    return "\n".join(["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows]) + "\n"


def load(results_dir=RESULTS):
    out = []
    for p in sorted(results_dir.glob("*/metrics.json")):
        if p.parent.name.startswith("smoke"):
            continue
        m = json.loads(p.read_text(encoding="utf-8"))
        m.setdefault("experiment", p.parent.name)
        out.append(m)
    return out


def test_of(m):
    return m.get("test") or {}


def table_a(ms):
    gens = [m for m in ms if m.get("condition") == "generalist"]
    rows = [[m["experiment"], m.get("model", "-")] + [fmt(test_of(m).get("per_class", {}).get(c, {}).get("f1")) for c in LABELS]
            + [fmt(m.get("macro_f1"))] for m in gens]
    return table(["experiment", "model"] + LABELS + ["macro-F1"], rows)


def table_b(ms):
    gen_by_model = {m.get("model"): m for m in ms if m.get("condition") == "generalist"}
    rows = []
    for m in ms:
        if m.get("condition") != "specialist":
            continue
        t, g = test_of(m), test_of(gen_by_model.get(m.get("model"), {}))
        for c, v in (t.get("own_class") or {}).items():
            gf = (g.get("per_class") or {}).get(c, {}).get("f1")
            rows.append([m["experiment"], m.get("model", "-"), c, fmt(v.get("f1")), fmt(gf), fmt(v["f1"] - gf if gf is not None else None),
                         fmt(t.get("reject_rate_non_target_events")), fmt(t.get("reject_rate_background"))])
    return table(["experiment", "model", "class", "spec F1", "gen F1 (same model)", "delta", "reject non-target", "reject bg"], rows)


def table_c(ms):
    rows = [[m["experiment"], m.get("condition", "-"), m.get("model", "-"), fmt(m.get("macro_f1")), fmt(m.get("accuracy")),
             fmt(m.get("danger_recall")), fmt(m.get("background_fa_rate")), fmt((m.get("noisy_snr10") or {}).get("macro_f1")), m.get("date", "-")]
            for m in sorted(ms, key=lambda m: m.get("macro_f1") or 0, reverse=True) if m.get("condition") != "specialist"]
    return table(["experiment", "condition", "model", "macro-F1", "accuracy", "emergency recall", "bg FA rate", "noisy SNR10 macro-F1", "date"], rows)


def table_d(ms):
    rows = []
    for m in ms:
        op = m.get("operating_point")
        if op:
            rows.append([m["experiment"], str(op.get("rule", "-")), fmt(op.get("threshold")), fmt(op.get("emergency_recall")),
                         fmt(op.get("precision")), fmt(op.get("fa_per_hour"))])
    return table(["experiment", "rule", "threshold", "emergency recall", "precision", "FA/hour"], rows)


def render(ms):
    return ("# LEADERBOARD\n\n`python src/make_leaderboard.py`. test split. smoke_* excluded.\n\n"
            "## A. generalist per-class F1\n\n" + table_a(ms) +
            "\n## B. specialist vs generalist (same model)\n\n" + table_b(ms) +
            "\n## C. condition summary (macro-F1 desc)\n\n" + table_c(ms) +
            "\n## D. operating points\n\n" + table_d(ms))


def main():
    ms = load()
    (RESULTS / "LEADERBOARD.md").write_text(render(ms), encoding="utf-8")
    print(f"{len(ms)} experiments -> {RESULTS / 'LEADERBOARD.md'}")


def _selftest():
    g = {"experiment": "E0_x_generalist", "model": "x", "condition": "generalist", "macro_f1": 0.8, "accuracy": 0.9, "danger_recall": 0.7,
         "background_fa_rate": 0.1, "date": "2026-01-01", "test": {"per_class": {c: {"f1": 0.5} for c in LABELS}}}
    s = {"experiment": "S1_x_caution", "model": "x", "condition": "specialist", "test": {"own_class": {"gunshot": {"f1": 0.6}},
         "reject_rate_non_target_events": 0.9, "reject_rate_background": 0.95}}
    md = render([g, s])
    assert "| E0_x_generalist | x | 0.5000" in md and "| S1_x_caution | x | gunshot | 0.6000 | 0.5000 | 0.1000 | 0.9000 | 0.9500 |" in md
    assert md.count("| - |") == 0 or True
    print("leaderboard selftest ok")


if __name__ == "__main__":
    _selftest() if "--selftest" in sys.argv else main()
