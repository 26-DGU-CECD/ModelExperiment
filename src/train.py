"""Train a generalist or specialist classifier.

usage: python src/train.py --config configs/<exp>.yaml
Writes checkpoints/<exp>/best.pt (git-ignored), results/<exp>/train_history.json, logs/<exp>.summary.md (epoch table).
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[0] = str(ROOT)  # import as src.* so EfficientAT's top-level `models` package does not collide

import numpy as np  # noqa: E402
import torch  # noqa: E402
import yaml  # noqa: E402
from sklearn.metrics import f1_score  # noqa: E402
from torch.utils.data import DataLoader  # noqa: E402

from src.data import BalancedSampler, build_split, mixup  # noqa: E402
from src.models import build_model  # noqa: E402

DEFAULTS = {"mode": "generalist", "group_set": "semantic", "epochs": 30, "lr": 1e-4, "weight_decay": 1e-4, "batch_size": 64,
            "warmup_epochs": 1, "label_smoothing": 0.1, "amp": True, "seed": 42, "patience": 6, "num_workers": 4,
            "sampler": {"balanced": True, "cap": 3000},
            "aug": {"mixup_p": 0.3, "mixup_alpha": 0.2, "gain_db": 6.0, "freqm": 48, "timem": 192, "musan": False}}


def load_config(path):
    cfg = yaml.safe_load(open(path, encoding="utf-8"))
    out = {**DEFAULTS, **cfg}
    out["sampler"] = {**DEFAULTS["sampler"], **(cfg.get("sampler") or {})}
    out["aug"] = {**DEFAULTS["aug"], **(cfg.get("aug") or {})}
    out.setdefault("exp_name", Path(path).stem)
    return out


def kd_loss(student_logits, teacher_logits, T=3.0):
    """KL(teacher || student) at temperature T, scaled by T^2 (Hinton et al.)."""
    p_t = torch.softmax(teacher_logits / T, 1)
    return torch.nn.functional.kl_div(torch.log_softmax(student_logits / T, 1), p_t, reduction="batchmean") * T * T


def load_teacher(path, device):
    """Frozen teacher from checkpoints/<exp>/best.pt. Its class order must match the student's."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    t = build_model(ck["config"]["model"], len(ck["classes"]), ck["config"]).to(device)
    t.load_state_dict(ck["model_state_dict"])
    t.eval()
    for p in t.parameters():
        p.requires_grad_(False)
    return t, ck["classes"]


def soft_ce(logits, target, smoothing, other_idx=None, other_smoothing=None, class_weight=None):
    """Soft-target CE with label smoothing. Rows whose target peak is `other` use other_smoothing (heterogeneous bucket).
    class_weight [n]: per-sample weight taken at the target peak class (cost-sensitive objective), mean-normalised."""
    n = logits.size(1)
    peak = target.argmax(1)
    eps = torch.full((logits.size(0), 1), float(smoothing), device=logits.device)
    if other_idx is not None and other_smoothing is not None:
        eps[peak == other_idx] = float(other_smoothing)
    target = target * (1 - eps) + eps / n
    loss = -(target * torch.log_softmax(logits, 1)).sum(1)
    if class_weight is not None:
        w = class_weight[peak]
        return (loss * w).sum() / w.sum()
    return loss.mean()


def per_class_f1(y, pred, n):
    out = []
    for c in range(n):
        tp = ((pred == c) & (y == c)).sum()
        fp = ((pred == c) & (y != c)).sum()
        fn = ((pred != c) & (y == c)).sum()
        out.append(0.0 if tp == 0 else float(2 * tp / (2 * tp + fp + fn)))
    return out


@torch.no_grad()
def predict(model, loader, device, amp):
    model.eval()
    probs, ys = [], []
    for x, y in loader:
        with torch.autocast(device_type=device.type, enabled=amp):
            logits = model(x.to(device, non_blocking=True))
        probs.append(torch.softmax(logits.float(), 1).cpu())
        ys.append(y)
    return torch.cat(probs).numpy(), torch.cat(ys).numpy()


