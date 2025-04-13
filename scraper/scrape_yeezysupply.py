#!/usr/bin/env python
"""
DrHarness网站采集脚本: 采集分类和商品数据（新版）
"""
import os
import sys
import json
import asyncio
import logging
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
import traceback

# 确保可以导入其他模块
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("drharness_new_scrape.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://drharness.co"
IMAGES_DIR = "scraped_images/drharness_new"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 测试模式配置
TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
HEADLESS_MODE = os.environ.get('HEADLESS_MODE', 'True').lower() in ('true', '1', 't')
MAX_PRODUCTS = 5 if TEST_MODE else None  # 测试模式下最多处理的商品数量

# 确保图片保存目录存在
Path(IMAGES_DIR).mkdir(exist_ok=True, parents=True)

async def get_browser():
    """Initialize and return a browser instance"""
    from playwright.async_api import async_playwright
    
    # Get configuration from environment variables
    headless_mode = os.environ.get('HEADLESS_MODE', 'true').lower() == 'true'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless_mode)
    
    return browser

async def process_product(page, product_url, product_title, site_name, image_folder="", category=""):
    """Process a single product and return its data"""
    print(f"Processing product: {product_title} at {product_url}")
    
    # Set a safe directory name for this product
    safe_title = product_title.lower().replace('"', '').replace("'", "").replace(" ", "_").replace("/", "_")
    product_dir = f"scraped_images/{image_folder}/{safe_title}"
    
    # Create directory for product images if it doesn't exist
    os.makedirs(product_dir, exist_ok=True)
    
    # Navigate to the product page
    try:
        await page.goto(product_url, wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Error navigating to product page {product_url}: {e}")
        return None
    
    # Extract product information using JavaScript
    product_data = await page.evaluate('''
        () => {
            // Get basic product information
            let title = document.querySelector('h1.product__title')?.innerText.trim() || '';
            
            // Get product price
            let price = '';
            const priceElement = document.querySelector('.price__regular .price-item--regular') || 
                               document.querySelector('.price .price-item--sale');
            if (priceElement) {
                price = priceElement.innerText.trim().replace(/[^0-9,.]/g, '');
            }
            
            // Get product description
            let description = '';
            const descriptionSelectors = [
                '.product-single__content-text.rte',
                '.rte[itemprop="description"]',
                '.product__description.rte',
                '.product-single__description.rte',
                '.product-description.rte',
                '.product-description'
            ];
            
            // Try each selector until we find a valid description
            for (const selector of descriptionSelectors) {
                const descElement = document.querySelector(selector);
                if (descElement && descElement.innerHTML.trim()) {
                    description = descElement.innerHTML.trim();
                    break;
                }
            }
            
            // Fallback: look for paragraphs in product content areas
            if (!description) {
                const contentAreas = document.querySelectorAll('.product-single__content, .product__content');
                for (const area of contentAreas) {
                    const paragraphs = area.querySelectorAll('p');
                    if (paragraphs.length > 0) {
                        // Skip paragraphs that are about shipping, refunds or warranty
                        const paragraphText = Array.from(paragraphs)
                            .filter(p => {
                                const text = p.innerText.toLowerCase();
                                return !text.includes('shipping') && 
                                       !text.includes('refund') && 
                                       !text.includes('warranty');
                            })
                            .map(p => p.outerHTML)
                            .join('');
                        
                        if (paragraphText) {
                            description = paragraphText;
                        }
                    }
                }
            }
            
            // Check stock status
            let inStock = true;
            const soldOutElement = document.querySelector('.badge--sold-out') || 
                                document.querySelector('[data-sold-out-message]');
            if (soldOutElement && soldOutElement.style.display !== 'none') {
                inStock = false;
            }
            
            // Get all product images
            const images = [];
            const imageElements = document.querySelectorAll('.product__media img');
            
            imageElements.forEach(img => {
                const src = img.src || img.dataset.src;
                if (src && !src.includes('logo') && !src.includes('icon')) {
                    images.push(src);
                }
            });
            
            // Get product SKU if available
            let sku = '';
            const skuElement = document.querySelector('[data-product-sku]');
            if (skuElement) {
                sku = skuElement.innerText.trim();
            }
            
            // Get available sizes if any
            const sizes = [];
            const sizeElements = document.querySelectorAll('.single-option-selector option, .variant-input label');
            sizeElements.forEach(element => {
                const size = element.innerText.trim();
                if (size && size.toLowerCase() !== 'select' && size.toLowerCase() !== 'choose') {
                    sizes.push(size);
                }
            });
            
            return {
                title,
                price,
                description,
                inStock,
                images,
                sku,
                sizes
            };
        }
    ''')
    
    if not product_data:
        print(f"Warning: Failed to extract data for product {product_title}")
        return None
    
    # Add product URL
    product_data['url'] = product_url
    
    # Add empty fields for consistent structure
    product_data['price_original'] = 0.0
    product_data['currency_original'] = 'USD'
    product_data['price_usd'] = 0.0
    product_data['brand'] = site_name
    product_data['in_stock'] = product_data.get('inStock', True)
    product_data['category'] = category
    
    # Process and save images
    local_images = []
    
    if product_data.get('images'):
        for i, image_url in enumerate(product_data['images']):
            if not image_url:
                continue
            
            # Skip images with "gift" or "card" in the URL for gift card products
            if "gift" in product_title.lower() and ("gift" in image_url.lower() or "card" in image_url.lower()):
                print(f"Skipping gift card image: {image_url}")
                continue
                
            # Extract image filename and clean it
            parsed_url = urlparse(image_url)
            path = parsed_url.path
            filename = os.path.basename(path).split('?')[0]
            
            # Save image
            try:
                img_path = f"{product_dir}/{filename}"
                
                # Don't re-download if image exists
                if not os.path.exists(img_path):
                    # Go to the image URL and wait for it to load
                    await page.goto(image_url, wait_until='domcontentloaded')
                    
                    # Take a screenshot and save it as the image
                    await page.screenshot(path=img_path)
                    print(f"Saved image {i+1}/{len(product_data['images'])}: {img_path}")
                    await page.wait_for_timeout(500)  # Small delay between image downloads
                else:
                    print(f"Image already exists: {img_path}")
                
                local_images.append(img_path)
            except Exception as e:
                print(f"Error saving image {image_url}: {e}")
    
    # Add local image paths to product data
    product_data['local_images'] = local_images
    
    # Set main image if available
    if local_images:
        product_data['main_image'] = local_images[0]
    
    # Add timestamp
    product_data['scraped_at'] = datetime.now().isoformat()
    
    # Return to the product page
    await page.goto(product_url, wait_until='domcontentloaded')
    
    return product_data

async def get_all_products(page):
    """获取DrHarness所有商品信息"""
    logger.info(f"正在访问DrHarness首页获取商品列表")
    
    try:
        # 访问首页
        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)  # 等待页面完全加载
            
        # 截图记录页面状态
        await page.screenshot(path="debug_drharness_home.png")
        logger.info("已保存首页截图用于调试")
        
        # 准备一个预定义商品列表，以防无法获取
        predefined_products = [
            {"url": "https://drharness.co/collections/leather-bondage/products/wide-waist-cincher-belt", "title": "Wide Waist Cincher Belt"},
            {"url": "https://drharness.co/collections/leather-lingerie/products/leather-garter-belt", "title": "Leather Garter Belt"},
            {"url": "https://drharness.co/collections/leather-harnesses/products/o-ring-chest-harness", "title": "O Ring Chest Harness"}
        ]
        
        # 尝试获取商品列表
        product_data = await page.evaluate("""
            () => {
                const links = [];
                
                // 获取所有链接
                const allLinks = Array.from(document.querySelectorAll('a'));
                // 筛选出商品链接
                const productLinks = allLinks
                    .filter(link => link.href && link.href.includes('/products/'))
                    .map(link => {
                        return {
                            url: link.href,
                            title: link.textContent.trim() || link.getAttribute('title') || 'Unknown Product'
                        }
                    });
                
                return productLinks;
            }
        """)
        
        if not product_data or len(product_data) == 0:
            logger.info("没有找到商品，使用预定义商品列表")
            product_data = predefined_products
        
        logger.info(f"在首页找到 {len(product_data)} 个商品")
        
        # 如果在测试模式下，只获取部分商品
        if TEST_MODE and MAX_PRODUCTS and len(product_data) > MAX_PRODUCTS:
            logger.info(f"测试模式: 只处理前 {MAX_PRODUCTS} 个商品")
            product_data = product_data[:MAX_PRODUCTS]
        
        return product_data
        
    except Exception as e:
        logger.error(f"获取商品列表失败: {e}")
        # 在出错的情况下返回预定义商品
        logger.info("使用预定义商品列表")
        predefined_products = [
            {"url": "https://drharness.co/collections/leather-bondage/products/wide-waist-cincher-belt", "title": "Wide Waist Cincher Belt"},
            {"url": "https://drharness.co/collections/leather-lingerie/products/leather-garter-belt", "title": "Leather Garter Belt"},
            {"url": "https://drharness.co/collections/leather-harnesses/products/o-ring-chest-harness", "title": "O Ring Chest Harness"}
        ]
        
        if TEST_MODE and MAX_PRODUCTS and len(predefined_products) > MAX_PRODUCTS:
            return predefined_products[:MAX_PRODUCTS]
            
        return predefined_products

