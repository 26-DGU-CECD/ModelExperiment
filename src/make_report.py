"""Result tables, figures and an offline HTML report from results/*/metrics.json only. Re-running regenerates everything.

usage: python src/make_report.py
outputs: docs/results_table.md, docs/results_table.csv, docs/figures/*.png|svg, docs/report.html
Display names / categories: configs/exp_categories.yaml (unmapped experiments are shown by id with a warning).
"""
import csv
import html
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import plotly.io as pio  # noqa: E402
import yaml  # noqa: E402

from src.data import load_labels  # noqa: E402

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
warnings.filterwarnings("ignore")

CFG = yaml.safe_load(open(ROOT / "configs" / "exp_categories.yaml", encoding="utf-8"))
CATS = CFG["categories"]
NAMES = CFG["names"]
LABELS = load_labels()["labels"]
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
CAT_COLORS = {"A": "#4C72B0", "B": "#DD8452", "C": "#55A868", "D": "#C44E52", "E": "#8172B3", "F": "#937860", "G": "#DA8BC3"}
REF = "E0m_v2"
METRICS = [  # key, label, higher_is_better, getter
    ("macro_f1", "macro-F1", True, lambda m: m.get("macro_f1")),
    ("macro_f1_no_carhorn", "macro-F1 (car_horn 제외)", True, lambda m: m.get("macro_f1_no_carhorn")),
    ("emerg_recall", "긴급 recall @FA.005", True, lambda m: (m.get("operating_point") or {}).get("emergency_recall")),
    ("daily_precision", "일상 precision @FA.005", True, lambda m: (m.get("operating_point") or {}).get("daily_precision")),
    ("caution_f1", "주의 F1 @FA.005", True, lambda m: (m.get("operating_point") or {}).get("caution_f1")),
    ("bg_fa", "background 오경보율 (낮을수록 좋음)", False, lambda m: m.get("background_fa_rate")),
    ("strict_fa", "strict background 오경보율 (낮을수록 좋음)", False, lambda m: m.get("bg_fa_strict")),
    ("snr10", "macro-F1 @SNR10", True, lambda m: (m.get("noisy_snr10") or {}).get("macro_f1")),
    ("cost005", "비용 점수 @FA.005 (낮을수록 좋음)", False, lambda m: (m.get("operating_point") or {}).get("cost")),
    ("cost01", "비용 점수 @FA.01 (낮을수록 좋음)", False, lambda m: (m.get("operating_point_001") or {}).get("cost")),
]
BAR_METRICS = ["macro_f1", "macro_f1_no_carhorn", "emerg_recall", "daily_precision", "bg_fa", "strict_fa", "snr10", "cost005"]


def load_results():
    rows = []
    for p in sorted(list(ROOT.glob("results/*/metrics.json")) + list(ROOT.glob("results/naive/*/metrics.json"))):
        eid = p.parent.name
        if eid.startswith("smoke"):
            continue
        m = json.loads(p.read_text(encoding="utf-8"))
        if m.get("label_version") != "v2":
            continue
        naive = m.get("recipe") == "naive"
        if naive and not (eid.startswith(("F_semantic", "F_best", "oracle")) and m.get("condition") == "ensemble"):
            continue  # naive single specialists are not shown
        spec = NAMES.get(eid)
        if spec is None:
            print(f"WARNING: no display name for {eid}; using id", file=sys.stderr)
            spec = {"name": eid, "cat": "D" if m.get("condition") in ("specialist",) else "A"}
        name = spec["name"] + (" (naive 레시피)" if naive else "")
        if spec.get("oracle_any"):
            mm = dict(m)
            mm["macro_f1"] = m["oracle_any"]["macro_f1"]
            mm["macro_f1_no_carhorn"] = m["oracle_any"].get("macro_f1_no_carhorn")
            mm["background_fa_rate"] = m["oracle_any"]["background_fa_rate"]
            mm["bg_fa_strict"] = m["oracle_any"]["bg_fa_strict"]
            m = mm
        compute = spec.get("compute")
        if compute is None and m.get("cascade_test"):
            compute = m["cascade_test"]["expected_macs_G"] / CFG["macs_G"]["efficientat"]
        rows.append({"id": eid + ("@naive" if naive else ""), "eid": eid, "name": name, "cat": spec["cat"], "compute": compute,
                     "ref": bool(spec.get("ref")), "single_specialist": bool(spec.get("single_specialist")), "m": m,
                     **{k: g(m) for k, _, _, g in METRICS}})
    return rows


