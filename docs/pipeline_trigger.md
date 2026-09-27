# 파이프라인과 이벤트 트리거

## 구조 변경

처음에는 하나의 파이프라인이 노트북을 순서대로 실행했다 (30분 Schedule).

```
01 API → Bronze  →  02 Bronze → Silver  →  03 Silver → Gold
```

이후 수집과 가공을 나눠, Raw 파일이 생기면 가공이 시작되는 이벤트 기반 구조로 바꿨다.

```
Pipeline1 (Schedule 30분)   API → Raw JSON 저장 (OneLake Files)
        │
        ▼  FileCreated 이벤트
Pipeline2 (Trigger)         Raw → Bronze → Silver → Gold → ML 예측
```

## Pipeline1 — 수집

- 30분마다 공항 혼잡도 Open API 를 호출해 응답을 OneLake Files 영역에 JSON 으로 저장
- 파일명에 수집 시각을 넣어 응답 원본을 모두 보관

```
Files/raw/airport_congestion/airport_congestion_20260706_071223.json
```

## OneLake Event Trigger

| 항목 | 값 |
|---|---|
| Trigger Type | OneLake Event |
| Event Type | `Microsoft.Fabric.OneLake.FileCreated` |
| Monitoring Path | `Files/raw/airport_congestion` |
| Filter | subject contains `Files/raw/airport_congestion/`, subject ends with `.json` |
| Action | Pipeline2 실행 |

## Pipeline2 — 가공

| 단계 | 내용 |
|---|---|
| Raw → Bronze | JSON 파싱 → Spark DataFrame → Delta Append, `source_file`, `bronze_load_dttm` 추가 |
| Bronze → Silver | 공항 코드 표준화, 공항명 매핑, 타입 변환, 날짜/시간 파생, MERGE |
| Silver → Gold | Fact 와 요약 테이블 Overwrite |
| ML | Random Forest 예측 결과 저장 |
