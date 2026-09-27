# Notebook 05 — 30분 후 혼잡도 예측 (Random Forest Regressor, Spark ML)
#
# 출처: 작업 기록(노션)에 남아 있는 코드를 그대로 옮김. display() 는 Fabric 노트북 함수.
# df 는 앞 셀에서 읽은 입력 DataFrame 이다 (읽는 셀은 기록에 없음).
# 평가 방식 등 개선 과제는 docs/ml.md 참고.

#30분 뒤 혼잡도 타깃 만들기
from pyspark.sql.window import Window
from pyspark.sql.functions import lead, col

w = Window.partitionBy("airport_code").orderBy("process_datetime")

ml_df = df.withColumn(
    "target_next_total_level",
    lead("total_level").over(w)
).filter(
    col("target_next_total_level").isNotNull()
)

display(ml_df)

#Linear regression : 선형 아니라서 x
#Decision tree : 규칙을 만드나, 과적합 발생
#Random forest : 평균 내에서 사용
#XGBoost : fabric notebook 기본으로 없음. 

from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml import Pipeline
import mlflow
mlflow.autolog(disable=True)

airport_indexer = StringIndexer(
    inputCol="airport_code",
    outputCol="airport_index",
    handleInvalid="keep"
)

dow_indexer = StringIndexer(
    inputCol="day_of_week",
    outputCol="day_of_week_index",
    handleInvalid="keep"
)

assembler = VectorAssembler(
    inputCols=[
        "airport_index",
        "day_of_week_index",
        "hour",
        "minute",
        "checkin_level",
        "security_check_level",
        "boarding_level",
        "total_level"
    ],
    outputCol="features"
)

rf = RandomForestRegressor(
    featuresCol="features",
    labelCol="target_next_total_level",
    predictionCol="predicted_next_total_level",
    numTrees=50,
    maxDepth=5,
    seed=42
)

model_pipeline = Pipeline(stages=[
    airport_indexer,
    dow_indexer,
    assembler,
    rf
])

#학습
train_df, test_df = ml_df.randomSplit([0.8, 0.2], seed=42)

model = model_pipeline.fit(train_df)

pred_df = model.transform(test_df)

display(pred_df.select(
    "airport_name",
    "process_datetime",
    "total_level",
    "target_next_total_level",
    "predicted_next_total_level"
))


#결과저장
prediction_df = pred_df.select(
    "airport_code",
    "airport_name",
    "process_datetime",
    "date",
    "hour",
    "minute",
    "day_of_week",
    "total_level",
    "target_next_total_level",
    "predicted_next_total_level"
)

prediction_df.write \
    .mode("overwrite") \
    .format("delta") \
    .option("overwriteSchema", "true") \
    .saveAsTable("prediction_airport_congestion")

print("prediction_airport_congestion 저장 완료")
