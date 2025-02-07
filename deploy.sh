#!/bin/sh

# 设置项目目录
PROJECT_DIR=/var/www/html
UPLOAD_DIR=/app/uploads

# 创建项目目录和上传目录
mkdir -p $PROJECT_DIR
mkdir -p $UPLOAD_DIR

chmod -R 777 $UPLOAD_DIR
chmod -R 777 /app

# 复制静态文件和模板
cp -r /app/static $PROJECT_DIR
cp -r /app/templates $PROJECT_DIR

# 设置运行用户
# shellcheck disable=SC2034
USER_ID=$(id -u)
# shellcheck disable=SC2034
GROUP_ID=$(id -g)

# 启动 Flask 应用
cd /app || exit
python3 app.py