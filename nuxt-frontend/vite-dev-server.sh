#!/bin/bash

# 设置环境变量
export NODE_OPTIONS="--max-old-space-size=4096"
export NUXT_TELEMETRY_DISABLED=1
export VITE_CJS_IGNORE_WARNING=true
export VITE_CJS_TRACE=true

# 增加系统文件描述符限制
ulimit -n 4096

# 清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf node_modules/.vite

# 使用Vite直接启动，绕过Nuxt的文件监视
echo "Starting Vite dev server..."
npx vite --port 3003 --host localhost