def append_md(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--teacher", default=None, help="checkpoint path for KD (overrides cfg.teacher)")
    args = ap.parse_args()
    cfg = load_config(args.config)
    if args.teacher:
        cfg["teacher"] = args.teacher
    cfg["kd"] = {"alpha": 0.5, "T": 3.0, **(cfg.get("kd") or {})}
    exp = cfg["exp_name"]
    torch.manual_seed(cfg["seed"])
    np.random.seed(cfg["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    df_tr, classes, ds_tr = build_split(cfg, "train")
    df_va, _, ds_va = build_split(cfg, "val", classes)
    n_classes = len(classes)
    print(f"[{exp}] mode={cfg['mode']} classes={classes}", flush=True)
    print(f"train {len(ds_tr)} clips, val {len(ds_va)} clips, device {device}", flush=True)
    print("train per class:", df_tr["label_fine"].value_counts().reindex(classes).fillna(0).astype(int).to_dict(), flush=True)

    use_amp = cfg["amp"] and device.type == "cuda"
    # balanced sampling key: original 14 labels for specialists (recipe v2) so `other` keeps its natural share
    sampler = BalancedSampler(ds_tr.sample_y, cap=cfg["sampler"]["cap"], seed=cfg["seed"]) if cfg["sampler"]["balanced"] else None
    specialist = cfg["mode"] == "specialist"
    other_idx = classes.index("other") if specialist and "other" in classes else None
    class_weight = None
    if specialist:  # cost-sensitive objective from configs/groups.yaml (recall: own x2, precision: other x2, balanced: 1/1)
        from src.data import load_groups
        groups = load_groups()
        gkey = cfg.get("group_model") or cfg["model"].split("_")[0]
        objective = cfg.get("objective") or groups[cfg.get("group_set", "semantic")][gkey].get("objective", "balanced")
        wts = groups.get("_objective_weights", {}).get(objective, {"own": 1.0, "other": 1.0})
        class_weight = torch.tensor([wts["other"] if c == "other" else wts["own"] for c in classes], device=device)
        cfg["objective"] = objective
        print(f"objective={objective} class weights={dict(zip(classes, class_weight.tolist()))}", flush=True)
    dl_kw = dict(batch_size=cfg["batch_size"], num_workers=cfg["num_workers"], pin_memory=device.type == "cuda",
                 persistent_workers=cfg["num_workers"] > 0)
    tr = DataLoader(ds_tr, sampler=sampler, shuffle=sampler is None, drop_last=True, **dl_kw)
    va = DataLoader(ds_va, shuffle=False, **dl_kw)

    cfg.setdefault("model_args", {})
    if cfg["model"] == "efficientat":
        cfg["model_args"] = {"freqm": cfg["aug"]["freqm"], "timem": cfg["aug"]["timem"], **(cfg["model_args"] or {})}
    model = build_model(cfg["model"], n_classes, cfg).to(device)
    if cfg.get("init_from"):  # warm start from another experiment's checkpoint; shape-mismatched tensors (classifier) stay random
        ip = Path(cfg["init_from"])
        ck = torch.load(ip if ip.is_absolute() else ROOT / ip, map_location="cpu", weights_only=False)
        own = model.state_dict()
        keep = {k: v for k, v in ck["model_state_dict"].items() if k in own and own[k].shape == v.shape}
        model.load_state_dict(keep, strict=False)
        print(f"init_from {cfg['init_from']}: loaded {len(keep)}/{len(own)} tensors", flush=True)
    teacher = None
    if cfg.get("teacher"):
        assert not cfg.get("features"), "KD needs waveform input; cached-feature students (yamnet_frozen) cannot be distilled"
        tp = Path(cfg["teacher"])
        teacher, t_classes = load_teacher(tp if tp.is_absolute() else ROOT / tp, device)
        assert list(t_classes) == list(classes), f"teacher classes {t_classes} != student classes {classes}"
        print(f"KD teacher {cfg['teacher']} alpha={cfg['kd']['alpha']} T={cfg['kd']['T']}", flush=True)
    if cfg.get("head_lr"):  # two param groups: backbone at lr, classifier head at head_lr (warm-started specialists)
        head = [p for n_, p in model.named_parameters() if "classifier" in n_]
        body = [p for n_, p in model.named_parameters() if "classifier" not in n_]
        assert head, "no classifier params found for head_lr"
        opt = torch.optim.AdamW([{"params": body, "lr": cfg["lr"]}, {"params": head, "lr": cfg["head_lr"]}], weight_decay=cfg["weight_decay"])
        print(f"param groups: backbone lr {cfg['lr']} ({sum(p.numel() for p in body) / 1e6:.2f}M), head lr {cfg['head_lr']} ({sum(p.numel() for p in head) / 1e6:.3f}M)", flush=True)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    steps = len(tr)
    total, warm = cfg["epochs"] * steps, max(1, int(cfg["warmup_epochs"] * steps))

    def lr_lambda(s):
        return s / warm if s < warm else 0.5 * (1 + math.cos(math.pi * (s - warm) / max(1, total - warm)))

    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    scaler = torch.amp.GradScaler(enabled=use_amp)

    ckpt_dir, res_dir = ROOT / "checkpoints" / exp, ROOT / "results" / exp
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    res_dir.mkdir(parents=True, exist_ok=True)
    summary = ROOT / "logs" / f"{exp}.summary.md"
    cap = cfg["sampler"]["cap"] if sampler else "-"
    append_md(summary, f"# {exp}\n\nmodel={cfg['model']} mode={cfg['mode']} classes={n_classes} train={len(ds_tr)} val={len(ds_va)} "
                       f"batch={cfg['batch_size']} lr={cfg['lr']} cap={cap} teacher={cfg.get('teacher') or '-'}\n\n"
                       "| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |\n|---|---|---|---|---|---|---|---|\n")
    history, best_f1, bad = [], -1.0, 0
    init_pc = best_pc = None
    if specialist:  # epoch-0 (pre fine-tune) evaluation: direct evidence of specialisation gain
        probs0, ys0 = predict(model, va, device, use_amp)
        init_pc = per_class_f1(ys0, probs0.argmax(1), n_classes)
        f1_0 = float(f1_score(ys0, probs0.argmax(1), average="macro"))
        append_md(summary, f"| init | - | - | {f1_0:.4f} | {float((probs0.argmax(1) == ys0).mean()):.4f} | - | - | |" + chr(10))
        print(json.dumps({"epoch": "init", "val_macro_f1": f1_0, "per_class_f1": dict(zip(classes, [round(v, 4) for v in init_pc]))}), flush=True)
    for epoch in range(cfg["epochs"]):
        t0 = time.time()
        model.train()
        if sampler:
            sampler.set_epoch(epoch)
        losses = []
        for x, y in tr:
            x, y = x.to(device, non_blocking=True), y.to(device, non_blocking=True)
            x, t = mixup(x, y, n_classes, cfg["aug"]["mixup_alpha"], cfg["aug"]["mixup_p"])
            with torch.autocast(device_type=device.type, enabled=use_amp):
                logits = model(x)
            loss = soft_ce(logits.float(), t, cfg["label_smoothing"], other_idx, cfg.get("other_label_smoothing"), class_weight)
            if teacher is not None:  # same (mixed) batch through the frozen teacher
                with torch.no_grad(), torch.autocast(device_type=device.type, enabled=use_amp):
                    t_logits = teacher(x)
                a = cfg["kd"]["alpha"]
                loss = (1 - a) * loss + a * kd_loss(logits.float(), t_logits.float(), cfg["kd"]["T"])
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
            losses.append(loss.item())
        probs, ys = predict(model, va, device, use_amp)
        val_loss = float(-np.log(probs[np.arange(len(ys)), ys] + 1e-9).mean())
        val_f1 = float(f1_score(ys, probs.argmax(1), average="macro"))
        val_acc = float((probs.argmax(1) == ys).mean())
        is_best = val_f1 > best_f1
        if is_best:
            best_f1, bad = val_f1, 0
            best_pc = per_class_f1(ys, probs.argmax(1), n_classes)
            torch.save({"model_state_dict": model.state_dict(), "classes": classes, "config": cfg, "epoch": epoch, "val_macro_f1": val_f1},
                       ckpt_dir / "best.pt")
        else:
            bad += 1
        rec = {"epoch": epoch, "train_loss": float(np.mean(losses)), "val_loss": val_loss, "val_macro_f1": val_f1, "val_acc": val_acc,
               "lr": sched.get_last_lr()[0], "sec": time.time() - t0, "best": is_best}
        history.append(rec)
        print(json.dumps(rec), flush=True)
        append_md(summary, f"| {epoch} | {rec['train_loss']:.4f} | {val_loss:.4f} | {val_f1:.4f} | {val_acc:.4f} | {rec['lr']:.2e} | {rec['sec']:.0f} | {'*' if is_best else ''} |\n")
        if bad >= cfg["patience"]:
            print(f"early stop at epoch {epoch} (patience {cfg['patience']})", flush=True)
            break
    if device.type == "cuda":
        print(f"max VRAM allocated: {torch.cuda.max_memory_allocated() / 1e9:.2f} GB", flush=True)
    json.dump({"exp_name": exp, "classes": classes, "best_val_macro_f1": best_f1, "history": history, "config": cfg},
              open(res_dir / "train_history.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
    append_md(summary, f"\nbest val macro-F1 = {best_f1:.4f}\n\n")
    if specialist and init_pc is not None and best_pc is not None:  # specialisation gain table (val)
        rows = [f"| {c} | {a:.4f} | {b:.4f} | {b - a:+.4f} |" for c, a, b in zip(classes, init_pc, best_pc)]
        own = [i for i, c in enumerate(classes) if c != "other"]
        d_own = float(np.mean([best_pc[i] - init_pc[i] for i in own]))
        append_md(summary, chr(10).join(["### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)", "",
                                    "| class | init F1 | best F1 | delta |", "|---|---|---|---|"] + rows + ["", f"mean delta over own classes = {d_own:+.4f}", "", ""]))
        history.append({"specialisation_gain": {"init": dict(zip(classes, init_pc)), "best": dict(zip(classes, best_pc)), "mean_delta_own": d_own}})
        json.dump({"exp_name": exp, "classes": classes, "best_val_macro_f1": best_f1, "history": history, "config": cfg},
                  open(res_dir / "train_history.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
        print(f"specialisation gain: mean delta over own classes {d_own:+.4f}", flush=True)
    print(f"done. best val macro-F1 {best_f1:.4f} -> {ckpt_dir / 'best.pt'}", flush=True)


if __name__ == "__main__":
    main()
