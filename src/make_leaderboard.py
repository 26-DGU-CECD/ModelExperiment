"""Collect results/*/metrics.json into results/LEADERBOARD.md. Schema: docs/metrics_schema.md"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
COLS = ["experiment", "model", "condition", "accuracy", "macro_f1", "danger_recall", "background_fa_rate", "date"]
HEADER = "| 실험명 | 모델 | 조건 | accuracy | macro-F1 | 위험음 recall | background FA율 | 날짜 |"


def fmt(v):
    return f"{v:.4f}" if isinstance(v, float) else str(v if v is not None else "")


def load(results_dir=RESULTS):
    rows = []
    for p in sorted(results_dir.glob("*/metrics.json")):
        m = json.loads(p.read_text(encoding="utf-8"))
        m.setdefault("experiment", p.parent.name)
        rows.append({c: m.get(c) for c in COLS})
    rows.sort(key=lambda r: r["macro_f1"] or 0, reverse=True)
    return rows


def render(rows):
    lines = ["# LEADERBOARD", "", "macro-F1 내림차순. `python src/make_leaderboard.py`로 생성.", "", HEADER, "|" + "---|" * len(COLS)]
    lines += ["| " + " | ".join(fmt(r[c]) for c in COLS) + " |" for r in rows]
    return "\n".join(lines) + "\n"


def main():
    rows = load()
    out = RESULTS / "LEADERBOARD.md"
    out.write_text(render(rows), encoding="utf-8")
    print(f"{len(rows)} experiments -> {out}")


def _selftest():
    rows = [{"experiment": "a", "model": "m", "condition": "generalist", "accuracy": 0.5, "macro_f1": 0.4, "danger_recall": 0.3, "background_fa_rate": 0.1, "date": "2026-01-01"},
            {"experiment": "b", "model": "m", "condition": "ensemble", "accuracy": 0.9, "macro_f1": 0.8, "danger_recall": None, "background_fa_rate": 0.0, "date": "2026-01-02"}]
    rows.sort(key=lambda r: r["macro_f1"] or 0, reverse=True)
    md = render(rows)
    assert md.index("| b |") < md.index("| a |"), "sort by macro_f1 desc"
    assert "| 0.9000 |" in md and "| 2026-01-02 |" in md
    print("selftest ok")


if __name__ == "__main__":
    _selftest() if "--selftest" in sys.argv else main()
