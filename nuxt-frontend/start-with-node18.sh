#!/bin/bash

# 设置环境变量
export NODE_OPTIONS="--max-old-space-size=4096"
export NUXT_TELEMETRY_DISABLED=1
export CHOKIDAR_USEPOLLING=0
export CHOKIDAR_USE_WATCHMAN=true

# 增加系统文件描述符限制
ulimit -n 4096

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf node_modules/.vite

# 使用Node.js 18启动Nuxt开发服务器
echo "Starting Nuxt with Node.js 18.20.8..."

# 使用指定的Node.js 18版本路径
/Users/jimmu/.nvm/versions/node/v18.20.8/bin/node /Users/jimmu/.nvm/versions/node/v18.20.8/bin/npx nuxt dev --port 3003 --no-clear
