#!/usr/bin/env python
"""
测试脚本：专门测试图片提取功能
"""
import asyncio
import logging
import json
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 测试URL
TEST_URL = "https://houseofsxn.com/products/servage-classic-posture-collar-high"

async def test_image_extraction():
    """测试多种图片提取方法"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        logger.info(f"正在打开页面: {TEST_URL}")
        await page.goto(TEST_URL)
        await page.wait_for_load_state('networkidle')
        
        # 1. 提取页面上所有图片元素
        logger.info("提取所有<img>元素")
        all_images = await page.query_selector_all('img')
        logger.info(f"找到 {len(all_images)} 个<img>元素")
        
        for i, img in enumerate(all_images):
            src = await img.get_attribute('src') or ''
            alt = await img.get_attribute('alt') or ''
            classname = await img.get_attribute('class') or ''
            if 'product' in src.lower() or 'product' in classname.lower():
                logger.info(f"商品相关图片 {i+1}: src={src}, alt={alt}, class={classname}")
        
        # 2. 提取产品图库相关元素
        logger.info("\n提取产品图库元素")
        gallery_selectors = [
            '.product-single__photo-wrapper',
            '.product__photo-container',
            '.product-gallery',
            '.product-single__media-group',
            '.product-page--images',
            '.product-media-modal__content'
        ]
        
        for selector in gallery_selectors:
            gallery_elements = await page.query_selector_all(selector)
            logger.info(f"选择器 '{selector}': 找到 {len(gallery_elements)} 个元素")
            
            if gallery_elements:
                for i, elem in enumerate(gallery_elements):
                    html = await elem.inner_html()
                    logger.info(f"  - 元素 {i+1} HTML (前200字符): {html[:200]}...")
        
        # 3. 从全局变量中提取图片信息
        logger.info("\n从全局变量中提取产品图片信息")
        js_product_images = await page.evaluate("""
            () => {
                // 尝试提取所有可能存储图片URL的全局变量
                const imageData = {
                    'window.meta': window.meta ? true : false,
                    'window.product': window.product ? true : false,
                    'window.theme': window.theme ? true : false
                };
                
                // 从window.product获取图片信息
                if (window.product && window.product.images) {
                    imageData.productImages = window.product.images;
                }
                
                // 从JSON元素中获取
                const jsonElements = Array.from(document.querySelectorAll('[id*="ProductJson"], [data-product-json]'));
                imageData.jsonElements = jsonElements.map(el => {
                    try {
                        return JSON.parse(el.textContent);
                    } catch (e) {
                        return null;
                    }
                }).filter(Boolean);
                
                // 提取页面中所有可能的产品图片URL
                const allProductImageUrls = [];
                document.querySelectorAll('img').forEach(img => {
                    if (img.src && img.src.includes('/products/')) {
                        allProductImageUrls.push({
                            src: img.src,
                            width: img.width,
                            height: img.height,
                            alt: img.alt,
                            className: img.className
                        });
                    }
                });
                imageData.allProductImageUrls = allProductImageUrls;
                
                return imageData;
            }
        """)
        
        logger.info(f"JS提取结果: {json.dumps(js_product_images, indent=2)}")
        
        # 4. 查看页面源码，寻找特定模式的图片URL
        logger.info("\n从页面源码中提取图片URL")
        html_content = await page.content()
        import re
        
        # 查找各种可能的图片URL模式
        patterns = [
            r'(https://cdn\.shopify\.com/[^"\']*?/products/[^"\']*?\.(?:jpe?g|png|gif|webp))',
            r'(\/\/cdn\.shopify\.com/[^"\']*?/products/[^"\']*?\.(?:jpe?g|png|gif|webp))',
            r'data-src="([^"]*?/products/[^"]*?\.(?:jpe?g|png|gif|webp))"',
            r'data-srcset="([^"]*?/products/[^"]*?\.(?:jpe?g|png|gif|webp)[^"]*?)"'
        ]
        
        all_urls = []
        for pattern in patterns:
            urls = re.findall(pattern, html_content)
            logger.info(f"模式 '{pattern}': 找到 {len(urls)} 个匹配")
            all_urls.extend(urls)
        
        # 去重并显示找到的URL
        unique_urls = list(set(all_urls))
        logger.info(f"总共找到 {len(unique_urls)} 个唯一图片URL")
        for i, url in enumerate(unique_urls[:10]):  # 只显示前10个
            logger.info(f"图片URL {i+1}: {url}")
        
        # 5. 截图保存
        logger.info("\n为进一步分析保存页面截图")
        await page.screenshot(path="product_page_screenshot.png", full_page=True)
        logger.info("页面截图已保存为 product_page_screenshot.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_image_extraction()) 