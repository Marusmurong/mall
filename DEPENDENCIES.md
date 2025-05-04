# 项目依赖说明文档

本文档详细记录了项目中使用的所有主要依赖、SDK和插件，包括它们的用途和版本信息。

## 后端依赖 (Python/Django)

### 核心框架
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Django | 5.1.7 | Web应用框架，项目的核心后端框架 |
| Channels | 4.2.1 | Django的WebSocket支持，实现实时通信 |
| Daphne | 4.1.2 | ASGI服务器，处理异步HTTP和WebSocket请求 |
| Django-simpleui | 2025.1.13 | 美化Django管理后台界面 |
| Django-debug-toolbar | 5.1.0 | 开发调试工具，用于性能分析和调试 |

### 异步任务和缓存
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Celery | 5.4.0 | 分布式任务队列，处理异步任务 |
| Redis | 5.2.1 | 缓存和消息代理，用于Celery和会话存储 |
| Kombu | 5.5.1 | 消息传递库，Celery的依赖 |

### 数据处理和集成
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Pillow | 11.1.0 | 图像处理库，用于商品图片处理 |
| Playwright | 1.51.0 | 浏览器自动化库，用于网页爬虫 |
| Beautifulsoup4 | 4.13.3 | HTML解析库，用于网页内容提取 |
| Requests | 2.32.3 | HTTP客户端库，用于API调用和数据抓取 |

### 安全和加密
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Cryptography | 44.0.2 | 密码学工具，用于加密功能 |
| PyOpenSSL | 25.0.0 | OpenSSL的Python包装器，用于SSL/TLS |

## 前端依赖

### Nuxt前端 (nuxt-frontend/)

#### 核心框架
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Nuxt | 3.17.1 | Vue.js的SSR框架，项目的前端框架 |
| Vue | 3.5.13 | 前端JavaScript框架 |
| Vue Router | 4.2.5 | Vue.js的官方路由管理器 |
| Pinia | 2.1.7 | Vue 3的状态管理库，替代Vuex |

#### UI和样式
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Tailwind CSS | 3.3.6 | 实用优先的CSS框架 |
| @nuxtjs/tailwindcss | 6.10.1 | Tailwind CSS的Nuxt集成 |
| @headlessui/vue | 1.7.16 | 无样式的UI组件，与Tailwind配合使用 |
| @heroicons/vue | 2.1.1 | SVG图标集合 |

#### 功能扩展
| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| @nuxtjs/i18n | 8.0.0 | 国际化支持 |
| Axios | 1.6.2 | HTTP客户端，用于API请求 |
| Vue Toastification | 2.0.0-rc.5 | Toast通知库 |
| UUID | 11.1.0 | 生成唯一标识符 |
| DOMPurify | 3.2.5 | HTML内容净化，防止XSS攻击 |
| Marked | 15.0.8 | Markdown解析器 |
| @vueuse/core | 10.7.0 | Vue组合式API工具集 |

### Vue应用 (vue-app/)

| 依赖名称 | 版本 | 用途描述 |
|---------|------|---------|
| Vue | 3.2.0 | 前端JavaScript框架 |
| Vue Router | 4.0.0 | Vue.js的官方路由管理器 |
| Vuex | 4.0.0 | Vue.js的状态管理库 |
| @vue/cli-service | 5.0.0 | Vue CLI的项目服务 |

## 插件配置

### Nuxt插件
| 插件名称 | 文件路径 | 用途描述 |
|---------|----------|---------|
| Toast插件 | nuxt-frontend/plugins/toast.ts | 全局Toast通知配置 |
| 认证插件 | nuxt-frontend/plugins/auth.ts | 用户认证和身份验证 |

## 依赖更新和维护指南

### 版本更新策略

1. **安全更新优先**：优先更新含有安全漏洞的依赖
2. **主要版本谨慎更新**：对于主要版本更新，需先在开发环境测试
3. **保持同步**：相关依赖应保持相互兼容的版本

### 定期审查流程

1. 每月使用以下命令检查依赖安全性：
   ```bash
   # 后端依赖检查
   pip-audit
   
   # 前端依赖检查
   cd nuxt-frontend && npm audit
   cd vue-app && npm audit
   ```

2. 每季度进行一次非安全性依赖更新评估

### 依赖添加规范

在添加新依赖时，请遵循以下规则：

1. 确认是否确实需要新依赖，是否有已存在的库可以实现同样功能
2. 评估依赖的活跃度、维护状态和社区支持
3. 确保添加的依赖与现有技术栈兼容
4. 在添加后更新本文档

### 版本锁定

1. Python依赖版本通过requirements.txt精确锁定：
   ```bash
   pip freeze > requirements.txt
   ```

2. JavaScript依赖通过package-lock.json锁定：
   ```bash
   npm ci  # 使用而非npm install确保精确版本
   ```

---

**最后更新日期**: 2025年5月5日 