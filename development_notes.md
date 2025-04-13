## 商品采集系统开发

### 更新内容：完成商品采集和导入系统
### 文件路径：
- scraper/scrape_direct.py
- scraper/import_categories_products.py
- scraper/run_scrape_import.py
- scraper/test_single_product.py
- scraper/README.md

### 修改说明：
1. 开发了一套完整的商品采集和导入系统，支持从House of SXN网站采集商品数据
2. 实现功能包括：
   - 分类和子分类采集与导入，支持父子关系处理
   - 商品详情采集，支持从JSON-LD结构化数据中提取信息
   - 价格自动转换为USD
   - 多图片采集与导入
   - 增量更新支持（避免重复创建商品）
   - 交互式一键采集和导入
   - 单商品测试功能
3. 采集系统包含四个主要脚本：
   - 主采集脚本(scrape_direct.py)
   - 数据导入脚本(import_categories_products.py)
   - 一键运行脚本(run_scrape_import.py)
   - 单商品测试脚本(test_single_product.py)
4. 添加了详细的README文档，说明各脚本功能和使用方法

### 相关联动：
- 与goods模型关联，采集的商品数据会导入到goods模型中
- 为商品管理后台添加了source_url和goods_desc字段，便于管理采集的商品
- 与图片模型关联，支持多图片导入

### 使用方法：
1. 一键采集和导入：
   ```bash
   source venv/bin/activate
   python scraper/run_scrape_import.py
   ```
2. 测试单个商品采集和导入：
   ```bash
   source venv/bin/activate
   python scraper/test_single_product.py
   ```

### 后续优化方向：
1. 支持更多电商网站的采集
2. 增加商品属性（如尺寸、颜色等）的采集和导入
3. 优化图片处理，支持图片压缩和水印
4. 增加定时任务功能，实现自动采集更新
5. 增加采集监控和报警机制 