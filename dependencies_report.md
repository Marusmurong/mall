# 项目依赖清单报告

## 后端依赖 (requirements.txt)

后端使用Django框架，主要依赖包括：
- Django 5.1.7
- Channels 4.2.1 (WebSocket支持)
- Celery 5.4.0 (异步任务队列)
- Redis 5.2.1 (缓存和消息代理)
- Playwright 1.51.0 (网页自动化和爬虫)
- Pillow 11.1.0 (图像处理)
- Twisted 24.11.0 (异步网络框架)
- Django-simpleui 2025.1.13 (Admin界面美化)
- Django-debug-toolbar 5.1.0 (调试工具)

## 前端依赖

### 根目录 package.json
基础版本的前端依赖:
- Vue 3.5.13
- Vue Router 4.5.0
- Vuex 4.1.0
- Axios 1.8.4
- Nuxt 3.9.0

### Nuxt前端 (nuxt-frontend/package.json)
Nuxt框架主要项目:
- Nuxt 3.17.1
- Vue 3.5.13
- Pinia 2.1.7 (状态管理)
- @nuxtjs/i18n 8.0.0 (国际化)
- @nuxtjs/tailwindcss 6.10.1 (CSS框架)
- Axios 1.6.2 (HTTP客户端)
- Tailwind CSS 3.3.6
- HeadlessUI 1.7.16 (UI组件)
- HeroIcons 2.1.1 (图标库)
- Vue Toastification 2.0.0-rc.5 (提示消息)
- DOMPurify 3.2.5 (XSS保护)
- UUID 11.1.0 (唯一ID生成)

### Vue应用 (vue-app/package.json)
较简单的Vue应用:
- Vue 3.2.0
- Vue Router 4.0.0
- Vuex 4.0.0
- Vue CLI 5.0.0

## 插件和SDK

### Nuxt插件
- `toast.ts`: Vue Toastification插件配置
- `auth.ts`: 认证插件配置

### 配置的第三方服务/API
- 通过环境变量配置的API服务: `NUXT_PUBLIC_API_BASE_URL`

## 建议更新和完善

1. **依赖版本不一致问题**:
   - 不同目录中Vue版本不一致 (3.2.0 vs 3.5.13)
   - Axios版本不一致 (1.6.2 vs 1.8.4)

2. **缺失的依赖文档**:
   - 需要完善各第三方SDK的文档，包括用途和版本

3. **依赖管理改进**:
   - 考虑使用yarn workspaces或pnpm管理多包项目
   - 为子项目创建统一的依赖管理

4. **安全更新**:
   - 确保所有包都是最新的安全版本
   - 特别关注DOMPurify等安全相关包的版本

以上是对项目依赖的初步分析。建议根据实际开发需求进一步完善依赖管理。 