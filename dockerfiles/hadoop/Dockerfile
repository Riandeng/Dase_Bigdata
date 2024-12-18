# 使用腾讯云的镜像源作为基础镜像
FROM ubuntu-ssh

#安装java
ADD jdk-8u431-linux-x64.tar.gz /usr/local/
RUN mv /usr/local/jdk1.8.0_431 /usr/local/jdk1.8

#配置JAVA环境变量
ENV JAVA_HOME /usr/local/jdk1.8
ENV PATH $JAVA_HOME/bin:$PATH
#安装hadoop
ADD hadoop-3.4.1.tar.gz /usr/local
RUN mv /usr/local/hadoop-3.4.1 /usr/local/hadoop
#配置hadoop环境变量
ENV HADOOP_HOME /usr/local/hadoop
ENV PATH $HADOOP_HOME/bin:$PATH

#安装scala 注意Spark2.0.1对于Scala的版本要求是2.11.x
ADD scala-2.13.15.tgz /usr/local
RUN mv /usr/local/scala-2.13.15 /usr/local/scala2.13.15

#配置scala环境变量
ENV SCALA_HOME /usr/local/scala
ENV PATH $SCALA_HOME/bin:$PATH

#安装spark
ADD spark-3.4.4-bin-hadoop3.tgz /usr/local
RUN mv /usr/local/spark-3.4.4-bin-hadoop3 /usr/local/spark3.4.4

#配置spark环境变量
ENV SPARK_HOME /usr/local/spark3.4.4
ENV PATH $SPARK_HOME/bin:$PATH

#创建hdfs账号
RUN useradd hdfs
RUN echo "hdfs:12345678" | chpasswd

# 更新apt源并安装sudo和debianutils（包含which）
RUN apt-get update && apt-get install -y sudo debianutils