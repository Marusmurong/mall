# Fashion Leather Mall 部署说明

本文档提供关于Fashion Leather Mall电子商城系统的部署指南。

## 系统要求

- Python 3.11+
- Django 5.1.7
- SQLite 3 (生产环境建议使用MySQL或PostgreSQL)
- 静态文件服务器 (Nginx等)

## 部署步骤

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 数据库配置

项目默认使用SQLite数据库，如需使用其他数据库，请修改`mall/settings.py`中的数据库配置。

3. 设置环境变量

在生产环境，需要设置Django的SECRET_KEY环境变量。为了安全起见，不应使用代码中默认的密钥。

```bash
export DJANGO_SECRET_KEY='你的安全密钥'
```

4. 配置静态文件

静态文件已收集到`staticfiles`目录，需要配置Web服务器(如Nginx)指向此目录，并配置媒体文件目录。

5. 启动应用

使用WSGI或ASGI服务器运行应用程序，推荐使用Gunicorn和Nginx:

```bash
gunicorn --bind 0.0.0.0:8000 mall.wsgi:application
```

## Nginx配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 功能更新说明

本版本包含以下功能:
1. 商品分类与展示
2. 产品详情页面
3. 分类筛选功能
4. 价格区间筛选
5. 心愿单功能
6. 支付和订单处理
7. 用户登录和注册

## 联系支持

如有任何部署问题，请联系技术支持人员。 