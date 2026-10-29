# S_103 청취 자료

E0 test에서 alarm→fire_alarm 오분류 380건이 전부 시나리오 코드 `S_103`에서 나와서 만든 청취 세트. 파일명 접두어:

- `A_s103_alarm_wrong__` : 라벨 alarm, 시나리오 S_103, E0가 fire_alarm으로 예측한 소스 5개 (오분류 수 상위)에서 orig 1개씩
- `B_alarm_other_scen__` : 라벨 alarm, S_103 외 시나리오(S_101) 소스 5개
- `C_fire_alarm__`       : 라벨 fire_alarm 소스 5개 (fire_alarm은 전부 S_103)

## 시나리오 코드 의미

AI Hub 파일명 `S-YYMMDD_<S_NNN>_<C|D|L>_<번호>_0001`. repo 안 README/CHANGELOG/CSV(dataset_labels, integrated_*)에는 코드 설명이 **없음**
(CSV는 경로+라벨뿐). 데이터로 추정:

| 코드 | alarm 소스 | fire_alarm 소스 | 추정 |
|---|---|---|---|
| S_101 | 97 | 0 | 일반 경보(차량 경보 등; E0 오분류가 car_horn 쪽) |
| S_102 | 132 | 0 | 일반 경보 |
| S_103 | 166 | **167** | **화재경보 시나리오**. fire_alarm 소스 전부가 S_103이고 alarm S_103은 같은 코드 → 같은 녹음 시나리오를 두 라벨로 나눈 것 |

### 코드 체계 (파일명에서 추정)

`S-YYMMDD_<카테고리문자>_<NNN>_<C|D|L>_<번호>`. 카테고리 문자가 라벨 대분류와 1:1로 맞는다:

| 문자 | 추정 대분류 | 코드 → 라벨 |
|---|---|---|
| S | 경보/신호 | S_101, S_102 → alarm · **S_103 → fire_alarm(167) + alarm(166)** · S_202 → bicycle |
| H | 사람 소리 | H_302 → cry(울음) · H_303 → scream(비명) |
| L | 생활 소리 | L_306, L_307 → water |
| O | 물체 | O_201 → glass_break |
| W | 무기 | W_101, W_102 → gunshot |

즉 S_103은 "경보" 대분류의 세 번째 하위 시나리오이고, fire_alarm 소스 **전부**가 이 코드다. alarm 라벨의 S_103 소스는 같은 시나리오에서
라벨만 다르게 붙은 것으로 보인다 (뒤 문자 C/D/L은 녹음 조건 추정, 라벨과 무관).

## alarm 시나리오별 E0 test 성능

| scenario | alarm sources (all) | test sources | test clips | recall | F1* | 주요 오분류 |
|---|---|---|---|---|---|---|
| S_101 | 97 | 22 | 347 | 0.928 | 0.917 | car_horn 20, bicycle 2 |
| S_102 | 132 | 25 | 339 | 0.988 | 0.948 | glass_break 2, background 2 |
| S_103 | 166 | 31 | 412 | **0.061** | 0.106 | **fire_alarm 380**, glass_break 5 |

(* F1은 alarm 전체 FP 33을 모든 시나리오에 공통 적용)

결론: alarm의 S_103 소스(166개, alarm 소스의 42%)는 사실상 fire_alarm과 같은 시나리오. 선택지는 `src/relabel.py`의
`--mode relabel_s103`(S_103 alarm → fire_alarm) 또는 `--mode merge_siren`(alarm+fire_alarm → siren). 청취 후 결정.
