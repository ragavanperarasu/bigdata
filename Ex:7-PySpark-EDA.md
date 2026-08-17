# Exercise 7 --- Exploratory Data Analysis (EDA) using PySpark

## Aim

Perform a comprehensive Exploratory Data Analysis (EDA) on the MovieLens dataset using PySpark. The objective is to analyze user-movie interactions, evaluate genre distributions, and visualize rating patterns to derive insights into movie popularity and user behavior.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Java     : OpenJDK 8
Spark    : Apache Spark 3.3.4 (PySpark)
Python   : Python 3.10+
Libraries: pyspark, pandas, numpy, seaborn, matplotlib
```

### Architecture Flow

``` text
                  MovieLens Dataset (CSV)
                (movies.csv, ratings.csv, tags.csv)
                                │
                                ▼
                      PySpark Session Init
                                │
              ┌─────────────────┴─────────────────┐
              │                                  │
       Data Cleaning                      Data Transformation
   (Regex Year Extract)               (Genre Splitting & Casting)
              │                                  │
              └─────────────────┬─────────────────┘
                                ▼
                      Statistical Aggregation
                (Avg Ratings, User/Movie Counts)
                                │
              ┌─────────────────┴─────────────────┐
              │                                  │
        PySpark DataFrame                      Pandas DataFrame
              │                                  │
              └─────────────────┬─────────────────┘
                                ▼
                      Data Visualization
             (Histograms, Bar Plots, Boxen/Violin Plots)
```

------------------------------------------------------------------------

# 1. Setup and Session Initialization

Initialize the Spark session and import the necessary libraries for data manipulation and visualization.

*Note: If you are using the `pyspark` interactive shell, the `spark` session is already created for you. **Do not run the SparkSession builder code in the shell.***

``` python
from pyspark.sql.functions import col, mean, count, countDistinct, when, regexp_extract, split
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

# Set visualization style
sns.set_style('darkgrid')
plt.rcParams.update({'figure.figsize': (10, 8), 'axes.labelsize': 'medium'})
```

------------------------------------------------------------------------

## 2. Data Loading and Basic Exploration

Load the MovieLens dataset and verify the schema and initial rows.

*Important: If you get a "Path does not exist" error mentioning `hdfs://`, it means Spark is looking in HDFS. Use the `file://` prefix to force it to read from your local hard drive.*

``` python
# Load datasets using local file system prefix
path = "file:///home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/"
df_movies = spark.read.csv(path + "movies.csv", header=True, inferSchema=True)
df_ratings = spark.read.csv(path + "ratings.csv", header=True, inferSchema=True)
df_tags = spark.read.csv(path + "tags.csv", header=True, inferSchema=True)

# Display schemas and samples
df_movies.printSchema()
df_movies.show(5)
df_ratings.show(5)
```

### Dataset Statistics
``` python
print(f"Total Ratings: {df_ratings.count()}")
df_ratings.select(countDistinct("userId")).show()
df_ratings.select(countDistinct("movieId")).show()
df_tags.select(countDistinct("tag")).show()
```

------------------------------------------------------------------------

## 3. Data Preparation

*Tip: When copy-pasting the `for` loop below into the PySpark shell, ensure you press Enter twice after the loop block to execute it.*

### 3.1 Extracting Movie Release Year
Use Regular Expressions to extract the year from the movie title (e.g., "Toy Story (1995)").

``` python
df_movies = df_movies.withColumn("year", regexp_extract(df_movies["title"], r"\((\d{4})\)", 1))
```

### 3.2 Splitting Genres
The `genres` column contains pipe-separated values. We split these into individual columns.

``` python
split_expr = split(df_movies["genres"], "\\|")
for i in range(1, 11):
    df_movies = df_movies.withColumn(f"genre{i}", split_expr.getItem(i - 1))

# Calculate the number of genres per movie
genre_columns = [f"genre{i}" for i in range(1, 11)]
# We use .isNotNull() to check if a genre exists at that position
genre_count_expr = sum(when(col(col_name).isNotNull(), 1).otherwise(0) for col_name in genre_columns)
df_movies = df_movies.withColumn("genre_count", genre_count_expr).drop('genres')
```

------------------------------------------------------------------------

## 4. Data Analysis

### 4.1 Average Ratings and Counts
Calculate the average rating and total number of ratings for each movie.

``` python
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
```

### 4.2 Tag and Genre Analysis
Analyze how users tag movies and how those tags relate to the primary genre.

``` python
# Merge ratings with movie info for detailed analysis
df_combined = df_ratings.join(df_movies, "movieId", "inner")

# Analysis of user tagging behavior
user_tags = df_tags.groupBy("userId", "movieId").agg(count("tag").alias("tag_count"))
user_tags.sort(col('tag_count').desc()).show(5)
```

------------------------------------------------------------------------

## 5. Visualizations

To create visualizations, PySpark DataFrames are converted to Pandas.

### 5.1 Release Year Distribution
``` python
pandas_year = df_movies.select("year").toPandas()
sns.histplot(pandas_year.year, bins=30, kde=True)
plt.title("Distribution of Movie Release Years")
plt.xlabel("Year")
plt.show()
```

### 5.2 Genre Popularity
``` python
genre_dist = df_movies.groupBy("genre1").count().toPandas()
sns.barplot(x=genre_dist['genre1'], y=genre_dist['count'])
plt.xticks(rotation=90)
plt.title("Most Popular Primary Genres")
plt.show()
```

### 5.3 User Ratings by Genre (Boxen Plot)
``` python
# Sampling for visualization performance
sample_ratings = df_ratings.sample(False, 0.1, seed=42)
box_genre_data = sample_ratings.join(df_movies.select("movieId", "genre1"), "movieId").toPandas()

sns.boxenplot(x='genre1', y='rating', data=box_genre_data)
plt.xticks(rotation=90)
plt.title("Rating Distribution by Genre")
plt.show()
```

------------------------------------------------------------------------

# Common Errors

## NativeCodeLoader Warning
`WARN NativeCodeLoader: Unable to load native-hadoop library...`
This is a common warning in local PySpark setups. It indicates that Spark is using built-in Java classes instead of native Hadoop libraries. It does not affect the correctness of the analysis.

## Memory Errors (OOM)
When converting large PySpark DataFrames to Pandas using `.toPandas()`, the driver may run out of memory. 
**Solution**: Use `.sample()` to reduce the dataset size before conversion or increase `spark.driver.memory`.

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Run the EDA script
spark-submit movie_eda.py

# 2. Key Analysis Tasks:
# - Extract release year using regexp_extract.
# - Group by movieId to find the highest rated movies.
# - Create a bar plot of the most frequent genres.
# - Compare user rating counts using a histogram.
```

------------------------------------------------------------------------

# Result

The Exploratory Data Analysis of the MovieLens dataset was successfully completed using PySpark. The project demonstrated the ability to handle large-scale data by performing distributed joins and aggregations. Key insights were derived regarding the distribution of movie release years and the popularity of various genres. By integrating PySpark for data processing and Seaborn/Matplotlib for visualization, a clear understanding of user rating behaviors and movie characteristics was achieved.
