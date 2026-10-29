"""Highlights report: docs/report_highlights.html + docs/figures/highlights/ (PNG 300 dpi + SVG).

Everything is recomputed from saved predictions CSVs (no training): source_file cluster bootstrap (95% CI), operating curves,
group confusion, PR-AUC, calibration, error overlap, source-origin performance, FA/hour, Pareto, radar.
Conditions / names / colors: configs/highlights.yaml.  Run via: python src/make_report.py --highlights
"""
import html
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)

import matplotlib  # noqa: E402
import matplotlib.ticker  # noqa: E402

matplotlib.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import plotly.io as pio  # noqa: E402
import yaml  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

from src.data import load_labels  # noqa: E402
from src.opoint import CAUTION, DAILY, EMERG, decide  # noqa: E402

warnings.filterwarnings("ignore")
CFG = yaml.safe_load(open(ROOT / "configs" / "highlights.yaml", encoding="utf-8"))
LABELS = load_labels()["labels"]
IDX = {c: i for i, c in enumerate(LABELS)}
BG = IDX["background"]
NC = len(LABELS)
FIG = ROOT / "docs" / "figures" / "highlights"
FIG.mkdir(parents=True, exist_ok=True)
FONT = "Pretendard" if any(f.name == "Pretendard" for f in fm.fontManager.ttflist) else "Malgun Gothic"
INK, INK2, INK3, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
EMPH = CFG["emphasis_color"]
REF, EMP = CFG["reference"], CFG["emphasis"]
plt.rcParams.update({"font.family": FONT, "axes.unicode_minus": False, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": INK3,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK, "axes.titleweight": "bold", "axes.titlesize": 13,
                     "grid.color": GRID, "grid.linewidth": 0.8, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
                     "legend.frameon": False, "legend.fontsize": 8})
EMERG5 = ["alarm", "fire_alarm", "scream", "cry", "car_horn"]
GROUP_OF = {}
for c in LABELS:
    GROUP_OF[c] = "긴급" if c in EMERG else ("일상" if c in DAILY else ("주의" if c in CAUTION else "배경"))
G4 = ["긴급", "주의", "일상", "배경"]
METRICS = [("macro_f1", "macro-F1", True), ("macro_f1_no_carhorn", "macro-F1 (car_horn 제외)", True), ("emerg_recall", "긴급 recall @FA.005", True),
           ("daily_precision", "일상 precision @FA.005", True), ("caution_f1", "주의 F1 @FA.005", True), ("bg_fa", "background 오경보율", False),
           ("strict_fa", "strict background 오경보율", False), ("snr10", "macro-F1 @SNR10", True), ("cost005", "비용 점수 @FA.005", False)]


# ---------------------------------------------------------------- data
def rel_manifest_path(fp):
    return fp[len("data/miimo/"):] if fp.startswith("data/miimo/") else fp


class Cond:
    def __init__(self, spec, manifest, strict_set, noisy_map):
        self.id, self.name, self.group, self.compute = spec["id"], spec["name"], spec["group"], spec.get("compute")
        d = ROOT / "results" / self.id
        self.meta = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
        if self.compute is None and self.meta.get("cascade_test"):
            self.compute = self.meta["cascade_test"]["expected_macs_G"] / 0.128
        self.color = EMPH if self.id == EMP else CFG["groups"][self.group]["color"]
        t = pd.read_csv(d / "predictions_test.csv", low_memory=False)
        self.fp = t["filepath"].to_numpy()
        self.y = t["label_fine"].map(IDX).to_numpy()
        self.P = t[[f"prob_{c}" for c in LABELS]].to_numpy(dtype=float)
        self.P = np.nan_to_num(self.P)
        self.pred = self.P.argmax(1)
        op = self.meta.get("operating_point") or {}
        self.taus = op.get("thresholds")
        self.pred_op = decide(self.P, self.taus, op.get("scale", 1.0)) if self.taus else self.pred
        op1 = self.meta.get("operating_point_001") or {}
        self.pred_op1 = decide(self.P, op1["thresholds"], op1.get("scale", 1.0)) if op1.get("thresholds") else self.pred_op
        self.src = manifest.loc[self.fp, "source_file"].to_numpy()
        self.origin = manifest.loc[self.fp, "source_origin"].to_numpy()
        self.strict = np.array([f in strict_set for f in self.fp])
        self.noisy = {}
        for snr in (20, 15, 10):
            p = d / f"predictions_noisy_snr{snr}.csv"
            if p.exists():
                n = pd.read_csv(p, low_memory=False)
                Pn = np.nan_to_num(n[[f"prob_{c}" for c in LABELS]].to_numpy(dtype=float))
                self.noisy[snr] = {"y": n["label_fine"].map(IDX).to_numpy(), "pred": Pn.argmax(1), "src": np.array([noisy_map.get(f, "?") for f in n["filepath"]])}


def load_conditions():
    man = pd.read_csv(ROOT / "data" / "splits" / "manifest.csv", low_memory=False).set_index("filepath")
    strict = pd.read_csv(ROOT / "data" / "splits" / "bg_strict.csv")
    strict_set = set(strict.loc[strict["strict"], "filepath"])
    nm = pd.read_csv(ROOT / "data" / "splits" / "manifest_test_noisy.csv", low_memory=False)
    noisy_map = dict(zip(nm["filepath"], nm["source_file"]))
    conds = []
    for spec in CFG["conditions"]:
        if not (ROOT / "results" / spec["id"] / "predictions_test.csv").exists():
            if spec.get("optional"):
                print(f"skip optional {spec['id']} (no results yet)")
                continue
            raise FileNotFoundError(spec["id"])
        conds.append(Cond(spec, man, strict_set, noisy_map))
    return conds, man


# ---------------------------------------------------------------- weighted metrics + bootstrap
def wcm(y, pred, w, n=NC):
    return np.bincount(y * n + pred, weights=w, minlength=n * n).reshape(n, n)


def f1_from_cm(cm):
    tp = np.diag(cm)
    fp = cm.sum(0) - tp
    fn = cm.sum(1) - tp
    return np.where(tp > 0, 2 * tp / np.maximum(2 * tp + fp + fn, 1e-9), 0.0)


def metrics_from(c, w, w10=None):
    cm = wcm(c.y, c.pred, w)
    cmo = wcm(c.y, c.pred_op, w)
    f1 = f1_from_cm(cm)
    f1o = f1_from_cm(cmo)
    em = [IDX[x] for x in EMERG]
    da = [IDX[x] for x in DAILY]
    ca = [IDX[x] for x in CAUTION]
    bgw = w[c.y == BG]
    sw = w[(c.y == BG) & c.strict]
    cost = 0.0
    for t in range(NC):
        for p in range(NC):
            if t == p or cmo[t, p] == 0:
                continue
            cost += cmo[t, p] * (5.0 if t in em else (2.0 if p in da else 1.0))
    out = {"macro_f1": f1.mean(), "macro_f1_no_carhorn": np.mean([f1[i] for i in range(NC) if LABELS[i] != "car_horn"]),
           "emerg_recall": cmo[em][:, em].trace() / max(cmo[em].sum(), 1e-9), "daily_precision": cmo[:, da][da].trace() / max(cmo[:, da].sum(), 1e-9),
           "caution_f1": f1o[ca].mean(), "bg_fa": 1 - cm[BG, BG] / max(bgw.sum(), 1e-9),
           "strict_fa": (w * ((c.y == BG) & c.strict & (c.pred != BG))).sum() / max(sw.sum(), 1e-9), "cost005": cost / max(w.sum(), 1e-9)}
    if 10 in c.noisy and w10 is not None:
        out["snr10"] = f1_from_cm(wcm(c.noisy[10]["y"], c.noisy[10]["pred"], w10)).mean()
    else:
        out["snr10"] = None
    return out


def bootstrap(conds, n_boot, seed):
    rng = np.random.default_rng(seed)
    sources = np.unique(conds[0].src)
    sidx = {s: i for i, s in enumerate(sources)}
    src_i = {c.id: np.array([sidx[s] for s in c.src]) for c in conds}
    src10 = {c.id: np.array([sidx.get(s, -1) for s in c.noisy[10]["src"]]) if 10 in c.noisy else None for c in conds}
    samples = {c.id: [] for c in conds}
    point = {c.id: metrics_from(c, np.ones(len(c.y)), np.ones(len(c.noisy[10]["y"])) if 10 in c.noisy else None) for c in conds}
    for _ in range(n_boot):
        draw = rng.integers(0, len(sources), len(sources))
        mult = np.bincount(draw, minlength=len(sources)).astype(float)
        for c in conds:
            w = mult[src_i[c.id]]
            w10 = mult[np.clip(src10[c.id], 0, None)] * (src10[c.id] >= 0) if src10[c.id] is not None else None
            samples[c.id].append(metrics_from(c, w, w10))
    out = {}
    for c in conds:
        res = {}
        for k, _, _ in METRICS:
            vals = np.array([s[k] for s in samples[c.id] if s[k] is not None], dtype=float)
            res[k] = {"point": point[c.id][k], "lo": float(np.percentile(vals, 2.5)) if len(vals) else None, "hi": float(np.percentile(vals, 97.5)) if len(vals) else None}
        if c.id != REF:  # paired difference vs reference (same source resample)
            res["diff_vs_ref"] = {}
            for k, _, _ in METRICS:
                a = [s[k] for s in samples[c.id]]
                b = [s[k] for s in samples[REF]]
                d = np.array([x - y for x, y in zip(a, b) if x is not None and y is not None], dtype=float)
                if len(d):
                    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
                    res["diff_vs_ref"][k] = {"point": (point[c.id][k] or 0) - (point[REF][k] or 0), "lo": lo, "hi": hi, "significant": bool(lo > 0 or hi < 0)}
        res["n_boot"], res["cluster"], res["n_sources"] = n_boot, "source_file", int(len(sources))
        (ROOT / "results" / c.id / "bootstrap.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        out[c.id] = res
    return out


# ---------------------------------------------------------------- helpers
def save(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def style_plotly(pf, height=None, title=None):
    pf.update_layout(template="plotly_white", font=dict(family=f"{FONT}, Malgun Gothic, sans-serif", size=12, color=INK2), title_font=dict(size=16, color=INK),
                     paper_bgcolor=SURFACE, plot_bgcolor=SURFACE, margin=dict(t=64, r=24, b=48), hoverlabel=dict(bgcolor="white", font_size=12), legend=dict(bgcolor="rgba(0,0,0,0)"))
    pf.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, showline=False)
    pf.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, showline=False)
    if height:
        pf.update_layout(height=height)
    if title:
        pf.update_layout(title=title)
    return pf


