# 使用腾讯云的镜像源作为基础镜像
FROM deccr.ccs.tencentyun.com/tkeimages/ubuntu-base:22.04

# 更新系统并安装一些基础工具
RUN apt-get update && \
    apt-get install -y curl vim git wget openjdk-8-jdk openssh-server sudo openssh-client && \
    apt-get clean

# 配置 SSH 服务
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "Port 22" >> /etc/ssh/sshd_config

# 配置 root 用户密码
RUN echo "root:123456" | chpasswd

# 配置 sudo 权限
RUN echo "root   ALL=(ALL)       ALL" >> /etc/sudoers

# 生成 SSH 密钥
RUN mkdir -p /etc/ssh && \
    ssh-keygen -A

# 创建 SSH 运行目录
RUN mkdir /var/run/sshd

# 开放 SSH 端口
EXPOSE 22

# 启动 SSH 服务并保持容器运行
CMD ["/usr/sbin/sshd", "-D"]
