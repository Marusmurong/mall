#!/usr/bin/env python
"""
测试脚本：验证修复后的采集功能
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from playwright.async_api import async_playwright

# 将项目根目录添加到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 设置环境变量
os.environ['TEST_MODE'] = 'False'
os.environ['HEADLESS_MODE'] = 'True'

# 导入采集函数
from scraper.scrape_direct import scrape_products_in_category

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def test_category_scrape():
    """测试特定类目的采集功能"""
    print("\n🔍 开始测试商品采集功能...")
    
    # 测试类目
    test_categories = [
        {
            'name': 'Fetish Wear',
            'url': 'https://houseofsxn.com/collections/leather-fetish-wear'
        },
        {
            'name': 'Leather Lingerie',
            'url': 'https://houseofsxn.com/collections/lingerie'
        }
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        total_products = 0
        
        # 测试每个类目
        for i, category in enumerate(test_categories, 1):
            print(f"\n📁 测试类目 {i}/{len(test_categories)}: {category['name']}")
            
            # 采集商品
            products = await scrape_products_in_category(page, category)
            
            # 统计图片
            image_count = sum(len(product.get('images', [])) for product in products)
            
            # 输出结果
            print(f"\n✅ 类目 '{category['name']}' 采集结果:")
            print(f"  - 采集到 {len(products)} 个商品")
            print(f"  - 采集到 {image_count} 张图片")
            
            total_products += len(products)
        
        await browser.close()
    
    print(f"\n🎉 测试完成! 总共采集到 {total_products} 个商品")

if __name__ == "__main__":
    asyncio.run(test_category_scrape()) 