def ci_text(b, nd=3):
    return f"{b['point']:.{nd}f} [{b['lo']:.{nd}f}, {b['hi']:.{nd}f}]" if b and b.get("lo") is not None else (f"{b['point']:.{nd}f}" if b and b.get("point") is not None else "-")


def group_bands(ax, conds, y_positions, x=-0.012):
    """left-side group labels with gaps between groups"""
    for g in dict.fromkeys(c.group for c in conds):
        ys = [y_positions[i] for i, c in enumerate(conds) if c.group == g]
        ax.text(x, (min(ys) + max(ys)) / 2, CFG["groups"][g]["label"], transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=8.5, fontweight="bold",
                color=CFG["groups"][g]["color"], rotation=90)


def ypos(conds):
    """bar positions with a gap between groups"""
    pos, cur, prev = [], 0.0, None
    for c in conds:
        if prev is not None and c.group != prev:
            cur += 0.7
        pos.append(cur)
        cur += 1
        prev = c.group
    return np.array(pos)


# ---------------------------------------------------------------- figures
def fig_metric_bar(conds, boot, key, label, higher, fname):
    vals = [boot[c.id][key]["point"] for c in conds]
    lo = [boot[c.id][key]["lo"] for c in conds]
    hi = [boot[c.id][key]["hi"] for c in conds]
    ok = [v is not None for v in vals]
    pos = ypos(conds)
    fig, ax = plt.subplots(figsize=(10.5, 0.46 * len(conds) + 2.2))
    for i, c in enumerate(conds):
        if not ok[i]:
            continue
        ax.barh(pos[i], vals[i], height=0.62, color=c.color, edgecolor=SURFACE, linewidth=1.5)
        if lo[i] is not None:
            ax.errorbar(vals[i], pos[i], xerr=[[vals[i] - lo[i]], [hi[i] - vals[i]]], fmt="none", ecolor=INK, elinewidth=1, capsize=3)
            ax.text(max(hi[i], vals[i]), pos[i], f"  {vals[i]:.3f} [{lo[i]:.3f}, {hi[i]:.3f}]", va="center", fontsize=7, color=INK2)
    ax.set_yticks(pos)
    ax.set_yticklabels([c.name for c in conds], fontsize=8.5)
    ax.invert_yaxis()
    group_bands(ax, conds, pos, x=-0.60)
    ref = boot[REF][key]["point"] if REF in boot else None
    v = [x for x in vals if x is not None] + [x for x in hi if x is not None] + [x for x in lo if x is not None]
    lo_ax = max(0, min(v) - (max(v) - min(v)) * 0.6) if higher else 0
    hi_ax = max(v) + (max(v) - min(v) + 1e-6) * 0.75
    ax.set_xlim(lo_ax, hi_ax)
    if ref is not None:
        ax.axvline(ref, ls="--", color=INK, lw=1)
        ax.text(ref, -0.9, f"기준선 {ref:.3f}", ha="center", va="bottom", fontsize=8, color=INK)
    sub = "축 범위 확대" if lo_ax > 0 else ""
    ax.set_xlabel(label + ("" if higher else " (낮을수록 좋음)") + (f"  ·  {sub}" if sub else ""))
    ax.set_title(label + " — source_file 클러스터 부트스트랩 95% CI", loc="left")
    ax.grid(axis="x")
    save(fig, fname)
    pf = go.Figure()
    for i, c in enumerate(conds):
        if not ok[i]:
            continue
        pf.add_bar(y=[c.name], x=[vals[i]], orientation="h", marker_color=c.color, name=c.name, showlegend=False,
                   error_x=dict(type="data", symmetric=False, array=[hi[i] - vals[i]] if hi[i] is not None else [0], arrayminus=[vals[i] - lo[i]] if lo[i] is not None else [0], color=INK, thickness=1),
                   customdata=[[c.id, CFG["groups"][c.group]["label"], lo[i], hi[i]]],
                   hovertemplate="%{y}<br>" + label + " %{x:.4f}  [%{customdata[2]:.3f}, %{customdata[3]:.3f}]<br>%{customdata[1]}<br>id: %{customdata[0]}<extra></extra>")
    if ref is not None:
        pf.add_vline(x=ref, line_dash="dash", line_color=INK, annotation_text=f"기준선 {ref:.3f}", annotation_position="top")
    style_plotly(pf, 42 * len(conds) + 150, label)
    pf.update_layout(margin=dict(l=420), yaxis=dict(autorange="reversed", categoryorder="array", categoryarray=[c.name for c in conds][::-1]), xaxis=dict(range=[lo_ax, hi_ax], title=label + ("" if higher else " (낮을수록 좋음)")), bargap=0.35)
    return pf


def fig_headline(conds, boot):
    """three headline charts: macro-F1, emergency recall, cost"""
    out = {}
    for key, label, higher, fname in [("macro_f1", "macro-F1", True, "headline_macro_f1"), ("emerg_recall", "긴급 recall @FA.005", True, "headline_emerg_recall"), ("cost005", "비용 점수 @FA.005", False, "headline_cost")]:
        out[fname] = (label, fig_metric_bar(conds, boot, key, label, higher, fname), fname)
    return out


def sweep_curves(c, grid):
    """event-vs-bg threshold sweep: (strict_fa, emerg_recall, daily_precision, daily_recall) per threshold"""
    ev = np.delete(np.arange(NC), BG)
    s = 1 - c.P[:, BG]
    arg_ev = ev[c.P[:, ev].argmax(1)]
    em = np.isin(c.y, [IDX[x] for x in EMERG])
    da_idx = [IDX[x] for x in DAILY]
    da = np.isin(c.y, da_idx)
    bgs = (c.y == BG) & c.strict
    rows = []
    for t in grid:
        pred = np.where(s >= t, arg_ev, BG)
        pda = np.isin(pred, da_idx)
        rows.append((float((pred[bgs] != BG).mean()), float((pred[em] == c.y[em]).mean()), float((c.y[pda] == pred[pda]).mean()) if pda.any() else np.nan, float((pred[da] == c.y[da]).mean())))
    return np.array(rows)


def fig_operating_curves(conds):
    grid = np.linspace(0.0, 0.999, 300)
    curves = {c.id: sweep_curves(c, grid) for c in conds}
    # dominance of the emphasised condition on the emergency curve (interpolated on a common strict-FA grid)
    fa_grid = np.linspace(0.002, 0.05, 40)
    def rec_at(cid):
        cu = curves[cid]
        o = np.argsort(cu[:, 0])
        return np.interp(fa_grid, cu[o, 0], cu[o, 1])
    dom = EMP in curves and all(np.all(rec_at(EMP) >= rec_at(c.id) - 1e-9) for c in conds if c.id != EMP)
    cap = ("강조 조건이 strict FA 0.002~0.05 전 구간에서 다른 모든 조건 이상 → 지배" if dom else "강조 조건은 전 구간 지배 아님 (구간별로 순위 바뀜)")
    figs = {}
    for which, fname, xl, yl, xi, yi in [("emerg", "curve_emergency", "strict background 오경보율", "긴급 recall", 0, 1), ("daily", "curve_daily", "일상 recall", "일상 precision", 3, 2)]:
        fig, ax = plt.subplots(figsize=(8.5, 6))
        pf = go.Figure()
        for c in conds:
            cu = curves[c.id]
            lw = 2.6 if c.id == EMP else 1.4
            ax.plot(cu[:, xi], cu[:, yi], color=c.color, lw=lw, label=c.name, alpha=0.95 if c.id in (EMP, REF) else 0.75)
            pf.add_scatter(x=cu[:, xi], y=cu[:, yi], mode="lines", name=c.name, line=dict(color=c.color, width=3 if c.id == EMP else 1.6),
                           customdata=[[c.id, t] for t in grid], hovertemplate="%{fullData.name}<br>" + xl + " %{x:.4f}<br>" + yl + " %{y:.4f}<br>임계값 %{customdata[1]:.3f}<extra></extra>")
        if which == "emerg":
            for v, lab in ((0.005, "운영점 0.005"), (0.01, "운영점 0.01")):
                ax.axvline(v, ls=":", color=INK3, lw=1)
                ax.text(v, 1.003, lab, va="bottom", ha="center", fontsize=7.5, color=INK3, clip_on=False)
                pf.add_vline(x=v, line_dash="dot", line_color=INK3, annotation_text=lab, annotation_position="top")
            ax.set_xlim(0, 0.06)
            ax.set_ylim(0.7, 1.0)
            pf.update_xaxes(range=[0, 0.06])
            pf.update_yaxes(range=[0.7, 1.0])
            ax.set_title("운영 곡선: 긴급 recall vs strict 오경보율 (bg 임계값 sweep, test)", loc="left")
            ax.text(0.0, -0.12, cap, transform=ax.transAxes, fontsize=8, color=INK2)
        else:
            ax.set_xlim(0.6, 1.0)
            ax.set_ylim(0.6, 1.0)
            pf.update_xaxes(range=[0.6, 1.0])
            pf.update_yaxes(range=[0.6, 1.0])
            ax.set_title("운영 곡선: 일상 precision vs recall (bg 임계값 sweep, test)", loc="left")
        ax.set_xlabel(xl + ("  ·  축 범위 확대" if which == "daily" else ""))
        ax.set_ylabel(yl)
        ax.grid(alpha=0.6)
        ax.legend(fontsize=7, loc="lower right")
        save(fig, fname)
        style_plotly(pf, 560, ("긴급 recall vs strict 오경보율" if which == "emerg" else "일상 precision vs recall") + " (bg 임계값 sweep)")
        pf.update_layout(xaxis_title=xl, yaxis_title=yl, legend=dict(font=dict(size=10)))
        figs[fname] = (("운영 곡선 · 긴급 (" + cap + ")") if which == "emerg" else "운영 곡선 · 일상", pf, fname)
    return figs, cap


