# S_mn10_daily

model=efficientat mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0477 | 0.0410 | - | - | |
| 0 | 0.7445 | 0.2012 | 0.9047 | 0.9734 | 1.99e-05 | 41 | * |
| 1 | 0.7314 | 0.2192 | 0.9012 | 0.9743 | 1.95e-05 | 28 |  |
| 2 | 0.7271 | 0.2427 | 0.9010 | 0.9724 | 1.89e-05 | 28 |  |
| 3 | 0.7275 | 0.2291 | 0.8994 | 0.9714 | 1.81e-05 | 28 |  |
| 4 | 0.7278 | 0.2260 | 0.9035 | 0.9741 | 1.71e-05 | 27 |  |
| 5 | 0.7259 | 0.2414 | 0.8991 | 0.9733 | 1.59e-05 | 28 |  |
| 6 | 0.7239 | 0.2275 | 0.9022 | 0.9741 | 1.45e-05 | 28 |  |
| 7 | 0.7235 | 0.2766 | 0.8935 | 0.9722 | 1.31e-05 | 28 |  |
| 8 | 0.7198 | 0.2516 | 0.8949 | 0.9728 | 1.16e-05 | 28 |  |

best val macro-F1 = 0.9047

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| water | 0.0000 | 0.8867 | +0.8867 |
| knock | 0.0085 | 0.8852 | +0.8768 |
| dog_bark | 0.0904 | 0.8553 | +0.7650 |
| cat_meow | 0.0934 | 0.9103 | +0.8169 |
| other | 0.0464 | 0.9858 | +0.9395 |

mean delta over own classes = +0.8363


## evaluate (2026-10-30) best epoch 0

#### vs generalist E0m_v2 (remapped to own+other), val: mean delta own +0.0163

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8862 | 0.8867 | +0.0005 |
| knock | 0.8308 | 0.8852 | +0.0545 |
| dog_bark | 0.8395 | 0.8553 | +0.0158 |
| cat_meow | 0.9158 | 0.9103 | -0.0055 |
| other | 0.9842 | 0.9858 | +0.0016 |

### val: acc 0.9734 macro-F1 0.8844 reject(non-target events) 0.9991391678622669 reject(bg) 0.9617918313570487

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 364 | 1 | 2 | 0 | 55 |
| knock | 0 | 27 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 68 | 6 | 14 |
| cat_meow | 0 | 1 | 1 | 208 | 12 |
| other | 35 | 5 | 0 | 21 | 4942 |

#### vs generalist E0m_v2 (remapped to own+other), test: mean delta own +0.0131

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9287 | 0.9073 | -0.0214 |
| knock | 0.8857 | 0.9841 | +0.0984 |
| dog_bark | 0.9877 | 0.9875 | -0.0002 |
| cat_meow | 0.9293 | 0.9050 | -0.0243 |
| other | 0.9888 | 0.9871 | -0.0017 |

### test: acc 0.9777 macro-F1 0.9460 reject(non-target events) 0.9997251992305578 reject(bg) 0.975886524822695

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 460 | 0 | 0 | 0 | 71 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 79 | 0 | 2 |
| cat_meow | 0 | 0 | 0 | 162 | 23 |
| other | 23 | 1 | 0 | 11 | 5014 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0125

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9332 | 0.9067 | -0.0265 |
| knock | 0.8158 | 0.9394 | +0.1236 |
| dog_bark | 0.9814 | 0.9686 | -0.0128 |
| cat_meow | 0.9030 | 0.8686 | -0.0345 |
| other | 0.9887 | 0.9865 | -0.0021 |

### noisy_snr20: acc 0.9757 macro-F1 0.9208 reject(non-target events) 0.9997251992305578 reject(bg) 0.9780141843971631

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 457 | 1 | 0 | 0 | 73 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 1 | 0 | 77 | 2 | 1 |
| cat_meow | 0 | 1 | 1 | 152 | 31 |
| other | 19 | 2 | 0 | 11 | 5017 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0318

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9201 | 0.8916 | -0.0285 |
| knock | 0.7294 | 0.8955 | +0.1661 |
| dog_bark | 0.9518 | 0.9620 | +0.0102 |
| cat_meow | 0.9121 | 0.8914 | -0.0207 |
| other | 0.9855 | 0.9848 | -0.0007 |

### noisy_snr15: acc 0.9733 macro-F1 0.9101 reject(non-target events) 0.9989007969222314 reject(bg) 0.9780141843971631

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 444 | 0 | 0 | 0 | 87 |
| knock | 0 | 30 | 0 | 0 | 1 |
| dog_bark | 0 | 0 | 76 | 2 | 3 |
| cat_meow | 0 | 0 | 0 | 156 | 29 |
| other | 21 | 6 | 1 | 7 | 5014 |

#### vs generalist E0m_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0269

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.9099 | 0.8710 | -0.0389 |
| knock | 0.6517 | 0.8169 | +0.1652 |
| dog_bark | 0.9506 | 0.9427 | -0.0079 |
| cat_meow | 0.8747 | 0.8639 | -0.0107 |
| other | 0.9831 | 0.9820 | -0.0012 |

### noisy_snr10: acc 0.9677 macro-F1 0.8736 reject(non-target events) 0.9989007969222314 reject(bg) 0.9723404255319149

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 432 | 1 | 0 | 0 | 98 |
| knock | 1 | 29 | 0 | 0 | 1 |
| dog_bark | 1 | 0 | 74 | 2 | 4 |
| cat_meow | 0 | 1 | 0 | 146 | 38 |
| other | 27 | 9 | 2 | 5 | 5006 |

