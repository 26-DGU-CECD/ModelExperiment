"""YAMNet (tensorflow_hub, CPU) stub. Interface: forward(waveform[B,32000]@16k) -> logits[B,n]. TODO (E1): embeddings + MLP head."""
import torch.nn as nn


class YAMNetClassifier(nn.Module):
    def __init__(self, n_classes, **kwargs):
        super().__init__()
        self.n_classes = n_classes
        raise NotImplementedError("yamnet wrapper not implemented yet (E1)")

    def forward(self, wav):
        raise NotImplementedError
