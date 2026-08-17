from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, col

spark = SparkSession.builder.appName("StockAnalysis").getOrCreate()

# Load data using file:// prefix for local disk
df = spark.read.csv("file:///home/kavimugil-r/Desktop/Big Data/stock_data.csv", header=True, inferSchema=True)

# Define window: partition by Ticker, order by Date, look back 2 rows + current row = 3-day moving avg
windowSpec = Window.partitionBy("Ticker").orderBy("Date").rowsBetween(-2, 0)

# Calculate moving average
df_result = df.withColumn("MovingAvg", avg(col("Price")).over(windowSpec))

df_result.show()
spark.stop()
