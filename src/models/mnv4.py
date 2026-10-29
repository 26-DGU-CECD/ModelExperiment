"""MobileNetV4-conv-small (timm, ImageNet-pretrained, in_chans=1) on a 16 kHz log-mel frontend.

Frontend deliberately differs from EfficientAT (ensemble diversity): 16 kHz, 64 mel bins, n_fft 1024, hop 160 -> [B,1,64,201].
Per-utterance log-mel normalisation (mean/std). SpecAugment (freq/time masks) in train mode.
"""
import torch
import torch.nn as nn
import torchaudio


class MNv4Classifier(nn.Module):
    SR = 16000

    def __init__(self, n_classes, backbone="mobilenetv4_conv_small.e2400_r224_in1k", pretrained=True,
                 n_mels=64, n_fft=1024, hop=160, freqm=12, timem=40):
        super().__init__()
        import timm
        self.mel = torchaudio.transforms.MelSpectrogram(sample_rate=self.SR, n_fft=n_fft, win_length=n_fft, hop_length=hop,
                                                        n_mels=n_mels, f_min=20.0, f_max=8000.0, power=2.0)
        self.freqm = torchaudio.transforms.FrequencyMasking(freqm) if freqm else None
        self.timem = torchaudio.transforms.TimeMasking(timem) if timem else None
        self.net = timm.create_model(backbone, pretrained=pretrained, in_chans=1, num_classes=n_classes)
        self.n_classes = n_classes

    def frontend(self, wav):  # [B, T] -> [B, 1, n_mels, frames]
        with torch.autocast(device_type=wav.device.type, enabled=False):  # fp16 power-mel overflows -> NaN
            x = (self.mel(wav.float()) + 1e-6).log()
            x = (x - x.mean(dim=(1, 2), keepdim=True)) / (x.std(dim=(1, 2), keepdim=True) + 1e-5)
        if self.training:
            if self.freqm is not None:
                x = self.freqm(x)
            if self.timem is not None:
                x = self.timem(x)
        return x.unsqueeze(1)

    def forward(self, wav):
        return self.net(self.frontend(wav))


if __name__ == "__main__":
    m = MNv4Classifier(14).eval()
    with torch.no_grad():
        y = m(torch.zeros(2, 32000))
    assert y.shape == (2, 14)
    m.train()
    assert m(torch.randn(2, 32000) * 0.1).shape == (2, 14)
    print("mnv4 selftest ok, params %.2fM, mel %s" % (sum(p.numel() for p in m.parameters()) / 1e6, tuple(m.eval().frontend(torch.zeros(1, 32000)).shape)))