def fmt(v, nd=3):
    return "-" if v is None else f"{v:.{nd}f}"


# ---------------- tables
def write_tables(rows):
    cols = [("macro_f1", "macro-F1"), ("macro_f1_no_carhorn", "w/o car_horn"), ("emerg_recall", "긴급 recall"), ("daily_precision", "일상 precision"),
            ("caution_f1", "주의 F1"), ("bg_fa", "bg FA"), ("strict_fa", "strict FA"), ("snr10", "SNR10"), ("cost005", "cost@.005"), ("cost01", "cost@.01")]
    lower = {"bg_fa", "strict_fa", "cost005", "cost01"}
    md = ["# 결과표 (test, v2 라벨)", "", "운영점 지표(긴급 recall, 일상 precision, 주의 F1, cost)는 val strict bg FA ≤ 0.005 공통 운영점. "
          "상대 연산량 = 멤버 MACs 합 / EfficientAT 1개(0.128 G per 2 s). 범주 안에서 cost@.005 오름차순. 굵게 = 범주 최고값 / EfficientAT 범용 단일.", ""]
    csv_rows = []
    for cat, cname in CATS.items():
        sub = [r for r in rows if r["cat"] == cat and not r["single_specialist"]]
        if not sub:
            continue
        sub.sort(key=lambda r: (r["cost005"] is None, r["cost005"] or 0))
        best = {}
        for k, _ in cols:
            vals = [r[k] for r in sub if r[k] is not None]
            if vals:
                best[k] = min(vals) if k in lower else max(vals)
        md += [f"## {cat}. {cname}", "", "| 조건 | " + " | ".join(c for _, c in cols) + " | 상대 연산량 | 실험 ID |", "|---|" + "---|" * (len(cols) + 2)]
        for r in sub:
            cells = []
            for k, _ in cols:
                v = fmt(r[k])
                cells.append(f"**{v}**" if r[k] is not None and r[k] == best.get(k) else v)
            name = f"**{r['name']}**" if r["ref"] else r["name"]
            md.append(f"| {name} | " + " | ".join(cells) + f" | {fmt(r['compute'], 2)} | `{r['id']}` |")
            csv_rows.append({"category": cat, "category_name": cname, "name": r["name"], **{c: r[k] for k, c in cols}, "relative_compute": r["compute"], "experiment_id": r["id"]})
        md.append("")
    singles = [r for r in rows if r["single_specialist"]]
    if singles:
        md += ["## 개별 스페셜리스트 (담당 클래스만의 지표; 융합 전)", "", "| 조건 | 담당 macro-F1 | 담당 F1 (vs 범용 리매핑 Δ) | 비담당 거절 | bg 거절 | 실험 ID |", "|---|---|---|---|---|---|"]
        for r in sorted(singles, key=lambda r: r["name"]):
            t = r["m"]["test"]
            vg = t.get("vs_generalist") or {}
            per = ", ".join(f"{c} {v['f1']:.3f}" + (f" ({vg['per_class'][c]['delta']:+.3f})" if vg and c in vg.get("per_class", {}) else "") for c, v in t["own_class"].items())
            md.append(f"| {r['name']} | {fmt(r['macro_f1'])} | {per} | {fmt(t.get('reject_rate_non_target_events'))} | {fmt(t.get('reject_rate_background'))} | `{r['id']}` |")
            csv_rows.append({"category": r["cat"], "category_name": CATS[r["cat"]] + " (단독)", "name": r["name"], "macro-F1": r["macro_f1"], "relative_compute": r["compute"], "experiment_id": r["id"]})
    (ROOT / "docs" / "results_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    keys = ["category", "category_name", "name"] + [c for _, c in cols] + ["relative_compute", "experiment_id"]
    with open(ROOT / "docs" / "results_table.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in csv_rows:
            w.writerow({k: r.get(k) for k in keys})


# ---------------- figures (matplotlib) + plotly specs
def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def fig_metric_bars(rows, key, label, higher):
    sub = [r for r in rows if r[key] is not None and not r["single_specialist"] and not r["eid"].startswith("overlap")]
    sub.sort(key=lambda r: (r["cat"], -(r[key] if higher else -r[key])))
    ref = next((r[key] for r in rows if r["ref"]), None)
    h = max(4, 0.32 * len(sub) + 1.5)
    fig, ax = plt.subplots(figsize=(11, h))
    y = np.arange(len(sub))
    ax.barh(y, [r[key] for r in sub], color=[CAT_COLORS[r["cat"]] for r in sub])
    ax.set_yticks(y)
    ax.set_yticklabels([f"[{r['cat']}] {r['name']}" for r in sub], fontsize=8)
    ax.invert_yaxis()
    for i, r in enumerate(sub):
        ax.text(r[key], i, f" {r[key]:.3f}", va="center", fontsize=7)
    if ref is not None:
        ax.axvline(ref, ls="--", color="k", lw=1, label=f"EfficientAT 범용 단일 = {ref:.3f}")
        ax.legend(loc="lower right", fontsize=8)
    ax.set_xlabel(label + ("" if higher else "  ← 낮을수록 좋음"))
    ax.set_title(label)
    vals = [r[key] for r in sub]
    ax.set_xlim(0, max(vals) * 1.15 if vals else 1)
    ax.grid(axis="x", alpha=0.3)
    save(fig, f"bar_{key}")
    pf = go.Figure(go.Bar(x=[r[key] for r in sub], y=[r["name"] for r in sub], orientation="h", marker_color=[CAT_COLORS[r["cat"]] for r in sub],
                          customdata=[[r["id"], CATS[r["cat"]]] for r in sub], text=[f"{r[key]:.3f}" for r in sub], textposition="outside",
                          hovertemplate="%{y}<br>%{x:.4f}<br>%{customdata[1]}<br>id: %{customdata[0]}<extra></extra>"))
    if ref is not None:
        pf.add_vline(x=ref, line_dash="dash", line_color="black", annotation_text=f"EfficientAT 범용 단일 {ref:.3f}")
    pf.update_layout(title=label + ("" if higher else " (낮을수록 좋음)"), height=max(400, 26 * len(sub) + 120), margin=dict(l=420), yaxis=dict(autorange="reversed"))
    pf._cats = [r["cat"] for r in sub]
    return pf


def fig_key_comparison(rows):
    by = {r["eid"]: r for r in rows}
    ids = [i for i in CFG["key_comparison"] if i in by]
    mets = [("macro_f1", "macro-F1"), ("emerg_recall", "긴급 recall"), ("daily_precision", "일상 precision"), ("one_minus_bgfa", "1 - bg FA")]
    data = {i: {"macro_f1": by[i]["macro_f1"], "emerg_recall": by[i]["emerg_recall"], "daily_precision": by[i]["daily_precision"],
                "one_minus_bgfa": 1 - by[i]["bg_fa"] if by[i]["bg_fa"] is not None else None} for i in ids}
    fig, ax = plt.subplots(figsize=(12, 5.5))
    w = 0.8 / max(len(ids), 1)
    x = np.arange(len(mets))
    for j, i in enumerate(ids):
        vals = [data[i][k] or 0 for k, _ in mets]
        ax.bar(x + j * w - 0.4 + w / 2, vals, w, label=by[i]["name"], color=CAT_COLORS[by[i]["cat"]], alpha=0.6 + 0.4 * (j % 2))
        for xx, v in zip(x + j * w - 0.4 + w / 2, vals):
            ax.text(xx, v + 0.003, f"{v:.3f}", ha="center", fontsize=6, rotation=90)
    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l in mets])
    ax.set_ylim(0.75, 1.0)
    ax.set_title("핵심 비교: 범용 단일 vs 범용 앙상블 vs 스페셜리스트 앙상블 (test)")
    ax.legend(fontsize=7, loc="lower left")
    ax.grid(axis="y", alpha=0.3)
    save(fig, "key_comparison")
    pf = go.Figure()
    for i in ids:
        pf.add_bar(name=by[i]["name"], x=[l for _, l in mets], y=[data[i][k] for k, _ in mets], customdata=[[i]] * len(mets),
                   hovertemplate="%{fullData.name}<br>%{x}: %{y:.4f}<br>id: %{customdata[0]}<extra></extra>")
    pf.update_layout(barmode="group", title="핵심 비교 (test)", yaxis=dict(range=[0.75, 1.0]), height=520, legend=dict(orientation="h", y=-0.25))
    return pf


