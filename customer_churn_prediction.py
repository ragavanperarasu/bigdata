from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline

# Initialize Spark Session
spark = SparkSession.builder.appName("CustomerChurnPrediction").getOrCreate()

# 1. Load the dataset
df = spark.read.csv("file:///home/kavimugil-r/Desktop/Big Data/customer_churn.csv", header=True, inferSchema=True)

# 2. Feature Engineering
# We use age, tenure, monthlyCharges, and totalCharges as features to predict 'churn'
feature_cols = ['age', 'tenure', 'monthlyCharges', 'totalCharges']
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# Create a pipeline: VectorAssembler -> LogisticRegression
lr = LogisticRegression(labelCol="churn", featuresCol="features")
pipeline = Pipeline(stages=[assembler, lr])

# 3. Split data into Training (80%) and Test (20%) sets
train_data, test_data = df.randomSplit([0.8, 0.2], seed=42)

# 4. Train the model
model = pipeline.fit(train_data)

# 5. Make predictions
predictions = model.transform(test_data)

# 6. Evaluate the model
evaluator = BinaryClassificationEvaluator(labelCol="churn", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
roc_auc = evaluator.evaluate(predictions)

print(f"Model Area Under ROC: {roc_auc}")
predictions.select("customerId", "churn", "prediction").show()

spark.stop()
