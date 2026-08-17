# Exercise 5a --- HiveQL Advanced Operations

## Aim

Perform basic data retrieval, filtering, aggregation, sorting, and joining operations using HiveQL. Implement partitioning and bucketing to optimize data retrieval and join operations.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Hadoop   : Apache Hadoop 3.3.6
Java     : OpenJDK 8
Hive     : Apache Hive 3.1.3
Dataset  : MovieLens
```

------------------------------------------------------------------------

## 1. Basic HiveQL Operations

Using the `movielens` database, we perform the following essential data retrieval operations.

### 1.1 Data Retrieval
Retrieve the first 5 records from the movies table.
``` sql
USE movielens;
SELECT * FROM movies LIMIT 5;
```

### 1.2 Filtering
Find all movies that belong to the 'Animation' genre.
``` sql
SELECT title FROM movies WHERE genres LIKE '%Animation%' LIMIT 5;
```

### 1.3 Aggregation
Count the total number of ratings in the dataset.
``` sql
SELECT COUNT(*) as total_ratings FROM ratings;
```

### 1.4 Sorting
List movies sorted by title in descending order.
``` sql
SELECT title FROM movies ORDER BY title DESC LIMIT 5;
```

### 1.5 Joining
Join movies and ratings tables to see the rating for each movie.
``` sql
SELECT m.title, r.rating 
FROM movies m JOIN ratings r ON m.movieId = r.movieId 
LIMIT 5;
```

------------------------------------------------------------------------

## 2. Partitioning

Partitioning is used to divide the table into parts based on the value of a column, which improves query performance by skipping irrelevant partitions.

### 2.1 Create Partitioned Table
We create a table `ratings_partitioned` partitioned by the `rating` value.

``` sql
CREATE TABLE ratings_partitioned (
    userId INT, 
    movieId INT, 
    `timestamp` BIGINT
) 
PARTITIONED BY (rating FLOAT) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';
```

### 2.2 Load Data into Partitioned Table
We use dynamic partitioning to insert data from the original `ratings` table.

``` sql
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

INSERT OVERWRITE TABLE ratings_partitioned PARTITION(rating) 
SELECT userId, movieId, `timestamp`, rating FROM ratings;
```

### 2.3 Verify Partitioning
Querying only a specific partition (e.g., rating = 5.0) is much faster.
``` sql
SELECT * FROM ratings_partitioned WHERE rating = 5.0 LIMIT 5;
```

------------------------------------------------------------------------

## 3. Bucketing

Bucketing organizes data into a fixed number of files (buckets) based on a hash of a column, which optimizes joins and sampling.

### 3.1 Create Bucketed Table
We create a table `movies_bucketed` clustered by `movieId` into 4 buckets.

``` sql
CREATE TABLE movies_bucketed (
    movieId INT, 
    title STRING, 
    genres STRING
) 
CLUSTERED BY (movieId) INTO 4 BUCKETS 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';
```

### 3.2 Load Data into Bucketed Table
``` sql
INSERT OVERWRITE TABLE movies_bucketed SELECT * FROM movies;
```

### 3.3 Verify Bucketing
``` sql
SELECT * FROM movies_bucketed LIMIT 5;
```

------------------------------------------------------------------------

# Common Errors

## Dynamic Partitioning Disabled
If `INSERT` into a partitioned table fails, Hive often requires dynamic partitioning to be explicitly enabled.
**Solution:** Run `SET hive.exec.dynamic.partition = true;` and `SET hive.exec.dynamic.partition.mode = nonstrict;`.

## Bucketing not applied
Bucketing only takes effect when data is inserted via a MapReduce job (like `INSERT OVERWRITE`). `LOAD DATA` does not bucket the data.

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Basic Queries
hive -e "USE movielens; SELECT title FROM movies WHERE genres LIKE '%Animation%' LIMIT 5;"

# 2. Partitioning
hive -e "USE movielens; 
CREATE TABLE ratings_part (userId INT, movieId INT, \`timestamp\` BIGINT) PARTITIONED BY (rating FLOAT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','; 
SET hive.exec.dynamic.partition=true; SET hive.exec.dynamic.partition.mode=nonstrict; 
INSERT OVERWRITE TABLE ratings_part PARTITION(rating) SELECT userId, movieId, \`timestamp\`, rating FROM ratings;"

# 3. Bucketing
hive -e "USE movielens; 
CREATE TABLE movies_buck (movieId INT, title STRING, genres STRING) CLUSTERED BY (movieId) INTO 4 BUCKETS ROW FORMAT DELIMITED FIELDS TERMINATED BY ','; 
INSERT OVERWRITE TABLE movies_buck SELECT * FROM movies;"
```

------------------------------------------------------------------------

# Result

The basic HiveQL operations (retrieval, filtering, aggregation, sorting, and joining) were successfully implemented on the MovieLens dataset. Furthermore, the concepts of Partitioning (by rating) and Bucketing (by movieId) were demonstrated, showing how to optimize data retrieval and storage in Hive.