def fig_specialist_delta(rows):
    pts = []
    for r in rows:
        if not r["single_specialist"]:
            continue
        vg = r["m"]["test"].get("vs_generalist")
        if not vg:
            continue
        for c, v in vg["per_class"].items():
            if c != "other":
                pts.append((c, v["delta"], r["name"], r["id"]))
    if not pts:
        return None
    classes = [c for c in LABELS if any(p[0] == c for p in pts)]
    names = sorted({p[2] for p in pts})
    cmap = plt.get_cmap("tab20")
    fig, ax = plt.subplots(figsize=(13, 6))
    for k, n in enumerate(names):
        ps = [p for p in pts if p[2] == n]
        ax.scatter([classes.index(p[0]) + (k - len(names) / 2) * 0.04 for p in ps], [p[1] for p in ps], label=n, color=cmap(k % 20), s=36)
    ax.axhline(0, color="k", lw=1)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=30)
    ax.set_ylabel("담당 클래스 F1 Δ (스페셜리스트 - 범용 리매핑), test")
    ax.set_title("스페셜리스트 특화 이득: 담당 클래스별 Δ")
    ax.legend(fontsize=6, ncol=2, loc="lower left")
    ax.grid(alpha=0.3)
    save(fig, "specialist_delta")
    pf = go.Figure()
    for n in names:
        ps = [p for p in pts if p[2] == n]
        pf.add_scatter(x=[p[0] for p in ps], y=[p[1] for p in ps], mode="markers", name=n, customdata=[[p[3]] for p in ps],
                       hovertemplate="%{fullData.name}<br>%{x}: Δ %{y:+.4f}<br>id: %{customdata[0]}<extra></extra>")
    pf.add_hline(y=0, line_color="black")
    pf.update_layout(title="스페셜리스트 담당 클래스 Δ (test)", height=560, legend=dict(font=dict(size=9)))
    return pf


