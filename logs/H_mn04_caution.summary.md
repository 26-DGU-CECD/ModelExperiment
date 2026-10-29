# H_mn04_caution

model=efficientat mode=specialist classes=5 train=48060 val=5762 batch=64 lr=2e-05 cap=3000 teacher=-

| epoch | train_loss | val_loss | val_macro_f1 | val_acc | lr | sec | best |
|---|---|---|---|---|---|---|---|
| init | - | - | 0.1597 | 0.3292 | - | - | |
| 0 | 0.8113 | 0.2439 | 0.9408 | 0.9623 | 1.99e-05 | 63 | * |
| 1 | 0.7958 | 0.2328 | 0.9408 | 0.9608 | 1.95e-05 | 49 |  |
| 2 | 0.7953 | 0.2177 | 0.9481 | 0.9660 | 1.89e-05 | 48 | * |
| 3 | 0.7862 | 0.2326 | 0.9456 | 0.9649 | 1.81e-05 | 47 |  |
| 4 | 0.7904 | 0.2342 | 0.9459 | 0.9677 | 1.71e-05 | 48 |  |
| 5 | 0.7891 | 0.2335 | 0.9473 | 0.9672 | 1.59e-05 | 48 |  |
| 6 | 0.7851 | 0.2092 | 0.9476 | 0.9667 | 1.45e-05 | 48 |  |
| 7 | 0.7823 | 0.2350 | 0.9470 | 0.9641 | 1.31e-05 | 50 |  |
| 8 | 0.7821 | 0.2205 | 0.9482 | 0.9669 | 1.16e-05 | 48 | * |
| 9 | 0.7795 | 0.2273 | 0.9474 | 0.9667 | 1.00e-05 | 48 |  |
| 10 | 0.7756 | 0.2197 | 0.9521 | 0.9688 | 8.44e-06 | 48 | * |
| 11 | 0.7776 | 0.2284 | 0.9485 | 0.9662 | 6.91e-06 | 48 |  |
| 12 | 0.7691 | 0.2185 | 0.9496 | 0.9675 | 5.46e-06 | 48 |  |
| 13 | 0.7674 | 0.2148 | 0.9494 | 0.9665 | 4.12e-06 | 50 |  |
| 14 | 0.7749 | 0.2138 | 0.9500 | 0.9684 | 2.93e-06 | 48 |  |
| 15 | 0.7703 | 0.2123 | 0.9507 | 0.9681 | 1.91e-06 | 48 |  |
| 16 | 0.7739 | 0.2128 | 0.9519 | 0.9691 | 1.09e-06 | 48 |  |
| 17 | 0.7693 | 0.2118 | 0.9516 | 0.9686 | 4.90e-07 | 48 |  |
| 18 | 0.7728 | 0.2135 | 0.9524 | 0.9698 | 1.23e-07 | 48 | * |
| 19 | 0.7736 | 0.2142 | 0.9518 | 0.9689 | 0.00e+00 | 50 |  |

best val macro-F1 = 0.9524

### specialisation gain (val per-class F1: init = warm start before fine-tune, best = selected epoch)

| class | init F1 | best F1 | delta |
|---|---|---|---|
| bicycle | 0.0037 | 0.9310 | +0.9273 |
| baby_cry | 0.0022 | 0.9821 | +0.9799 |
| gunshot | 0.0078 | 0.9333 | +0.9256 |
| glass_break | 0.3731 | 0.9346 | +0.5615 |
| other | 0.4117 | 0.9811 | +0.5694 |

mean delta over own classes = +0.8486


## evaluate (2026-10-30) best epoch 18

#### vs generalist G_mn04 (remapped to own+other), val: mean delta own +0.0041

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.9322 | 0.9310 | -0.0012 |
| baby_cry | 0.9821 | 0.9821 | +0.0000 |
| gunshot | 0.9267 | 0.9333 | +0.0066 |
| glass_break | 0.9237 | 0.9346 | +0.0108 |
| other | 0.9806 | 0.9811 | +0.0005 |

