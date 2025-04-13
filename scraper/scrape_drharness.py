#!/usr/bin/env python
"""
DrHarness网站采集脚本: 采集分类和商品数据
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

# 确保可以导入其他模块
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("drharness_scrape.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://drharness.co"
CATEGORIES_URL = "https://drharness.co/collections/"
IMAGES_DIR = "scraped_images/drharness"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 汇率换算 - 使用与前一个脚本相同的汇率
USD_TO_USD_RATE = 1.0  # DrHarness网站价格已经是美元

# 测试模式配置
TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
HEADLESS_MODE = os.environ.get('HEADLESS_MODE', 'True').lower() in ('true', '1', 't')
MAX_CATEGORIES = 2 if TEST_MODE else None  # 测试模式下最多处理的分类数量
MAX_PRODUCTS_PER_CATEGORY = 5 if TEST_MODE else None  # 测试模式下每个分类最多处理的商品数量

# 确保图片保存目录存在
Path(IMAGES_DIR).mkdir(exist_ok=True, parents=True)

async def scrape_categories(page):
    """从DrHarness网站采集分类"""
    logger.info(f"正在访问分类页面: {CATEGORIES_URL}")
    try:
        # 使用更宽松的加载条件domcontentloaded，并增加超时为45秒
        await page.goto(CATEGORIES_URL, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        logger.error(f"访问分类页面失败: {e}")
        logger.info("继续使用预定义分类")
    
    # 等待页面基本加载完成
    await asyncio.sleep(3)  # 给予页面充分加载时间
    
    # 截图记录页面状态
    await page.screenshot(path="debug_categories_page.png")
    logger.info("已保存分类页面截图用于调试")
    
    # 直接使用预定义的主要分类
    logger.info("使用预定义的主要分类列表")
    categories = [
        {"name": "Leather Bondage", "url": "https://drharness.co/collections/leather-bondage"},
        {"name": "Leather Harnesses", "url": "https://drharness.co/collections/leather-harnesses"},
        {"name": "Leather Lingerie", "url": "https://drharness.co/collections/leather-lingerie"},
        {"name": "Accessories", "url": "https://drharness.co/collections/accessories"}
    ]
    logger.info(f"使用 {len(categories)} 个预定义分类")
    
    # 如果在测试模式下，只返回部分分类
    if TEST_MODE and MAX_CATEGORIES and len(categories) > MAX_CATEGORIES:
        logger.info(f"测试模式: 只处理前 {MAX_CATEGORIES} 个分类")
        return categories[:MAX_CATEGORIES]
    
    return categories

async def scrape_products_in_category(page, category):
    """采集分类中的所有商品"""
    category_name = category['name']
    category_url = category['url']
    
    logger.info(f"正在采集分类 '{category_name}' 中的商品: {category_url}")
    
    try:
        await page.goto(category_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)  # 等待页面完全加载
        
        # 截图记录页面状态
        screenshot_path = f"debug_category_{category_name.replace(' ', '_')}.png"
        await page.screenshot(path=screenshot_path)
        logger.info(f"已保存分类页面截图用于调试: {screenshot_path}")
        
        # 使用最基本的方式获取所有产品链接
        product_urls = await page.evaluate("""
            () => {
                // 获取所有链接
                const allLinks = Array.from(document.querySelectorAll('a'));
                // 筛选出商品链接
                const productLinks = allLinks
                    .filter(link => link.href && link.href.includes('/products/'))
                    .map(link => link.href);
                // 去重
                return [...new Set(productLinks)];
            }
        """)
        
        logger.info(f"在分类 '{category_name}' 中找到 {len(product_urls)} 个商品链接")
        
        # 如果在测试模式下，只获取部分商品
        if TEST_MODE and MAX_PRODUCTS_PER_CATEGORY and len(product_urls) > MAX_PRODUCTS_PER_CATEGORY:
            logger.info(f"测试模式: 只处理前 {MAX_PRODUCTS_PER_CATEGORY} 个商品")
            product_urls = product_urls[:MAX_PRODUCTS_PER_CATEGORY]
        
        # 采集每个产品的详细信息
        products = []
        for i, product_url in enumerate(product_urls, 1):
            logger.info(f"正在处理商品 {i}/{len(product_urls)}: {product_url}")
            
            try:
                product = await scrape_product_details(page, product_url, category_name)
                if product:
                    products.append(product)
                    logger.info(f"成功采集商品: {product['title']}")
                else:
                    logger.warning(f"无法采集商品信息: {product_url}")
            except Exception as e:
                logger.error(f"采集商品失败: {product_url}, 错误: {e}")
        
        logger.info(f"完成分类 '{category_name}' 中的 {len(products)}/{len(product_urls)} 个商品采集")
        return products
    
    except Exception as e:
        logger.error(f"采集分类 '{category_name}' 失败: {e}")
        return []

async def scrape_product_details(page, product_url, category_name):
    """采集商品详细信息"""
    try:
        # 尝试访问商品页面
        await page.goto(product_url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)  # 等待页面完全加载
        
        # 提取商品ID用于日志和文件命名
        product_id = product_url.split('/')[-1].split('?')[0]
        
        # 截图记录页面状态
        screenshot_path = f"debug_product_{product_id}.png"
        await page.screenshot(path=screenshot_path)
        logger.info(f"已保存商品页面截图用于调试: {screenshot_path}")
        
        # 使用简化的方式获取商品信息
        product_data = await page.evaluate("""
            () => {
                // 尝试获取标题 (多种可能的位置)
                let title = '';
                const h1Elements = document.querySelectorAll('h1');
                for (const h1 of h1Elements) {
                    if (h1.textContent.trim()) {
                        title = h1.textContent.trim();
                        break;
                    }
                }
                
                // 尝试获取价格 (多种可能的格式)
                let price = '0';
                const priceElements = document.querySelectorAll('.price, [class*="price"], .money, span[class*="Price"]');
                for (const el of priceElements) {
                    const text = el.textContent.trim();
                    if (text && /\$\d+(\.\d+)?/.test(text)) {
                        price = text.replace(/[^0-9.]/g, '');
                        break;
                    }
                }
                
                // 尝试获取描述
                let description = '';
                // 1. 先尝试常见的商品描述容器
                const descContainers = document.querySelectorAll(
                    '.product-single__description, .product-description, #product-description, ' +
                    '.product-single__content-text, [itemprop="description"], .product__description, ' +
                    '.product-content, .product-detail__description, .product-detail-text, ' +
                    '.product-single__content div[class*="desc"], [data-product-information-tab="description"]'
                );
                
                for (const container of descContainers) {
                    if (container && container.innerHTML.trim().length > 20) {
                        description = container.innerHTML;
                        break;
                    }
                }
                
                // 2. 如果找不到明确的描述容器，尝试查找商品内容区域的所有段落
                if (!description) {
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
                            description = descParagraphs.join('');
                        }
                    }
                }
                
                // 3. 最后的备选方案：尝试从页面中找出所有类似描述的内容
                if (!description) {
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
                        description = descTexts.join('');
                    }
                }
                
                // 检查库存状态
                const soldOutElements = document.querySelectorAll('[class*="sold-out"], [class*="soldOut"], .out-of-stock');
                const inStock = soldOutElements.length === 0;
                
                // 获取所有图片
                const images = [];
                // 收集产品图片元素，使用更精确的选择器
                const productSlider = document.querySelector('.product-single__photos, .product-images, #ProductPhoto, [class*="product-media"], [id*="product-gallery"]');
                
                if (productSlider) {
                    // 如果找到了产品图片区域，只从这个区域获取图片
                    const imgElements = productSlider.querySelectorAll('img');
                    imgElements.forEach(img => {
                        const src = img.dataset.src || img.dataset.originalSrc || img.src;
                        if (src && (src.includes('.jpg') || src.includes('.png') || src.includes('.webp'))) {
                            // 排除明显的礼品卡图片
                            if (!src.toLowerCase().includes('gift') && !src.toLowerCase().includes('card')) {
                                const cleanSrc = src.split('?')[0].replace(/(_\d+x\d+|_small|_medium|_large|_grande)/, '');
                                images.push(cleanSrc);
                            }
                        }
                    });
                } else {
                    // 如果找不到产品图片区域，尝试更保守的方法
                    // 1. 尝试找到所有大尺寸图片（通常是产品图片）
                    const largeImages = document.querySelectorAll('img[width="1080"], img[width="720"], img[width="800"], img[width="600"], img[width="500"]');
                    if (largeImages.length > 0) {
                        largeImages.forEach(img => {
                            const src = img.dataset.src || img.src;
                            if (src && (src.includes('.jpg') || src.includes('.png') || src.includes('.webp'))) {
                                const cleanSrc = src.split('?')[0].replace(/(_\d+x\d+|_small|_medium|_large|_grande)/, '');
                                images.push(cleanSrc);
                            }
                        });
                    } else {
                        // 2. 尝试筛选更可能是产品图片的图片（通过路径关键词）
                        const imgElements = document.querySelectorAll('img');
                        imgElements.forEach(img => {
                            const src = img.dataset.src || img.src;
                            // 只选择包含产品图片特征的图片URL
                            if (src && (src.includes('/products/') || src.includes('/collection/') || src.includes('/assets/') || src.includes('/uploads/')) 
                                && (src.includes('.jpg') || src.includes('.png') || src.includes('.webp'))) {
                                // 排除明显的logo和图标
                                if (!src.includes('logo') && !src.includes('icon') && !src.includes('payment') && 
                                    !src.toLowerCase().includes('gift') && !src.toLowerCase().includes('card')) {
                                    const cleanSrc = src.split('?')[0].replace(/(_\d+x\d+|_small|_medium|_large|_grande)/, '');
                                    images.push(cleanSrc);
                                }
                            }
                        });
                    }
                }
                
                return {
                    title,
                    price,
                    description,
                    inStock,
                    images: [...new Set(images)] // 去重
                };
            }
        """)
        
        # 提取基本信息
        title = product_data.get('title', '')
        if not title:
            title = product_url.split('/')[-1].replace('-', ' ').title()
            logger.warning(f"使用URL生成商品标题: {title}")
        
        price_str = product_data.get('price', '0')
        try:
            price_usd = float(price_str)
        except (ValueError, TypeError):
            price_usd = 0
            logger.warning(f"商品价格无效，使用默认价格0: {product_url}")
            
        description = product_data.get('description', '')
        in_stock = product_data.get('inStock', True)
        
        # 处理图片链接
        images = product_data.get('images', [])
        
        # 过滤图片URL，排除可能的导航图标和logo
        filtered_images = []
        for img_url in images:
            # 确保是绝对路径
            if not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(BASE_URL, img_url)
            
            # 排除明显的小图标、logo和导航图片
            if any(keyword in img_url.lower() for keyword in ['logo', 'icon', 'banner', 'payment', 'favicon', 'gift', 'card']):
                logger.info(f"排除非产品图片: {img_url}")
                continue
            
            # 基于尺寸筛选 - 通常产品图片会较大
            if '_50x50' in img_url or '_100x100' in img_url or 'thumbnail' in img_url:
                logger.info(f"排除缩略图: {img_url}")
                continue
            
            # 排除特定的图片模式 - 礼品卡相关
            if 'gift' in title.lower() or 'card' in title.lower():
                logger.info(f"排除礼品卡相关图片: {img_url}")
                continue
                
            filtered_images.append(img_url)
        
        # 使用过滤后的图片列表
        images = filtered_images
        
        # 去重
        images = list(dict.fromkeys(images))
        
        if not images:
            logger.warning(f"未找到商品图片: {product_url}")
        
        # 为当前商品创建专属文件夹名称
        product_folder_name = re.sub(r'[^\w\-]', '_', title)[:50]  # 安全的文件夹名，限制长度
        
        # 如果是礼品卡，跳过处理
        if 'gift' in title.lower() or 'card' in title.lower():
            logger.info(f"跳过礼品卡商品: {title}")
            return {
                'title': title,
                'url': product_url,
                'price_original': price_usd,
                'currency_original': 'USD',
                'price_usd': price_usd,
                'description': description,
                'sku': product_id,
                'brand': 'DrHarness',
                'in_stock': in_stock,
                'main_image': '',
                'images': [],
                'local_images': [],
                'category': category_name,
                'scraped_at': datetime.now().isoformat()
            }
            
        product_image_dir = os.path.join(IMAGES_DIR, product_folder_name)
        
        # 确保商品图片目录存在
        Path(product_image_dir).mkdir(exist_ok=True, parents=True)
        
        # 下载图片
        local_images = []
        for i, img_url in enumerate(images[:10]):  # 限制最多下载10张图片
            try:
                # 生成文件名
                file_ext = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
                filename = f"{i+1}{file_ext}"
                local_path = os.path.join(product_folder_name, filename)  # 相对路径
                full_path = os.path.join(product_image_dir, filename)     # 完整路径
                
                # 下载图片前验证文件大小
                response = requests.head(img_url, timeout=10)
                content_length = int(response.headers.get('content-length', 0))
                
                # 跳过小于10KB的图片，可能是图标
                if content_length < 10240:
                    logger.warning(f"跳过小图片(可能是图标): {img_url}, 大小: {content_length} bytes")
                    continue
                
                # 下载图片
                response = requests.get(img_url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(full_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    local_images.append(local_path)
                    logger.info(f"图片已保存: {local_path}")
                else:
                    logger.warning(f"下载图片失败: {img_url}, 状态码: {response.status_code}")
            except Exception as e:
                logger.warning(f"下载图片错误: {img_url}, 错误: {e}")
        
        # 创建商品对象
        product = {
            'title': title,
            'url': product_url,
            'price_original': price_usd,
            'currency_original': 'USD',
            'price_usd': price_usd,
            'description': description,
            'sku': product_id,  # 使用URL中的产品ID作为SKU
            'brand': 'DrHarness',
            'in_stock': in_stock,
            'main_image': images[0] if images else '',
            'images': images,
            'local_images': local_images,
            'category': category_name,
            'scraped_at': datetime.now().isoformat()
        }
        
        return product
    
    except Exception as e:
        logger.error(f"采集商品详情失败: {product_url}, 错误: {e}")
        return None

async def main():
    """主函数"""
    start_time = datetime.now()
    
    logger.info("=== 开始采集DrHarness网站数据 ===")
    logger.info(f"采集目标网站: {BASE_URL}")
    if TEST_MODE:
        logger.info("运行在测试模式，将仅处理有限的分类和商品")
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
        
        # 采集所有分类
        categories = await scrape_categories(page)
        logger.info(f"共找到 {len(categories)} 个分类")
        
        # 保存分类数据
        with open('drharness_categories.json', 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
        logger.info(f"分类数据已保存到 drharness_categories.json")
        
        # 采集每个分类中的商品
        all_products = []
        for i, category in enumerate(categories, 1):
            logger.info(f"正在处理分类 ({i}/{len(categories)}): {category['name']}")
            
            products = await scrape_products_in_category(page, category)
            all_products.extend(products)
            
            logger.info(f"分类 '{category['name']}' 已采集 {len(products)} 个商品")
            
            # 每采集完一个分类就保存一次数据，以防中途出错
            with open(f'drharness_products_{category["name"].replace(" ", "_")}.json', 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
        
        # 保存所有商品数据
        with open('drharness_all_products.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        await browser.close()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== DrHarness网站数据采集完成! ===")
    logger.info(f"统计信息:")
    logger.info(f"- 分类: {len(categories)} 个")
    logger.info(f"- 商品: {len(all_products)} 个")
    logger.info(f"- 耗时: {duration:.2f} 秒")
    
    return categories, all_products

if __name__ == "__main__":
    asyncio.run(main()) 