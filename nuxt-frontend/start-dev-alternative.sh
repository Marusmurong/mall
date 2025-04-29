#!/bin/bash

# 设置更高的文件描述符限制
ulimit -n 10000

# 确保使用 Node.js 18+
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

# 使用 NODE_DEV 环境变量，Nuxt 会使用这个来配置开发
NODE_ENV=development NODE_OPTIONS="--max-old-space-size=4096" npx nuxi dev --no-clear 