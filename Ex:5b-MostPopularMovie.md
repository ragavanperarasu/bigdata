# Exercise 5b --- Most Popular Movie Analysis

## Aim

Analyze the MovieLens dataset using HiveQL to find the most popular movie based on the total number of ratings received.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Hadoop   : Apache Hadoop 3.3.6
Java     : OpenJDK 8
Hive     : Apache Hive 3.1.3
Dataset  : MovieLens
```

------------------------------------------------------------------------

## 1. Implementation

To find the most popular movie, we join the `movies` table with the `ratings` table, group the results by the movie title, and count the number of ratings for each.

### HiveQL Query:
``` sql
USE movielens;
SELECT m.title, COUNT(r.rating) as rating_count 
FROM movies m JOIN ratings r ON m.movieId = r.movieId 
GROUP BY m.title 
ORDER BY rating_count DESC 
LIMIT 1;
```

------------------------------------------------------------------------

## 2. Analysis of Result

The query aggregates the total count of ratings for every movie in the dataset. The movie with the highest count is returned as the most popular.

**Expected Result:**
The most popular movie in the MovieLens dataset is **Forrest Gump (1994)**.

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
hive -e "USE movielens; SELECT m.title, COUNT(r.rating) as rating_count FROM movies m JOIN ratings r ON m.movieId = r.movieId GROUP BY m.title ORDER BY rating_count DESC LIMIT 1;"
```

------------------------------------------------------------------------

# Result

The most popular movie in the MovieLens dataset was successfully identified using HiveQL by joining the movies and ratings tables and performing a count aggregation.
