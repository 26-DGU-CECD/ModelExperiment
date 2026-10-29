# metrics.json 스키마

`results/<실험명>/metrics.json`. `src/make_leaderboard.py`가 읽는다.

```json
{
  "experiment": "yamnet_generalist_v1",
  "model": "yamnet+mlp",
  "condition": "generalist",
  "date": "2026-10-29",
  "accuracy": 0.912,
  "macro_f1": 0.887,
  "danger_recall": 0.934,
  "background_fa_rate": 0.041,
  "per_class": {
    "alarm": {"precision": 0.9, "recall": 0.9, "f1": 0.9, "support": 120}
  },
  "confusion_matrix": [[...]],
  "notes": ""
}
```

| 키 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `experiment` | str | O | 실험명. 디렉터리명과 동일 |
| `model` | str | O | 백본/구조 (예: `yamnet+mlp`, `efficientnet_b0`, `ensemble(yamnet,ast)`) |
| `condition` | str | O | `generalist` / `ensemble` / `specialist` 중 하나 |
| `date` | str | O | `YYYY-MM-DD` |
| `accuracy` | float | O | test 전체 정확도 (0~1) |
| `macro_f1` | float | O | 13클래스 macro-F1 (0~1) |
| `danger_recall` | float | O | 위험음 recall. 위험음 = `fire_alarm, scream, glass_break, gunshot, car_horn`. 해당 클래스 샘플 중 정답 클래스로 맞춘 비율 (micro) |
| `background_fa_rate` | float | O | background 정답 샘플 중 비-background로 예측된 비율 (false alarm) |
| `per_class` | dict | X | 클래스별 precision/recall/f1/support |
| `confusion_matrix` | list[list[int]] | X | 13x13, 라벨 고정 순서. 행=정답, 열=예측 |
| `notes` | str | X | 자유 메모 |

- 평가는 test split, `is_augmented == 0` orig 클립만.
- 라벨 순서: `alarm, fire_alarm, water, scream, glass_break, bicycle, gunshot, baby_cry, car_horn, cat_meow, dog_bark, knock, background`

# predictions.csv 스키마

| 컬럼 | 설명 |
|---|---|
| `clip_id` | 클립 식별자 |
| `source_file` | 원본 파일 (GroupKFold 그룹) |
| `y_true` | 정답 라벨명 |
| `y_pred` | 예측 라벨명 |
| `p_<label>` ×13 | 클래스별 확률 |
