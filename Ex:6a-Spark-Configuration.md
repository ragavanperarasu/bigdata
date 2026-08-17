# Exercise 6a --- Spark Installation and Configuration

## Aim

Install and configure Apache Spark 3.3.4 on Ubuntu 24.04 LTS, integrating it with an existing Hadoop 3.3.6 environment. The installation is verified through Scala Spark shell, PySpark, and a data analysis task using Spark SQL Window functions.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Java     : OpenJDK 8
Hadoop   : Apache Hadoop 3.3.6
Hive     : Apache Hive 3.1.3
Spark    : Apache Spark 3.3.4 (Scala 2.12)
```

### Architecture Flow

``` text
                    Ubuntu 24.04 LTS
                           │
                    OpenJDK 8
                           │
              ┌────────────┴────────────┐
              │                         │
        Hadoop 3.3.6                Spark 3.3.4
              │                         │
       ┌──────┴──────┐             ┌────┴─────┐
       │             │             │          │
      HDFS          YARN        Scala     PySpark
       │             │
       └─────────────┤
                     │
                 Hive 3.1.3
                     │
              Hive Metastore
```

------------------------------------------------------------------------

## 1. Install Spark

Extract the binary distribution:

``` bash
cd ~/Downloads
tar -xzf spark-3.3.4-bin-hadoop3.tgz
mv spark-3.3.4-bin-hadoop3 ~/spark
```

------------------------------------------------------------------------

## 2. Configure Environment Variables

Add the following to `~/.bashrc`:

``` bash
# Spark
export SPARK_HOME=$HOME/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
```

Reload the configuration:
``` bash
source ~/.bashrc
```

Verify the installation:
``` bash
spark-submit --version
```

------------------------------------------------------------------------

## 3. Configure Spark Settings

### 3.1 Spark Environment (`spark-env.sh`)
Create the environment file:
``` bash
cp $SPARK_HOME/conf/spark-env.sh.template $SPARK_HOME/conf/spark-env.sh
```

Add the following paths to `spark-env.sh`:
``` bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=$HOME/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_HOME=$HOME/spark
```

### 3.2 Spark Defaults (`spark-defaults.conf`)
Create the defaults file:
``` bash
cp $SPARK_HOME/conf/spark-defaults.conf.template $SPARK_HOME/conf/spark-defaults.conf
```

Configure local mode and memory limits:
``` properties
spark.master                     local[*]
spark.driver.memory              2g
spark.executor.memory            2g
spark.sql.warehouse.dir          /tmp/spark-warehouse
```

------------------------------------------------------------------------

## 4. Verification and Testing

### 4.1 Scala Spark Shell
Start the shell and test a simple sequence:
``` scala
spark-shell
val data = Seq(1, 2, 3, 4, 5)
data.sum
:quit
```

### 4.2 PySpark Test
Start PySpark and test a simple operation. *Note: Use the DataFrame API instead of RDDs to avoid serialization errors in Python 3.11/3.12.*
``` python
pyspark
# Use DataFrame API to avoid Python 3.12 serialization bugs
df = spark.range(1, 6)
df.agg({"id": "sum"}).show()
exit()
```

### 4.3 HDFS Integration Test
Verify Spark can read files from HDFS:
``` bash
echo "Hello Spark Hadoop Hive" > ~/spark-test.txt
hdfs dfs -mkdir -p /spark/input
hdfs dfs -put -f ~/spark-test.txt /spark/input/
```

``` python
# In PySpark
data = sc.textFile("hdfs:///spark/input/spark-test.txt")
data.collect()
```

------------------------------------------------------------------------

## 5. Advanced Data Analysis: Stock Market Moving Average

In this task, we use Spark SQL and Window functions to calculate a 3-day moving average of stock prices.

### 5.1 Prepare Stock Data
Create a CSV file `stock_data.csv` with Date, Ticker, and Price.

**Sample Data Content:**
``` text
Date,Ticker,Price
2023-01-01,AAPL,150.00
2023-01-02,AAPL,152.50
2023-01-03,AAPL,151.20
2023-01-04,AAPL,153.00
2023-01-05,AAPL,155.10
2023-01-01,GOOGL,2800.00
2023-01-02,GOOGL,2820.00
2023-01-03,GOOGL,2810.00
2023-01-04,GOOGL,2830.00
2023-01-05,GOOGL,2840.00
```

### 5.2 Implementation (PySpark)
Create a script `spark_moving_avg.py`:

``` python
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, col

spark = SparkSession.builder.appName("StockAnalysis").getOrCreate()

# Load data from local filesystem
df = spark.read.csv("file:///home/kavimugil-r/Desktop/Big Data/stock_data.csv", header=True, inferSchema=True)

# Define window: partition by Ticker, order by Date, look back 2 rows + current row = 3-day moving avg
windowSpec = Window.partitionBy("Ticker").orderBy("Date").rowsBetween(-2, 0)

# Calculate moving average
df_result = df.withColumn("MovingAvg", avg(col("Price")).over(windowSpec))

df_result.show()
spark.stop()
```

### 5.3 Execute and Verify
``` bash
spark-submit "/home/kavimugil-r/Desktop/Big Data/spark_moving_avg.py"
```

------------------------------------------------------------------------

# Common Errors

## Command Not Found
If `spark-submit` is not found, ensure `SPARK_HOME/bin` is added to your `PATH` in `.bashrc` and you have run `source ~/.bashrc`.

## Path not exist (HDFS vs Local)
When reading files in PySpark, use `file:///` for local disk and `hdfs:///` for HDFS to avoid `AnalysisException`.

## PicklingError / IndexError (Serialization)
If you encounter `_pickle.PicklingError: Could not serialize object: IndexError: tuple index out of range` during RDD operations, it is due to a version mismatch between the Python version (e.g., Python 3.12) and the Spark version (3.3.4). Spark 3.3.x is not fully compatible with Python 3.12's bytecode.

**Solution**: 
1. **Use DataFrames**: Instead of `sc.parallelize()`, use `spark.range()` or `spark.createDataFrame()`. This bypasses the Python serialization bug.
2. **Downgrade Python**: Use Python 3.10 for full RDD support.
3. **Upgrade Spark**: Use Spark 3.5.0 or later.


------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Verify environment
spark-submit --version

# 2. Run moving average script
spark-submit "/home/kavimugil-r/Desktop/Big Data/spark_moving_avg.py"

# 3. Test PySpark shell
pyspark
```

------------------------------------------------------------------------

# Result

Apache Spark 3.3.4 was successfully installed and configured to work with Hadoop 3.3.6. The installation was verified using both Scala and PySpark shells. The advanced data analysis task was completed using Spark SQL Window functions to calculate moving averages for stock market data, demonstrating Spark's powerful data processing capabilities.
