#!/bin/bash

# 设置环境变量
export NODE_OPTIONS="--max-old-space-size=8192"
export NUXT_TELEMETRY_DISABLED=1

# 大幅增加系统文件描述符限制
ulimit -n 10240

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf .output
rm -rf node_modules/.vite

# 构建静态版本
echo "Building static version..."
npx nuxi build --preset=node-server

# 启动预览服务器
echo "Starting preview server on http://localhost:3003..."
PORT=3003 node .output/server/index.mjs
