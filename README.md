# 多站点电商平台 (Mall)

这是一个基于Django和Vue/Nuxt的多站点电商平台系统，支持通过单一后台管理多个前端站点。

## 系统架构

### 后端
- **Django**: 提供API和管理后台
- **Django REST Framework**: 构建RESTful API
- **JWT认证**: 用户身份验证
- **多站点支持**: 通过SiteMiddleware实现多站点管理

### 前端
- **Vue 3/Nuxt**: 现代化前端框架
- **Vuex/Pinia**: 状态管理
- **Vue Router**: 路由管理

## 主要功能

### 多站点管理
- 通过单一Django后台管理多个前端站点
- 每个站点可以有独立的配置、主题和商品集合
- 通过visible_in字段控制商品在不同站点的可见性

### 商品系统
- 商品分类与展示
- 产品详情页面
- 分类筛选功能
- 价格区间筛选

### 用户系统
- JWT认证
- 用户注册和登录
- 用户资料管理

### 心愿单功能
- 创建和管理心愿单
- 心愿单分享功能
- 优化的移动端心愿单展示

### 购物与支付
- 购物车功能
- 订单管理
- 多种支付方式支持

### 其他功能
- Telegram机器人集成
- 信息页面系统(关于我们、购物指南、售后服务)
- API监控与管理(Alokai集成)

## 系统要求

- Python 3.11+
- Node.js 16+
- SQLite 3 (生产环境建议使用MySQL或PostgreSQL)

## 快速开始

### 后端设置

1. 激活虚拟环境
```bash
source venv/bin/activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行数据库迁移
```bash
python manage.py migrate
```

4. 创建超级用户
```bash
python manage.py createsuperuser
```

5. 启动开发服务器
```bash
python manage.py runserver
```

### 前端设置

1. 安装依赖
```bash
cd nuxt-frontend
npm install
```

2. 启动开发服务器
```bash
npm run dev
```

## 部署

### 后端部署

使用WSGI或ASGI服务器运行应用程序，推荐使用Gunicorn和Nginx:

```bash
gunicorn --bind 0.0.0.0:8000 mall.wsgi:application
```

### 前端部署

```bash
cd nuxt-frontend
npm run build
```

## 站点配置

站点配置存储在settings.py中的SITE_MAPPING和SITE_NAMES中。要添加新站点，请更新这些设置并确保相应的域名指向您的服务器。

## 贡献

欢迎提交问题和拉取请求。对于重大更改，请先打开一个问题讨论您想要更改的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/) 