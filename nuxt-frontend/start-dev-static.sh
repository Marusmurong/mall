#!/bin/bash

# 设置更高的文件描述符限制
ulimit -n 10000

# 确保使用 Node.js 18+
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

# 先构建静态版本
echo "Building static version..."
NODE_OPTIONS="--max-old-space-size=4096" ./node_modules/.bin/nuxt build

# 启动预览服务器
echo "Starting preview server..."
NODE_OPTIONS="--max-old-space-size=4096" ./node_modules/.bin/nuxt preview 