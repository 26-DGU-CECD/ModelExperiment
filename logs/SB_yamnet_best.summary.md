# SB_yamnet_best

model=yamnet_ft mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.2651 | 0.3570 | - | - | |
| 0 | 0.6656 | 0.2119 | 0.9232 | 0.9840 | 1.99e-05 | 35 | * |
| 1 | 0.6491 | 0.2034 | 0.9254 | 0.9804 | 1.95e-05 | 29 | * |
| 2 | 0.6453 | 0.2092 | 0.9184 | 0.9804 | 1.89e-05 | 29 |  |
| 3 | 0.6396 | 0.2274 | 0.9130 | 0.9766 | 1.81e-05 | 29 |  |
| 4 | 0.6446 | 0.2194 | 0.9276 | 0.9813 | 1.71e-05 | 29 | * |
| 5 | 0.6449 | 0.2185 | 0.9289 | 0.9792 | 1.59e-05 | 29 | * |
| 6 | 0.6385 | 0.2205 | 0.9297 | 0.9804 | 1.45e-05 | 29 | * |
| 7 | 0.6403 | 0.2267 | 0.9359 | 0.9846 | 1.31e-05 | 29 | * |
| 8 | 0.6377 | 0.2060 | 0.9290 | 0.9839 | 1.16e-05 | 29 |  |
| 9 | 0.6408 | 0.2286 | 0.9281 | 0.9830 | 1.00e-05 | 29 |  |
| 10 | 0.6319 | 0.2067 | 0.9304 | 0.9830 | 8.44e-06 | 29 |  |
| 11 | 0.6344 | 0.2161 | 0.9315 | 0.9820 | 6.91e-06 | 29 |  |
| 12 | 0.6274 | 0.2282 | 0.9252 | 0.9781 | 5.46e-06 | 29 |  |
| 13 | 0.6264 | 0.2064 | 0.9309 | 0.9825 | 4.12e-06 | 29 |  |
# SB_yamnet_best

model=yamnet_ft mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.2651 | 0.3570 | - | - | |
| 0 | 0.6656 | 0.2119 | 0.9232 | 0.9840 | 1.99e-05 | 32 | * |
| 1 | 0.6491 | 0.2034 | 0.9254 | 0.9804 | 1.95e-05 | 29 | * |
| 2 | 0.6453 | 0.2092 | 0.9184 | 0.9804 | 1.89e-05 | 28 |  |
| 3 | 0.6396 | 0.2274 | 0.9130 | 0.9766 | 1.81e-05 | 29 |  |
| 4 | 0.6446 | 0.2194 | 0.9276 | 0.9813 | 1.71e-05 | 29 | * |
| 5 | 0.6449 | 0.2185 | 0.9289 | 0.9792 | 1.59e-05 | 29 | * |
| 6 | 0.6385 | 0.2205 | 0.9297 | 0.9804 | 1.45e-05 | 29 | * |
| 7 | 0.6403 | 0.2267 | 0.9359 | 0.9846 | 1.31e-05 | 29 | * |
| 8 | 0.6377 | 0.2060 | 0.9290 | 0.9839 | 1.16e-05 | 29 |  |
| 9 | 0.6408 | 0.2286 | 0.9281 | 0.9830 | 1.00e-05 | 29 |  |
| 10 | 0.6319 | 0.2067 | 0.9304 | 0.9830 | 8.44e-06 | 29 |  |
| 11 | 0.6344 | 0.2161 | 0.9315 | 0.9820 | 6.91e-06 | 29 |  |
| 12 | 0.6274 | 0.2282 | 0.9252 | 0.9781 | 5.46e-06 | 29 |  |
| 13 | 0.6264 | 0.2064 | 0.9309 | 0.9825 | 4.12e-06 | 29 |  |
| 14 | 0.6308 | 0.2172 | 0.9316 | 0.9788 | 2.93e-06 | 29 |  |
| 15 | 0.6297 | 0.2167 | 0.9360 | 0.9818 | 1.91e-06 | 29 | * |
| 16 | 0.6331 | 0.2113 | 0.9291 | 0.9802 | 1.09e-06 | 29 |  |
| 17 | 0.6297 | 0.2135 | 0.9262 | 0.9813 | 4.90e-07 | 29 |  |
| 18 | 0.6365 | 0.2113 | 0.9280 | 0.9825 | 1.23e-07 | 29 |  |
| 19 | 0.6328 | 0.2129 | 0.9295 | 0.9807 | 0.00e+00 | 29 |  |

best val macro-F1 = 0.9360

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| alarm | 0.8420 | 0.9644 | +0.1224 |
| gunshot | 0.0000 | 0.9420 | +0.9420 |
| dog_bark | 0.0101 | 0.8026 | +0.7925 |
| knock | 0.0115 | 0.9818 | +0.9703 |
| other | 0.4618 | 0.9891 | +0.5273 |

