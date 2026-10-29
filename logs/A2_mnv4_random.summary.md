# A2_mnv4_random

model=mnv4 mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.2573 | 0.2742 | - | - | |
| 0 | 0.7215 | 0.2455 | 0.9322 | 0.9599 | 1.99e-05 | 32 | * |
| 1 | 0.6660 | 0.2515 | 0.9335 | 0.9644 | 1.95e-05 | 19 | * |
| 2 | 0.6587 | 0.2472 | 0.9295 | 0.9618 | 1.89e-05 | 18 |  |
| 3 | 0.6524 | 0.2332 | 0.9322 | 0.9646 | 1.81e-05 | 18 |  |
| 4 | 0.6548 | 0.2390 | 0.9266 | 0.9641 | 1.71e-05 | 18 |  |
| 5 | 0.6556 | 0.2367 | 0.9269 | 0.9630 | 1.59e-05 | 18 |  |
| 6 | 0.6487 | 0.2363 | 0.9237 | 0.9616 | 1.45e-05 | 18 |  |
| 7 | 0.6524 | 0.2437 | 0.9288 | 0.9646 | 1.31e-05 | 18 |  |
| 8 | 0.6483 | 0.2414 | 0.9286 | 0.9648 | 1.16e-05 | 18 |  |
| 9 | 0.6494 | 0.2311 | 0.9278 | 0.9655 | 1.00e-05 | 19 |  |

best val macro-F1 = 0.9335

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| glass_break | 0.5047 | 0.9335 | +0.4288 |
| dog_bark | 0.0598 | 0.8421 | +0.7824 |
| fire_alarm | 0.6553 | 0.9920 | +0.3368 |
| cry | 0.0000 | 0.9276 | +0.9276 |
| other | 0.0666 | 0.9723 | +0.9057 |

mean delta over own classes = +0.6189


## evaluate (2026-10-30) best epoch 1

#### vs generalist E2k_v2 (remapped to own+other), val: mean delta own -0.0041

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| glass_break | 0.9425 | 0.9335 | -0.0090 |
| dog_bark | 0.8535 | 0.8421 | -0.0114 |
| fire_alarm | 0.9874 | 0.9920 | +0.0047 |
| cry | 0.9283 | 0.9276 | -0.0008 |
| other | 0.9743 | 0.9723 | -0.0020 |

### val: acc 0.9644 macro-F1 0.9238 reject(non-target events) 0.9858898497951752 reject(bg) 0.9446640316205533

| true \ pred | glass_break | dog_bark | fire_alarm | cry | other |
|---|---|---|---|---|---|
| glass_break | 716 | 0 | 0 | 0 | 50 |
| dog_bark | 0 | 64 | 0 | 0 | 24 |
| fire_alarm | 0 | 0 | 748 | 0 | 4 |
| cry | 0 | 0 | 0 | 429 | 12 |
| other | 52 | 0 | 8 | 55 | 3600 |

#### vs generalist E2k_v2 (remapped to own+other), test: mean delta own -0.0053

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| glass_break | 0.9485 | 0.9534 | +0.0049 |
| dog_bark | 0.9753 | 0.9634 | -0.0119 |
| fire_alarm | 0.9885 | 0.9867 | -0.0019 |
| cry | 0.9371 | 0.9247 | -0.0124 |
| other | 0.9797 | 0.9785 | -0.0012 |

### test: acc 0.9721 macro-F1 0.9570 reject(non-target events) 0.9936006825938567 reject(bg) 0.9460992907801419

| true \ pred | glass_break | dog_bark | fire_alarm | cry | other |
|---|---|---|---|---|---|
| glass_break | 757 | 0 | 0 | 0 | 37 |
| dog_bark | 0 | 79 | 0 | 0 | 2 |
| fire_alarm | 0 | 0 | 815 | 0 | 22 |
| cry | 0 | 3 | 0 | 399 | 9 |
| other | 37 | 1 | 0 | 53 | 3663 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0008

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| glass_break | 0.9431 | 0.9398 | -0.0033 |
| dog_bark | 0.9133 | 0.9294 | +0.0161 |
| fire_alarm | 0.6672 | 0.6656 | -0.0016 |
| cry | 0.9012 | 0.8931 | -0.0081 |
| other | 0.9238 | 0.9225 | -0.0013 |

### noisy_snr20: acc 0.8957 macro-F1 0.8570 reject(non-target events) 0.8494194484760522 reject(bg) 0.9113475177304965

| true \ pred | glass_break | dog_bark | fire_alarm | cry | other |
|---|---|---|---|---|---|
| glass_break | 750 | 0 | 0 | 0 | 44 |
| dog_bark | 0 | 79 | 0 | 0 | 2 |
| fire_alarm | 0 | 0 | 412 | 1 | 12 |
| cry | 0 | 3 | 0 | 397 | 11 |
| other | 52 | 7 | 401 | 80 | 3626 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr15: mean delta own -0.0045

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| glass_break | 0.9463 | 0.9467 | +0.0004 |
| dog_bark | 0.9080 | 0.9080 | +0.0000 |
| fire_alarm | 0.6688 | 0.6645 | -0.0043 |
| cry | 0.8939 | 0.8799 | -0.0140 |
| other | 0.9242 | 0.9219 | -0.0023 |

### noisy_snr15: acc 0.8947 macro-F1 0.8498 reject(non-target events) 0.8454281567489115 reject(bg) 0.9212765957446809

| true \ pred | glass_break | dog_bark | fire_alarm | cry | other |
|---|---|---|---|---|---|
| glass_break | 746 | 0 | 0 | 0 | 48 |
| dog_bark | 0 | 79 | 0 | 0 | 2 |
| fire_alarm | 0 | 0 | 412 | 1 | 12 |
| cry | 0 | 3 | 0 | 392 | 16 |
| other | 36 | 11 | 403 | 87 | 3629 |

#### vs generalist E2k_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0089

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| glass_break | 0.9288 | 0.9361 | +0.0073 |
| dog_bark | 0.8800 | 0.9176 | +0.0376 |
| fire_alarm | 0.6677 | 0.6688 | +0.0011 |
| cry | 0.8846 | 0.8741 | -0.0104 |
| other | 0.9194 | 0.9206 | +0.0011 |

### noisy_snr10: acc 0.8926 macro-F1 0.8492 reject(non-target events) 0.8457910014513788 reject(bg) 0.9276595744680851

| true \ pred | glass_break | dog_bark | fire_alarm | cry | other |
|---|---|---|---|---|---|
| glass_break | 733 | 0 | 0 | 0 | 61 |
| dog_bark | 0 | 78 | 0 | 0 | 3 |
| fire_alarm | 0 | 0 | 414 | 0 | 11 |
| cry | 0 | 3 | 0 | 382 | 26 |
| other | 39 | 8 | 399 | 81 | 3639 |

