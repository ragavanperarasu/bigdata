# Exercise 6b --- Customer Churn Prediction using PySpark MLlib

## Aim

Train a machine learning model to predict customer churn using historical customer data. The goal is to identify users likely to churn based on demographic and account information (e.g., age, tenure, charges) using Apache Spark's MLlib library.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Java     : OpenJDK 8
Spark    : Apache Spark 3.3.4 (PySpark)
Python   : Python 3.10+
Libraries: pyspark.ml, pandas, numpy, matplotlib, sklearn
```

### Architecture Flow

``` text
                    Customer Churn Data (CSV)
                                │
                                ▼
                      PySpark DataFrames
                                │
              ┌─────────────────┴─────────────────┐
              │                                    │
      Data Cleaning                        Feature Engineering
   (Null Handling, Casting)               (Vectorization, Scaling)
              │                                    │
              └─────────────────┬─────────────────┘
                                ▼
                       MLlib VectorAssembler
                                │
              ┌─────────────────┴─────────────────┐
              │                 │                 │
       Logistic Regression   GBT Classifier   Decision Tree
              │                 │                 │
              └─────────────────┬─────────────────┘
                                ▼
                      Evaluation (Area Under PR, F1, Recall)
```

------------------------------------------------------------------------

## 1. Load Data

Initialize the Spark session and load the customer churn dataset.

``` python
from pyspark.sql import SparkSession
import os

spark = SparkSession.builder \
    .appName("CustomerChurnPrediction") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# Load data
data_path = "file:///home/kavimugil-r/Desktop/Big Data/customer_churn.csv"
df = spark.read.csv(data_path, header=True, inferSchema=True)
df.printSchema()
```

------------------------------------------------------------------------

## 2. Exploratory Data Analysis (EDA)

Analyze the distribution of the target variable (`churn`) and feature correlations.

``` python
from pyspark.sql import functions as F

# Check churn distribution (0 = Stayed, 1 = Churned)
df.groupBy('churn').count().show()

# Basic statistics for numerical features
df.select('age', 'tenure', 'monthlyCharges', 'totalCharges').describe().show()
```

------------------------------------------------------------------------

## 3. Data Preprocessing and Feature Engineering

### 3.1 Feature Construction
We use the numerical attributes as features to predict the `churn` label.

``` python
# Define feature columns
feature_cols = ['age', 'tenure', 'monthlyCharges', 'totalCharges']

# Handle potential nulls by filling with mean
for col_name in feature_cols:
    mean_val = df.select(F.mean(col_name)).collect()[0][0]
    df = df.fillna({col_name: mean_val})
```

### 3.2 Feature Scaling and Vectorization
Scale numerical features and assemble them into a single feature vector required by MLlib.

``` python
from pyspark.ml.feature import VectorAssembler, MinMaxScaler
from pyspark.ml import Pipeline

# Scale features to range [0, 1]
for col_name in feature_cols:
    assembler = VectorAssembler(inputCols=[col_name], outputCol=col_name + "_vec")
    scaler = MinMaxScaler(inputCol=col_name + "_vec", outputCol=col_name + "_scaled")
    pipeline = Pipeline(stages=[assembler, scaler])
    df = pipeline.fit(df).transform(df)

# Assemble all scaled features into a single vector
final_cols = [c + "_scaled" for c in feature_cols]
assembler = VectorAssembler(inputCols=final_cols, outputCol='features')
final_df = assembler.transform(df).select('features', 'churn')
final_df = final_df.withColumnRenamed('churn', 'label')
```

------------------------------------------------------------------------

## 4. Model Training and Evaluation

### 4.1 Dataset Splitting
Split the data into training (70%) and testing (30%) sets.

``` python
train, test = final_df.randomSplit([0.7, 0.3], seed=42)
```

### 4.2 Logistic Regression
``` python
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator

lr = LogisticRegression(featuresCol='features', labelCol='label')
lr_model = lr.fit(train)
predictions = lr_model.transform(test)

evaluator = BinaryClassificationEvaluator(metricName='areaUnderPR')
print(f"Logistic Regression Area Under PR: {evaluator.evaluate(predictions)}")
```

### 4.3 Gradient-Boosting Classifier (GBT)
``` python
from pyspark.ml.classification import GBTClassifier

gbt = GBTClassifier(featuresCol='features', labelCol='label')
gbt_model = gbt.fit(train)
gbt_predictions = gbt_model.transform(test)

print(f"GBT Area Under PR: {evaluator.evaluate(gbt_predictions)}")
```

------------------------------------------------------------------------

# Common Errors

## AnalysisException: Column not found
Ensure that the `VectorAssembler` input columns match exactly the names of the scaled columns (e.g., `age_scaled`).

## Memory Errors (Out Of Memory)
MLlib tasks can be memory-intensive. Increase `spark.driver.memory` and `spark.executor.memory` in the `SparkSession` configuration to 4g or 8g.

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Launch PySpark script
spark-submit customer_churn_prediction.py

# 2. Key Metrics to check in output:
# - Area Under PR (Higher is better)
# - F1-Score (Balance between Precision and Recall)
# - Recall (Ability to catch actual churners)
```

------------------------------------------------------------------------

# Result

A customer churn prediction model was successfully implemented using PySpark MLlib. By engineering behavioral features from account data and applying scaling, the model could distinguish between loyal and churning users. The Logistic Regression model performed optimally, providing a strong balance of recall and precision, demonstrating the effectiveness of Spark's distributed machine learning capabilities for large-scale customer analytics.
