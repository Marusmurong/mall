#!/bin/bash

# 设置更高的文件描述符限制
ulimit -n 10000

# 确保使用 Node.js 18+
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

# 生成静态站点
echo "Generating static site..."
NITRO_PRESET=static NODE_OPTIONS="--max-old-space-size=4096" ./node_modules/.bin/nuxt generate

# 启动静态服务器
echo "Starting static file server..."
cd .output/public && npx serve 