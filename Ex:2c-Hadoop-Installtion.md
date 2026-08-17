# Exercise 2c --- Hadoop Single-Node Installation

## Aim

Install and configure Apache Hadoop 3.3.6 in single-node (pseudo-distributed) mode on Ubuntu 24.04 LTS to provide a foundation for HDFS, YARN, and MapReduce processing.

## Environment

``` text
OS       : Ubuntu 24.04 LTS
Java     : OpenJDK 8
Python   : Python 3
Hadoop   : Apache Hadoop 3.3.6
SSH      : OpenSSH
Mode     : Single-node / pseudo-distributed
```

``` text
                    One Ubuntu Laptop
                           |
                    Apache Hadoop 3.3.6
                           |
             +-------------+-------------+
             |                           |
            HDFS                        YARN
             |                           |
       +-----+------+              +-----+------+
       |            |              |            |
   NameNode      DataNode    ResourceManager  NodeManager
             \                           /
              \-------- MapReduce ------/
```

This is a **single-node / pseudo-distributed Hadoop setup**. No second laptop or external Hadoop cluster is required.

------------------------------------------------------------------------

## 1. Install Required Software

Update packages and install Java, Python, and SSH:

``` bash
sudo apt update
sudo apt install openjdk-8-jdk python3 openssh-client openssh-server -y
sudo systemctl enable --now ssh
```

Check:
``` bash
java -version
python3 --version
ssh -V
systemctl is-active ssh
```

Expected:
``` text
Java 1.8.x
Python 3.x
active
```

------------------------------------------------------------------------

## 2. Find and Configure JAVA_HOME

Find the actual Java installation path:
``` bash
readlink -f "$(which java)"
```

Example output:
``` text
/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
```

Therefore, set:
``` text
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```
*Do not blindly copy this path if another Java installation is active. You can verify with `ls /usr/lib/jvm/`.*

Add to `~/.bashrc`:
``` bash
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc
```

Verify:
``` bash
echo $JAVA_HOME
$JAVA_HOME/bin/java -version
```

------------------------------------------------------------------------

## 3. Install Apache Hadoop 3.3.6