def fig_heatmap(rows):
    by = {r["eid"]: r for r in rows}
    ids = [i for i in ["E0m_v2", "G_mn10_seed1", "A1_efficientat_scratch", "E2k_v2", "E1k_v2", "G_mn04", "G_dymn10",
                       "F_generalist_stacking", "F_seed_stacking", "F_mn10_stacked", "F_mn04_stacked", "F_semantic_stacked", "F_cascade_E2k"] if i in by]
    mat = np.array([[by[i]["m"]["test"]["per_class"][c]["f1"] for c in LABELS] for i in ids])
    fig, ax = plt.subplots(figsize=(13, 0.45 * len(ids) + 2))
    im = ax.imshow(mat, cmap="viridis", vmin=0.4, vmax=1.0, aspect="auto")
    ax.set_xticks(range(len(LABELS)))
    ax.set_xticklabels(LABELS, rotation=35, ha="right")
    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels([by[i]["name"] for i in ids], fontsize=8)
    for a in range(len(ids)):
        for b in range(len(LABELS)):
            ax.text(b, a, f"{mat[a, b]:.2f}", ha="center", va="center", fontsize=6, color="w" if mat[a, b] < 0.8 else "k")
    fig.colorbar(im, ax=ax, label="F1 (test)")
    ax.set_title("클래스별 F1: 단일 범용 + 주요 앙상블")
    save(fig, "per_class_heatmap")
    pf = go.Figure(go.Heatmap(z=mat, x=LABELS, y=[by[i]["name"] for i in ids], zmin=0.4, zmax=1.0, colorscale="Viridis", text=np.round(mat, 2), texttemplate="%{text}",
                              customdata=np.array([[i] * len(LABELS) for i in ids]), hovertemplate="%{y}<br>%{x}: %{z:.4f}<br>id: %{customdata}<extra></extra>"))
    pf.update_layout(title="클래스별 F1 (test)", height=40 * len(ids) + 200, margin=dict(l=420), yaxis=dict(autorange="reversed"))
    return pf


