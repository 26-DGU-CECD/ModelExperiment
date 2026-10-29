"""MobileNetV4 (timm) stub. Interface: forward(waveform[B,32000]@16k) -> logits[B,n]. TODO (E2): mel frontend + timm backbone."""
import torch.nn as nn


class MNv4Classifier(nn.Module):
    def __init__(self, n_classes, **kwargs):
        super().__init__()
        self.n_classes = n_classes
        raise NotImplementedError("mnv4 wrapper not implemented yet (E2)")

    def forward(self, wav):
        raise NotImplementedError
