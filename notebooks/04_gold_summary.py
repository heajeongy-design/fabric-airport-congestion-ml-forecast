# Notebook 04 — Silver/Gold Fact → Gold 요약 테이블 (Microsoft Fabric Notebook, PySpark)
#
# 출처: 작업 기록(노션)에 남아 있는 코드를 그대로 옮김.
# gold_df 는 앞 셀에서 준비된 Gold Fact(gold_airport_congestion) DataFrame 이다.
# 앞 셀(gold_df 생성, Gold Fact 적재)은 기록에 코드가 없어 포함하지 않음 — README "코드 포함 범위" 참고.

#공항별 요약 gold
from pyspark.sql.functions import avg, max, count

gold_airport_summary_df = gold_df.groupBy(
    "date",
    "airport_code",
    "airport_name"
).agg(
    avg("total_level").alias("avg_total_level"),
    max("total_level").alias("max_total_level"),
    count("*").alias("record_count")
)

gold_airport_summary_df.write \
    .mode("overwrite") \
    .format("delta") \
    .option("overwriteSchema", "true") \
    .saveAsTable("gold_airport_summary")

print("gold_airport_summary 저장 완료")


#시간대별 요약 gold
from pyspark.sql.functions import avg, max, count

gold_hourly_df = gold_df.groupBy(
    "date",
    "hour"
).agg(
    avg("total_level").alias("avg_total_level"),
    max("total_level").alias("max_total_level"),
    count("*").alias("record_count")
)

gold_hourly_df.write \
    .mode("overwrite") \
    .format("delta") \
    .option("overwriteSchema", "true") \
    .saveAsTable("gold_hourly_congestion")

print("gold_hourly_congestion 저장 완료")
