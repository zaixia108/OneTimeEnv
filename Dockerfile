FROM python:3.11.11-bookworm

# 安装必要的工具
RUN apt-get update && apt-get install -y nodejs npm zip tar build-essential

# 设置工作目录
WORKDIR /app

# 复制 Flask 应用和部署脚本
COPY app.py deploy.sh ./

# 复制前端文件
COPY static ./static
COPY templates ./templates

# 安装 Flask 依赖
RUN pip install flask flask-socketio -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动 Flask 应用和部署脚本
EXPOSE 8000
CMD sh deploy.sh