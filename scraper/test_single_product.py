#!/usr/bin/env python
"""
测试脚本：对单个商品进行采集和测试
"""
import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_product.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 设置测试商品URL
TEST_PRODUCT_URL = "https://houseofsxn.com/products/servage-classic-posture-collar-high"
TEST_CATEGORY = "测试分类"
TEST_RESULT_FILE = "test_product.json"

async def test_single_product():
    """测试对单个商品的采集"""
    try:
        # 导入这里才进行，避免循环导入
        from scraper.scrape_direct import scrape_product_details
        from playwright.async_api import async_playwright
        
        logger.info(f"=== 开始测试单个商品采集 ===")
        logger.info(f"测试URL: {TEST_PRODUCT_URL}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # 使用无头模式
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            # 采集商品详情
            product_data = await scrape_product_details(page, TEST_PRODUCT_URL, TEST_CATEGORY)
            
            if product_data:
                logger.info(f"成功采集商品: {product_data['title']}")
                logger.info(f"商品价格(美元): ${product_data['price_usd']}")
                logger.info(f"图片数量: {len(product_data['images'])}")
                
                # 保存结果到文件
                with open(TEST_RESULT_FILE, "w", encoding="utf-8") as f:
                    json.dump(product_data, f, ensure_ascii=False, indent=2)
                logger.info(f"测试结果已保存到 {TEST_RESULT_FILE}")
            else:
                logger.error("商品采集失败")
            
            await browser.close()
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")

def test_import_single_product():
    """测试导入单个商品"""
    try:
        # 检查测试结果文件是否存在
        if not os.path.exists(TEST_RESULT_FILE):
            logger.error(f"测试结果文件不存在: {TEST_RESULT_FILE}")
            return False
        
        # 加载测试数据
        with open(TEST_RESULT_FILE, "r", encoding="utf-8") as f:
            product_data = json.load(f)
        
        logger.info(f"=== 开始测试单个商品导入 ===")
        logger.info(f"商品: {product_data['title']}")
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
        import django
        django.setup()
        
        # 导入Django模型
        from goods.models import Goods, GoodsCategory
        from scraper.import_categories_products import import_products
        
        # 创建测试分类
        category, created = GoodsCategory.objects.get_or_create(
            name=TEST_CATEGORY,
            defaults={'level': 1, 'description': '测试分类', 'is_active': True}
        )
        
        # 创建分类映射
        category_map = {TEST_CATEGORY: category.id}
        
        # 导入商品
        total_created, total_updated, total_skipped = import_products([product_data], category_map)
        
        logger.info(f"导入完成: 新建 {total_created}, 更新 {total_updated}, 跳过 {total_skipped}")
        
        # 验证商品是否已导入数据库
        try:
            product = Goods.objects.get(source_url=product_data['url'])
            logger.info(f"商品已成功导入数据库: {product.name}, ID: {product.id}")
            return True
        except Goods.DoesNotExist:
            logger.error(f"商品未成功导入数据库")
            return False
        
    except Exception as e:
        logger.error(f"测试导入过程中发生错误: {e}")
        return False

def main():
    """主函数：运行采集和导入测试"""
    # 测试采集
    asyncio.run(test_single_product())
    
    # 提示用户是否继续测试导入
    continue_import = input("\n采集测试完成，是否继续测试导入? (y/n): ").lower().strip() == 'y'
    if continue_import:
        success = test_import_single_product()
        if success:
            print("\n✅ 测试成功! 商品已成功采集并导入到数据库。")
        else:
            print("\n❌ 测试失败! 导入过程中出现错误。")
    else:
        print("\n测试结束。只完成了采集测试，未进行导入测试。")

if __name__ == "__main__":
    main() 