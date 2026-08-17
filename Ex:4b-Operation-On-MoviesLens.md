# Exercise 4b --- Operations on MovieLens Dataset

## Aim

Load the MovieLens dataset into Apache Hive and perform various data analysis operations using both primitive and advanced data types to demonstrate Hive's querying capabilities.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Hadoop   : Apache Hadoop 3.3.6
Java     : OpenJDK 8
Hive     : Apache Hive 3.1.3
Dataset  : MovieLens (CSV files)
Source   : https://grouplens.org/datasets/movielens/
```

------------------------------------------------------------------------

## 1. Download and Prepare Dataset

Download the MovieLens dataset manually from the official source:
**URL:** [https://grouplens.org/datasets/movielens/](https://grouplens.org/datasets/movielens/)

Extract the files and place them in your preferred dataset folder:
``` bash
# Move the downloaded CSV files (movies.csv, ratings.csv, tags.csv, links.csv) into the dataset folder
```

------------------------------------------------------------------------

## 2. Create Database and Tables (Primitive Types)

First, we create a dedicated database for the project and define tables that match the CSV structure using primitive types (`INT`, `STRING`, `FLOAT`, `BIGINT`).

``` bash
CREATE DATABASE IF NOT EXISTS movielens;
USE movielens;

CREATE TABLE IF NOT EXISTS movies (
    movieId INT, 
    title STRING, 
    genres STRING
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
TBLPROPERTIES ('skip.header.line.count'='1');

CREATE TABLE IF NOT EXISTS ratings (
    userId INT, 
    movieId INT, 
    rating FLOAT, 
    `timestamp` BIGINT
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
TBLPROPERTIES ('skip.header.line.count'='1');

CREATE TABLE IF NOT EXISTS tags (
    userId INT, 
    movieId INT, 
    tag STRING, 
    `timestamp` BIGINT
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
TBLPROPERTIES ('skip.header.line.count'='1');

CREATE TABLE IF NOT EXISTS links (
    movieId INT, 
    imdbId STRING, 
    tmdbId STRING
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
STORED AS TEXTFILE 
TBLPROPERTIES ('skip.header.line.count'='1');
```

------------------------------------------------------------------------

## 2. Load Data from Local CSVs

Load the dataset from the local directory into the Hive tables.

``` bash
USE movielens;
LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/movies.csv' INTO TABLE movies;
LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/ratings.csv' INTO TABLE ratings;
LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/tags.csv' INTO TABLE tags;
LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/links.csv' INTO TABLE links;
```

------------------------------------------------------------------------

## 3. Perform Operations (Primitive Types)

Execute analytical queries using joins and aggregations.

### 3.1 Find Top 5 Highest Rated Movies
``` sql
USE movielens;
SELECT m.title, r.rating 
FROM movies m JOIN ratings r ON (m.movieId = r.movieId) 
WHERE r.rating = 5.0 
LIMIT 5;
```

### 3.2 Calculate Average Rating per Movie
``` sql
SELECT m.title, AVG(r.rating) as avg_rating 
FROM movies m JOIN ratings r ON (m.movieId = r.movieId) 
GROUP BY m.title 
ORDER BY avg_rating DESC 
LIMIT 5;
```

------------------------------------------------------------------------

## 4. Demonstrate Advanced Data Types

Hive supports complex data types like `ARRAY`, `MAP`, and `STRUCT`.

### 4.1 ARRAY Type (Using `split` function)
The `genres` column is a pipe-separated string. We can convert it into an `ARRAY<STRING>` on the fly.

``` sql
SELECT title, split(genres, '[|]') as genre_array 
FROM movies 
LIMIT 5;
```

### 4.2 MAP Type
A `MAP` stores key-value pairs. We create a table to store movie statistics.

``` sql
CREATE TABLE movie_stats (
    movieId INT, 
    stats MAP<STRING, INT>
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
COLLECTION ITEMS TERMINATED BY ':';

INSERT INTO movie_stats VALUES 
(1, map('views', 100, 'likes', 50)), 
(2, map('views', 200, 'likes', 80));

SELECT * FROM movie_stats;
```

### 4.3 STRUCT Type
A `STRUCT` groups multiple related fields into a single column.

``` sql
CREATE TABLE movie_info (
    movieId INT, 
    info STRUCT<title:STRING, genre:STRING>
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
COLLECTION ITEMS TERMINATED BY ':';

INSERT INTO movie_info VALUES 
(1, named_struct('title', 'Toy Story', 'genre', 'Animation')), 
(2, named_struct('title', 'Jumanji', 'genre', 'Adventure'));

SELECT movie_info.info.title, movie_info.info.genre FROM movie_info;
```

------------------------------------------------------------------------

# Common Errors

## Reserved Keyword Error
Using `timestamp` as a column name causes a `ParseException` because it is a reserved keyword in Hive.
**Solution:** Use backticks: `` `timestamp` ``.

## Data Type Mismatch in MAP/STRUCT
Inserting plain strings into `MAP` or `STRUCT` columns fails.
**Solution:** Use the `map()` and `named_struct()` functions to construct the complex types during insertion.

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Create Database and Tables
hive -e "CREATE DATABASE IF NOT EXISTS movielens; USE movielens; 
CREATE TABLE movies (movieId INT, title STRING, genres STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' TBLPROPERTIES ('skip.header.line.count'='1');
CREATE TABLE ratings (userId INT, movieId INT, rating FLOAT, \`timestamp\` BIGINT) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' TBLPROPERTIES ('skip.header.line.count'='1');"

# 2. Load Data
hive -e "USE movielens; LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/movies.csv' INTO TABLE movies; 
LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/MoveisLens-DataSet/ratings.csv' INTO TABLE ratings;"

# 3. Query
hive -e "USE movielens; SELECT m.title, AVG(r.rating) FROM movies m JOIN ratings r ON (m.movieId = r.movieId) GROUP BY m.title LIMIT 5;"

# 4. Advanced Type (Array)
hive -e "USE movielens; SELECT title, split(genres, '[|]') FROM movies LIMIT 5;"
```

------------------------------------------------------------------------

# Result

The MovieLens dataset was successfully loaded into Apache Hive. Basic operations using primitive types were performed via joins and aggregations to find top-rated movies. Additionally, advanced data types (`ARRAY`, `MAP`, and `STRUCT`) were successfully implemented and queried, demonstrating Hive's ability to handle complex semi-structured data.
