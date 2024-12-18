# 大规模课程实验
## 实验流程
### 实验环境
服务器：
操作系统：Ubuntu22.04
Hadoop:3.4.1
Spark:3.4.4
Java:1.8.0_431
### 启动服务
已经用Dockerfile配置好了实验所需镜像环境，从腾讯云拉取实验镜像

```bash
docker pull ccr.ccs.tencentyun.com/ecnu_bigdata/hadoop:latest
```
运行一主二从三个节点，
```bash
docker run   -d -P -p 50070:50070 -p 8088:8088 -p 8080:8080 --name master -h master --add-host slave01:172.17.0.6 --add-host slave02:172.17.0.7 hadoop:latest
docker run   -d -P --name slave01 -h slave01 --add-host master:172.17.0.5 --add-host slave02:172.17.0.7  hadoop:latest
docker run   -d -P --name slave02 -h slave02 --add-host master:172.17.0.5 --add-host slave01:172.17.0.6  hadoop:latest
```
启动服务
```bash
start-all.sh #在/usr/local/spark3.4.4/sbin下
#master节点
./start-master.sh
#slave节点
./start-worker.sh spark:172.17.0.5:7077     
```