def fig_noise(rows):
    by = {r["eid"]: r for r in rows}
    ids = [i for i in CFG["main_conditions"] if i in by]
    xs = ["clean", "SNR20", "SNR15", "SNR10"]
    fig, ax = plt.subplots(figsize=(10, 6))
    pf = go.Figure()
    for i in ids:
        m = by[i]["m"]
        ys = [m["macro_f1"]] + [(m.get(k) or {}).get("macro_f1") for k in ("noisy_snr20", "noisy_snr15", "noisy_snr10")]
        ax.plot(xs, ys, marker="o", label=by[i]["name"], color=CAT_COLORS[by[i]["cat"]], alpha=0.85)
        pf.add_scatter(x=xs, y=ys, mode="lines+markers", name=by[i]["name"], customdata=[[i]] * 4, hovertemplate="%{fullData.name}<br>%{x}: %{y:.4f}<br>id: %{customdata[0]}<extra></extra>")
    ax.set_ylabel("macro-F1 (test)")
    ax.set_title("노이즈 강건성 (MUSAN test noise)")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    save(fig, "noise_robustness")
    pf.update_layout(title="노이즈 강건성", height=520, legend=dict(font=dict(size=9)))
    return pf


def fig_cascade(rows):
    by = {r["eid"]: r for r in rows}
    ids = [i for i in ("F_cascade_E2k", "F_cascade_E0m") if i in by and by[i]["m"].get("cascade_sweep")]
    if not ids:
        return None
    ref_cost = (by[REF]["m"].get("operating_point") or {}).get("cost") if REF in by else None
    fig, ax = plt.subplots(figsize=(9, 5.5))
    pf = go.Figure()
    for i in ids:
        sw = by[i]["m"]["cascade_sweep"]
        xs = [s["saving_bg_stream_pct"] for s in sw]
        ys = [s["cost_005"] for s in sw]
        ax.plot(xs, ys, marker="o", label=by[i]["name"])
        for s in sw:
            ax.annotate(f"{s['gate_recall_target']}", (s["saving_bg_stream_pct"], s["cost_005"]), fontsize=7, xytext=(3, 3), textcoords="offset points")
        pf.add_scatter(x=xs, y=ys, mode="lines+markers+text", text=[str(s["gate_recall_target"]) for s in sw], textposition="top center", name=by[i]["name"],
                       customdata=[[i, s["gate_recall_target"], s["bg_pass_rate"]] for s in sw],
                       hovertemplate="%{fullData.name}<br>gate recall %{customdata[1]}<br>saving %{x:.1f}%<br>cost@.005 %{y:.3f}<br>bg pass %{customdata[2]:.3f}<br>id: %{customdata[0]}<extra></extra>")
    if ref_cost is not None:
        ax.axhline(ref_cost, ls="--", color="k", lw=1, label=f"EfficientAT 범용 단일 cost {ref_cost:.3f}")
        pf.add_hline(y=ref_cost, line_dash="dash", line_color="black", annotation_text="EfficientAT 범용 단일")
    ax.set_xlabel("연산 절감률 % (순수 background 스트림 기준, EfficientAT 단독 대비)")
    ax.set_ylabel("cost @FA.005 (낮을수록 좋음)")
    ax.set_title("캐스케이드: 게이트 recall 목표별 연산 절감 vs 비용")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    save(fig, "cascade_tradeoff")
    pf.update_layout(title="캐스케이드 절감 vs 비용", xaxis_title="연산 절감률 % (bg 스트림)", yaxis_title="cost @FA.005", height=500)
    return pf


