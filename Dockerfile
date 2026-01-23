
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# 安装系统依赖和 VNC/图形组件
RUN apt-get update && apt-get install -y --no-install-recommends \
    x11vnc \
    xvfb \
    fluxbox \
    novnc \
    websockify \
    wget \
    net-tools \
    xterm \
    dos2unix \
    pciutils \
    gnupg2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 NVIDIA GPU 工具（如 nvidia-smi）
RUN apt-get update && apt-get install -y nvidia-utils-525 || true

# 设置 VNC 密码
RUN mkdir -p /root/.vnc && \
    x11vnc -storepasswd 123456 /root/.vnc/passwd

# 拷贝启动脚本
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh && dos2unix /startup.sh

EXPOSE 80 5900

CMD ["/startup.sh"]
