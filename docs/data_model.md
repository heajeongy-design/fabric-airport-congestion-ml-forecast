# 데이터 모델

## 계층별 저장 전략

| 계층 | 테이블 | 저장 방식 | 이유 |
|---|---|---|---|
| Bronze | `bronze_airport_congestion` | Append | API 원본을 바꾸지 않고 보관 → 재처리 가능 |
| Silver | 정제 테이블 | MERGE (key: `airport_code` + `process_datetime`) | 같은 공항·같은 시각이 다시 수집되면 UPDATE, 새 시각은 INSERT → 중복 적재 방지 |
| Gold | `gold_airport_congestion`, `gold_airport_summary`, `gold_hourly_congestion` | Overwrite | Silver 에서 언제든 재생성 가능한 분석용 테이블 |
| ML | `prediction_airport_congestion` | Overwrite | 실행마다 예측 결과를 새로 저장 |

## Silver 정제

| 항목 | 예 |
|---|---|
| 컬럼명 표준화 | `IATA_APCD` → `airport_code` |
| 공항 코드 → 공항명 | `GMP` → 김포공항 |
| 시각 생성 | `13:20` → `2026-07-03 13:20:00` |
| 파생 컬럼 | `date`, `hour`, `minute`, `day_of_week` |

## Gold

| 테이블 | 단위 | 컬럼 |
|---|---|---|
| `gold_airport_congestion` (Fact) | 공항 × 수집 시각 | 공항, 날짜, 시간, 체크인·신분확인·보안검색·전체 혼잡도 |
| `gold_airport_summary` | 날짜 × 공항 | 평균·최대 혼잡도, 수집 건수 |
| `gold_hourly_congestion` | 날짜 × 시간 | 평균·최대 혼잡도, 수집 건수 |

코드: [`notebooks/04_gold_summary.py`](../notebooks/04_gold_summary.py) (요약 테이블 2개)

## Star Schema (Semantic Model)

```
dim_date ── gold_airport_congestion ── dim_airport
```

| Dimension | 컬럼 |
|---|---|
| `dim_date` | date_key, year, month, day, week, quarter, day_of_week, is_weekend |
| `dim_airport` | airport_code, airport_name, airport_region |

DAX 측정값: [`powerbi/dax_measures.md`](../powerbi/dax_measures.md)
