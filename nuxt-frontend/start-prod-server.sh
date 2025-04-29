#!/bin/bash

# 设置环境变量
export NODE_OPTIONS="--max-old-space-size=4096"
export NUXT_TELEMETRY_DISABLED=1

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf node_modules/.vite

# 启动生产模式服务器
echo "Starting production server on http://localhost:3003..."
NODE_ENV=production npx nuxt start --port 3003