def fig_pr_auc(conds):
    groups = [("긴급", EMERG), ("주의", CAUTION), ("일상", DAILY)]
    vals = {c.id: [] for c in conds}
    for c in conds:
        for _, labs in groups:
            ids = [IDX[x] for x in labs]
            vals[c.id].append(average_precision_score(np.isin(c.y, ids), c.P[:, ids].max(1)))
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(groups))
    w = 0.8 / len(conds)
    pf = go.Figure()
    for j, c in enumerate(conds):
        ax.bar(x + j * w - 0.4 + w / 2, vals[c.id], w * 0.9, color=c.color, label=c.name, edgecolor=SURFACE)
        pf.add_bar(name=c.name, x=[g for g, _ in groups], y=vals[c.id], marker_color=c.color, customdata=[[c.id]] * 3, hovertemplate="%{fullData.name}<br>%{x} PR-AUC %{y:.4f}<br>id: %{customdata[0]}<extra></extra>")
    ax.set_xticks(x)
    ax.set_xticklabels([g for g, _ in groups])
    ax.set_ylim(0.85, 1.0)
    ax.set_ylabel("PR-AUC (그룹 점수 = 그룹 클래스 확률 최대값)  ·  축 범위 확대")
    ax.set_title("그룹별 PR-AUC (임계값 비의존)", loc="left")
    ax.legend(fontsize=7, ncol=2)
    ax.grid(axis="y")
    save(fig, "group_pr_auc")
    style_plotly(pf, 520, "그룹별 PR-AUC (임계값 비의존)")
    pf.update_layout(barmode="group", yaxis=dict(range=[0.85, 1.0]), legend=dict(font=dict(size=10)))
    return pf, vals


def group_cm(c, pred):
    gi = {g: i for i, g in enumerate(G4)}
    yg = np.array([gi[GROUP_OF[LABELS[i]]] for i in c.y])
    pg = np.array([gi[GROUP_OF[LABELS[i]]] for i in pred])
    cm = np.bincount(yg * 4 + pg, minlength=16).reshape(4, 4).astype(float)
    return cm / np.maximum(cm.sum(1, keepdims=True), 1)


def fig_group_confusion(conds):
    by = {c.id: c for c in conds}
    pair = [by[i] for i in (REF, EMP) if i in by]
    fig, axes = plt.subplots(1, len(pair), figsize=(5.2 * len(pair), 4.8))
    axes = np.atleast_1d(axes)
    for ax, c in zip(axes, pair):
        cm = group_cm(c, c.pred_op)
        ax.imshow(cm, cmap="Blues", vmin=0, vmax=1)
        for i in range(4):
            for j in range(4):
                ax.text(j, i, f"{cm[i, j]:.3f}", ha="center", va="center", fontsize=9, color="w" if cm[i, j] > 0.6 else INK)
        for j in (2, 3):  # emergency -> daily / background: worst for safety
            ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1, 1, fill=False, edgecolor=EMPH, lw=2.5))
        ax.set_xticks(range(4))
        ax.set_xticklabels(G4)
        ax.set_yticks(range(4))
        ax.set_yticklabels(G4)
        ax.set_xlabel("예측 그룹")
        ax.set_ylabel("정답 그룹")
        ax.set_title(c.name, fontsize=10, loc="left")
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle("그룹 혼동 행렬 (행 정규화, 운영점 @FA.005 판정, test) — 테두리 = 긴급 → 일상/배경 오판", x=0.01, ha="left", fontsize=12, fontweight="bold")
    save(fig, "group_confusion")
    pf = go.Figure()
    from plotly.subplots import make_subplots
    pf = make_subplots(rows=1, cols=len(pair), subplot_titles=[c.name for c in pair], horizontal_spacing=0.12)
    for k, c in enumerate(pair):
        cm = group_cm(c, c.pred_op)
        pf.add_trace(go.Heatmap(z=cm, x=G4, y=G4, zmin=0, zmax=1, colorscale="Blues", text=np.round(cm, 3), texttemplate="%{text}", showscale=k == len(pair) - 1,
                                hovertemplate="정답 %{y} → 예측 %{x}: %{z:.4f}<extra>" + c.id + "</extra>"), row=1, col=k + 1)
        pf.update_yaxes(autorange="reversed", row=1, col=k + 1)
    style_plotly(pf, 460, "그룹 혼동 행렬 (운영점 @FA.005, 행 정규화)")
    # cross-group misjudgement bar: emergency -> daily or bg
    rates = [(c, group_cm(c, c.pred_op)[0, 2] + group_cm(c, c.pred_op)[0, 3]) for c in conds]
    pos = ypos(conds)
    fig, ax = plt.subplots(figsize=(10, 0.46 * len(conds) + 2))
    for i, (c, r) in enumerate(rates):
        ax.barh(pos[i], r, height=0.62, color=c.color, edgecolor=SURFACE)
        ax.text(r, pos[i], f"  {r:.3f}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(pos)
    ax.set_yticklabels([c.name for c in conds], fontsize=8.5)
    ax.invert_yaxis()
    group_bands(ax, conds, pos, x=-0.60)
    ax.set_xlabel("긴급 정답이 일상 또는 배경으로 판정된 비율 (낮을수록 좋음)")
    ax.set_title("교차 그룹 오판율: 긴급 → 일상/배경 (운영점 @FA.005)", loc="left")
    ax.grid(axis="x")
    save(fig, "cross_group_miss")
    pb = go.Figure(go.Bar(y=[c.name for c, _ in rates], x=[r for _, r in rates], orientation="h", marker_color=[c.color for c, _ in rates], text=[f"{r:.3f}" for _, r in rates], textposition="outside",
                          customdata=[[c.id] for c, _ in rates], hovertemplate="%{y}<br>%{x:.4f}<br>id: %{customdata[0]}<extra></extra>"))
    style_plotly(pb, 42 * len(conds) + 140, "교차 그룹 오판율: 긴급 → 일상/배경")
    pb.update_layout(margin=dict(l=420), yaxis=dict(autorange="reversed"), xaxis_title="비율 (낮을수록 좋음)")
    return pf, pb


def fig_emergency_classes(conds):
    figs = {}
    for which, fname in (("recall", "emergency_recall_by_class"), ("precision", "emergency_precision_by_class")):
        vals = {}
        for c in conds:
            cm = wcm(c.y, c.pred_op, np.ones(len(c.y)))
            v = []
            for cl in EMERG5:
                i = IDX[cl]
                v.append(cm[i, i] / max(cm[i].sum(), 1e-9) if which == "recall" else cm[i, i] / max(cm[:, i].sum(), 1e-9))
            vals[c.id] = v
        n_car = int((conds[0].y == IDX["car_horn"]).sum())
        xt = [f"{cl} (n={n_car})" if cl == "car_horn" else cl for cl in EMERG5]
        fig, ax = plt.subplots(figsize=(11, 5))
        x = np.arange(len(EMERG5))
        w = 0.8 / len(conds)
        pf = go.Figure()
        for j, c in enumerate(conds):
            ax.bar(x + j * w - 0.4 + w / 2, vals[c.id], w * 0.9, color=c.color, label=c.name, edgecolor=SURFACE)
            pf.add_bar(name=c.name, x=xt, y=vals[c.id], marker_color=c.color, customdata=[[c.id]] * len(xt), hovertemplate="%{fullData.name}<br>%{x}: %{y:.4f}<br>id: %{customdata[0]}<extra></extra>")
        ax.set_xticks(x)
        ax.set_xticklabels(xt)
        ax.set_ylim(0.3, 1.0)
        ax.set_ylabel(f"긴급 클래스 {which} @FA.005  ·  축 범위 확대")
        ax.set_title(f"긴급 클래스별 {which} (운영점 판정, test)", loc="left")
        ax.legend(fontsize=7, ncol=2, loc="lower left")
        ax.grid(axis="y")
        save(fig, fname)
        style_plotly(pf, 520, f"긴급 클래스별 {which} (운영점 @FA.005)")
        pf.update_layout(barmode="group", yaxis=dict(range=[0.3, 1.0]), legend=dict(font=dict(size=10)))
        figs[fname] = (f"긴급 클래스별 {which}", pf, fname)
    return figs


def fig_heatmap(conds):
    n_car = int((conds[0].y == IDX["car_horn"]).sum())
    xl = [f"{c}\n(n={n_car})" if c == "car_horn" else c for c in LABELS]
    mat = np.array([f1_from_cm(wcm(c.y, c.pred, np.ones(len(c.y)))) for c in conds])
    fig, ax = plt.subplots(figsize=(13, 0.5 * len(conds) + 2.2))
    im = ax.imshow(mat, cmap="Blues", vmin=0.4, vmax=1.0, aspect="auto")
    for a in range(len(conds)):
        for b in range(NC):
            ax.text(b, a, f"{mat[a, b]:.2f}", ha="center", va="center", fontsize=6.5, color="w" if mat[a, b] > 0.85 else INK)
    ax.set_xticks(range(NC))
    ax.set_xticklabels(xl, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(conds)))
    ax.set_yticklabels([c.name for c in conds], fontsize=8)
    fig.colorbar(im, ax=ax, label="F1 (test, argmax)")
    ax.set_title("클래스별 F1 (colorbar 0.4–1.0 고정)", loc="left")
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, "per_class_f1_heatmap")
    pf = go.Figure(go.Heatmap(z=mat, x=[x.replace("\n", " ") for x in xl], y=[c.name for c in conds], zmin=0.4, zmax=1.0, colorscale="Blues", text=np.round(mat, 2), texttemplate="%{text}",
                              customdata=np.array([[c.id] * NC for c in conds]), hovertemplate="%{y}<br>%{x}: F1 %{z:.4f}<br>id: %{customdata}<extra></extra>"))
    style_plotly(pf, 44 * len(conds) + 220, "클래스별 F1 (test)")
    pf.update_layout(margin=dict(l=420), yaxis=dict(autorange="reversed"))
    return pf