### val: acc 0.9698 macro-F1 0.9453 reject(non-target events) 0.9974198304460007 reject(bg) 0.924901185770751

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 270 | 0 | 0 | 2 | 18 |
| baby_cry | 0 | 192 | 0 | 0 | 1 |
| gunshot | 0 | 0 | 273 | 6 | 3 |
| glass_break | 0 | 0 | 8 | 743 | 15 |
| other | 20 | 6 | 22 | 73 | 4110 |

#### vs generalist G_mn04 (remapped to own+other), test: mean delta own +0.0073

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.8958 | 0.9108 | +0.0150 |
| baby_cry | 0.9253 | 0.9231 | -0.0022 |
| gunshot | 0.8857 | 0.8864 | +0.0007 |
| glass_break | 0.9429 | 0.9586 | +0.0157 |
| other | 0.9773 | 0.9785 | +0.0012 |

### test: acc 0.9658 macro-F1 0.9197 reject(non-target events) 0.9942078364565587 reject(bg) 0.9

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 245 | 0 | 0 | 0 | 2 |
| baby_cry | 0 | 192 | 0 | 0 | 4 |
| gunshot | 0 | 0 | 277 | 8 | 10 |
| glass_break | 2 | 0 | 7 | 775 | 10 |
| other | 44 | 28 | 46 | 40 | 4187 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr20: mean delta own +0.0041

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.8954 | 0.9050 | +0.0096 |
| baby_cry | 0.9050 | 0.9018 | -0.0032 |
| gunshot | 0.8839 | 0.8803 | -0.0036 |
| glass_break | 0.9381 | 0.9517 | +0.0137 |
| other | 0.9764 | 0.9767 | +0.0003 |

### noisy_snr20: acc 0.9624 macro-F1 0.9097 reject(non-target events) 0.9945485519591142 reject(bg) 0.9035460992907801

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 243 | 0 | 0 | 1 | 3 |
| baby_cry | 0 | 179 | 0 | 0 | 17 |
| gunshot | 1 | 0 | 272 | 6 | 16 |
| glass_break | 3 | 0 | 10 | 769 | 12 |
| other | 43 | 22 | 41 | 46 | 4193 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr15: mean delta own +0.0048

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.8793 | 0.8869 | +0.0076 |
| baby_cry | 0.8762 | 0.8715 | -0.0047 |
| gunshot | 0.8567 | 0.8585 | +0.0018 |
| glass_break | 0.9180 | 0.9327 | +0.0147 |
| other | 0.9708 | 0.9716 | +0.0008 |

### noisy_snr15: acc 0.9529 macro-F1 0.8874 reject(non-target events) 0.9908006814310051 reject(bg) 0.8900709219858156

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 243 | 0 | 0 | 0 | 4 |
| baby_cry | 0 | 173 | 0 | 0 | 23 |
| gunshot | 0 | 0 | 273 | 8 | 14 |
| glass_break | 4 | 0 | 22 | 748 | 20 |
| other | 54 | 28 | 46 | 54 | 4163 |

#### vs generalist G_mn04 (remapped to own+other), noisy_snr10: mean delta own +0.0081

| class | generalist F1 | specialist F1 | delta |
|---|---|---|---|
| bicycle | 0.8551 | 0.8732 | +0.0181 |
| baby_cry | 0.8557 | 0.8410 | -0.0147 |
| gunshot | 0.8173 | 0.8323 | +0.0149 |
| glass_break | 0.8995 | 0.9136 | +0.0141 |
| other | 0.9658 | 0.9672 | +0.0014 |

### noisy_snr10: acc 0.9440 macro-F1 0.8650 reject(non-target events) 0.9856899488926746 reject(bg) 0.8879432624113475

| true \ pred | bicycle | baby_cry | gunshot | glass_break | other |
|---|---|---|---|---|---|
| bicycle | 241 | 0 | 0 | 1 | 5 |
| baby_cry | 0 | 164 | 1 | 0 | 31 |
| gunshot | 1 | 0 | 263 | 14 | 17 |
| glass_break | 5 | 0 | 26 | 735 | 28 |
| other | 58 | 30 | 47 | 65 | 4145 |

