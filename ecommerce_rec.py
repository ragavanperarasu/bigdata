from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.functions import col

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("EcommerceRecommendation") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# 1. Load Real-World Dataset
# Using MovieLens ratings as user-item interactions (userId, movieId/productId, rating)
# Using file:/// prefix to force local filesystem access
data_path = "file:///home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/ratings.csv"
df = spark.read.csv(data_path, header=True, inferSchema=True)

# Rename movieId to productId for e-commerce context
df = df.withColumnRenamed("movieId", "productId")

# 2. Train-Test Split
(training, test) = df.randomSplit([0.8, 0.2], seed=42)

# 3. Build ALS Model
# coldStartStrategy="drop" ensures we don't get NaN for users not in training set
als = ALS(userCol="userId", itemCol="productId", ratingCol="rating",
          coldStartStrategy="drop", nonnegative=True)
model = als.fit(training)

# 4. Evaluation
predictions = model.transform(test)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="rating", predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print(f"Root Mean Square Error (RMSE): {rmse}")

# 5. Generate Actionable Insights: Top 5 recommendations for all users
user_recs = model.recommendForAllUsers(5)
user_recs.show(truncate=False)

spark.stop()
