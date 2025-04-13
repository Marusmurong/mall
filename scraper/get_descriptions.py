#!/usr/bin/env python
"""
从DrHarness网站获取商品描述并更新到数据库
"""
import os
import sys
import logging
import asyncio
import django
from pathlib import Path
from playwright.async_api import async_playwright

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

# 导入Django模型
from goods.models import Goods

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("get_descriptions.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
HEADLESS_MODE = os.environ.get('HEADLESS_MODE', 'true').lower() == 'true'
TEST_MODE = os.environ.get('TEST_MODE', 'false').lower() == 'true'
MAX_PRODUCTS = int(os.environ.get('MAX_PRODUCTS', '0')) if os.environ.get('MAX_PRODUCTS') else None
SCREENSHOT_DIR = os.path.join(BASE_DIR, 'debug_screenshots')

async def get_product_description(page, url):
    """获取商品描述"""
    try:
        logger.info(f"正在访问商品页面: {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)  # 等待页面完全加载
        
        # 截图记录页面状态
        if not os.path.exists(SCREENSHOT_DIR):
            os.makedirs(SCREENSHOT_DIR)
        
        product_id = url.split('/')[-1].split('?')[0]
        screenshot_path = os.path.join(SCREENSHOT_DIR, f"product_{product_id}.png")
        await page.screenshot(path=screenshot_path)
        
        # 使用更好的脚本提取商品描述
        description = await page.evaluate("""
            () => {
                // 1. 先尝试常见的商品描述容器
                const descContainers = document.querySelectorAll(
                    '.product-single__description, .product-description, #product-description, ' +
                    '.product-single__content-text, [itemprop="description"], .product__description, ' +
                    '.product-content, .product-detail__description, .product-detail-text, ' +
                    '.product-single__content div[class*="desc"], [data-product-information-tab="description"]'
                );
                
                for (const container of descContainers) {
                    if (container && container.innerHTML.trim().length > 20) {
                        return container.innerHTML;
                    }
                }
                
                // 2. 如果找不到明确的描述容器，尝试查找商品内容区域的所有段落
                const productContent = document.querySelector(
                    '.product-single__content, .product-content, .product-detail, ' +
                    '.product-container, [class*="product-main"], #shopify-section-product'
                );
                
                if (productContent) {
                    const paragraphs = productContent.querySelectorAll('p');
                    const descParagraphs = [];
                    
                    for (const p of paragraphs) {
                        const text = p.textContent.trim();
                        // 忽略太短的段落和明显不是描述的段落（如配送、退款说明等）
                        if (text.length > 20 && 
                            !text.toLowerCase().includes('shipping') && 
                            !text.toLowerCase().includes('refund') && 
                            !text.toLowerCase().includes('return')) {
                            descParagraphs.push(p.outerHTML);
                        }
                    }
                    
                    if (descParagraphs.length > 0) {
                        return descParagraphs.join('');
                    }
                }
                
                // 3. 最后的备选方案：尝试从页面中找出所有类似描述的内容
                const mainContent = document.querySelector('main') || document.body;
                const descElements = mainContent.querySelectorAll('.rte, .description, [class*="desc"], section p');
                const descTexts = [];
                
                for (const el of descElements) {
                    const text = el.textContent.trim();
                    if (text.length > 50 && 
                        !text.toLowerCase().includes('shipping') && 
                        !text.toLowerCase().includes('refund') && 
                        !text.toLowerCase().includes('return') &&
                        !el.closest('footer') && 
                        !el.closest('header')) {
                        descTexts.push(el.outerHTML);
                    }
                }
                
                if (descTexts.length > 0) {
                    return descTexts.join('');
                }
                
                return '';
            }
        """)
        
        return description
    except Exception as e:
        logger.error(f"获取商品描述失败: {url}, 错误: {e}")
        return None

async def update_product_descriptions():
    """更新商品描述"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS_MODE)
        page = await browser.new_page()
        
        # 获取需要更新描述的商品
        products = Goods.objects.filter(
            source_url__contains='drharness.co',
            description__isnull=True
        ).order_by('id')
        
        if not products.exists():
            # 如果找不到描述为空的商品，则获取所有DrHarness商品
            products = Goods.objects.filter(
                source_url__contains='drharness.co'
            ).order_by('id')
        
        logger.info(f"找到 {products.count()} 个需要更新描述的商品")
        
        # 如果在测试模式下，只处理部分商品
        if TEST_MODE and MAX_PRODUCTS and products.count() > MAX_PRODUCTS:
            logger.info(f"测试模式: 只处理前 {MAX_PRODUCTS} 个商品")
            products = products[:MAX_PRODUCTS]
        
        # 更新商品描述
        descriptions_updated = 0
        for i, product in enumerate(products, 1):
            try:
                logger.info(f"正在处理商品 {i}/{products.count()}: {product.name}")
                
                # 获取商品描述
                description = await get_product_description(page, product.source_url)
                
                if description:
                    # 更新商品描述
                    product.description = description
                    product.goods_desc = description
                    product.save(update_fields=['description', 'goods_desc'])
                    logger.info(f"成功更新商品 '{product.name}' 的描述")
                    descriptions_updated += 1
                else:
                    logger.warning(f"无法获取商品 '{product.name}' 的描述")
            except Exception as e:
                logger.error(f"更新商品 '{product.name}' 描述失败: {e}")
        
        await browser.close()
        
        logger.info(f"完成描述更新，共更新了 {descriptions_updated}/{products.count()} 个商品的描述")
        return descriptions_updated

async def main():
    """主函数"""
    logger.info("=== 开始更新DrHarness商品描述 ===")
    updated_count = await update_product_descriptions()
    logger.info(f"=== 完成更新 {updated_count} 个商品描述 ===")

if __name__ == "__main__":
    asyncio.run(main()) 