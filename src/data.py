"""Datasets for data/splits/manifest.csv.

- label_fine (configs/labels.yaml) is the only label space. NFC/NFD fallback for Korean filenames.
- returns (waveform float32 [32000] @16kHz, label index). Model-specific frontends (mel, resample) live in src/models.
- train-only waveform augs: random gain, mixup (batch-level helper), MUSAN hook (off by default).
  SpecAugment is applied by the model frontend (EfficientAT AugmentMelSTFT freqm/timem) in train mode.
- balanced sampler: fixed `cap` samples per class per epoch (with replacement when the class is smaller).
- specialist mode: labels -> group labels + "other"; "other" capped at 1.5x the group's train clips, background + confusers first.
"""
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
import torch
import yaml
from torch.utils.data import Dataset, Sampler

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "miimo"
MANIFEST = ROOT / "data" / "splits" / "manifest.csv"
SR, N_SAMPLES = 16000, 32000
OTHER = "other"


def load_labels(path=ROOT / "configs" / "labels.yaml"):
    return yaml.safe_load(open(path, encoding="utf-8"))


def load_groups(path=ROOT / "configs" / "groups.yaml"):
    return yaml.safe_load(open(path, encoding="utf-8"))


def resolve(root, rel):
    for form in (None, "NFC", "NFD"):
        p = root / (unicodedata.normalize(form, rel) if form else rel)
        if p.is_file():
            return p
    raise FileNotFoundError(rel)


def load_manifest(path=MANIFEST):
    return pd.read_csv(path, low_memory=False)


def specialist_labels(group_cfg):
    return list(group_cfg["labels"]) + [OTHER]


def remap_specialist(df, group_cfg, split, other_ratio=1.5, seed=42):
    """label_fine -> group label or OTHER (original kept in `_orig`). Train: cap OTHER rows, background + confusers first."""
    own = set(group_cfg["labels"])
    df = df.copy()
    df["_orig"] = df["label_fine"]
    df["label_fine"] = df["label_fine"].where(df["label_fine"].isin(own), OTHER)
    if split != "train":
        return df
    is_other = df["label_fine"] == OTHER
    cap = int(other_ratio * (~is_other).sum())
    others = df[is_other]
    if len(others) <= cap:
        return df
    rng = np.random.default_rng(seed)
    priority = ["background"] + list(group_cfg.get("confusers") or [])
    take, remaining = [], cap
    for tier in (priority, sorted(set(others["_orig"]) - set(priority))):  # priority classes first, equal share
        if remaining <= 0 or not tier:
            continue
        per = max(remaining // len(tier), 1)
        for lab in tier:
            idx = others.index[others["_orig"] == lab].to_numpy()
            k = min(per, len(idx), remaining)
            take.extend(rng.choice(idx, k, replace=False))
            remaining -= k
    return pd.concat([df[~is_other], df.loc[sorted(take)]]).reset_index(drop=True)


class ClipDataset(Dataset):
    def __init__(self, df, classes, train=False, gain_db=6.0, musan=None, seed=0):
        self.df = df.reset_index(drop=True)
        self.paths = [resolve(DATA, p) for p in self.df["filepath"]]
        self.class_to_idx = {c: i for i, c in enumerate(classes)}
        y = self.df["label_fine"].map(self.class_to_idx)
        assert not y.isna().any(), "label outside class list"
        self.y = y.to_numpy().astype(int)
        self.train, self.gain_db, self.musan = train, gain_db, musan
        self.rng = np.random.default_rng(seed)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        x, sr = sf.read(str(self.paths[i]), dtype="float32")
        assert sr == SR
        x = x[:N_SAMPLES] if x.ndim == 1 else x[:N_SAMPLES, 0]
        if len(x) < N_SAMPLES:
            x = np.pad(x, (0, N_SAMPLES - len(x)))
        if self.train:
            if self.gain_db:
                x = x * 10 ** (self.rng.uniform(-self.gain_db, self.gain_db) / 20)
            if self.musan is not None:  # hook: callable(x, rng) -> x, e.g. MUSAN online mix. default off
                x = self.musan(x, self.rng)
            x = np.clip(x, -1.0, 1.0)
        return torch.from_numpy(x.astype(np.float32)), int(self.y[i])


class EmbDataset(Dataset):
    """Cached features instead of waveforms (e.g. yamnet_frozen). Returns (feature float32 [D], label index)."""

    def __init__(self, df, classes, feature_dir, split):
        self.df = df.reset_index(drop=True)
        idx = pd.read_csv(feature_dir / f"{split}.csv")["filepath"]
        pos = pd.Series(np.arange(len(idx)), index=idx)
        missing = ~self.df["filepath"].isin(pos.index)
        assert not missing.any(), f"{int(missing.sum())} clips missing from feature cache {feature_dir}/{split}.csv"
        self.x = np.load(feature_dir / f"{split}.npy", mmap_mode="r")[pos.loc[self.df["filepath"]].to_numpy()]
        self.y = self.df["label_fine"].map({c: i for i, c in enumerate(classes)}).to_numpy().astype(int)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        return torch.from_numpy(np.asarray(self.x[i], dtype=np.float32)), int(self.y[i])


class BalancedSampler(Sampler):
    """`cap` indices per class per epoch; replacement only when the class has fewer than cap."""

    def __init__(self, y, cap=3000, seed=42):
        self.y, self.cap, self.seed, self.epoch = np.asarray(y), cap, seed, 0
        self.by_class = [np.flatnonzero(self.y == c) for c in np.unique(self.y)]

    def set_epoch(self, e):
        self.epoch = e

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch)
        idx = np.concatenate([rng.choice(ix, self.cap, replace=len(ix) < self.cap) for ix in self.by_class])
        rng.shuffle(idx)
        return iter(idx.tolist())

    def __len__(self):
        return self.cap * len(self.by_class)


