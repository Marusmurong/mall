#!/bin/bash

# 设置更高的文件描述符限制
ulimit -n 10000

# 确保使用 Node.js 18+
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

# 直接运行 nuxi 而不是通过 npm，禁用文件监控
NODE_OPTIONS="--max-old-space-size=4096 --no-watcher" npx nuxi dev 