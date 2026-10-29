# docs/figures/highlights

`python src/make_report.py --highlights` 가 재생성. PNG 300dpi + SVG. ★ = 논문 Fig 후보.

| 파일 | 설명 | 논문 |
|---|---|---|
| `headline_macro_f1.png/.svg` | Headline: macro-F1 (95% CI) | ★ Fig 1a |
| `headline_emerg_recall.png/.svg` | Headline: 긴급 recall @FA.005 | ★ Fig 1b |
| `headline_cost.png/.svg` | Headline: 비용 점수 @FA.005 | ★ Fig 1c |
| `pareto_cost_compute.png/.svg` | 정확도–효율 파레토 (연산량 vs cost) | ★ Fig 2 |
| `curve_emergency.png/.svg` | 운영 곡선: 긴급 recall vs strict FA | ★ Fig 3 |
| `curve_daily.png/.svg` | 운영 곡선: 일상 precision vs recall |  |
| `group_confusion.png/.svg` | 그룹 혼동 행렬 기준선 vs 강조 | ★ Fig 4 |
| `cross_group_miss.png/.svg` | 긴급 → 일상/배경 오판율 |  |
| `group_pr_auc.png/.svg` | 그룹별 PR-AUC |  |
| `emergency_recall_by_class.png/.svg` | 긴급 클래스별 recall |  |
| `emergency_precision_by_class.png/.svg` | 긴급 클래스별 precision |  |
| `per_class_f1_heatmap.png/.svg` | 클래스별 F1 히트맵 | ★ Fig 5 (부록) |
| `noise_robustness.png/.svg` | 노이즈 강건성 꺾은선 | ★ Fig 6 |
| `noise_drop.png/.svg` | 노이즈 하락폭 |  |
| `source_origin_macro_f1.png/.svg` | 출처별 macro-F1 |  |
| `fa_per_hour.png/.svg` | FA/hour 환산 | ★ (제품 지표) |
| `calibration_reliability.png/.svg` | Reliability diagram |  |
| `calibration_ece.png/.svg` | ECE |  |
| `error_overlap_venn.png/.svg` | 오류 중복 벤 다이어그램 3세트 | ★ Fig 7 |
| `specialist_delta_ci.png/.svg` | 스페셜리스트 Δ 산점도 (CI) | ★ Fig 8 |
| `radar_top4.png/.svg` | 상위 4개 레이더 (발표용) |  |
| `bar_macro_f1.png/.svg` | 지표별 막대: macro-F1 (95% CI) |  |
| `bar_macro_f1_no_carhorn.png/.svg` | 지표별 막대: macro-F1 (car_horn 제외) (95% CI) |  |
| `bar_emerg_recall.png/.svg` | 지표별 막대: 긴급 recall @FA.005 (95% CI) |  |
| `bar_daily_precision.png/.svg` | 지표별 막대: 일상 precision @FA.005 (95% CI) |  |
| `bar_caution_f1.png/.svg` | 지표별 막대: 주의 F1 @FA.005 (95% CI) |  |
| `bar_bg_fa.png/.svg` | 지표별 막대: background 오경보율 (95% CI) |  |
| `bar_strict_fa.png/.svg` | 지표별 막대: strict background 오경보율 (95% CI) |  |
| `bar_snr10.png/.svg` | 지표별 막대: macro-F1 @SNR10 (95% CI) |  |
| `bar_cost005.png/.svg` | 지표별 막대: 비용 점수 @FA.005 (95% CI) |  |
