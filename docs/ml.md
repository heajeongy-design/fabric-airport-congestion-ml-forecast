# ML — 30분 후 혼잡도 예측

코드: [`notebooks/05_ml_random_forest.py`](../notebooks/05_ml_random_forest.py)

| 항목 | 내용 |
|---|---|
| 과제 | 회귀 — 공항별 다음 수집 시점(30분 후)의 전체 혼잡도 |
| 알고리즘 | `RandomForestRegressor` (pyspark.ml) |
| 하이퍼파라미터 | `numTrees=50`, `maxDepth=5`, `seed=42` |
| 타깃 | `lead(total_level)` over (partition by `airport_code` order by `process_datetime`) |
| 입력 | `airport_index`, `day_of_week_index` (StringIndexer, `handleInvalid="keep"`), `hour`, `minute`, `checkin_level`, `security_check_level`, `boarding_level`, `total_level` |
| 구성 | StringIndexer(공항) → StringIndexer(요일) → VectorAssembler → RandomForestRegressor 를 Spark ML Pipeline 으로 묶음 |
| 분할 | `randomSplit([0.8, 0.2], seed=42)` |
| 출력 | `prediction_airport_congestion` (Overwrite) → Power BI 실제값 vs 예측값 |

## 모델 선택

| 후보 | 판단 |
|---|---|
| Linear Regression | 관계가 선형이 아니라 제외 |
| Decision Tree | 규칙은 만들지만 과적합 |
| XGBoost | Fabric 노트북 기본 환경에 없음 |
| Random Forest | 여러 트리의 평균으로 과적합 완화, 범주형·수치형 함께 사용, 소규모 데이터에서 안정 → 선택 |

## 개선 과제

- **평가 분할**: 시계열 데이터를 무작위로 나눠 미래 시점 행이 학습에 섞일 수 있다 → 시간 기준 분할로 바꾼다.
- **평가 지표**: 대시보드의 예측 정확도와 함께 MAE 등 회귀 오차 지표를 기록한다.
- **타깃 간격**: 수집이 빠진 구간이 있으면 `lead` 가 30분 후가 아닐 수 있다 → 두 시각의 차이가 30분인 행만 쓰도록 조건을 둔다.
