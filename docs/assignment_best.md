# best 배정 (val per-class F1 argmax)

입력: E0m_v2, E1k_v2, E2k_v2

| class | E0m_v2 | E1k_v2 | E2k_v2 | assigned |
|---|---|---|---|---|
| alarm | 0.9419 | **0.9658** | 0.9316 | yamnet |
| fire_alarm | 0.9611 | 0.9805 | **0.9874** | mnv4 |
| water | **0.8862** | 0.8843 | 0.8225 | efficientat |
| scream | **0.9394** | 0.9057 | 0.9208 | efficientat |
| glass_break | **0.9532** | 0.9512 | 0.9425 | efficientat |
| bicycle | 0.9408 | 0.9513 | **0.9540** | mnv4 |
| gunshot | 0.9442 | **0.9501** | 0.9221 | yamnet |
| baby_cry | **0.9847** | 0.9822 | 0.9772 | efficientat |
| cry | **0.9316** | 0.9255 | 0.9283 | efficientat |
| car_horn | 0.8923 | 0.8444 | **0.9286** | mnv4 |
| cat_meow | 0.9158 | 0.9091 | **0.9221** | mnv4 |
| dog_bark | 0.8395 | **0.8535** | 0.8535 | yamnet |
| knock | 0.8308 | **0.9310** | 0.8571 | yamnet |

## 결과 그룹 (objective = 포함 클래스 과반: 긴급 → recall, 일상 → precision, 그 외 balanced)

- **efficientat** (E0m_v2): water, scream, glass_break, baby_cry, cry → objective **balanced**
- **yamnet** (E1k_v2): alarm, gunshot, dog_bark, knock → objective **balanced**
- **mnv4** (E2k_v2): fire_alarm, bicycle, car_horn, cat_meow → objective **balanced**

background는 배정하지 않는다(모든 스페셜리스트가 other 안에서 모델링).