def fig_noise(conds):
    xs = ["clean", "SNR20", "SNR15", "SNR10"]
    series = {}
    for c in conds:
        ys = [f1_from_cm(wcm(c.y, c.pred, np.ones(len(c.y)))).mean()]
        for snr in (20, 15, 10):
            ys.append(f1_from_cm(wcm(c.noisy[snr]["y"], c.noisy[snr]["pred"], np.ones(len(c.noisy[snr]["y"])))).mean() if snr in c.noisy else np.nan)
        series[c.id] = ys
    fig, ax = plt.subplots(figsize=(9, 5.5))
    pf = go.Figure()
    for c in conds:
        ax.plot(xs, series[c.id], marker="o", color=c.color, lw=2.4 if c.id == EMP else 1.5, label=c.name)
        pf.add_scatter(x=xs, y=series[c.id], mode="lines+markers", name=c.name, line=dict(color=c.color, width=3 if c.id == EMP else 1.6), marker=dict(size=8),
                       customdata=[[c.id]] * 4, hovertemplate="%{fullData.name}<br>%{x}: %{y:.4f}<br>id: %{customdata[0]}<extra></extra>")
    ax.set_ylabel("macro-F1 (argmax)  ·  축 범위 확대")
    ax.set_ylim(0.75, 0.95)
    ax.set_title("노이즈 강건성 (MUSAN test noise)", loc="left")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.6)
    save(fig, "noise_robustness")
    style_plotly(pf, 520, "노이즈 강건성")
    pf.update_layout(yaxis=dict(range=[0.75, 0.95], title="macro-F1"), legend=dict(font=dict(size=10)))
    drops = [(c, series[c.id][0] - series[c.id][3]) for c in conds if not np.isnan(series[c.id][3])]
    pos = ypos([c for c, _ in drops])
    fig, ax = plt.subplots(figsize=(10, 0.46 * len(drops) + 2))
    for i, (c, d) in enumerate(drops):
        ax.barh(pos[i], d, height=0.62, color=c.color, edgecolor=SURFACE)
        ax.text(d, pos[i], f"  {d:.3f}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(pos)
    ax.set_yticklabels([c.name for c, _ in drops], fontsize=8.5)
    ax.invert_yaxis()
    group_bands(ax, [c for c, _ in drops], pos, x=-0.60)
    ax.set_xlabel("macro-F1 하락폭 (clean - SNR10, 낮을수록 좋음)")
    ax.set_title("노이즈 하락폭", loc="left")
    ax.grid(axis="x")
    save(fig, "noise_drop")
    pd_ = go.Figure(go.Bar(y=[c.name for c, _ in drops], x=[d for _, d in drops], orientation="h", marker_color=[c.color for c, _ in drops], text=[f"{d:.3f}" for _, d in drops], textposition="outside",
                           customdata=[[c.id] for c, _ in drops], hovertemplate="%{y}<br>하락폭 %{x:.4f}<br>id: %{customdata[0]}<extra></extra>"))
    style_plotly(pd_, 42 * len(drops) + 140, "노이즈 하락폭 (clean - SNR10)")
    pd_.update_layout(margin=dict(l=420), yaxis=dict(autorange="reversed"), xaxis_title="macro-F1 하락폭 (낮을수록 좋음)")
    return pf, pd_


def fig_pareto(conds, boot):
    pts = [(c, c.compute, boot[c.id]["cost005"]["point"]) for c in conds if c.compute is not None and boot[c.id]["cost005"]["point"] is not None]
    pts.sort(key=lambda t: t[1])
    front, best = [], np.inf
    for c, x, y in pts:
        if y < best - 1e-12:
            front.append((x, y))
            best = y
    fig, ax = plt.subplots(figsize=(9, 6))
    for c, x, y in pts:
        ax.scatter(x, y, s=120 if c.id == EMP else 70, color=c.color, edgecolor=SURFACE, linewidth=1.5, zorder=3)
        ax.annotate(c.name, (x, y), fontsize=7, xytext=(6, 4), textcoords="offset points", color=INK2)
    if front:
        ax.plot([f[0] for f in front], [f[1] for f in front], color=INK3, lw=1.2, ls="--", zorder=2, label="파레토 프론트")
    ax.set_xscale("log")
    ticks = [0.4, 0.6, 1.0, 1.5, 2.0, 3.0]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"×{t:g}" for t in ticks])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("상대 연산량 (× EfficientAT 1개, log)")
    ax.set_ylabel("비용 점수 @FA.005 (낮을수록 좋음)")
    ax.set_title("정확도–효율 파레토 (test)", loc="left")
    ax.grid(alpha=0.6, which="both")
    ax.legend(fontsize=8)
    save(fig, "pareto_cost_compute")
    pf = go.Figure()
    for c, x, y in pts:
        b = boot[c.id]["cost005"]
        pf.add_scatter(x=[x], y=[y], mode="markers+text", text=[c.name], textposition="top right", textfont=dict(size=9), name=c.name, marker=dict(size=16 if c.id == EMP else 11, color=c.color, line=dict(width=1.5, color=SURFACE)),
                       error_y=dict(type="data", symmetric=False, array=[b["hi"] - y], arrayminus=[y - b["lo"]], color=INK3, thickness=1) if b.get("lo") is not None else None,
                       customdata=[[c.id]], hovertemplate="%{text}<br>연산량 ×%{x:.2f}<br>cost %{y:.4f}<br>id: %{customdata[0]}<extra></extra>", showlegend=False)
    if front:
        pf.add_scatter(x=[f[0] for f in front], y=[f[1] for f in front], mode="lines", line=dict(color=INK3, dash="dash"), name="파레토 프론트")
    style_plotly(pf, 600, "정확도–효율 파레토")
    pf.update_layout(xaxis=dict(type="log", title="상대 연산량 (× EfficientAT 1개)"), yaxis_title="비용 점수 @FA.005 (낮을수록 좋음)")
    return pf, front