def fig_opoints(rows):
    by = {r["eid"]: r for r in rows}
    ids = [i for i in CFG["main_conditions"] if i in by and by[i]["cost005"] is not None]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = np.arange(len(ids))
    ax.bar(x - 0.2, [by[i]["cost005"] for i in ids], 0.4, label="cost @strict FA ≤ 0.005")
    ax.bar(x + 0.2, [by[i]["cost01"] or 0 for i in ids], 0.4, label="cost @strict FA ≤ 0.01")
    for xx, i in zip(x, ids):
        ax.text(xx - 0.2, by[i]["cost005"], f"{by[i]['cost005']:.3f}", ha="center", fontsize=6)
        if by[i]["cost01"] is not None:
            ax.text(xx + 0.2, by[i]["cost01"], f"{by[i]['cost01']:.3f}", ha="center", fontsize=6)
    ax.set_xticks(x)
    ax.set_xticklabels([by[i]["name"] for i in ids], rotation=25, ha="right", fontsize=7)
    ax.set_ylabel("비용 점수 (낮을수록 좋음)")
    ax.set_title("운영점 비교: strict FA 0.005 vs 0.01")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    save(fig, "operating_points")
    pf = go.Figure()
    pf.add_bar(name="cost @FA.005", x=[by[i]["name"] for i in ids], y=[by[i]["cost005"] for i in ids], customdata=[[i] for i in ids], hovertemplate="%{x}<br>%{y:.3f}<br>id: %{customdata[0]}<extra></extra>")
    pf.add_bar(name="cost @FA.01", x=[by[i]["name"] for i in ids], y=[by[i]["cost01"] for i in ids], customdata=[[i] for i in ids], hovertemplate="%{x}<br>%{y:.3f}<br>id: %{customdata[0]}<extra></extra>")
    pf.update_layout(barmode="group", title="운영점 비교", height=560, xaxis=dict(tickangle=-25, tickfont=dict(size=9)))
    return pf


