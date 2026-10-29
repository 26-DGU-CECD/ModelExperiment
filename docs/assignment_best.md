# best 배정 (val per-class F1 argmax)

입력: E0m_efficientat_generalist_musan, E1k_yamnet_kd, E2k_mnv4_kd

| class | E0m_efficientat_generalist_musan | E1k_yamnet_kd | E2k_mnv4_kd | assigned |
|---|---|---|---|---|
| alarm | **0.7245** | 0.7126 | 0.7201 | efficientat |
| fire_alarm | 0.6404 | 0.6442 | **0.6496** | mnv4 |
| water | 0.8919 | **0.8923** | 0.8197 | yamnet |
| scream | **0.9354** | 0.9189 | 0.9313 | efficientat |
| glass_break | **0.9551** | 0.9487 | 0.9422 | efficientat |
| bicycle | 0.9477 | 0.9546 | **0.9658** | mnv4 |
| gunshot | 0.9472 | **0.9599** | 0.9211 | yamnet |
| baby_cry | 0.9821 | **0.9822** | 0.9772 | yamnet |
| cry | **0.9344** | 0.9275 | 0.9293 | efficientat |
| car_horn | 0.8769 | 0.8444 | **0.9649** | mnv4 |
| cat_meow | **0.9177** | 0.9091 | 0.9075 | efficientat |
| dog_bark | 0.8415 | 0.8333 | **0.8590** | mnv4 |
| knock | 0.8182 | **0.9153** | 0.8710 | yamnet |

## 결과 그룹

- **efficientat** (E0m_efficientat_generalist_musan): alarm, scream, glass_break, cry, cat_meow
- **yamnet** (E1k_yamnet_kd): water, gunshot, baby_cry, knock
- **mnv4** (E2k_mnv4_kd): fire_alarm, bicycle, car_horn, dog_bark

background는 배정하지 않는다(모든 스페셜리스트가 other 안에서 모델링).
