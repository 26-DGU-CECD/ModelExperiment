# A2_yamnet_random

model=yamnet_ft mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.0929 | 0.2470 | - | - | |
| 0 | 0.6795 | 0.2653 | 0.9338 | 0.9684 | 1.99e-05 | 32 | * |
| 1 | 0.6591 | 0.2444 | 0.9310 | 0.9662 | 1.95e-05 | 29 |  |
| 2 | 0.6553 | 0.2320 | 0.9348 | 0.9688 | 1.89e-05 | 29 | * |
| 3 | 0.6523 | 0.2613 | 0.9276 | 0.9637 | 1.81e-05 | 29 |  |
| 4 | 0.6568 | 0.2664 | 0.9289 | 0.9651 | 1.71e-05 | 29 |  |
| 5 | 0.6537 | 0.2478 | 0.9284 | 0.9651 | 1.59e-05 | 29 |  |
| 6 | 0.6504 | 0.2604 | 0.9294 | 0.9642 | 1.45e-05 | 29 |  |
| 7 | 0.6486 | 0.2556 | 0.9263 | 0.9648 | 1.31e-05 | 29 |  |
| 8 | 0.6476 | 0.2481 | 0.9271 | 0.9648 | 1.16e-05 | 29 |  |
| 9 | 0.6475 | 0.2748 | 0.9292 | 0.9641 | 1.00e-05 | 29 |  |
| 10 | 0.6421 | 0.2548 | 0.9264 | 0.9634 | 8.44e-06 | 29 |  |

best val macro-F1 = 0.9348

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| scream | 0.0090 | 0.9141 | +0.9050 |
| gunshot | 0.0000 | 0.9449 | +0.9449 |
| bicycle | 0.0000 | 0.9603 | +0.9603 |
| water | 0.0047 | 0.8741 | +0.8694 |
| other | 0.4510 | 0.9806 | +0.5297 |

mean delta over own classes = +0.9199


## evaluate (2026-10-30) best epoch 2

#### vs generalist E1k_v2 (remapped to own+other), val: mean delta own +0.0005

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| scream | 0.9057 | 0.9141 | +0.0084 |
| gunshot | 0.9501 | 0.9449 | -0.0051 |
| bicycle | 0.9513 | 0.9603 | +0.0090 |
| water | 0.8843 | 0.8741 | -0.0102 |
| other | 0.9808 | 0.9806 | -0.0001 |

### val: acc 0.9688 macro-F1 0.9233 reject(non-target events) 0.9977542508822586 reject(bg) 0.9552042160737813

| true \ pred | scream | gunshot | bicycle | water | other |
|---|---|---|---|---|---|
| scream | 117 | 0 | 0 | 0 | 16 |
| gunshot | 0 | 266 | 0 | 0 | 16 |
| bicycle | 0 | 0 | 278 | 0 | 12 |
| water | 0 | 0 | 0 | 361 | 61 |
| other | 6 | 15 | 11 | 43 | 4560 |

#### vs generalist E1k_v2 (remapped to own+other), test: mean delta own -0.0115

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| scream | 0.9574 | 0.9356 | -0.0218 |
| gunshot | 0.9259 | 0.9143 | -0.0116 |
| bicycle | 0.9142 | 0.9173 | +0.0031 |
| water | 0.9100 | 0.8943 | -0.0157 |
| other | 0.9793 | 0.9763 | -0.0030 |

### test: acc 0.9624 macro-F1 0.9154 reject(non-target events) 0.9956883276870958 reject(bg) 0.9354609929078014

| true \ pred | scream | gunshot | bicycle | water | other |
|---|---|---|---|---|---|
| scream | 138 | 0 | 0 | 0 | 9 |
| gunshot | 0 | 272 | 0 | 0 | 23 |
| bicycle | 0 | 0 | 233 | 0 | 14 |
| water | 0 | 0 | 0 | 461 | 70 |
| other | 10 | 28 | 28 | 39 | 4552 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr20: mean delta own +0.0014

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| scream | 0.9316 | 0.9459 | +0.0143 |
| gunshot | 0.9172 | 0.9138 | -0.0034 |
| bicycle | 0.9081 | 0.9222 | +0.0141 |
| water | 0.9119 | 0.8926 | -0.0193 |
| other | 0.9778 | 0.9769 | -0.0009 |

### noisy_snr20: acc 0.9632 macro-F1 0.9186 reject(non-target events) 0.9959963042808746 reject(bg) 0.9418439716312057

| true \ pred | scream | gunshot | bicycle | water | other |
|---|---|---|---|---|---|
| scream | 140 | 0 | 0 | 0 | 7 |
| gunshot | 0 | 265 | 0 | 0 | 30 |
| bicycle | 0 | 0 | 237 | 0 | 10 |
| water | 0 | 0 | 0 | 457 | 74 |
| other | 9 | 20 | 30 | 36 | 4562 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr15: mean delta own +0.0038

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| scream | 0.9016 | 0.9310 | +0.0294 |
| gunshot | 0.9091 | 0.9057 | -0.0034 |
| bicycle | 0.9121 | 0.9234 | +0.0112 |
| water | 0.9031 | 0.8812 | -0.0219 |
| other | 0.9762 | 0.9749 | -0.0013 |

### noisy_snr15: acc 0.9600 macro-F1 0.9103 reject(non-target events) 0.9947643979057592 reject(bg) 0.9411347517730496

| true \ pred | scream | gunshot | bicycle | water | other |
|---|---|---|---|---|---|
| scream | 135 | 0 | 0 | 0 | 12 |
| gunshot | 0 | 264 | 0 | 0 | 31 |
| bicycle | 0 | 0 | 241 | 0 | 6 |
| water | 0 | 0 | 0 | 445 | 86 |
| other | 8 | 24 | 34 | 34 | 4557 |

#### vs generalist E1k_v2 (remapped to own+other), noisy_snr10: mean delta own +0.0107

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| scream | 0.9057 | 0.9347 | +0.0290 |
| gunshot | 0.8838 | 0.9028 | +0.0190 |
| bicycle | 0.8901 | 0.8977 | +0.0076 |
| water | 0.8906 | 0.8776 | -0.0130 |
| other | 0.9713 | 0.9734 | +0.0022 |

### noisy_snr10: acc 0.9573 macro-F1 0.9032 reject(non-target events) 0.9916846319679704 reject(bg) 0.9397163120567376

| true \ pred | scream | gunshot | bicycle | water | other |
|---|---|---|---|---|---|
| scream | 136 | 0 | 0 | 0 | 11 |
| gunshot | 0 | 260 | 0 | 1 | 34 |
| bicycle | 0 | 0 | 237 | 1 | 9 |
| water | 0 | 1 | 0 | 448 | 82 |
| other | 8 | 20 | 44 | 40 | 4545 |

