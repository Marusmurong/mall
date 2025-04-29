#!/bin/bash

# 设置更高的文件描述符限制
ulimit -n 10000

# 确保使用 Node.js 18+
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

# 使用 --no-watch 参数禁用文件监控
echo "Starting dev server without file watching..."
NITRO_PRESET=node-server NODE_ENV=development NODE_OPTIONS="--max-old-space-size=4096" NUXT_WATCH_IGNORE_PATHS="public/goods/images" ./node_modules/.bin/nuxt dev --max-file-watcher-limit=1000 --no-clear 