def fig_calibration(conds):
    bins = np.linspace(0, 1, 11)
    fig, ax = plt.subplots(figsize=(7, 6.5))
    pf = go.Figure()
    ece = []
    for c in conds:
        conf = c.P.max(1)
        corr = (c.pred == c.y).astype(float)
        xs, ys, e = [], [], 0.0
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (conf > lo) & (conf <= hi)
            if m.sum() == 0:
                continue
            xs.append(conf[m].mean())
            ys.append(corr[m].mean())
            e += m.mean() * abs(corr[m].mean() - conf[m].mean())
        ece.append((c, e))
        ax.plot(xs, ys, marker="o", ms=4, color=c.color, lw=2.2 if c.id == EMP else 1.3, label=f"{c.name} (ECE {e:.3f})")
        pf.add_scatter(x=xs, y=ys, mode="lines+markers", name=f"{c.name} (ECE {e:.3f})", line=dict(color=c.color, width=3 if c.id == EMP else 1.5), customdata=[[c.id]] * len(xs),
                       hovertemplate="%{fullData.name}<br>confidence %{x:.3f} → accuracy %{y:.3f}<extra></extra>")
    ax.plot([0, 1], [0, 1], ls=":", color=INK3)
    pf.add_scatter(x=[0, 1], y=[0, 1], mode="lines", line=dict(color=INK3, dash="dot"), name="완벽 보정", showlegend=False)
    ax.set_xlabel("예측 confidence (max prob)")
    ax.set_ylabel("실제 정확도")
    ax.set_title("Reliability diagram (test, argmax)", loc="left")
    ax.legend(fontsize=6.5, loc="upper left")
    ax.grid(alpha=0.6)
    save(fig, "calibration_reliability")
    style_plotly(pf, 600, "Reliability diagram")
    pf.update_layout(xaxis_title="confidence", yaxis_title="accuracy", legend=dict(font=dict(size=9)))
    pos = ypos([c for c, _ in ece])
    fig, ax = plt.subplots(figsize=(10, 0.46 * len(ece) + 2))
    for i, (c, e) in enumerate(ece):
        ax.barh(pos[i], e, height=0.62, color=c.color, edgecolor=SURFACE)
        ax.text(e, pos[i], f"  {e:.3f}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(pos)
    ax.set_yticklabels([c.name for c, _ in ece], fontsize=8.5)
    ax.invert_yaxis()
    group_bands(ax, [c for c, _ in ece], pos, x=-0.60)
    ax.set_xlabel("ECE (10 bins, 낮을수록 좋음)")
    ax.set_title("Expected Calibration Error", loc="left")
    ax.grid(axis="x")
    save(fig, "calibration_ece")
    pe = go.Figure(go.Bar(y=[c.name for c, _ in ece], x=[e for _, e in ece], orientation="h", marker_color=[c.color for c, _ in ece], text=[f"{e:.3f}" for _, e in ece], textposition="outside",
                          customdata=[[c.id] for c, _ in ece], hovertemplate="%{y}<br>ECE %{x:.4f}<br>id: %{customdata[0]}<extra></extra>"))
    style_plotly(pe, 42 * len(ece) + 140, "ECE")
    pe.update_layout(margin=dict(l=420), yaxis=dict(autorange="reversed"), xaxis_title="ECE (낮을수록 좋음)")
    return pf, pe, ece


def wrong_set(eid, specialist=False):
    p = pd.read_csv(ROOT / "results" / eid / "predictions_test.csv", low_memory=False)
    if specialist:
        truth = p["label_group"] if "label_group" in p else p["label_fine"]
        return set(p.loc[p["pred"] != truth, "filepath"])
    return set(p.loc[p["pred"] != p["label_fine"], "filepath"])


def fig_venn(sets_cfg):
    from matplotlib.patches import Circle
    fig, axes = plt.subplots(1, len(sets_cfg), figsize=(5.6 * len(sets_cfg), 5.2))
    axes = np.atleast_1d(axes)
    summary = []
    pf_rows = []
    for ax, sc in zip(axes, sets_cfg):
        ids = sc["ids"]
        if not all((ROOT / "results" / i / "predictions_test.csv").exists() for i in ids):
            ax.set_title(sc["title"] + " (결과 없음)")
            ax.axis("off")
            continue
        A, B, C = [wrong_set(i, sc.get("specialist", False)) for i in ids]
        regions = {"A": len(A - B - C), "B": len(B - A - C), "C": len(C - A - B), "AB": len((A & B) - C), "AC": len((A & C) - B), "BC": len((B & C) - A), "ABC": len(A & B & C)}
        union = len(A | B | C)
        cols = ["#2a78d6", "#eb6834", "#1baf7a"]
        centers = [(0, 0.3), (-0.45, -0.45), (0.45, -0.45)]
        for (x, y), col in zip(centers, cols):
            ax.add_patch(Circle((x, y), 0.85, alpha=0.28, color=col, lw=0))
        txt = {"A": (0, 0.85), "B": (-0.9, -0.75), "C": (0.9, -0.75), "AB": (-0.5, 0.1), "AC": (0.5, 0.1), "BC": (0, -0.8), "ABC": (0, -0.15)}
        for k, (x, y) in txt.items():
            ax.text(x, y, str(regions[k]), ha="center", va="center", fontsize=10, color=INK, fontweight="bold" if k == "ABC" else "normal")
        for (x, y), i, col in zip([(0, 1.35), (-1.25, -1.35), (1.25, -1.35)], ids, cols):
            ax.text(x, y, f"{i}\n틀림 {len({'A': A, 'B': B, 'C': C}[chr(65 + ids.index(i))])}", ha="center", va="center", fontsize=8, color=col)
        ax.set_xlim(-1.9, 1.9)
        ax.set_ylim(-1.8, 1.7)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"{sc['title']}  (합집합 {union}, 셋 다 틀림 {regions['ABC']} = {regions['ABC'] / max(union, 1):.0%})", fontsize=10)
        summary.append((sc["title"], union, regions["ABC"], regions))
        pf_rows.append((sc["title"], regions))
    fig.suptitle("오류 중복: 틀린 test 클립 집합의 3원 벤 다이어그램", x=0.01, ha="left", fontsize=12, fontweight="bold")
    save(fig, "error_overlap_venn")
    pf = go.Figure()
    keys = ["A", "B", "C", "AB", "AC", "BC", "ABC"]
    for title, regions in pf_rows:
        pf.add_bar(name=title, x=["A만", "B만", "C만", "A∩B", "A∩C", "B∩C", "A∩B∩C"], y=[regions[k] for k in keys], hovertemplate="%{fullData.name}<br>%{x}: %{y}<extra></extra>")
    style_plotly(pf, 460, "오류 중복 영역별 클립 수 (A/B/C = 멤버 순서)")
    pf.update_layout(barmode="group", yaxis_title="틀린 클립 수")
    return pf, summary


def fig_specialist_delta(man):
    """all single specialists with vs_generalist: per own class delta + cluster bootstrap CI"""
    rng = np.random.default_rng(CFG["bootstrap"]["seed"])
    pts = []
    for mp in sorted(ROOT.glob("results/*/metrics.json")):
        m = json.loads(mp.read_text(encoding="utf-8"))
        if m.get("condition") != "specialist" or m.get("label_version") != "v2" or not m.get("test", {}).get("vs_generalist"):
            continue
        eid = mp.parent.name
        gen = m["test"]["vs_generalist"]["generalist"]
        sp = pd.read_csv(mp.parent / "predictions_test.csv", low_memory=False)
        gp = pd.read_csv(ROOT / "results" / gen / "predictions_test.csv", low_memory=False)
        own = [c for c in m["classes"] if c != "other"]
        truth = sp["label_group"].to_numpy()
        spred = sp["pred"].to_numpy()
        gpred = gp["pred"].where(gp["pred"].isin(own), "other").to_numpy()
        src = man.loc[sp["filepath"].to_numpy(), "source_file"].to_numpy()
        srcs, inv = np.unique(src, return_inverse=True)
        def f1s(w):
            out = []
            for c in own:
                t = truth == c
                tp_s = (w * (t & (spred == c))).sum(); fp_s = (w * (~t & (spred == c))).sum(); fn_s = (w * (t & (spred != c))).sum()
                tp_g = (w * (t & (gpred == c))).sum(); fp_g = (w * (~t & (gpred == c))).sum(); fn_g = (w * (t & (gpred != c))).sum()
                f_s = 2 * tp_s / max(2 * tp_s + fp_s + fn_s, 1e-9); f_g = 2 * tp_g / max(2 * tp_g + fp_g + fn_g, 1e-9)
                out.append(f_s - f_g)
            return np.array(out)
        point = f1s(np.ones(len(truth)))
        boots = []
        for _ in range(min(CFG["bootstrap"]["n"], 400)):
            draw = rng.integers(0, len(srcs), len(srcs))
            boots.append(f1s(np.bincount(draw, minlength=len(srcs)).astype(float)[inv]))
        boots = np.array(boots)
        lo, hi = np.percentile(boots, 2.5, axis=0), np.percentile(boots, 97.5, axis=0)
        for k, c in enumerate(own):
            pts.append({"class": c, "delta": float(point[k]), "lo": float(lo[k]), "hi": float(hi[k]), "spec": eid})
    if not pts:
        return None, []
    classes = [c for c in LABELS if any(p["class"] == c for p in pts)]
    specs = sorted({p["spec"] for p in pts})
    cmap = plt.get_cmap("tab20")
    fig, ax = plt.subplots(figsize=(14, 6.5))
    for k, s in enumerate(specs):
        ps = [p for p in pts if p["spec"] == s]
        xs = [classes.index(p["class"]) + (k - len(specs) / 2) * 0.045 for p in ps]
        ax.errorbar(xs, [p["delta"] for p in ps], yerr=[[p["delta"] - p["lo"] for p in ps], [p["hi"] - p["delta"] for p in ps]], fmt="o", ms=5, color=cmap(k % 20), ecolor=cmap(k % 20), elinewidth=0.8, capsize=2, label=s, alpha=0.9)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=30)
    ax.set_ylabel("담당 클래스 F1 Δ (스페셜리스트 - 범용 리매핑), 95% CI")
    ax.set_title("스페셜리스트 특화 이득 — 개별 스페셜리스트 전부, source_file 부트스트랩 CI", loc="left")
    ax.legend(fontsize=6, ncol=3, loc="lower left")
    ax.grid(alpha=0.5)
    save(fig, "specialist_delta_ci")
    pf = go.Figure()
    for s in specs:
        ps = [p for p in pts if p["spec"] == s]
        pf.add_scatter(x=[p["class"] for p in ps], y=[p["delta"] for p in ps], mode="markers", name=s, marker=dict(size=9),
                       error_y=dict(type="data", symmetric=False, array=[p["hi"] - p["delta"] for p in ps], arrayminus=[p["delta"] - p["lo"] for p in ps], thickness=1),
                       hovertemplate="%{fullData.name}<br>%{x}: Δ %{y:+.4f}<extra></extra>")
    pf.add_hline(y=0, line_color=INK)
    style_plotly(pf, 620, "스페셜리스트 담당 클래스 Δ (95% CI)")
    pf.update_layout(legend=dict(font=dict(size=9)))
    return pf, pts


