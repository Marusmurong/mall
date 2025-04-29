#!/bin/bash

# 设置环境变量以限制文件监视
export NODE_OPTIONS="--max-old-space-size=4096"
export CHOKIDAR_USEPOLLING=0
export NUXT_TELEMETRY_DISABLED=1
export WATCHPACK_POLLING=false
export BABEL_DISABLE_CACHE=1

# 确保使用 Watchman
export CHOKIDAR_USE_WATCHMAN=true
export WATCHMAN_SOCKNAME=/usr/local/var/run/watchman/jimmu-state/sock

# 设置文件监视限制
ulimit -n 2048

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf node_modules/.vite

# 确保 Watchman 正在运行
echo "Ensuring Watchman is running..."
watchman watch-project $(pwd)

# 以开发模式启动，使用 --no-clear 避免清屏
echo "Starting Nuxt in development mode with Watchman..."
npx nuxt dev --no-clear
