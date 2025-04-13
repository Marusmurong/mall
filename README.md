# 多站点电商平台 (Mall)

这是一个基于Django和Vue/Nuxt的多站点电商平台系统，支持通过单一后台管理多个前端站点。系统采用微服务架构，具有高可扩展性和可维护性。

## 系统架构

### 后端架构

#### 核心框架
- **Django 5.1.7**: 提供API和管理后台
- **Django REST Framework 3.14.0**: 构建RESTful API
- **djangorestframework-simplejwt 5.3.0**: JWT认证实现
- **django-cors-headers 4.3.1**: 处理跨域请求
- **django-oauth-toolkit 2.3.0**: OAuth2支持

#### 数据库
- **SQLite** (开发环境)
- **PostgreSQL** (生产环境推荐)

#### 多站点支持
- **SiteMiddleware**: 检测当前请求所属站点
- **get_current_site()**: 获取当前站点标识
- **Site模型**: 站点配置存储
- **SiteTheme模型**: 站点主题管理
- **SiteConfig模型**: 站点配置管理
- **SiteSlide模型**: 站点幻灯片管理

#### API管理模块 (Alokai集成)
- **alokai_integration.py**: 提供API注册、监控和文档导出功能
- **@alokai_api_monitoring**: API监控装饰器
- **API版本管理**: 支持v1版本的API结构
- **统一响应格式**: {code, message, data}标准格式

#### 应用模块
- **goods**: 商品管理模块
  - GoodsCategory: 商品分类模型
  - Goods: 商品模型，包含visible_in字段控制站点可见性
  - GoodsImage: 商品图片模型

- **cart**: 购物车功能

- **order**: 订单系统
  - Order: 订单模型
  - OrderItem: 订单项模型
  - OrderLog: 订单日志模型

- **payment**: 支付系统
  - PaymentMethod: 支付方式模型
  - PaymentWebhookLog: 支付回调日志
  - 支持多种支付方式: 信用卡、PayPal、USDT等

- **users**: 用户管理
  - UserProfile: 用户资料模型
  - ShippingAddress: 收货地址模型

- **wishlist/wishlist_new**: 愿望清单功能
  - Wishlist: 愿望清单模型
  - WishlistItem: 愿望清单项模型
  - WishlistView: 愿望清单查看记录

- **telegram_bot/tg_bot**: Telegram机器人集成
  - TelegramBotSettings: 机器人设置
  - TelegramNotification: 通知模型
  - UserTelegramBinding: 用户绑定模型

### 前端架构

#### 核心框架
- **Vue 3**: 现代化前端框架
- **Nuxt 3**: Vue的服务端渲染框架
- **Vuex 4/Pinia**: 状态管理
- **Vue Router 4**: 路由管理

#### UI组件
- **Element Plus**: UI组件库
- **Tailwind CSS**: 实用工具类的CSS框架

#### 关键模块
- **useApi.ts**: API调用封装
- **JWT认证集成**: 处理用户登录和认证
- **动态路由**: 支持信息页面系统
- **心愿单分享页面**: 独立设计的分享页面

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

## 系统要求与项目依赖

### 系统要求
- Python 3.11+
- Node.js 16+
- SQLite 3 (开发环境)
- PostgreSQL 14+ (生产环境推荐)
- Nginx (生产环境)
- Redis (可选，用于缓存和会话存储)

### 后端依赖
```
Django==5.1.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
django-oauth-toolkit==2.3.0
Pillow==10.1.0  # 图片处理
gunicorn==21.2.0  # WSGI服务器
psycopg2-binary==2.9.9  # PostgreSQL驱动
dj-database-url==2.1.0  # 数据库URL配置
whitenoise==6.6.0  # 静态文件处理
python-dotenv==1.0.0  # 环境变量管理
```

### 前端依赖
```json
{
  "dependencies": {
    "@nuxtjs/axios": "^5.13.6",
    "@pinia/nuxt": "^0.5.1",
    "element-plus": "^2.4.2",
    "nuxt": "^3.8.0",
    "pinia": "^2.1.7",
    "vue": "^3.3.4",
    "vue-router": "^4.2.5",
    "vuex": "^4.1.0"
  },
  "devDependencies": {
    "@nuxtjs/tailwindcss": "^6.8.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "sass": "^1.69.5",
    "tailwindcss": "^3.3.5"
  }
}
```

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

## API路径结构

系统采用版本化的API结构，所有API请求都需要包含站点标识符。

### 基础路径
```
/api/v1/
```

### 认证相关
```
/api/v1/auth/login/      # 用户登录，获取JWT令牌
/api/v1/auth/refresh/    # 刷新JWT令牌
/api/v1/auth/verify/     # 验证JWT令牌
```

### 用户相关
```
/api/v1/user/register/   # 用户注册
/api/v1/user/profile/    # 用户资料
```

### 商品相关
```
/api/v1/products/        # 商品列表
/api/v1/products/{id}/   # 商品详情
/api/v1/categories/      # 分类列表
/api/v1/categories/{id}/ # 分类详情
```

### 心愿单相关
```
/api/v1/wishlists/                # 心愿单列表
/api/v1/wishlists/{id}/           # 心愿单详情
/api/v1/wishlists/{id}/share/     # 分享心愿单
```

### 订单相关
```
/api/v1/orders/          # 订单列表
/api/v1/orders/{id}/     # 订单详情
```

### 支付相关
```
/api/v1/payments/methods/  # 支付方式列表
/api/v1/payments/create/   # 创建支付
```

### 站点相关
```
/api/v1/sites/current/     # 获取当前站点信息
/api/v1/sites/themes/      # 获取站点主题
/api/v1/sites/config/      # 获取站点配置
/api/v1/sites/slides/      # 获取站点幻灯片
```

## 多站点配置

多站点配置存储在settings.py中的SITE_MAPPING和SITE_NAMES中。

### 站点映射配置示例
```python
SITE_MAPPING = {
    'example.com': 'default',
    'store.example.com': 'store',
    'wholesale.example.com': 'wholesale',
    'localhost:8000': 'default',
    '127.0.0.1:8000': 'default',
}

SITE_NAMES = {
    'default': '默认站点',
    'store': '零售商城',
    'wholesale': '批发商城',
}
```

### 商品站点可见性配置
商品模型中的`visible_in`字段使用JSONField存储商品在不同站点的可见性。例如：

```python
# 在所有站点可见
visible_in = ["default", "store", "wholesale"]

# 只在批发站点可见
visible_in = ["wholesale"]
```

### 添加新站点步骤
1. 在`settings.py`中更新SITE_MAPPING和SITE_NAMES
2. 创建新站点的主题和配置
3. 设置商品在新站点的可见性
4. 确保相应的域名指向您的服务器

## 贡献

欢迎提交问题和拉取请求。对于重大更改，请先打开一个问题讨论您想要更改的内容。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/) 