mean delta over own classes = +0.7068


## evaluate (2026-10-30) best epoch 15

#### vs generalist E1k_v2 (remapped to own+other), val: mean delta own -0.0024

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9658 | 0.9644 | -0.0014 |
| gunshot | 0.9501 | 0.9420 | -0.0081 |
| dog_bark | 0.8535 | 0.8026 | -0.0509 |
| knock | 0.9310 | 0.9818 | +0.0508 |
| other | 0.9901 | 0.9891 | -0.0010 |

### val: acc 0.9818 macro-F1 0.9227 reject(non-target events) 0.9945088468578401 reject(bg) 0.9782608695652174

| true \ pred | alarm | gunshot | dog_bark | knock | other |
|---|---|---|---|---|---|
| alarm | 556 | 0 | 0 | 0 | 13 |
| gunshot | 0 | 268 | 0 | 0 | 14 |
| dog_bark | 0 | 0 | 61 | 0 | 27 |
| knock | 0 | 0 | 0 | 27 | 0 |
| other | 28 | 19 | 3 | 1 | 4745 |

#### vs generalist E1k_v2 (remapped to own+other), test: mean delta own -0.0005

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.9461 | 0.9370 | -0.0091 |
| gunshot | 0.9259 | 0.9157 | -0.0102 |
| dog_bark | 0.8931 | 0.9103 | +0.0172 |
| knock | 0.9180 | 0.9180 | +0.0000 |
| other | 0.9858 | 0.9842 | -0.0017 |

### test: acc 0.9740 macro-F1 0.9203 reject(non-target events) 0.991701244813278 reject(bg) 0.9765957446808511

| true \ pred | alarm | gunshot | dog_bark | knock | other |
|---|---|---|---|---|---|
| alarm | 625 | 0 | 0 | 0 | 61 |
| gunshot | 0 | 277 | 0 | 1 | 17 |
| dog_bark | 0 | 0 | 71 | 0 | 10 |
| knock | 0 | 0 | 0 | 28 | 3 |
| other | 23 | 33 | 4 | 1 | 4723 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0015

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7192 | 0.7220 | +0.0029 |
| gunshot | 0.9172 | 0.9028 | -0.0144 |
| dog_bark | 0.8712 | 0.9091 | +0.0379 |
| knock | 0.9091 | 0.8889 | -0.0202 |
| other | 0.9389 | 0.9391 | +0.0002 |

### noisy_snr20: acc 0.9045 macro-F1 0.8557 reject(non-target events) 0.9932478055367995 reject(bg) 0.975886524822695

| true \ pred | alarm | gunshot | dog_bark | knock | other |
|---|---|---|---|---|---|
| alarm | 626 | 0 | 0 | 0 | 472 |
| gunshot | 0 | 274 | 0 | 1 | 20 |
| dog_bark | 0 | 0 | 70 | 0 | 11 |
| knock | 0 | 0 | 0 | 28 | 3 |
| other | 10 | 38 | 3 | 3 | 4318 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0042

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7166 | 0.7192 | +0.0026 |
| gunshot | 0.9091 | 0.9128 | +0.0037 |
| dog_bark | 0.8659 | 0.8987 | +0.0329 |
| knock | 0.8406 | 0.8182 | -0.0224 |
| other | 0.9378 | 0.9393 | +0.0015 |

### noisy_snr15: acc 0.9044 macro-F1 0.8372 reject(non-target events) 0.9939230249831195 reject(bg) 0.9787234042553191

| true \ pred | alarm | gunshot | dog_bark | knock | other |
|---|---|---|---|---|---|
| alarm | 621 | 0 | 1 | 1 | 475 |
| gunshot | 0 | 272 | 0 | 1 | 22 |
| dog_bark | 0 | 0 | 71 | 0 | 10 |
| knock | 0 | 0 | 0 | 27 | 4 |
| other | 8 | 29 | 5 | 6 | 4324 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0464

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| alarm | 0.7161 | 0.7172 | +0.0011 |
| gunshot | 0.8838 | 0.9061 | +0.0223 |
| dog_bark | 0.8452 | 0.8917 | +0.0465 |
| knock | 0.6842 | 0.8000 | +0.1158 |
| other | 0.9343 | 0.9377 | +0.0035 |

### noisy_snr10: acc 0.9023 macro-F1 0.8287 reject(non-target events) 0.9912221471978393 reject(bg) 0.9773049645390071

| true \ pred | alarm | gunshot | dog_bark | knock | other |
|---|---|---|---|---|---|
| alarm | 620 | 0 | 0 | 0 | 478 |
| gunshot | 0 | 275 | 0 | 1 | 19 |
| dog_bark | 0 | 0 | 70 | 0 | 11 |
| knock | 0 | 0 | 0 | 24 | 7 |
| other | 11 | 37 | 6 | 4 | 4314 |

