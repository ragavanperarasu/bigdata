# Exercise 5c --- Highest Rated Movie Analysis

## Aim

Analyze the MovieLens dataset using HiveQL to find the movie with the highest average rating, ensuring the result is statistically significant.

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

To find the highest rated movie, we calculate the average rating per movie. To avoid movies with only one or two 5-star ratings, we add a filter to only consider movies with more than 10 ratings.

### HiveQL Query:
``` sql
USE movielens;
SELECT m.title, AVG(r.rating) as avg_rating 
FROM movies m JOIN ratings r ON m.movieId = r.movieId 
GROUP BY m.title 
HAVING COUNT(r.rating) > 10 
ORDER BY avg_rating DESC 
LIMIT 1;
```

------------------------------------------------------------------------

## 2. Analysis of Result

The query computes the mean of the `rating` column for each movie. By using the `HAVING` clause, we ensure that the result is a movie that is widely liked, not just a movie with a single high rating.

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
hive -e "USE movielens; SELECT m.title, AVG(r.rating) as avg_rating FROM movies m JOIN ratings r ON m.movieId = r.movieId GROUP BY m.title HAVING COUNT(r.rating) > 10 ORDER BY avg_rating DESC LIMIT 1;"
```

------------------------------------------------------------------------

# Result

The movie with the highest average rating in the MovieLens dataset was successfully identified using HiveQL by employing the AVG function and a HAVING clause for data validation.