def fig_source_origin(conds):
    origins = ["aihub", "esc50", "donateacry", "other"]
    vals = {}
    for c in conds:
        v = []
        for o in origins:
            m = c.origin == o
            if m.sum() == 0:
                v.append(np.nan)
                continue
            cm = wcm(c.y[m], c.pred[m], np.ones(int(m.sum())))
            present = cm.sum(1) > 0
            v.append(f1_from_cm(cm)[present].mean())
        vals[c.id] = v
    ns = {o: int((conds[0].origin == o).sum()) for o in origins}
    xt = [f"{o}\n(n={ns[o]})" for o in origins]
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(origins))
    w = 0.8 / len(conds)
    pf = go.Figure()
    for j, c in enumerate(conds):
        ax.bar(x + j * w - 0.4 + w / 2, vals[c.id], w * 0.9, color=c.color, label=c.name, edgecolor=SURFACE)
        pf.add_bar(name=c.name, x=[t.replace("\n", " ") for t in xt], y=vals[c.id], marker_color=c.color, customdata=[[c.id]] * 4, hovertemplate="%{fullData.name}<br>%{x}: macro-F1 %{y:.4f}<br>id: %{customdata[0]}<extra></extra>")
    ax.set_xticks(x)
    ax.set_xticklabels(xt)
    ax.set_ylim(0.6, 1.0)
    ax.set_ylabel("macro-F1 (해당 출처에 존재하는 클래스만)  ·  축 범위 확대")
    ax.set_title("출처별 성능 (test, argmax) — 녹음 환경 일반화", loc="left")
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    ax.grid(axis="y")
    save(fig, "source_origin_macro_f1")
    style_plotly(pf, 520, "출처별 macro-F1")
    pf.update_layout(barmode="group", yaxis=dict(range=[0.6, 1.0]), legend=dict(font=dict(size=10)))
    return pf


def fig_fa_per_hour(conds, boot):
    rows = []
    for c in conds:
        bg = c.y == BG
        fa = float((c.pred_op[bg] != BG).mean())
        sfa = float((c.pred_op[bg & c.strict] != BG).mean())
        rows.append((c, fa * 3600, sfa * 3600))
    pos = ypos(conds)
    fig, ax = plt.subplots(figsize=(10.5, 0.5 * len(conds) + 2.2))
    for i, (c, a, s) in enumerate(rows):
        ax.barh(pos[i] - 0.17, a, height=0.32, color=c.color, edgecolor=SURFACE, label="전체 background" if i == 0 else None)
        ax.barh(pos[i] + 0.17, s, height=0.32, color=c.color, alpha=0.45, edgecolor=SURFACE, label="strict background" if i == 0 else None)
        ax.text(a, pos[i] - 0.17, f"  {a:.0f}/h", va="center", fontsize=7, color=INK2)
        ax.text(s, pos[i] + 0.17, f"  {s:.0f}/h", va="center", fontsize=7, color=INK2)
    ax.set_yticks(pos)
    ax.set_yticklabels([c.name for c in conds], fontsize=8.5)
    ax.invert_yaxis()
    group_bands(ax, conds, pos, x=-0.60)
    ax.set_xlabel("시간당 오경보 횟수 (낮을수록 좋음) = 오경보율 × 3600 판정/시간")
    ax.set_title("FA/hour 환산 (운영점 @FA.005 판정)", loc="left")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x")
    save(fig, "fa_per_hour")
    pf = go.Figure()
    pf.add_bar(name="전체 background", y=[c.name for c, _, _ in rows], x=[a for _, a, _ in rows], orientation="h", marker_color=[c.color for c, _, _ in rows], customdata=[[c.id] for c, _, _ in rows], hovertemplate="%{y}<br>%{x:.0f} /h<br>id: %{customdata[0]}<extra></extra>")
    pf.add_bar(name="strict background", y=[c.name for c, _, _ in rows], x=[s for _, _, s in rows], orientation="h", marker_color=[c.color for c, _, _ in rows], opacity=0.45, customdata=[[c.id] for c, _, _ in rows], hovertemplate="%{y}<br>%{x:.0f} /h<br>id: %{customdata[0]}<extra></extra>")
    style_plotly(pf, 48 * len(conds) + 160, "FA/hour 환산")
    pf.update_layout(barmode="group", margin=dict(l=420), yaxis=dict(autorange="reversed"), xaxis_title="시간당 오경보 횟수 (낮을수록 좋음)")
    return pf, rows


def fig_radar(conds, boot):
    top = sorted([c for c in conds if boot[c.id]["cost005"]["point"] is not None], key=lambda c: boot[c.id]["cost005"]["point"])[:4]
    axes_lab = ["macro-F1", "긴급 recall", "일상 precision", "1 - bg FA", "SNR10", "효율 (1/연산량, 정규화)"]
    comp = [c.compute or 1.0 for c in top]
    def vec(c):
        b = boot[c.id]
        return [b["macro_f1"]["point"], b["emerg_recall"]["point"], b["daily_precision"]["point"], 1 - b["bg_fa"]["point"], b["snr10"]["point"] or 0, (1 / (c.compute or 1.0)) / max(1 / x for x in comp)]
    ang = np.linspace(0, 2 * np.pi, len(axes_lab), endpoint=False).tolist()
    fig = plt.figure(figsize=(7.5, 7))
    ax = plt.subplot(111, polar=True)
    pf = go.Figure()
    for c in top:
        v = vec(c)
        ax.plot(ang + ang[:1], v + v[:1], color=c.color, lw=2.4 if c.id == EMP else 1.5, label=c.name)
        ax.fill(ang + ang[:1], v + v[:1], color=c.color, alpha=0.08)
        pf.add_scatterpolar(r=v + v[:1], theta=axes_lab + axes_lab[:1], name=c.name, line=dict(color=c.color, width=3 if c.id == EMP else 1.6), fill="toself", opacity=0.75,
                            customdata=[[c.id]] * 7, hovertemplate="%{fullData.name}<br>%{theta}: %{r:.3f}<extra></extra>")
    ax.set_xticks(ang)
    ax.set_xticklabels(axes_lab, fontsize=8)
    ax.set_ylim(0.6, 1.0)
    ax.set_title("상위 4개 조건 (cost 기준) × 6지표  ·  반경 0.6–1.0", loc="left", pad=20)
    ax.legend(fontsize=7, loc="upper right", bbox_to_anchor=(1.35, 1.1))
    save(fig, "radar_top4")
    style_plotly(pf, 600, "상위 4개 조건 레이더")
    pf.update_layout(polar=dict(radialaxis=dict(range=[0.6, 1.0], gridcolor=GRID), angularaxis=dict(gridcolor=GRID), bgcolor=SURFACE), legend=dict(font=dict(size=10)))
    return pf


# ---------------------------------------------------------------- html
def card(key, title, pf, png, caption=""):
    div = pio.to_html(pf, include_plotlyjs=False, full_html=False, div_id=f"fig_{key}", config={"displaylogo": False, "responsive": True})
    cap = f"<p class=cap>{html.escape(caption)}</p>" if caption else ""
    return f"<div class=card id='sec_{key}'><h3>{html.escape(title)}</h3>{div}{cap}<p class=links>정적 이미지: <a href='figures/highlights/{png}.png'>PNG 300dpi</a> · <a href='figures/highlights/{png}.svg'>SVG</a></p></div>"


