"""EfficientAT mn10_as (MobileNetV3, AudioSet-pretrained) fine-tuning wrapper. See docs/third_party.md."""
import sys
from pathlib import Path

import torch
import torch.nn as nn
import torchaudio

ROOT = Path(__file__).resolve().parents[2]
EAT = ROOT / "third_party" / "EfficientAT"
if str(EAT) not in sys.path:
    sys.path.insert(0, str(EAT))
import os  # noqa: E402

_cwd = os.getcwd()
os.chdir(EAT)  # helpers.utils reads metadata/class_labels_indices.csv relative to cwd at import time
try:
    import models.mn.model as mn  # noqa: E402  EfficientAT package (not src.models)
    import models.dymn.model as dymn  # noqa: E402  dynamic MobileNet (dymn04/10/20_as)
    from models.preprocess import AugmentMelSTFT  # noqa: E402
finally:
    os.chdir(_cwd)

mn.model_dir = str(ROOT / "checkpoints" / "pretrained")  # mn10_as.pt cache (git-ignored)
dymn.model_dir = mn.model_dir


def name_to_width(name):  # "mn10_as" -> 1.0, "mn04_as" -> 0.4, "dymn10_as" -> 1.0 (helpers.utils.NAME_TO_WIDTH needs cwd-relative metadata)
    import re
    return int(re.search(r"(\d{2})", name).group(1)) / 10


class EfficientATClassifier(nn.Module):
    IN_SR, SR = 16000, 32000

    def __init__(self, n_classes, pretrained_name="mn10_as", width_mult=None, head_type="mlp", freqm=48, timem=192):
        super().__init__()
        Path(mn.model_dir).mkdir(parents=True, exist_ok=True)
        self.mel = AugmentMelSTFT(n_mels=128, sr=self.SR, win_length=800, hopsize=320, n_fft=1024, freqm=freqm, timem=timem)
        if width_mult is None:
            width_mult = name_to_width(pretrained_name) if pretrained_name else 1.0
        # pretrained_name=None -> random init (ablation A1). "dymn*" -> dynamic MobileNet family (no head_type arg).
        if pretrained_name and pretrained_name.startswith("dymn"):
            self.net = dymn.get_model(num_classes=n_classes, pretrained_name=pretrained_name, width_mult=width_mult)
        else:
            self.net = mn.get_model(num_classes=n_classes, pretrained_name=pretrained_name or None, width_mult=width_mult, head_type=head_type)
        self.n_classes = n_classes

    def forward(self, wav):  # wav [B, 32000] @16k
        x = torchaudio.functional.resample(wav, self.IN_SR, self.SR)  # [B, 64000]
        x = self.mel(x).unsqueeze(1)  # [B, 1, 128, T]; SpecAugment only in train mode
        out = self.net(x)
        logits = out[0] if isinstance(out, (tuple, list)) else out
        return logits.reshape(wav.size(0), self.n_classes)


if __name__ == "__main__":
    m = EfficientATClassifier(14).eval()
    with torch.no_grad():
        y = m(torch.zeros(2, 32000))
    assert y.shape == (2, 14)
    print("efficientat selftest ok, params: %.2fM" % (sum(p.numel() for p in m.parameters()) / 1e6))