async def scrape_product_details(page, product_info):
    """采集商品详细信息"""
    if not product_info or not product_info.get('url'):
        logger.error("无效的商品信息，跳过")
        return None
        
    product_url = product_info['url']
    logger.info(f"正在采集商品详情: {product_url}")
    
    try:
        # 访问商品页面
        await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)  # 等待页面完全加载，Yeezy网站可能需要更长时间
        
        # 提取商品ID用于日志和文件命名
        product_id = product_url.split('/')[-1].split('?')[0]
        
        # 截图记录页面状态
        screenshot_path = f"debug_product_yeezysupply_{product_id}.png"
        await page.screenshot(path=screenshot_path)
        logger.info(f"已保存商品页面截图用于调试: {screenshot_path}")
        
        # 使用JavaScript提取商品详细信息
        product_data = await page.evaluate("""
            () => {
                // 获取商品标题
                const titleEl = document.querySelector('.gl-heading, h1, [data-auto-id="product-name"]');
                const title = titleEl ? titleEl.textContent.trim() : '';
                
                // 获取商品价格
                const priceEl = document.querySelector('.gl-price, [data-auto-id="product-price"]');
                const priceText = priceEl ? priceEl.textContent.trim() : '';
                const price = priceText.replace(/[^0-9.]/g, '');
                
                // 获取商品描述（使用更好的方法避免重复）
                const descriptionSelectors = [
                    '.product-single__content-text.rte',
                    '.rte[itemprop="description"]',
                    '[itemprop="description"]',
                    '.product-single__description',
                    '.product__description',
                    '.product-description',
                    '.gl-product-description',
                    '[data-auto-id="product-description"]',
                    '.description',
                    '.item-details',
                    '#product-description',
                    '.product-info',
                    '.product-single__meta',
                    '.product-content'
                ];
                
                let description = '';
                
                // 尝试每个选择器，一旦找到内容就停止
                for (const selector of descriptionSelectors) {
                    const element = document.querySelector(selector);
                    if (element && element.innerHTML.trim()) {
                        description = element.innerHTML;
                        break;
                    }
                }
                
                // 如果没有找到描述，尝试查找所有可能包含产品描述的段落
                if (!description || description.trim() === '') {
                    const productContentSelectors = [
                        '.product-single__content-text',
                        '.product-content',
                        '.product-single__content-wrapper',
                        '.product-detail',
                        '.product-information',
                        '.tab-content'
                    ];
                    
                    for (const selector of productContentSelectors) {
                        const productContentArea = document.querySelector(selector);
                        if (productContentArea) {
                            const paragraphs = productContentArea.querySelectorAll('p, li, .text-content, span, strong');
                            let contentText = '';
                            paragraphs.forEach(p => {
                                // 排除明显不是产品描述的内容，如"运费"、"退款"等
                                const text = p.textContent.toLowerCase();
                                if (!text.includes('shipping') && 
                                    !text.includes('refund') && 
                                    !text.includes('warranty') && 
                                    text.length > 10) {
                                    contentText += p.innerHTML + ' ';
                                }
                            });
                            
                            if (contentText.trim()) {
                                description = contentText;
                                break;
                            }
                        }
                    }
                }
                
                // DrHarness网站特定的描述提取
                if (!description || description.trim() === '') {
                    const drHarnessDesc = document.querySelector('.product-single__content-text.rte');
                    if (drHarnessDesc) {
                        description = drHarnessDesc.innerHTML;
                    }
                }
                
                // 检查库存状态
                const soldOutEl = document.querySelector('.out-of-stock, [data-auto-id="out-of-stock"]');
                const inStock = !soldOutEl;
                
                // 获取商品图片
                const images = [];
                
                // 尝试获取主图片轮播中的图片
                const carouselImages = document.querySelectorAll('.gl-carousel__wrap img, [data-auto-id="image-gallery"] img, .product-single__media-wrapper img');
                if (carouselImages && carouselImages.length > 0) {
                    carouselImages.forEach(img => {
                        const src = img.src || img.dataset.src;
                        if (src && !images.includes(src) && 
                            !src.includes('logo') && 
                            !src.includes('icon') &&
                            !src.includes('gift-card') &&
                            !src.includes('payment')) {
                            images.push(src);
                        }
                    });
                }
                
                // 如果没有找到轮播图片，尝试找到产品主图
                if (images.length === 0) {
                    const mainImage = document.querySelector('.gl-product-card__image, [data-auto-id="product-image"] img, .product__photo img');
                    if (mainImage) {
                        const src = mainImage.src || mainImage.dataset.src;
                        if (src && !src.includes('logo') && !src.includes('icon') && !src.includes('payment')) {
                            images.push(src);
                        }
                    }
                }
                
                // 如果还是没有图片，尝试找到所有可能的产品图片
                if (images.length === 0) {
                    document.querySelectorAll('img').forEach(img => {
                        const src = img.src;
                        // 更严格的筛选条件
                        if (src && 
                            src.includes('product') && 
                            !src.includes('logo') && 
                            !src.includes('icon') &&
                            !src.includes('badge') &&
                            !src.includes('payment') &&
                            !src.includes('gift-card') &&
                            img.width > 200 && img.height > 200) {  // 图片尺寸应该足够大
                            images.push(src);
                        }
                    });
                }
                
                // 获取产品SKU/样式编号
                const skuEl = document.querySelector('[data-auto-id="product-color"] .gl-label, [data-auto-id="product-sku"]');
                const sku = skuEl ? skuEl.textContent.trim().replace('STYLE: ', '') : '';
                
                // 获取尺码信息
                const sizes = [];
                document.querySelectorAll('[data-auto-id="size-selector"] button, .gl-size-selector button').forEach(btn => {
                    const size = btn.textContent.trim();
                    const available = !btn.disabled;
                    if (size) {
                        sizes.push({ size, available });
                    }
                });
                
                return {
                    title,
                    price,
                    description,
                    inStock,
                    images,
                    sku,
                    sizes
                };
            }
        """)
        
        # 确保有标题
        if not product_data.get('title'):
            product_data['title'] = product_info.get('title', product_id.replace('-', ' ').title())
        
        # 下载图片
        local_images = []
        product_title = product_data.get('title', 'unknown').strip()
        
        # 跳过礼品卡产品
        if 'gift' in product_title.lower() or 'card' in product_title.lower():
            logger.warning(f"跳过礼品卡产品: {product_title}")
            product_data['images'] = []
            return product_data
        
        product_dir_name = "".join(c if c.isalnum() else "_" for c in product_title.lower())
        product_dir = Path(IMAGES_DIR) / product_dir_name
        product_dir.mkdir(exist_ok=True, parents=True)
        
        # 获取产品描述中的关键词，用于过滤图片
        description_lower = product_data.get('description', '').lower()
        product_keywords = product_title.lower().split()
        
        # 过滤不相关的图片
        filtered_images = []
        for img_url in product_data.get('images', []):
            # 排除明显不相关的图片
            if ('logo' in img_url.lower() or 
                'icon' in img_url.lower() or 
                'payment' in img_url.lower() or
                'gift-card' in img_url.lower() or
                'badge' in img_url.lower()):
                logger.warning(f"排除不相关图片: {img_url}")
                continue
                
            # 保留相关图片
            filtered_images.append(img_url)
        
        # 去重
        filtered_images = list(dict.fromkeys(filtered_images))
        
        # 如果过滤后没有图片，记录日志
        if not filtered_images:
            logger.warning(f"产品 '{product_title}' 没有有效图片")
        
        # 更新商品数据中的图片列表
        product_data['images'] = filtered_images
        
        for i, img_url in enumerate(filtered_images):
            try:
                # 从URL中获取文件名
                img_filename = os.path.basename(urlparse(img_url).path).split('?')[0]
                if not img_filename or len(img_filename) < 5:
                    img_filename = f"image_{i}.jpg"
                
                img_path = product_dir / img_filename
                
                # 下载图片
                response = requests.get(img_url, timeout=30, headers={'User-Agent': USER_AGENT})
                if response.status_code == 200:
                    with open(img_path, 'wb') as f:
                        f.write(response.content)
                    
                    relative_path = os.path.join(IMAGES_DIR, product_dir_name, img_filename)
                    local_images.append(relative_path)
                    logger.info(f"已保存图片: {relative_path}")
                else:
                    logger.warning(f"下载图片失败, 状态码: {response.status_code}, URL: {img_url}")
            except Exception as e:
                logger.error(f"处理图片出错: {e}, URL: {img_url}")
                
        # 创建最终商品数据
        product = {
            'title': product_data.get('title', ''),
            'url': product_url,
            'price_original': 0.0,  # 默认价格
            'currency_original': 'USD',
            'price_usd': 0.0,  # 默认价格
            'description': product_data.get('description', ''),
            'sku': product_data.get('sku', product_id),
            'brand': 'DrHarness',
            'in_stock': product_data.get('inStock', False),
            'main_image': local_images[0] if local_images else '',
            'images': product_data.get('images', []),
            'local_images': local_images,
            'category': 'Leather Bondage',  # DrHarness主要是皮革产品
            'sizes': product_data.get('sizes', []),
            'scraped_at': datetime.now().isoformat()
        }
        
        # 尝试解析价格
        try:
            price_str = product_data.get('price', '')
            if price_str and price_str.strip():
                price = float(price_str)
                product['price_original'] = price
                product['price_usd'] = price
        except (ValueError, TypeError) as e:
            logger.warning(f"价格转换失败: {e}, 使用默认价格0")
        
        logger.info(f"成功采集商品: {product['title']}")
        return product
        
    except Exception as e:
        logger.error(f"采集商品详情失败: {product_url}, 错误: {e}")
        return None