def build_html(conds, boot, cards, conclusions, table_rows):
    plotlyjs = pio.get_plotlyjs() if hasattr(pio, "get_plotlyjs") else __import__("plotly").offline.get_plotlyjs()
    chips = "".join(f"<span class=chip><i style='background:{g['color']}'></i>{html.escape(g['label'])}</span>" for g in CFG["groups"].values()) + f"<span class=chip><i style='background:{EMPH}'></i>강조 조건</span>"
    cols = ["조건", "범주", "macro-F1", "w/o car_horn", "긴급 recall", "일상 precision", "주의 F1", "bg FA", "strict FA", "SNR10", "cost@.005", "cost@.01", "Δcost vs 기준 (95% CI)", "상대 연산량", "실험 ID"]
    thead = "".join(f"<th>{c}</th>" for c in cols)
    tbody = "".join(table_rows)
    page = f"""<!doctype html><html lang=ko><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>핵심 결과 — 소리인식 키링 스페셜리스트 앙상블</title>
<style>
:root{{--surface:#fcfcfb;--card:#fff;--ink:#0b0b0b;--ink2:#52514e;--ink3:#8a8984;--line:#e6e5e1;--accent:#E4572E;--ref:#fff6d6}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--surface);color:var(--ink);font-family:Pretendard,'Malgun Gothic','Segoe UI',system-ui,sans-serif;font-size:14px;line-height:1.55}}
.layout{{display:grid;grid-template-columns:240px 1fr;min-height:100vh}}
aside{{position:sticky;top:0;height:100vh;overflow:auto;padding:28px 18px;border-right:1px solid var(--line);background:var(--card)}}
aside h1{{font-size:15px;margin:0 0 4px;line-height:1.35}} aside .sub{{color:var(--ink3);font-size:12px;margin-bottom:18px}}
aside nav a{{display:block;padding:6px 10px;margin:1px 0;border-radius:8px;color:var(--ink2);text-decoration:none;font-size:13px}} aside nav a:hover{{background:#f1f3f7;color:var(--ink)}}
main{{padding:36px 44px 80px;max-width:1500px}}
h2{{font-size:22px;margin:52px 0 6px;letter-spacing:-.01em}} h2:first-of-type{{margin-top:0}} h3{{font-size:15px;margin:0 0 10px}}
.lead{{color:var(--ink2);margin:0 0 18px;max-width:900px}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}} .chip{{display:inline-flex;align-items:center;gap:7px;padding:4px 10px;border:1px solid var(--line);border-radius:999px;background:var(--card);font-size:12px;color:var(--ink2)}} .chip i{{width:10px;height:10px;border-radius:50%;display:inline-block}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 18px 12px;margin:16px 0;box-shadow:0 1px 2px rgba(0,0,0,.03)}}
.card .links{{font-size:12px;color:var(--ink3);margin:6px 0 0}} .card .links a{{color:#2a78d6;text-decoration:none}} .cap{{font-size:12.5px;color:var(--ink2);margin:4px 0 0}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}} @media(max-width:1300px){{.grid3{{grid-template-columns:1fr}} .layout{{grid-template-columns:1fr}} aside{{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}}}}
.summary{{background:var(--card);border-left:4px solid var(--accent);border-radius:10px;padding:14px 18px;margin:12px 0}} .summary li{{margin:4px 0}}
.tablewrap{{overflow:auto;border:1px solid var(--line);border-radius:14px;background:var(--card)}}
table{{border-collapse:separate;border-spacing:0;font-size:12.5px;width:100%}} th,td{{padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap}} td.num{{text-align:right;font-variant-numeric:tabular-nums}}
th{{position:sticky;top:0;background:#f6f7f9;color:var(--ink2);font-weight:600;cursor:pointer;user-select:none;text-align:left;z-index:2}} th[data-asc="1"]::after{{content:" ▲";font-size:10px}} th[data-asc="0"]::after{{content:" ▼";font-size:10px}}
tbody tr:hover{{background:#f7f9fc}} tr.ref td{{background:var(--ref);font-weight:700}} tr.emph td:first-child{{color:var(--accent);font-weight:700}} .sig{{color:#0ca30c;font-weight:700}} .nsig{{color:var(--ink3)}}
.idcol{{color:var(--ink3);font-family:ui-monospace,Consolas,monospace;font-size:11.5px}} td.cat i{{width:9px;height:9px;border-radius:50%;display:inline-block;margin-right:6px;vertical-align:middle}}
footer{{color:var(--ink3);font-size:12px;margin-top:60px;border-top:1px solid var(--line);padding-top:14px}}
</style><script>{plotlyjs}</script></head><body><div class=layout>
<aside><h1>핵심 결과<br>스페셜리스트 앙상블</h1><div class=sub>test split · 라벨 v2 · 95% CI = source_file 클러스터 부트스트랩 {CFG['bootstrap']['n']}회</div>
<nav><a href="#headline">Headline</a><a href="#summary">결론 요약</a><a href="#pareto">파레토</a><a href="#curves">운영 곡선</a><a href="#metrics">지표별</a><a href="#confusion">그룹 혼동 · 교차 오판</a><a href="#emerg">긴급 클래스별</a><a href="#noise">노이즈</a><a href="#origin">출처별</a><a href="#calib">캘리브레이션</a><a href="#overlap">오류 중복</a><a href="#delta">Δ 산점도</a><a href="#radar">레이더</a><a href="#table">요약 표</a></nav>
<div class=chips style="margin-top:18px">{chips}</div></aside>
<main>
<section id=headline><h2>Headline</h2><p class=lead>조건 {len(conds)}개 (고정 순서, 4범주). 막대 끝 값 옆 [ ]는 95% 신뢰구간. 기준선 = EfficientAT 범용 단일, 강조 = EfficientAT 스페셜리스트 3개 스태킹.</p>
<div class=grid3>{cards['headline_macro_f1']}{cards['headline_emerg_recall']}{cards['headline_cost']}</div></section>
<section id=summary><h2>결론 요약</h2><div class=summary><ol>{''.join(f'<li>{html.escape(c)}</li>' for c in conclusions)}</ol></div></section>
<section id=pareto><h2>정확도–효율 파레토</h2><p class=lead>x = 상대 연산량 (× EfficientAT 1개, log), y = 비용 점수 @FA.005. 점선 = 파레토 프론트. 에지 배포 관점의 핵심 그림.</p>{cards['pareto']}</section>
<section id=curves><h2>운영 곡선</h2><p class=lead>background 임계값을 sweep해 그린 트레이드오프. 세로 점선 = 운영점 strict FA 0.005 / 0.01.</p>{cards['curve_emergency']}{cards['curve_daily']}</section>
<section id=metrics><h2>지표별 (95% CI)</h2>{''.join(cards[k] for k in ['bar_macro_f1','bar_macro_f1_no_carhorn','bar_emerg_recall','bar_daily_precision','bar_caution_f1','bar_bg_fa','bar_strict_fa','bar_snr10','bar_cost005'])}{cards['pr_auc']}</section>
<section id=confusion><h2>그룹 혼동 · 교차 오판</h2>{cards['group_confusion']}{cards['cross_group']}</section>
<section id=emerg><h2>긴급 클래스별</h2>{cards['emergency_recall_by_class']}{cards['emergency_precision_by_class']}{cards['heatmap']}</section>
<section id=noise><h2>노이즈 강건성</h2>{cards['noise']}{cards['noise_drop']}</section>
<section id=origin><h2>출처별 성능</h2>{cards['origin']}{cards['fa_hour']}</section>
<section id=calib><h2>캘리브레이션</h2>{cards['calib']}{cards['ece']}</section>
<section id=overlap><h2>오류 중복</h2>{cards['venn']}</section>
<section id=delta><h2>스페셜리스트 Δ 산점도</h2>{cards.get('delta', '')}</section>
<section id=radar><h2>레이더</h2>{cards['radar']}</section>
<section id=table><h2>요약 표</h2><p class=lead>값 [95% CI]. "유의" = 강조·비교 조건과 기준선의 cost 차이 CI가 0을 포함하지 않음. 열 클릭 정렬.</p><div class=tablewrap><table id=tbl><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div></section>
<footer>생성: src/make_report.py --highlights · 입력: results/*/predictions_*.csv, metrics.json · 그림: docs/figures/highlights/ · 부트스트랩: results/&lt;exp&gt;/bootstrap.json</footer>
</main></div>
<script>
document.querySelectorAll('#tbl th').forEach((th,i)=>th.addEventListener('click',()=>{{const tb=th.closest('table').tBodies[0];const rows=[...tb.rows];const asc=th.dataset.asc!=='1';document.querySelectorAll('#tbl th').forEach(h=>delete h.dataset.asc);th.dataset.asc=asc?'1':'0';
 rows.sort((a,b)=>{{const x=a.cells[i].dataset.v,y=b.cells[i].dataset.v;const nx=parseFloat(x),ny=parseFloat(y);const c=(isNaN(nx)||isNaN(ny))?x.localeCompare(y):nx-ny;return asc?c:-c;}});rows.forEach(r=>tb.appendChild(r));}}));
</script></body></html>"""
    (ROOT / "docs" / "report_highlights.html").write_text(page, encoding="utf-8")


