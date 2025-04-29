#!/bin/bash

# 设置环境变量
export NODE_OPTIONS="--max-old-space-size=4096"
export NUXT_TELEMETRY_DISABLED=1

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf .output
rm -rf node_modules/.vite

# 构建静态版本
echo "Building static version..."
npx nuxt build --prerender

# 启动静态服务器
echo "Starting static server on http://localhost:3003..."
npx serve .output/public -l 3003
