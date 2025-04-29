#!/bin/bash

# 设置更高的文件描述符限制
ulimit -n 50000

# 确保使用 Node.js 18+
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 18

echo "Starting production build..."

# 首先清理缓存
echo "Cleaning cache..."
rm -rf .nuxt
rm -rf node_modules/.cache
rm -rf node_modules/.vite

# 使用增加的内存和优化设置构建
echo "Building for production..."
NODE_ENV=production \
NODE_OPTIONS="--max-old-space-size=8192" \
NITRO_PRESET=node-server \
NUXT_IMAGE_DOMAINS="localhost" \
./node_modules/.bin/nuxt build --max-file-watcher-limit=0

echo "Production build completed successfully!"

# Exit on any error
set -e

# 显示执行的每一条命令
set -x

# 进入前端目录
cd "$(dirname "$0")"

# 确保npm依赖已安装
npm install

# 复制生产环境配置
cp ../production-config/.env.production ./.env

# 清理之前的构建
rm -rf ./.output || true

# 构建生产版本
npm run build

# 验证构建结果
if [ -d "./.output" ]; then
  echo "✅ 构建成功，输出目录 ./.output 已创建"
  
  # 显示构建信息
  du -sh ./.output
  
  # 创建部署包
  DEPLOY_FILE="mall-frontend-$(date +%Y%m%d_%H%M%S).tar.gz"
  tar -czvf "../$DEPLOY_FILE" ./.output
  
  echo "✅ 部署包已创建: $DEPLOY_FILE"
  echo "✅ 可以将此文件上传到生产服务器并解压到网站根目录"
else
  echo "❌ 构建失败，未找到 ./.output 目录"
  exit 1
fi 