def main():
    conds, man = load_conditions()
    print(f"{len(conds)} conditions")
    boot = bootstrap(conds, CFG["bootstrap"]["n"], CFG["bootstrap"]["seed"])
    print("bootstrap done")
    cards = {}
    for fname, (title, pf, png) in fig_headline(conds, boot).items():
        cards[fname] = card(fname, title, pf, png)
    for key, label, higher in METRICS:
        pf = fig_metric_bar(conds, boot, key, label, higher, f"bar_{key}")
        cards[f"bar_{key}"] = card(f"bar_{key}", label + ("" if higher else " (낮을수록 좋음)"), pf, f"bar_{key}")
    curves, dom_caption = fig_operating_curves(conds)
    for fname, (title, pf, png) in curves.items():
        cards[fname] = card(fname, title, pf, png, dom_caption if fname == "curve_emergency" else "")
    pf, pr = fig_pr_auc(conds)
    cards["pr_auc"] = card("pr_auc", "그룹별 PR-AUC (임계값 비의존)", pf, "group_pr_auc")
    pf, pb = fig_group_confusion(conds)
    cards["group_confusion"] = card("group_confusion", "그룹 혼동 행렬 — 기준선 vs 강조 조건 (운영점 판정)", pf, "group_confusion", "테두리 셀 = 긴급 정답이 일상/배경으로 판정된 비율 (안전상 최악의 오류).")
    cards["cross_group"] = card("cross_group", "교차 그룹 오판율: 긴급 → 일상/배경", pb, "cross_group_miss")
    for fname, (title, pf, png) in fig_emergency_classes(conds).items():
        cards[fname] = card(fname, title + " (운영점 판정)", pf, png, "car_horn은 test 26클립이라 CI가 넓음.")
    cards["heatmap"] = card("heatmap", "클래스별 F1 히트맵 (0.4–1.0 고정)", fig_heatmap(conds), "per_class_f1_heatmap")
    pf, pdrop = fig_noise(conds)
    cards["noise"] = card("noise", "노이즈 강건성: clean → SNR20/15/10", pf, "noise_robustness")
    cards["noise_drop"] = card("noise_drop", "노이즈 하락폭 (clean - SNR10)", pdrop, "noise_drop")
    pf, front = fig_pareto(conds, boot)
    cards["pareto"] = card("pareto", "정확도–효율 파레토", pf, "pareto_cost_compute", "캐스케이드 연산량 = test 분포 기준 기대값(게이트 + 통과율 × 분류기). 세로 오차막대 = cost 95% CI.")
    pf, pe, ece = fig_calibration(conds)
    cards["calib"] = card("calib", "Reliability diagram", pf, "calibration_reliability", "임계값 튜닝은 확률이 보정돼 있을수록 test에서 유지됨. 대각선 = 완벽 보정.")
    cards["ece"] = card("ece", "Expected Calibration Error", pe, "calibration_ece")
    pf, venn_summary = fig_venn(CFG["overlap_sets"])
    cards["venn"] = card("venn", "오류 중복 (틀린 test 클립 집합)", pf, "error_overlap_venn", "; ".join(f"{t}: 합집합 {u}, 셋 다 틀림 {a}" for t, u, a, _ in venn_summary))
    pf, pts = fig_specialist_delta(man)
    if pf is not None:
        cards["delta"] = card("delta", "스페셜리스트 담당 클래스 Δ (전체, 95% CI)", pf, "specialist_delta_ci", "Δ = 스페셜리스트 F1 - 범용(담당+other 리매핑) F1. 0 걸치면 이득 없음.")
    cards["origin"] = card("origin", "출처별 macro-F1 (aihub / esc50 / donateacry / other)", fig_source_origin(conds), "source_origin_macro_f1", "macro는 각 출처에 존재하는 클래스만 평균. esc50/donateacry/other는 클래스 수가 적어 변동 큼.")
    pf, fa_rows = fig_fa_per_hour(conds, boot)
    cards["fa_hour"] = card("fa_hour", "FA/hour 환산", pf, "fa_per_hour", "가정: 1초 hop 슬라이딩(시간당 3600 판정), 순수 background 입력, 운영점 @FA.005 판정 사용. 클립 단위 오경보율 × 3600.")
    cards["radar"] = card("radar", "상위 4개 조건 × 6지표", fig_radar(conds, boot), "radar_top4", "효율 = 1/상대연산량을 최대 1로 정규화. 반경 0.6–1.0.")
    # conclusions (5 lines, from numbers)
    by = {c.id: c for c in conds}
    ref, emp = boot[REF], boot.get(EMP)
    best_cost = min(conds, key=lambda c: boot[c.id]["cost005"]["point"])
    best_f1 = max(conds, key=lambda c: boot[c.id]["macro_f1"]["point"])
    conclusions = [f"비용(@FA.005) 최저 = {best_cost.name} {ci_text(boot[best_cost.id]['cost005'])} vs 기준선 {ci_text(ref['cost005'])}.",
                   f"macro-F1 최고 = {best_f1.name} {ci_text(boot[best_f1.id]['macro_f1'])} (기준선 {ci_text(ref['macro_f1'])})."]
    if emp:
        d = emp["diff_vs_ref"]
        conclusions.append(f"강조 조건(EfficientAT 스페셜리스트 3개 스태킹) vs 기준선: Δmacro-F1 {d['macro_f1']['point']:+.3f} [{d['macro_f1']['lo']:+.3f}, {d['macro_f1']['hi']:+.3f}] "
                           f"({'유의' if d['macro_f1']['significant'] else '유의하지 않음'}), Δcost {d['cost005']['point']:+.3f} [{d['cost005']['lo']:+.3f}, {d['cost005']['hi']:+.3f}] ({'유의' if d['cost005']['significant'] else '유의하지 않음'}), 연산량 3배.")
    conclusions.append(dom_caption + ".")
    conclusions.append(f"파레토 프론트: {', '.join(f'×{x:.2f}→cost {y:.3f}' for x, y in front)}. " + ("동일 연산량 비교에서 EfficientAT-small 스페셜리스트 3개는 " + ci_text(boot['F_mn04_stacked']['cost005']) + " (기준선 " + ci_text(ref['cost005']) + ")." if "F_mn04_stacked" in boot else ""))
    # table
    rows = []
    for c in conds:
        b = boot[c.id]
        d = b.get("diff_vs_ref", {}).get("cost005")
        dtxt = f"{d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] <span class={'sig' if d['significant'] else 'nsig'}>{'유의' if d['significant'] else '—'}</span>" if d else "기준"
        cells = [f"<td data-v=\"{html.escape(c.name)}\">{html.escape(c.name)}</td>", f"<td class=cat data-v=\"{c.group}\"><i style='background:{CFG['groups'][c.group]['color']}'></i>{html.escape(CFG['groups'][c.group]['label'])}</td>"]
        for k in ["macro_f1", "macro_f1_no_carhorn", "emerg_recall", "daily_precision", "caution_f1", "bg_fa", "strict_fa", "snr10", "cost005"]:
            cells.append(f"<td class=num data-v=\"{b[k]['point'] if b[k]['point'] is not None else ''}\">{ci_text(b[k])}</td>")
        c01 = (c.meta.get("operating_point_001") or {}).get("cost")
        cells.append(f"<td class=num data-v=\"{c01 if c01 is not None else ''}\">{c01:.3f}</td>" if c01 is not None else "<td class=num data-v=''>-</td>")
        cells.append(f"<td class=num data-v=\"{d['point'] if d else 0}\">{dtxt}</td>")
        cells.append(f"<td class=num data-v=\"{c.compute or ''}\">{'' if c.compute is None else f'{c.compute:.2f}'}</td>")
        cells.append(f"<td class=idcol data-v=\"{c.id}\">{c.id}</td>")
        rows.append(f"<tr{' class=ref' if c.id == REF else (' class=emph' if c.id == EMP else '')}>" + "".join(cells) + "</tr>")
    build_html(conds, boot, cards, conclusions, rows)
    # README for figures
    readme = ["# docs/figures/highlights", "", "`python src/make_report.py --highlights` 가 재생성. PNG 300dpi + SVG. ★ = 논문 Fig 후보.", "", "| 파일 | 설명 | 논문 |", "|---|---|---|"]
    desc = [("headline_macro_f1", "Headline: macro-F1 (95% CI)", "★ Fig 1a"), ("headline_emerg_recall", "Headline: 긴급 recall @FA.005", "★ Fig 1b"), ("headline_cost", "Headline: 비용 점수 @FA.005", "★ Fig 1c"),
            ("pareto_cost_compute", "정확도–효율 파레토 (연산량 vs cost)", "★ Fig 2"), ("curve_emergency", "운영 곡선: 긴급 recall vs strict FA", "★ Fig 3"), ("curve_daily", "운영 곡선: 일상 precision vs recall", ""),
            ("group_confusion", "그룹 혼동 행렬 기준선 vs 강조", "★ Fig 4"), ("cross_group_miss", "긴급 → 일상/배경 오판율", ""), ("group_pr_auc", "그룹별 PR-AUC", ""),
            ("emergency_recall_by_class", "긴급 클래스별 recall", ""), ("emergency_precision_by_class", "긴급 클래스별 precision", ""), ("per_class_f1_heatmap", "클래스별 F1 히트맵", "★ Fig 5 (부록)"),
            ("noise_robustness", "노이즈 강건성 꺾은선", "★ Fig 6"), ("noise_drop", "노이즈 하락폭", ""), ("source_origin_macro_f1", "출처별 macro-F1", ""), ("fa_per_hour", "FA/hour 환산", "★ (제품 지표)"),
            ("calibration_reliability", "Reliability diagram", ""), ("calibration_ece", "ECE", ""), ("error_overlap_venn", "오류 중복 벤 다이어그램 3세트", "★ Fig 7"), ("specialist_delta_ci", "스페셜리스트 Δ 산점도 (CI)", "★ Fig 8"),
            ("radar_top4", "상위 4개 레이더 (발표용)", "")] + [(f"bar_{k}", f"지표별 막대: {l} (95% CI)", "") for k, l, _ in METRICS]
    readme += [f"| `{f}.png/.svg` | {d} | {p} |" for f, d, p in desc]
    (FIG / "README.md").write_text("\n".join(readme) + "\n", encoding="utf-8")
    print("-> docs/report_highlights.html, docs/figures/highlights/ (", len(list(FIG.glob("*.png"))), "png )")
    for c in conclusions:
        print("-", c)


if __name__ == "__main__":
    main()
