# DAX 측정값

출처: 작업 기록(노션). 원문 그대로 옮기고, 아래 두 가지만 표시했다.

- `예측 정확도` 는 기록이 중간에서 끊겨 있어 잘린 부분까지만 싣는다.
- `혼잡도 상태` 의 결과 문자열 앞에 있던 색 아이콘은 빼고 텍스트만 남겼다.

## 가장 혼잡한 시간

```dax
가장 혼잡한 시간 = 
VAR T =
TOPN(
    1,
    SUMMARIZE(
        gold_airport_congestion,
        gold_airport_congestion[hour],
        "AvgCongestion",
        AVERAGE(gold_airport_congestion[total_level])
    ),
    [AvgCongestion],
    DESC
)
RETURN
MAXX(T, gold_airport_congestion[hour])
```

## 공항별 혼잡도 비율

```dax
공항별 혼잡도 비율 = 
VAR AirportAvg =
    [현재 평균 혼잡도]

VAR TotalAirportAvg =
    SUMX(
        ALL(dim_airport[airport_name]),
        [현재 평균 혼잡도]
    )

RETURN
DIVIDE(AirportAvg, TotalAirportAvg)
```

## 예측 정확도

```dax
예측 정확도 = 
VAR CorrectCount =
    COUNTROWS(
        FILTER(
            prediction_airport_congestion,
            ROUND(
                prediction_airport_congestion[predicted_next_total_
```

## 오늘 수집 건수

```dax
오늘 수집 건수 = 
CALCULATE(
    COUNTROWS(gold_airport_congestion),
    dim_date[date] = TODAY()
)
```

## 총 수집 건수

```dax
총 수집 건수 = 
COUNTROWS(gold_airport_congestion)
```

## 최고 혼잡도

```dax
최고 혼잡도 = 
MAX(gold_airport_congestion[total_level])
```

## 평균 보안검색 혼잡도

```dax
평균 보안검색 혼잡도 = 
AVERAGE(gold_airport_congestion[boarding_level])
```

## 평균 신분확인 혼잡도

```dax
평균 신분확인 혼잡도 = 
AVERAGE(gold_airport_congestion[security_check_level])
```

## 평균 체크인 혼잡도

```dax
평균 체크인 혼잡도 = 
AVERAGE(gold_airport_congestion[checkin_level])
```

## 현재 평균 혼잡도

```dax
현재 평균 혼잡도 = 
AVERAGE(gold_airport_congestion[total_level])
```

## 혼잡도 상태

```dax
혼잡도 상태 = 
SWITCH(
    TRUE(),
    [현재 평균 혼잡도] < 2, "원활",
    [현재 평균 혼잡도] < 3, "보통",
    [현재 평균 혼잡도] < 4, "혼잡",
    "매우 혼잡"
)
```
