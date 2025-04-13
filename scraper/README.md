# 商品采集与导入系统

本目录包含用于从 House of SXN 网站采集商品数据并导入 Django 系统的脚本。

## 主要脚本

### 1. 采集脚本 (scrape_direct.py)

**功能**：从 House of SXN 网站采集分类和商品数据。

**特点**：
- 采集分类和子分类信息
- 采集商品基本信息（名称、描述、价格等）
- 采集商品详细信息（包括结构化数据）
- 支持价格自动转换为 USD
- 支持多种图片采集方法
- 支持分页采集

**使用方法**：
```bash
source venv/bin/activate
python scraper/scrape_direct.py
```

### 2. 导入脚本 (import_categories_products.py)

**功能**：将采集的数据导入到 Django 数据库中。

**特点**：
- 导入分类和子分类，处理父子关系
- 导入商品信息，与分类关联
- 下载并导入商品图片
- 支持增量更新（已存在的商品会更新，不会重复创建）
- 详细的日志记录

**使用方法**：
```bash
source venv/bin/activate
python scraper/import_categories_products.py
```

### 3. 一键运行脚本 (run_scrape_import.py)

**功能**：提供交互式界面，一键执行采集和导入过程。

**特点**：
- 交互式用户界面
- 支持测试模式（仅采集少量数据进行测试）
- 分步执行，用户可控制流程
- 详细的进度和结果反馈

**使用方法**：
```bash
source venv/bin/activate
python scraper/run_scrape_import.py
```

### 4. 单商品测试脚本 (test_single_product.py)

**功能**：测试对单个商品的采集和导入功能。

**特点**：
- 对单个商品进行采集测试
- 支持采集结果可视化（显示浏览器窗口）
- 可选择是否将测试商品导入数据库
- 详细的测试日志记录

**使用方法**：
```bash
source venv/bin/activate
python scraper/test_single_product.py
```

## 数据结构

采集的数据以 JSON 格式存储，结构如下：

### 分类数据
```json
[
  {
    "name": "分类名称",
    "parent": "父分类名称（如果有）",
    "description": "分类描述"
  }
]
```

### 商品数据
```json
[
  {
    "title": "商品名称",
    "description": "商品描述",
    "url": "商品URL",
    "category": "商品所属分类",
    "price": "原始价格",
    "currency": "原始货币",
    "price_usd": "转换为美元的价格",
    "in_stock": true/false,
    "images": ["图片URL1", "图片URL2", ...]
  }
]
```

## 运行环境要求

- Python 3.8+
- Django 3.2+
- Playwright (`pip install playwright && playwright install`)
- requests, beautifulsoup4, aiohttp 等依赖库

## 故障排除

如果在运行过程中遇到问题：

1. 检查日志文件（*.log）以获取详细错误信息
2. 确保网络连接正常
3. 可能需要更新 CSS 选择器（如网站更新了布局）
4. 对于导入失败，检查 Django 数据库配置和模型设置 