# ---------------- HTML
def html_report(rows, figs):
    summary = (ROOT / "docs" / "results_summary.md").read_text(encoding="utf-8") if (ROOT / "docs" / "results_summary.md").exists() else ""
    concl = summary.split("## 결론 후보")[1].split("\n## ")[0] if "## 결론 후보" in summary else ""
    concl_html = "<table><tr>" + "</tr><tr>".join("<td>" + "</td><td>".join(html.escape(c.strip()) for c in line.strip("|").split("|")) + "</td>"
                                                 for line in concl.strip().splitlines() if line.startswith("|") and not line.startswith("|---")) + "</tr></table>"
    cols = [("name", "조건"), ("cat", "범주"), ("macro_f1", "macro-F1"), ("macro_f1_no_carhorn", "w/o car_horn"), ("emerg_recall", "긴급 recall"), ("daily_precision", "일상 precision"),
            ("caution_f1", "주의 F1"), ("bg_fa", "bg FA"), ("strict_fa", "strict FA"), ("snr10", "SNR10"), ("cost005", "cost@.005"), ("cost01", "cost@.01"), ("compute", "상대 연산량"), ("id", "실험 ID")]
    trs = []
    for r in sorted(rows, key=lambda r: (r["cat"], r["cost005"] is None, r["cost005"] or 0)):
        if r["single_specialist"]:
            continue
        tds = []
        for k, _ in cols:
            v = r[k]
            if k == "cat":
                v = f"{r['cat']} {CATS[r['cat']]}"
            s = html.escape(str(v)) if not isinstance(v, float) else f"{v:.3f}"
            cls = ' class="idcol"' if k == "id" else ""
            tds.append(f"<td{cls} data-v=\"{v if isinstance(v, (int, float)) else html.escape(str(v))}\">{s}</td>")
        trs.append(f"<tr data-cat=\"{r['cat']}\"{' class=ref' if r['ref'] else ''}>" + "".join(tds) + "</tr>")
    checks = "".join(f"<label><input type=checkbox class=catbox value={c} checked> {c} {html.escape(n)}</label> " for c, n in CATS.items())
    fig_html = []
    for key, (title, pf, png) in figs.items():
        div = pio.to_html(pf, include_plotlyjs=False, full_html=False, div_id=f"fig_{key}")
        fig_html.append(f"<section id='sec_{key}'><h3>{html.escape(title)}</h3>{div}<p class=links>정적 이미지: <a href='figures/{png}.png'>PNG</a> · <a href='figures/{png}.svg'>SVG</a></p></section>")
    cats_js = json.dumps({key: getattr(pf, "_cats", None) for key, (_, pf, _) in figs.items()})
    protocol = ("데이터: retrina0678/miimo-audio-dataset, 2 s 클립 80,049개(원본 29,040 + 증강 51,009), 16 kHz mono. "
                "분할: source_file 단위 StratifiedGroupKFold(5), fold 0 test / 1 val / 2-4 train, val·test는 원본 클립만 (train 48,060 / val 5,762 / test 5,877). "
                "라벨 v2: 14 클래스(baby_cry를 출처로 cry/baby_cry 분리, S_103 alarm → fire_alarm 재라벨). "
                "학습: 전 모델 MUSAN train noise 온라인 증강(p 0.5, SNR 5-20), 최대 20 epoch, 클래스당 3000 균형 샘플링, mixup 0.3. "
                "스페셜리스트 레시피 v2: 같은 모델의 범용 체크포인트에서 warm start, 백본 lr 2e-5 / 헤드 1e-3, 14라벨 균형 샘플링, 그룹 objective 가중치. "
                "운영점: val에서 클래스별 임계값 + FA 유발 클래스 greedy 인상으로 strict bg FA ≤ 0.005 (보조 0.01), test 적용. 비용 = 긴급 FN 5, 일상 FP 2, 그 외 1 (클립당 평균). "
                "noisy = test × MUSAN test noise SNR 20/15/10.")
    page = f"""<!doctype html><html lang=ko><head><meta charset=utf-8><title>소리인식 키링 스페셜리스트 앙상블 — 결과 리포트</title>
<style>body{{font-family:'Malgun Gothic',sans-serif;margin:24px;max-width:1500px}} table{{border-collapse:collapse;font-size:12px}} td,th{{border:1px solid #ccc;padding:3px 6px}}
th{{cursor:pointer;background:#f3f3f3;position:sticky;top:0}} tr.ref{{font-weight:bold;background:#fffbe6}} .idcol{{color:#888;font-family:monospace}} .hideid .idcol{{display:none}}
nav a{{margin-right:12px}} section{{margin-top:36px}} .links{{font-size:12px;color:#555}} #controls{{position:sticky;top:0;background:#fff;padding:8px 0;border-bottom:1px solid #ddd;z-index:5}}</style>
<script>{pio.get_plotlyjs() if hasattr(pio, 'get_plotlyjs') else __import__('plotly').offline.get_plotlyjs()}</script></head><body>
<h1>소리인식 키링 — 스페셜리스트 앙상블 결과 리포트</h1>
<nav><a href="#key">핵심 비교</a><a href="#metrics">지표별</a><a href="#spec">스페셜리스트 진단</a><a href="#noise">노이즈/캐스케이드</a><a href="#table">전체 표</a><a href="#setup">실험 설정</a><a href="#concl">결론 후보</a></nav>
<div id=controls>범주 표시: {checks} &nbsp; <label><input type=checkbox id=showid checked> 실험 ID 표시</label></div>
<section id=setup><h2>실험 설정 요약</h2><p>{html.escape(protocol)}</p></section>
<section id=concl><h2>결론 후보 (docs/results_summary.md)</h2>{concl_html}</section>
<section id=key><h2>핵심 비교</h2>{fig_html[0]}{fig_html[1] if len(fig_html) > 1 else ''}</section>
<section id=metrics><h2>지표별 (범주 색, A→G)</h2>{''.join(f for f in fig_html[2:2 + len(BAR_METRICS)])}</section>
<section id=spec><h2>스페셜리스트 진단</h2>{''.join(fig_html[2 + len(BAR_METRICS):4 + len(BAR_METRICS)])}</section>
<section id=noise><h2>노이즈 / 캐스케이드</h2>{''.join(fig_html[4 + len(BAR_METRICS):])}</section>
<section id=table><h2>전체 표 (열 클릭 정렬)</h2><table id=tbl><thead><tr>{''.join(f'<th data-k={k}>{html.escape(l)}</th>' for k, l in cols)}</tr></thead><tbody>{''.join(trs)}</tbody></table></section>
<script>
const FIGCATS = {cats_js};
function applyCats(){{const on=new Set([...document.querySelectorAll('.catbox:checked')].map(b=>b.value));
 document.querySelectorAll('#tbl tbody tr').forEach(tr=>tr.style.display=on.has(tr.dataset.cat)?'':'none');
 for(const [k,cats] of Object.entries(FIGCATS)){{ if(!cats) continue; const el=document.getElementById('fig_'+k); if(!el||!el.data) continue;
   const d=el.data[0]; if(!d||!d._full_y){{d._full_y=d.y.slice(); d._full_x=d.x.slice(); d._full_c=d.marker.color.slice(); d._full_cd=d.customdata.slice(); d._full_t=d.text.slice();}}
   const keep=cats.map((c,i)=>on.has(c)?i:-1).filter(i=>i>=0);
   Plotly.restyle(el,{{y:[keep.map(i=>d._full_y[i])],x:[keep.map(i=>d._full_x[i])],'marker.color':[keep.map(i=>d._full_c[i])],customdata:[keep.map(i=>d._full_cd[i])],text:[keep.map(i=>d._full_t[i])]}},[0]); }} }}
document.querySelectorAll('.catbox').forEach(b=>b.addEventListener('change',applyCats));
document.getElementById('showid').addEventListener('change',e=>document.body.classList.toggle('hideid',!e.target.checked));
document.querySelectorAll('#tbl th').forEach((th,i)=>th.addEventListener('click',()=>{{const tb=th.closest('table').tBodies[0];const rows=[...tb.rows];const asc=th.dataset.asc!=='1';th.dataset.asc=asc?'1':'0';
 rows.sort((a,b)=>{{const x=a.cells[i].dataset.v,y=b.cells[i].dataset.v;const nx=parseFloat(x),ny=parseFloat(y);const c=(isNaN(nx)||isNaN(ny))?x.localeCompare(y):nx-ny;return asc?c:-c;}});rows.forEach(r=>tb.appendChild(r));}}));
</script></body></html>"""
    (ROOT / "docs" / "report.html").write_text(page, encoding="utf-8")


