#!/bin/bash

# 大幅增加系统文件描述符限制
ulimit -n 10240

# 设置环境变量
export NODE_OPTIONS="--max-old-space-size=8192"
export NUXT_TELEMETRY_DISABLED=1

# 使用Node.js 18启动
echo "Starting Nuxt dev server with Node.js 18..."
source ~/.nvm/nvm.sh
nvm use 18

# 启动开发服务器
npm run dev
