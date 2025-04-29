#!/bin/bash

# 增加系统文件描述符限制
echo "Setting higher file descriptor limits..."
ulimit -n 4096

# 设置环境变量以优化开发体验
export NODE_OPTIONS="--max-old-space-size=4096"
export NUXT_TELEMETRY_DISABLED=1
export CHOKIDAR_USEPOLLING=0
export CHOKIDAR_USE_WATCHMAN=true

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf node_modules/.vite

# 使用简化的开发配置启动
echo "Starting Nuxt in development mode with higher limits..."
NODE_ENV=development npx nuxt dev --port 3003 --no-clear