def mixup(x, y, n_classes, alpha=0.2, p=0.3):
    """Batch mixup. Returns x and soft targets [B, n_classes]."""
    t = torch.nn.functional.one_hot(y, n_classes).float()
    if p <= 0 or np.random.rand() > p:
        return x, t
    lam = float(np.random.beta(alpha, alpha))
    perm = torch.randperm(x.size(0), device=x.device)
    return lam * x + (1 - lam) * x[perm], lam * t + (1 - lam) * t[perm]


def build_split(cfg, split, classes=None):
    """Returns (df, classes, dataset) for a split, honouring mode/group/limit_per_class from cfg."""
    df = load_manifest()
    df = df[df["split"] == split]
    labels = load_labels()["labels"]
    if cfg.get("mode", "generalist") == "specialist":
        gkey = cfg.get("group_model") or cfg["model"].split("_")[0]  # yamnet_frozen / yamnet_ft -> "yamnet"
        gcfg = load_groups()[cfg.get("group_set", "semantic")][gkey]
        df = remap_specialist(df, gcfg, split, cfg.get("other_ratio", 1.5), cfg.get("seed", 42))
        classes = classes or specialist_labels(gcfg)
    else:
        classes = classes or labels
    n = cfg.get("limit_per_class")
    if n:
        df = df.sample(frac=1, random_state=cfg.get("seed", 42)).groupby("label_fine").head(n)
    if cfg.get("features"):  # cached features (data/cache/<features>/<split>.npy), see src/cache_yamnet_emb.py
        ds = EmbDataset(df, classes, ROOT / "data" / "cache" / cfg["features"], split)
        return df.reset_index(drop=True), classes, ds
    aug = cfg.get("aug", {})
    ds = ClipDataset(df, classes, train=(split == "train"), gain_db=aug.get("gain_db", 6.0) if split == "train" else 0.0,
                     seed=cfg.get("seed", 42))
    return df.reset_index(drop=True), classes, ds


if __name__ == "__main__":  # self-check on the real manifest
    cfg = {"model": "efficientat", "mode": "specialist", "limit_per_class": 20}
    df, classes, ds = build_split(cfg, "train")
    assert classes[-1] == OTHER and set(df["label_fine"]) <= set(classes)
    x, y = ds[0]
    assert x.shape == (N_SAMPLES,) and x.dtype == torch.float32 and 0 <= y < len(classes)
    dfv, _, _ = build_split(cfg, "val")
    assert (dfv["label_fine"].isin(classes)).all()
    s = BalancedSampler(ds.y, cap=5)
    assert len(list(iter(s))) == 5 * len(np.unique(ds.y))
    xb, tb = mixup(torch.stack([ds[i][0] for i in range(4)]), torch.tensor([ds[i][1] for i in range(4)]), len(classes), p=1.0)
    assert tb.shape == (4, len(classes)) and torch.allclose(tb.sum(1), torch.ones(4))
    print("data selftest ok", len(df), classes)
