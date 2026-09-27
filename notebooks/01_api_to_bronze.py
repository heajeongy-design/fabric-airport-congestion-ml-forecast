# Notebook 01 — 공항 혼잡도 Open API → Bronze (Microsoft Fabric Notebook, PySpark)
#
# 출처: 작업 기록(노션)의 첫 번째 노트북 코드를 옮김. 원문의 설명 메모는 # 주석으로 바꿨다.
# 이 버전은 이벤트 트리거를 붙이기 전, API 응답을 바로 Bronze 테이블에 쓰던 형태다.
# 이후 구조에서는 Pipeline1 이 응답을 Raw JSON 파일로 저장하고, 파일 생성 이벤트로 실행되는
# Pipeline2 가 Raw → Bronze 를 적재한다 (그 코드는 기록에 없음 — README "코드 포함 범위").
#
# 서비스 키는 코드에 두지 않는다. 원문에는 키가 직접 적혀 있었으나 여기서는 환경 변수로 바꿨다.

import os

import requests  # 데이터 가져오기

service_key = os.environ["AIRPORT_API_SERVICE_KEY"]  # 공공데이터 API 인증키 (.env.example 참고)

url = "https://apis.data.go.kr/B551178/airport-congestion/v1"  # API 주소

# 쿼리 파라미터 (Query Parameters)
params = {
    "serviceKey": service_key,
    "pageNo": 1,
    "numOfRows": 10,
    "type": "json",
}

response = requests.get(url, params=params)  # API 서버에 데이터 요청

print(response.status_code)  # 200 성공, 404 주소 없음, 500 서버 오류
print(response.url)
print(response.text[:1000])  # 원본 문자열 출력

# ---------------------------------------------------------------------------
import json

data = response.json()
# API 는 텍스트({...} 형식)로 준다. json() 으로 파이썬 자료구조로 바꾼다.
# 보기 좋게 다시 문자열로: indent=2, 한글 깨짐 방지 ensure_ascii=False
print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

# ---------------------------------------------------------------------------
items = data["response"]["body"]["items"]["item"]  # 실제 데이터 목록(item)만 추출

print(type(items))
print(len(items))
print(items[0])

# ---------------------------------------------------------------------------
from pyspark.sql import Row  # Spark 에서 한 행(row)을 만드는 객체

rows = [Row(**x) for x in items]  # ** 는 딕셔너리의 키와 값을 함수 인자처럼 펼치는 문법

# 파이썬 리스트를 Spark 가 처리할 수 있는 표 형태로 등록해야 분산 처리·SQL·저장 기능을 쓸 수 있다
bronze_df = spark.createDataFrame(rows)  # noqa: F821  (Fabric 노트북 세션)

display(bronze_df)  # noqa: F821

# ---------------------------------------------------------------------------
from pyspark.sql.functions import current_timestamp  # 적재 시간 추가

# 언제 적재되었는지(load timestamp)를 남긴다 → 최신 여부 확인, 장애 분석
bronze_df = bronze_df.withColumn("bronze_load_dttm", current_timestamp())

bronze_df.write \
    .mode("append") \
    .format("delta") \
    .saveAsTable("bronze_airport_congestion")
# append: 기존 데이터 뒤에 새 데이터를 붙임
# delta: Parquet 파일 + 변경 이력(_delta_log). 트랜잭션, 버전 관리, MERGE, 되돌리기 지원

print("bronze_airport_congestion 저장 완료")
