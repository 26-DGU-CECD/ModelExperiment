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


def soft_ce(logits, target, smoothing):
    n = logits.size(1)
    target = target * (1 - smoothing) + smoothing / n
    return -(target * torch.log_softmax(logits, 1)).sum(1).mean()


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
    cfg = load_config(ap.parse_args().config)
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
    sampler = BalancedSampler(ds_tr.y, cap=cfg["sampler"]["cap"], seed=cfg["seed"]) if cfg["sampler"]["balanced"] else None
    dl_kw = dict(batch_size=cfg["batch_size"], num_workers=cfg["num_workers"], pin_memory=device.type == "cuda",
                 persistent_workers=cfg["num_workers"] > 0)
    tr = DataLoader(ds_tr, sampler=sampler, shuffle=sampler is None, drop_last=True, **dl_kw)
    va = DataLoader(ds_va, shuffle=False, **dl_kw)

    cfg.setdefault("model_args", {})
    if cfg["model"] == "efficientat":
        cfg["model_args"] = {"freqm": cfg["aug"]["freqm"], "timem": cfg["aug"]["timem"], **(cfg["model_args"] or {})}
    model = build_model(cfg["model"], n_classes, cfg).to(device)
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
                       f"batch={cfg['batch_size']} lr={cfg['lr']} cap={cap}\n\n"
                       "| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |\n|---|---|---|---|---|---|---|---|\n")
    history, best_f1, bad = [], -1.0, 0
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
            loss = soft_ce(logits.float(), t, cfg["label_smoothing"])
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
    print(f"done. best val macro-F1 {best_f1:.4f} -> {ckpt_dir / 'best.pt'}", flush=True)


if __name__ == "__main__":
    main()
