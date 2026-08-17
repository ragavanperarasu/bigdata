from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, count, countDistinct, when, regexp_extract, split
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("MovieLens_EDA") \
    .getOrCreate()

# Set visualization style
sns.set_style('darkgrid')
plt.rcParams.update({'figure.figsize': (10, 8), 'axes.labelsize': 'medium'})

# Load datasets
df_movies = spark.read.csv("file:///home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/movies.csv", header=True, inferSchema=True)
df_ratings = spark.read.csv("file:///home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/ratings.csv", header=True, inferSchema=True)
df_tags = spark.read.csv("file:///home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/tags.csv", header=True, inferSchema=True)

# Display schemas and samples
df_movies.printSchema()
df_movies.show(5)
df_ratings.show(5)

# Dataset Statistics
print(f"Total Ratings: {df_ratings.count()}")
df_ratings.select(countDistinct("userId")).show()
df_ratings.select(countDistinct("movieId")).show()
df_tags.select(countDistinct("tag")).show()

# Data Preparation
# Extracting Movie Release Year
df_movies = df_movies.withColumn("year", regexp_extract(df_movies["title"], r"\((\d{4})\)", 1))

# Splitting Genres
split_expr = split(df_movies["genres"], "\\|")
for i in range(1, 11):
    df_movies = df_movies.withColumn(f"genre{i}", split_expr.getItem(i - 1))

# Calculate the number of genres per movie
genre_columns = [f"genre{i}" for i in range(1, 11)]
genre_count_expr = sum(when(col(col_name) != "0", 1).otherwise(0) for col_name in genre_columns)
# Note: The original MD says when(col(col_name) != "0", 1), but the column might be null.
# I will use .isNotNull() for better correctness.
genre_count_expr = sum(when(col(col_name).isNotNull(), 1).otherwise(0) for col_name in genre_columns)
df_movies = df_movies.withColumn("genre_count", genre_count_expr).drop('genres')

# Data Analysis
# Movie Aggregations
rating_avg = df_ratings.groupBy("movieId").agg(mean("rating").alias("rating_avg"))
rating_count = df_ratings.groupBy("movieId").agg(count("rating").alias("rating_count"))

# Join results into a single Movie DataFrame
df_movie_stats = rating_avg.join(rating_count, "movieId")

# User Aggregations
user_stats = df_ratings.groupBy("userId").agg(
    mean("rating").alias("user_rating_avg"),
    count("rating").alias("user_rating_count")
)

# Top Users by Rating Count
user_stats.sort(col('user_rating_count').desc()).show(10)

# Merge ratings with movie info for detailed analysis
df_combined = df_ratings.join(df_movies, "movieId", "inner")

# Analysis of user tagging behavior
user_tags = df_tags.groupBy("userId", "movieId").agg(count("tag").alias("tag_count"))
user_tags.sort(col('tag_count').desc()).show(5)

# Visualizations (Save to files since we are in a CLI)
# 5.1 Release Year Distribution
pandas_year = df_movies.select("year").toPandas()
plt.figure()
sns.histplot(pandas_year.year, bins=30, kde=True)
plt.title("Distribution of Movie Release Years")
plt.xlabel("Year")
plt.savefig("year_distribution.png")
plt.close()

# 5.2 Genre Popularity
genre_dist = df_movies.groupBy("genre1").count().toPandas()
plt.figure()
sns.barplot(x=genre_dist['genre1'], y=genre_dist['count'])
plt.xticks(rotation=90)
plt.title("Most Popular Primary Genres")
plt.savefig("genre_popularity.png")
plt.close()

# 5.3 User Ratings by Genre (Boxen Plot)
# Sampling for visualization performance
sample_ratings = df_ratings.sample(False, 0.1, seed=42)
box_genre_data = sample_ratings.join(df_movies.select("movieId", "genre1"), "movieId").toPandas()

plt.figure()
sns.boxenplot(x='genre1', y='rating', data=box_genre_data)
plt.xticks(rotation=90)
plt.title("Rating Distribution by Genre")
plt.savefig("genre_ratings.png")
plt.close()

print("EDA completed successfully. Visualizations saved as PNG files.")
spark.stop()
