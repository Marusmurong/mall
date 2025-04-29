# 商城前端部署指南

本文档提供了商城前端的部署步骤和注意事项。

## 系统要求

- 现代 Web 服务器（如 Nginx, Apache）
- Node.js v18+ (仅用于构建，生产服务器不需要)
- 足够的磁盘空间存储静态文件

## 构建步骤 (本地开发环境)

1. 确保已配置正确的生产环境变量
   - 编辑 `production-config/.env.production` 文件
   - 更新 API 地址为生产环境的实际地址

2. 执行构建脚本
   ```bash
   cd /path/to/mall/nuxt-frontend
   bash build-production.sh
   ```

3. 构建成功后会在项目根目录生成部署包 `mall-frontend-YYYYMMDD_HHMMSS.tar.gz`

## 部署步骤 (生产服务器)

1. 将生成的部署包上传到生产服务器
   ```bash
   scp mall-frontend-YYYYMMDD_HHMMSS.tar.gz user@production-server:/path/to/upload/
   ```

2. 在生产服务器上，解压部署包到网站根目录
   ```bash
   ssh user@production-server
   cd /path/to/webroot
   tar -xzvf /path/to/upload/mall-frontend-YYYYMMDD_HHMMSS.tar.gz
   ```

3. 配置 Web 服务器（Nginx 示例）
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       root /path/to/webroot/.output/public;
       index index.html;
       
       # API 代理配置
       location /api/ {
           proxy_pass https://api.example.com/api/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       # 静态文件缓存
       location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }
       
       # 处理 SPA 应用的页面刷新
       location / {
           try_files $uri $uri/ /index.html;
       }
   }
   ```

4. 重新加载 Nginx 配置
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## 关于编译资源的说明

- 所有静态资源都在构建时已经合并和压缩
- 所有 API 请求都会使用环境变量中配置的 API 基础地址
- 站点默认使用客户端路由，确保服务器将所有页面请求都重定向到 index.html

## 故障排除

如果遇到 API 连接问题：
1. 确认 `.env.production` 中的 API 地址是否正确
2. 确认生产服务器的 API 端点是否可访问
3. 检查 CORS 配置是否允许前端域名的请求
4. 检查浏览器控制台是否有网络错误

如果页面加载问题：
1. 确认所有静态资源是否成功加载（检查浏览器开发者工具）
2. 确认 Nginx 配置的 try_files 指令是否正确
3. 确保服务器文件权限配置正确 