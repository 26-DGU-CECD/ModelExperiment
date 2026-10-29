"""Model wrappers: build_model(name, n_classes, cfg) -> nn.Module with forward(waveform[B,32000]@16k) -> logits[B,n]."""


def build_model(name, n_classes, cfg=None):
    args = (cfg or {}).get("model_args", {}) or {}
    if name == "efficientat":
        from .efficientat import EfficientATClassifier
        return EfficientATClassifier(n_classes, **args)
    if name == "mnv4":
        from .mnv4 import MNv4Classifier
        return MNv4Classifier(n_classes, **args)
    if name == "yamnet":
        from .yamnet import YAMNetClassifier
        return YAMNetClassifier(n_classes, **args)
    raise ValueError(f"unknown model {name}")
