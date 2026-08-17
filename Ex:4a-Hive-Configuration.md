# Exercise 4a --- Hive Installation and Configuration

## Aim

Install and configure Apache Hive 3.1.3 on a single-node Hadoop cluster. The installation is verified by creating Hive tables with various data types (primitive, collection, array, struct, map) and loading data using multiple methods (local files and HDFS).

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Hadoop   : Apache Hadoop 3.3.6
Java     : OpenJDK 8
Hive     : Apache Hive 3.1.3
Metastore: Apache Derby (Embedded)
```

### Configuration Flow

``` text
                    Hive
                     |
                     |
             hive-site.xml
                     |
                     v
          Hadoop configuration
          /        |        \
         /         |         \
core-site.xml  hdfs-site.xml  yarn-site.xml
      |
      v
 fs.defaultFS
      |
      v
 hdfs://localhost:9000
      |
      v
     HDFS
```

------------------------------------------------------------------------

## 1. Install Hive

Extract the binary distribution:

``` bash
cd ~/Downloads
tar -xzf apache-hive-3.1.3-bin.tar.gz
mv apache-hive-3.1.3-bin ~/hive
```

------------------------------------------------------------------------

## 2. Configure Environment Variables

Add the following to `~/.bashrc`:

``` bash
export HIVE_HOME=$HOME/hive
export PATH=$PATH:$HIVE_HOME/bin
```

Reload the configuration:
``` bash
source ~/.bashrc
```

------------------------------------------------------------------------

## 3. Resolve Guava Version Conflict

Hive 3.1.3 and Hadoop 3.x often have conflicting versions of the Guava library. To fix this, replace Hive's guava jar with the one from Hadoop:

``` bash
rm $HIVE_HOME/lib/guava-19.0.jar
cp $HADOOP_HOME/share/hadoop/common/lib/guava-*.jar $HIVE_HOME/lib/
```

------------------------------------------------------------------------

## 4. Configure hive-site.xml

Create or edit the `hive-site.xml` configuration file to define the metastore connection and warehouse directory.

``` bash
nano $HIVE_HOME/conf/hive-site.xml
```

Use the following configuration based on the system setup:

``` xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>

    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:derby:;databaseName=/home/kavimugil-r/hive/metastore_db;create=true</value>
    </property>

    <property>
        <name>javax.jdo.option.ConnectionDriverName</name>
        <value>org.apache.derby.jdbc.EmbeddedDriver</value>
    </property>

    <property>
        <name>hive.metastore.uris</name>
        <value></value>
    </property>

    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>

</configuration>
```

------------------------------------------------------------------------

## 5. Initialize Hive Metastore

Hive requires a database to store metadata (table definitions, etc.). For a local setup, we use the embedded Derby database.

Run the schematool:
``` bash
$HIVE_HOME/bin/schematool -dbType derby -initSchema
```

Expected output: `schemaTool completed`.

------------------------------------------------------------------------

## 6. Verification and Capability Demonstration

Start the Hive CLI:
``` bash
hive
```

### 6.1 Primitive Data Types and Local Loading
Create a table with primitive types and load data from a local file.

``` sql
CREATE DATABASE IF NOT EXISTS hadoop_lab;
USE hadoop_lab;

CREATE TABLE students (
    id INT,
    name STRING,
    age INT,
    course STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';

LOAD DATA LOCAL INPATH '/home/kavimugil-r/Desktop/Big Data/students.txt' INTO TABLE students;

SELECT * FROM students;
```

### 6.2 Collection Data Types (Array, Map, Struct)
Demonstrate advanced data types using the following commands:

**Array Type:**
``` sql
CREATE TABLE array_test (id INT, tags ARRAY<STRING>);
INSERT INTO array_test VALUES (1, array('Hadoop', 'Hive', 'BigData'));
SELECT tags[0] FROM array_test;
```

**Map Type:**
``` sql
CREATE TABLE map_test (id INT, attributes MAP<STRING, STRING>);
INSERT INTO map_test VALUES (1, map('color', 'red', 'size', 'large'));
SELECT attributes['color'] FROM map_test;
```

**Struct Type:**
``` sql
CREATE TABLE struct_test (id INT, user_info STRUCT<name:STRING, city:STRING>);
INSERT INTO struct_test VALUES (1, named_struct('name', 'Kavimugil', 'city', 'Chennai'));
SELECT user_info.name FROM struct_test;
```

### 6.3 Loading Data from HDFS
Load data that is already stored in the HDFS filesystem.

``` bash
# First, put a file in HDFS
hdfs dfs -put -f "/home/kavimugil-r/Desktop/Big Data/hdfs_test.txt" /user/kavimugil-r/hdfs_test.txt
```

``` sql
CREATE TABLE hdfs_table (id INT, fruit STRING, color STRING) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',';

LOAD DATA INPATH '/user/kavimugil-r/hdfs_test.txt' INTO TABLE hdfs_table;

SELECT * FROM hdfs_table;
```

------------------------------------------------------------------------

# Common Errors

## SLF4J Multiple Bindings Warning
If you see `SLF4J: Class path contains multiple SLF4J bindings`, it is caused by a conflict between Hive's and Hadoop's logging libraries.
**Solution:** `rm $HIVE_HOME/lib/log4j-slf4j-impl-2.17.1.jar`

## HDFS Permission Denied
If `LOAD DATA INPATH` fails, ensure the Hive user has permissions to the HDFS file.
**Solution:** `hdfs dfs -chmod 777 /user/kavimugil-r/hdfs_test.txt`

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Setup
source ~/.bashrc
$HIVE_HOME/bin/schematool -dbType derby -initSchema

# 2. Basic Table & Local Load
hive -e "CREATE DATABASE IF NOT EXISTS lab; USE lab; 
CREATE TABLE t1 (id INT, name STRING) ROW FORMAT DELIMITED FIELDS TERMINATED BY ','; 
LOAD DATA LOCAL INPATH 'test.txt' INTO TABLE t1;"

# 3. Advanced Types
hive -e "USE lab; 
CREATE TABLE t2 (id INT, m MAP<STRING,INT>); 
INSERT INTO t2 VALUES (1, map('a',1));"

# 4. HDFS Load
hive -e "USE lab; 
CREATE TABLE t3 (id INT, name STRING); 
LOAD DATA INPATH '/user/kavimugil-r/test.txt' INTO TABLE t3;"
```

------------------------------------------------------------------------

# Result

Apache Hive 3.1.3 was successfully installed and configured. The installation was verified by demonstrating the creation of tables with primitive and complex data types (Array, Map, Struct) and successfully loading data using both local file paths and HDFS paths.

# Final Environment Summary

``` text
Hadoop Home : /home/kavimugil-r/hadoop
Hive Home   : /home/kavimugil-r/hive
Metastore   : Derby (local directory: /home/kavimugil-r/hive/metastore_db)
```
