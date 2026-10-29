"""YAMNet wrappers.

YAMNetFrozen: MLP head on cached TF-Hub YAMNet embeddings (1024-d). Needs cfg `features: yamnet_emb`
              (src/cache_yamnet_emb.py). forward(emb[B,1024]) -> logits. Teacher/student KD on waveforms not applicable.
YAMNetFT:     PyTorch port from third_party/torch_audioset (weights converted from TF yamnet.h5), full fine-tune.
              Frontend = the port's own log-mel (torch_audioset WaveformToInput.mel_trans_ope: 16 kHz, 25 ms / 10 ms, 64 mel 125-7500 Hz).
              A 2 s clip -> 2 non-overlapping 0.96 s patches [B*2,1,96,64] (pretraining layout); patch logits averaged.
              forward(waveform[B,32000]) -> logits.
"""
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torchaudio

ROOT = Path(__file__).resolve().parents[2]
TAS = ROOT / "third_party" / "torch_audioset"


class YAMNetFrozen(nn.Module):
    def __init__(self, n_classes, in_dim=1024, hidden=512, dropout=0.3):
        super().__init__()
        self.net = nn.Sequential(nn.LayerNorm(in_dim), nn.Linear(in_dim, hidden), nn.GELU(), nn.Dropout(dropout), nn.Linear(hidden, n_classes))
        self.n_classes = n_classes

    def forward(self, emb):
        return self.net(emb)


class YAMNetFT(nn.Module):
    SR = 16000

    def __init__(self, n_classes, pretrained=True, freqm=8, timem=20):
        super().__init__()
        if str(TAS) not in sys.path:
            sys.path.insert(0, str(TAS))
        from torch_audioset.yamnet.model import YAMNet, ckpt_url
        from torch_audioset.data.torch_input_processing import WaveformToInput
        self.mel = WaveformToInput().mel_trans_ope  # the port's own log-mel (VGGish/YAMNet params), [B,T] -> [B,64,frames] log-mel
        self.freqm = torchaudio.transforms.FrequencyMasking(freqm) if freqm else None
        self.timem = torchaudio.transforms.TimeMasking(timem) if timem else None
        self.net = YAMNet()
        if pretrained:
            sd = torch.hub.load_state_dict_from_url(ckpt_url, model_dir=str(ROOT / "checkpoints" / "pretrained"), map_location="cpu")
            self.net.load_state_dict(sd)
        self.net.classifier = nn.Linear(1024, n_classes)
        self.n_classes = n_classes

    PATCH = 96  # frames (0.96 s), as in YAMNet pretraining

    def frontend(self, wav):  # [B,T] -> [B*P,1,96,64] (YAMNet layout: time x mel), P = non-overlapping 0.96 s patches
        with torch.autocast(device_type=wav.device.type, enabled=False):
            x = self.mel(wav.float())  # log-mel from the port (log offset inside), [B,64,frames]
        if self.training:
            if self.freqm is not None:
                x = self.freqm(x)
            if self.timem is not None:
                x = self.timem(x)
        x = x.transpose(1, 2)  # [B,frames,64]
        n = x.size(1) // self.PATCH
        x = x[:, : n * self.PATCH].reshape(x.size(0) * n, 1, self.PATCH, x.size(2))
        return x

    def forward(self, wav):
        b = wav.size(0)
        logits = self.net(self.frontend(wav))  # [B*P, n]
        return logits.reshape(b, -1, self.n_classes).mean(1)  # average patch logits (2 patches for a 2 s clip)


if __name__ == "__main__":
    m = YAMNetFrozen(14).eval()
    assert m(torch.zeros(2, 1024)).shape == (2, 14)
    f = YAMNetFT(14).eval()
    with torch.no_grad():
        y = f(torch.zeros(2, 32000))
    assert y.shape == (2, 14)
    print("yamnet selftest ok: frozen %.2fM, ft %.2fM, frontend %s" % (
        sum(p.numel() for p in m.parameters()) / 1e6, sum(p.numel() for p in f.parameters()) / 1e6, tuple(f.frontend(torch.zeros(1, 32000)).shape)))
