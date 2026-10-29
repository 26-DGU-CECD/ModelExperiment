# S3_mnv4_daily

model=mnv4 mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0601 | 0.0691 | - | - | |
| 0 | 0.7424 | 0.2531 | 0.8996 | 0.9653 | 1.99e-05 | 33 | * |
| 1 | 0.6785 | 0.2650 | 0.8809 | 0.9592 | 1.95e-05 | 17 |  |
| 2 | 0.6724 | 0.2594 | 0.8928 | 0.9644 | 1.89e-05 | 18 |  |
| 3 | 0.6673 | 0.2545 | 0.8897 | 0.9641 | 1.81e-05 | 18 |  |
| 4 | 0.6698 | 0.2490 | 0.8860 | 0.9642 | 1.71e-05 | 18 |  |
| 5 | 0.6678 | 0.2506 | 0.8930 | 0.9665 | 1.59e-05 | 18 |  |
| 6 | 0.6668 | 0.2566 | 0.8931 | 0.9662 | 1.45e-05 | 18 |  |
| 7 | 0.6659 | 0.2619 | 0.8806 | 0.9629 | 1.31e-05 | 18 |  |
| 8 | 0.6625 | 0.2612 | 0.8871 | 0.9653 | 1.16e-05 | 17 |  |

best val macro-F1 = 0.8996

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| water | 0.2311 | 0.8339 | +0.6028 |
| knock | 0.0000 | 0.9310 | +0.9310 |
| dog_bark | 0.0027 | 0.8408 | +0.8381 |
| cat_meow | 0.0175 | 0.9115 | +0.8940 |
| other | 0.0491 | 0.9807 | +0.9315 |

mean delta over own classes = +0.8165


## evaluate (2026-10-29) best epoch 0

#### vs generalist E2k_v2 (remapped to own+other), val: mean delta own +0.0155

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8225 | 0.8339 | +0.0115 |
| knock | 0.8571 | 0.9310 | +0.0739 |
| dog_bark | 0.8535 | 0.8408 | -0.0127 |
| cat_meow | 0.9221 | 0.9115 | -0.0106 |
| other | 0.9782 | 0.9807 | +0.0024 |

### val: acc 0.9653 macro-F1 0.8793 reject(non-target events) 1.0 reject(bg) 0.9446640316205533

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 344 | 0 | 2 | 1 | 75 |
| knock | 0 | 27 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 66 | 1 | 21 |
| cat_meow | 0 | 1 | 1 | 206 | 14 |
| other | 59 | 3 | 0 | 22 | 4919 |

#### vs generalist E2k_v2 (remapped to own+other), test: mean delta own -0.0046

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8464 | 0.8315 | -0.0149 |
| knock | 0.9688 | 0.9524 | -0.0164 |
| dog_bark | 0.9753 | 0.9753 | +0.0000 |
| cat_meow | 0.8814 | 0.8941 | +0.0128 |
| other | 0.9797 | 0.9792 | -0.0005 |

### test: acc 0.9639 macro-F1 0.9133 reject(non-target events) 0.9994503984611157 reject(bg) 0.9574468085106383

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 417 | 0 | 0 | 0 | 114 |
| knock | 0 | 30 | 0 | 0 | 1 |
| dog_bark | 0 | 0 | 79 | 0 | 2 |
| cat_meow | 0 | 0 | 0 | 152 | 33 |
| other | 55 | 2 | 2 | 3 | 4987 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0155

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8408 | 0.8327 | -0.0081 |
| knock | 0.8378 | 0.8986 | +0.0607 |
| dog_bark | 0.9133 | 0.9349 | +0.0216 |
| cat_meow | 0.8701 | 0.8580 | -0.0121 |
| other | 0.9764 | 0.9775 | +0.0011 |

### noisy_snr20: acc 0.9607 macro-F1 0.8810 reject(non-target events) 0.9989007969222314 reject(bg) 0.951063829787234

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 418 | 0 | 0 | 1 | 112 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 79 | 0 | 2 |
| cat_meow | 0 | 0 | 1 | 142 | 42 |
| other | 55 | 7 | 8 | 3 | 4976 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0255

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8181 | 0.8186 | +0.0005 |
| knock | 0.7561 | 0.8732 | +0.1171 |
| dog_bark | 0.9080 | 0.9222 | +0.0141 |
| cat_meow | 0.8845 | 0.8545 | -0.0300 |
| other | 0.9741 | 0.9758 | +0.0017 |

### noisy_snr15: acc 0.9578 macro-F1 0.8671 reject(non-target events) 0.998351195383347 reject(bg) 0.9524822695035461

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 404 | 0 | 0 | 0 | 127 |
| knock | 0 | 31 | 0 | 0 | 0 |
| dog_bark | 0 | 0 | 77 | 0 | 4 |
| cat_meow | 0 | 1 | 0 | 141 | 43 |
| other | 52 | 8 | 9 | 4 | 4976 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0203

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| water | 0.8302 | 0.8095 | -0.0207 |
| knock | 0.7407 | 0.8286 | +0.0878 |
| dog_bark | 0.8800 | 0.9157 | +0.0357 |
| cat_meow | 0.8266 | 0.8050 | -0.0216 |
| other | 0.9741 | 0.9741 | +0.0000 |

### noisy_snr10: acc 0.9542 macro-F1 0.8397 reject(non-target events) 0.9975267930750206 reject(bg) 0.9588652482269504

| true \ pred | water | knock | dog_bark | cat_meow | other |
|---|---|---|---|---|---|
| water | 391 | 0 | 0 | 1 | 139 |
| knock | 1 | 29 | 0 | 0 | 1 |
| dog_bark | 0 | 0 | 76 | 0 | 5 |
| cat_meow | 0 | 0 | 2 | 130 | 53 |
| other | 43 | 10 | 7 | 7 | 4982 |