Download the binary distribution from the [Official Apache Hadoop Releases Page](https://hadoop.apache.org/releases.html).

Extract the binary distribution:
``` bash
cd ~/Downloads
wget https://downloads.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
tar -xzf hadoop-3.3.6.tar.gz
mv hadoop-3.3.6 ~/hadoop
```

Check directory structure:
``` bash
ls ~/hadoop
```
Expected: `bin`, `etc`, `include`, `lib`, `libexec`, `sbin`, `share`.

------------------------------------------------------------------------

## 4. Configure Hadoop Environment Variables

Add the following to `~/.bashrc`:

``` bash
# Hadoop Environment
export HADOOP_HOME=$HOME/hadoop
export HADOOP_HDFS_HOME=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
```

Reload and verify:
``` bash
source ~/.bashrc
hadoop version
```

------------------------------------------------------------------------

## 5. Configure Hadoop's Java Environment

Edit `$HADOOP_HOME/etc/hadoop/hadoop-env.sh`:

``` bash
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

Ensure this line exists exactly once:
``` bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```
*Do NOT write `export JAVA_HOME=export JAVA_HOME=...`*

Verify with grep:
``` bash
grep -n 'JAVA_HOME' $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

------------------------------------------------------------------------

## 6. Create Local HDFS Storage Directories

Create directories to store the NameNode and DataNode data:

``` bash
mkdir -p ~/hadoop_data/hdfs/namenode
mkdir -p ~/hadoop_data/hdfs/datanode
```

------------------------------------------------------------------------

## 7. Configure core-site.xml

Set the default filesystem URI:

``` bash
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

Use:
``` xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://127.0.0.1:9000</value>
    </property>
</configuration>
```

------------------------------------------------------------------------

## 8. Configure hdfs-site.xml

Set replication factor and storage paths:

``` bash
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

Use:
``` xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>file:///home/kavimugil-r/hadoop_data/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>file:///home/kavimugil-r/hadoop_data/hdfs/datanode</value>
    </property>
</configuration>
```

------------------------------------------------------------------------

## 9. Configure mapred-site.xml

Configure MapReduce to use YARN and set environment paths:

``` bash
nano $HADOOP_HOME/etc/hadoop/mapred-site.xml
```

Use:
``` xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
    <property>
        <name>mapreduce.application.classpath</name>
        <value>/home/kavimugil-r/hadoop/share/hadoop/mapreduce/*,/home/kavimugil-r/hadoop/share/hadoop/mapreduce/lib/*</value>
    </property>
    <property>
        <name>yarn.app.mapreduce.am.env</name>
        <value>HADOOP_MAPRED_HOME=/home/kavimugil-r/hadoop</value>
    </property>
    <property>
        <name>mapreduce.map.env</name>
        <value>HADOOP_MAPRED_HOME=/home/kavimugil-r/hadoop</value>
    </property>
    <property>
        <name>mapreduce.reduce.env</name>
        <value>HADOOP_MAPRED_HOME=/home/kavimugil-r/hadoop</value>
    </property>
</configuration>
```

------------------------------------------------------------------------

## 10. Configure yarn-site.xml

Set the ResourceManager and NodeManager configurations:

``` bash
nano $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

Use:
``` xml
<configuration>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>localhost</value>
    </property>
    <property>
        <name>yarn.resourcemanager.address</name>
        <value>localhost:8032</value>
    </property>
    <property>
        <name>yarn.resourcemanager.scheduler.address</name>
        <value>localhost:8030</value>
    </property>
    <property>
        <name>yarn.resourcemanager.resource-tracker.address</name>
        <value>localhost:8031</value>
    </property>
    <property>
        <name>yarn.resourcemanager.admin.address</name>
        <value>localhost:8033</value>
    </property>
    <property>
        <name>yarn.resourcemanager.webapp.address</name>
        <value>localhost:8088</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.nodemanager.aux-services.mapreduce_shuffle.class</name>
        <value>org.apache.hadoop.mapred.ShuffleHandler</value>
    </property>
</configuration>
```

------------------------------------------------------------------------

## 11. Configure Passwordless localhost SSH

Hadoop's `start-dfs.sh` and `start-yarn.sh` scripts use SSH to start/manage daemons.

Generate key and authorize it:
``` bash
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Test:
``` bash
ssh localhost
exit
```

------------------------------------------------------------------------

## 12. Final Verification and Formatting

Verify configuration before formatting:
``` bash
hadoop version
echo $JAVA_HOME
echo $HADOOP_HOME
hadoop getconf -confKey fs.defaultFS
hadoop getconf -confKey yarn.resourcemanager.address
```

Format the NameNode (required only once):
``` bash
hdfs namenode -format
```

------------------------------------------------------------------------

## 13. Start and Verify Hadoop Services

Start HDFS:
``` bash
start-dfs.sh
```

Start YARN:
``` bash
start-yarn.sh
```

Check running daemons:
``` bash
jps
```

Expected: `NameNode`, `DataNode`, `SecondaryNameNode`, `ResourceManager`, `NodeManager`.

------------------------------------------------------------------------

# Common Errors

## NameNode PID Conflict
If you see an error like `namenode is running as process XXXX. Stop it first and ensure /tmp/hadoop-kavimugil-r-namenode.pid file is empty before retry.`:
1. Check if the process is actually running: `ps -fp XXXX`
2. If not running, remove the stale PID file: `rm /tmp/hadoop-kavimugil-r-namenode.pid`
3. Start HDFS again: `start-dfs.sh`

## SSH Permission Denied
If `ssh localhost` fails:
``` bash
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
```

------------------------------------------------------------------------

# Practical Exam Short Version

``` bash
# 1. Start Services
start-dfs.sh
start-yarn.sh

# 2. Verify Daemons
jps

# 3. Check HDFS
hdfs dfs -ls /

# 4. Check YARN
yarn node -list

# 5. Stop Services
stop-yarn.sh
stop-dfs.sh
```

------------------------------------------------------------------------

# Result

Apache Hadoop 3.3.6 was successfully installed and configured in single-node (pseudo-distributed) mode on Ubuntu 24.04. The HDFS and YARN daemons were verified using the `jps` command, and the web interfaces are accessible at `http://localhost:9870` (NameNode) and `http://localhost:8088` (ResourceManager).

# Final Environment Summary

``` text
Operating System : Ubuntu 24.04 LTS
Java             : OpenJDK 8
Python           : Python 3
Hadoop           : Apache Hadoop 3.3.6
Storage          : HDFS
Resource Manager : YARN
Processing       : MapReduce
SSH              : OpenSSH
Deployment       : Single-node / pseudo-distributed
Machines         : 1 laptop
```

------------------------------------------------------------------------

# Official Resources

- **Official Download Page**: [Apache Hadoop Releases](https://hadoop.apache.org/releases.html)
- **Installation Guide**: [Hadoop Installation Guide](https://hadoop.apache.org/docs/stable/hadoop-install.html)
