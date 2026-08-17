# Exercise 3 --- Hadoop MapReduce Word Count

## Aim

Implement a Hadoop MapReduce Word Count program using **Python Mapper +
Python Reducer + Hadoop Streaming**.

## Environment

``` text
Ubuntu 24.04 LTS
Apache Hadoop 3.3.6
Java 8
Python 3
HDFS + YARN
```

------------------------------------------------------------------------

## 1. Start Hadoop

``` bash
start-dfs.sh
start-yarn.sh
```

Check:

``` bash
jps
```

Expected:
NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager, Jps.

------------------------------------------------------------------------

## 2. Create the Project Directory

``` bash
mkdir -p ~/hadoop-wordcount
cd ~/hadoop-wordcount
```

------------------------------------------------------------------------

## 3. Create the Input Corpus

``` bash
nano input.txt
```

Enter:

``` text
hello hadoop
hello world
hadoop is powerful
world of hadoop
hadoop makes big data processing easy
big data is powerful
```

------------------------------------------------------------------------

## 4. Create the Mapper

``` bash
nano mapper.py
```

Use:

``` python
#!/usr/bin/env python3

import sys

for line in sys.stdin:
    words = line.strip().split()

    for word in words:
        print(f"{word.lower()}\t1")
```

Make executable:

``` bash
chmod +x mapper.py
```

------------------------------------------------------------------------

## 5. Test the Mapper

``` bash
cat input.txt | ./mapper.py
```

------------------------------------------------------------------------

## 6. Create the Reducer

``` bash
nano reducer.py
```

Use:

``` python
#!/usr/bin/env python3

import sys

current_word = None
current_count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    word, count = line.split("\t", 1)
    count = int(count)

    if current_word == word:
        current_count += count
    else:
        if current_word is not None:
            print(f"{current_word}\t{current_count}")

        current_word = word
        current_count = count

if current_word is not None:
    print(f"{current_word}\t{current_count}")
```

Make executable:

``` bash
chmod +x reducer.py
```

------------------------------------------------------------------------

## 7. Test Mapper + Reducer Locally

``` bash
cat input.txt | ./mapper.py | sort | ./reducer.py
```

------------------------------------------------------------------------

## 8. Create HDFS Input Directory

``` bash
hdfs dfs -mkdir -p /wordcount/input
```

------------------------------------------------------------------------

## 9. Upload Input to HDFS

``` bash
hdfs dfs -put -f input.txt /wordcount/input/
```

------------------------------------------------------------------------

## 10. Remove Previous Output

``` bash
hdfs dfs -rm -r -f /wordcount/output
```

------------------------------------------------------------------------

## 11. Run Hadoop Streaming

``` bash
hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
-input /wordcount/input \
-output /wordcount/output \
-mapper ~/hadoop-wordcount/mapper.py \
-reducer ~/hadoop-wordcount/reducer.py
```

------------------------------------------------------------------------

## 12. View the Result

``` bash
hdfs dfs -cat /wordcount/output/part-00000
```

------------------------------------------------------------------------

## 13. Copy Output to Linux

``` bash
hdfs dfs -get -f /wordcount/output ~/hadoop-wordcount/
```

------------------------------------------------------------------------

## 14. Web-Interface

### For: HDFS / NameNode
```bash
http://localhost:9870
```
### For: YARN / ResourceManager
```bash
http://localhost:8088
```

------------------------------------------------------------------------

# MapReduce Logic

``` text
              input.txt
                  |
                  v
              HDFS Input
                  |
                  v
               Mapper
                  |
          word → 1 pairs
                  |
                  v
           Shuffle & Sort
                  |
       same words are grouped
                  |
                  v
               Reducer
                  |
             sum(values)
                  |
                  v
              HDFS Output
```

------------------------------------------------------------------------

# Common Errors

## `ssh localhost` → `Permission denied (publickey)`
Run:
``` bash
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

## `Connection refused` on HDFS
Check:
``` bash
jps
```
If NameNode is missing, run `start-dfs.sh`.

## Output directory already exists
``` bash
hdfs dfs -rm -r -f /wordcount/output
```

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
mkdir -p ~/hadoop-wordcount
cd ~/hadoop-wordcount

nano input.txt
nano mapper.py
nano reducer.py

chmod +x mapper.py reducer.py

cat input.txt | ./mapper.py | sort | ./reducer.py

start-dfs.sh
start-yarn.sh

hdfs dfs -mkdir -p /wordcount/input
hdfs dfs -put -f input.txt /wordcount/input/

hdfs dfs -rm -r -f /wordcount/output

hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
-input /wordcount/input \
-output /wordcount/output \
-mapper ~/hadoop-wordcount/mapper.py \
-reducer ~/hadoop-wordcount/reducer.py

hdfs dfs -cat /wordcount/output/part-00000
```

------------------------------------------------------------------------

# Result

The Hadoop MapReduce Word Count program was successfully implemented
using Python Mapper and Reducer programs with Hadoop Streaming. The
input corpus was stored in HDFS, processed through Mapper, Shuffle and
Sort, and Reducer stages, and the final word frequencies were stored in
HDFS.