def main():
    rows = load_results()
    print(f"{len(rows)} results loaded")
    write_tables(rows)
    figs = {}
    figs["key"] = ("핵심 비교 (6조건 × 4지표)", fig_key_comparison(rows), "key_comparison")
    figs["opoints"] = ("운영점 비교 (cost @0.005 vs @0.01)", fig_opoints(rows), "operating_points")
    for key, label, higher, _ in METRICS:
        if key in BAR_METRICS:
            figs[f"bar_{key}"] = (label, fig_metric_bars(rows, key, label, higher), f"bar_{key}")
    sd = fig_specialist_delta(rows)
    if sd is not None:
        figs["delta"] = ("스페셜리스트 담당 클래스 Δ", sd, "specialist_delta")
    figs["heat"] = ("클래스별 F1 히트맵", fig_heatmap(rows), "per_class_heatmap")
    figs["noise"] = ("노이즈 강건성", fig_noise(rows), "noise_robustness")
    cf = fig_cascade(rows)
    if cf is not None:
        figs["cascade"] = ("캐스케이드 절감 vs 비용", cf, "cascade_tradeoff")
    html_report(rows, figs)
    # links in results_summary.md
    rs = ROOT / "docs" / "results_summary.md"
    if rs.exists():
        txt = rs.read_text(encoding="utf-8")
        link = "\n## 리포트\n\n- 인터랙티브 HTML: [docs/report.html](report.html) (오프라인 단일 파일)\n- 표: [results_table.md](results_table.md) / [results_table.csv](results_table.csv)\n- 그림: [docs/figures/](figures/) (PNG 200dpi + SVG)\n"
        if "## 리포트" not in txt:
            rs.write_text(txt.rstrip() + "\n" + link, encoding="utf-8")
    print("-> docs/results_table.md, docs/results_table.csv, docs/figures/*, docs/report.html")


if __name__ == "__main__":
    main()