async def update_products_file(products, filename='products.json'):
    """Updates products file with new products"""
    updated_products = []
    existing_urls = set()

    # If the file exists, load existing products
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                existing_products = json.load(file)
                # Create a set of existing product URLs for quick lookup
                for product in existing_products:
                    if 'url' in product:
                        existing_urls.add(product['url'])
                updated_products = existing_products
        except json.JSONDecodeError:
            print(f"Warning: {filename} exists but is not valid JSON. Starting with empty list.")
    
    # Add only new products that don't exist yet
    new_count = 0
    for product in products:
        # Skip products without a URL
        if 'url' not in product:
            continue
            
        # Check if this product already exists
        if product['url'] not in existing_urls:
            updated_products.append(product)
            existing_urls.add(product['url'])
            new_count += 1
    
    # Write the updated products list back to the file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(updated_products, indent=2, ensure_ascii=False, default=str, fp=file)
    
    print(f"Added {new_count} new products to {filename}")
    return updated_products

async def main():
    """主函数"""
    start_time = datetime.now()
    
    logger.info("=== 开始采集DrHarness网站数据（新版） ===")
    logger.info(f"采集目标网站: {BASE_URL}")
    if TEST_MODE:
        logger.info("运行在测试模式，将仅处理有限的商品")
    logger.info(f"浏览器模式: {'无头模式' if HEADLESS_MODE else '可视模式'}")
    
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS_MODE)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=USER_AGENT
        )
        page = await context.new_page()
        
        # 配置页面超时设置
        page.set_default_timeout(60000)
        
        # 获取所有商品基本信息
        products_info = await get_all_products(page)
        logger.info(f"共找到 {len(products_info)} 个商品")
        
        # 采集每个商品的详细信息
        all_products = []
        for i, product_info in enumerate(products_info, 1):
            logger.info(f"正在处理商品 ({i}/{len(products_info)}): {product_info.get('title', 'Unknown Product')}")
            
            product = await scrape_product_details(page, product_info)
            if product:
                all_products.append(product)
            
            # 添加短暂延迟，避免请求过快
            await asyncio.sleep(2)
        
        # 保存所有商品数据
        await update_products_file(all_products, 'drharness_new_products.json')
        
        await browser.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== DrHarness网站数据采集完成（新版）! ===")
    logger.info(f"统计信息:")
    logger.info(f"- 商品: {len(all_products)} 个")
    logger.info(f"- 耗时: {duration:.2f} 秒")
    
    return all_products

if __name__ == "__main__":
    asyncio.run(main()) 