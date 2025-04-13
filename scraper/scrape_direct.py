#!/usr/bin/env python
"""
简化版采集脚本：只采集类目和商品信息
"""
import os
import json
import asyncio
import logging
import re
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from pathlib import Path
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_direct.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://houseofsxn.com"
RESULTS_FILE = "scraped_categories_products.json"
TIMEOUT = 60000  # 超时设置(ms)
IMAGES_DIR = "scraped_images"  # 图片保存目录

# 测试模式配置
TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
MAX_PRODUCTS_PER_CATEGORY = 3 if TEST_MODE else None  # 每个分类最多抓取的商品数量

# 无头模式配置
HEADLESS_MODE = os.environ.get('HEADLESS_MODE', 'True').lower() in ('true', '1', 't')

# 货币换算比率 (假设为马来西亚林吉特兑美元的比率)
# 根据实际情况调整这个值
MYR_TO_USD_RATE = 0.22  # 1 MYR ≈ 0.22 USD

# 确保图片保存目录存在
Path(IMAGES_DIR).mkdir(exist_ok=True, parents=True)

async def scrape_categories(page):
    """抓取网站的所有分类"""
    logger.info("正在抓取网站分类...")
    
    # 确保加载主页
    try:
        await page.goto(BASE_URL, timeout=TIMEOUT)
        await page.wait_for_load_state('networkidle')
    except Exception as e:
        logger.error(f"加载页面失败: {e}")
    
    # 获取顶级分类
    categories = []
    
    # 尝试从主导航中获取分类
    nav_elements = await page.query_selector_all('.site-nav__item a')
    for nav_element in nav_elements:
        try:
            name = await nav_element.text_content()
            url = await nav_element.get_attribute('href')
            if url:
                full_url = urljoin(BASE_URL, url)
                
                # 排除商品链接和带有价格标记的链接
                if 'products/' in full_url or '$' in name:
                    continue
                    
                # 仅保留collection类型的链接
                if '/collections/' in full_url:
                    categories.append({
                        'name': name.strip(),
                        'url': full_url,
                        'parent': None
                    })
                    logger.info(f"找到顶级分类: {name} - {full_url}")
        except Exception as e:
            logger.error(f"抓取分类项目时出错: {e}")
    
    logger.info(f"找到 {len(categories)} 个顶级分类项目")
    
    # 如果主导航没有分类，尝试其他方式获取
    if len(categories) == 0:
        logger.info("主导航未找到分类，尝试其他方式获取分类")
        
        # 获取顶部菜单中的"SHOP"链接
        shop_link = None
        shop_elements = await page.query_selector_all('a')
        for element in shop_elements:
            try:
                text = await element.text_content()
                if 'SHOP' in text or 'Shop' in text or 'Collection' in text or 'Collections' in text:
                    url = await element.get_attribute('href')
                    if url and '/collections/' in url:
                        shop_link = urljoin(BASE_URL, url)
                        break
            except:
                continue
        
        # 如果找到SHOP链接，获取其中的分类
        if shop_link:
            logger.info(f"找到SHOP链接: {shop_link}")
            await page.goto(shop_link)
            await page.wait_for_load_state('networkidle')
            
            # 获取分类链接
            collection_links = await page.query_selector_all('a')
            for link in collection_links:
                try:
                    href = await link.get_attribute('href')
                    if href and '/collections/' in href and 'products/' not in href:
                        name = await link.text_content()
                        name = name.strip()
                        
                        # 排除商品链接和带有价格标记的链接
                        if '$' in name or len(name) > 50:
                            continue
                            
                        url = urljoin(BASE_URL, href)
                        
                        # 检查是否已添加相同的分类
                        duplicate = False
                        for cat in categories:
                            if cat['name'] == name or cat['url'] == url:
                                duplicate = True
                                break
                                
                        if not duplicate:
                            categories.append({
                                'name': name,
                                'url': url,
                                'parent': None
                            })
                            logger.info(f"找到备用分类: {name} - {url}")
                except Exception as e:
                    # 忽略错误继续
                    pass
    
    logger.info(f"共找到 {len(categories)} 个分类")
    return categories

async def scrape_product_details(page, product_url, category_name, parent_category_name=''):
    """抓取单个商品详情"""
    logger.info(f"正在抓取商品详情: {product_url}")
    
    try:
        await page.goto(product_url, timeout=TIMEOUT)
        await page.wait_for_load_state('networkidle')
        
        # 从schema.org结构化数据中提取商品信息
        schema_data = await page.evaluate("""
            () => {
                const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                for (const script of scripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        if (data['@type'] === 'Product') {
                            return data;
                        }
                    } catch (e) {
                        console.error('Error parsing JSON-LD:', e);
                    }
                }
                return null;
            }
        """)
        
        if not schema_data:
            logger.warning(f"商品 {product_url} 未找到schema.org数据")
            return None
        
        # 提取商品标题
        title = schema_data.get('name', '未知商品')
        
        # 从页面内容获取商品描述，而非schema.org中的描述
        description = await page.evaluate("""
            () => {
                // 尝试查找产品描述容器
                const productDescriptionSelectors = [
                    '.product-single__description',
                    '.product__description',
                    '.product-description',
                    '#product-description',
                    '[id*="product-description"]',
                    '[class*="product-description"]',
                    '.rte',  // 一些Shopify主题使用这个类
                    '.tabs-content [id*="description"]',
                    '.tabs-content [id*="Description"]'
                ];
                
                for (const selector of productDescriptionSelectors) {
                    const el = document.querySelector(selector);
                    if (el && el.textContent.trim()) {
                        // 清理描述，移除多余空白
                        let text = el.innerHTML;
                        return text;
                    }
                }
                
                // 备用方案：尝试查找最可能包含产品描述的元素
                const possibleContainers = [
                    'main',
                    '#MainContent',
                    '.main-content',
                    '.product-template',
                    '.product-single'
                ];
                
                for (const container of possibleContainers) {
                    const el = document.querySelector(container);
                    if (el) {
                        // 在容器中查找描述性段落
                        const paragraphs = el.querySelectorAll('p, .rte p, [id*="description"] p');
                        if (paragraphs.length > 0) {
                            // 组合所有段落，忽略很短的（可能是价格等）
                            let combinedText = "";
                            for (const p of paragraphs) {
                                const text = p.textContent.trim();
                                if (text.length > 20) {  // 忽略太短的段落
                                    combinedText += "<p>" + p.innerHTML + "</p>";
                                }
                            }
                            if (combinedText) {
                                return combinedText;
                            }
                        }
                    }
                }
                
                // 如果上述方法都失败，返回一个空字符串
                return "";
            }
        """)
        
        # 如果从页面无法获取描述，回退到schema.org数据中的描述
        if not description:
            description = schema_data.get('description', '')
            logger.info(f"从schema.org获取商品描述: {description[:100]}...")
        else:
            logger.info(f"从页面内容获取商品描述 (长度: {len(description)})")
        
        # 提取商品SKU
        sku = schema_data.get('sku', '')
        
        # 提取商品品牌
        brand = schema_data.get('brand', '')
        
        # 提取商品价格 (从offers中获取)
        price_myr = 0
        currency = 'USD'
        if 'offers' in schema_data and isinstance(schema_data['offers'], list) and len(schema_data['offers']) > 0:
            offer = schema_data['offers'][0]
            price_myr = float(offer.get('price', 0))
            currency = offer.get('priceCurrency', 'USD')
        
        # 将价格转换为美元
        price_usd = round(price_myr * MYR_TO_USD_RATE, 2) if currency == 'MYR' else price_myr
        
        # 提取商品图片
        images = []
        
        # 获取当前商品URL中的关键部分，用于图片匹配
        product_key = product_url.split('/')[-1].split('?')[0]
        logger.info(f"当前商品关键词: {product_key}")
        
        # 更高效的图片获取逻辑
        try:
            # 1. 首先尝试从产品图库中提取当前商品图片
            js_images = await page.evaluate("""
                (productKey) => {
                    // 获取当前商品的图片
                    const images = [];
                    
                    // 查找主图片和变体图片
                    const productPhotoContainer = document.querySelector('.product__photos');
                    if (productPhotoContainer) {
                        // 获取可见的所有大图URL (主图区域)
                        const mainImgs = productPhotoContainer.querySelectorAll('img.photoswipe__image');
                        mainImgs.forEach(img => {
                            const src = img.src || img.dataset.src || '';
                            if (src) {
                                let highResSrc = src;
                                if (src.includes('width=')) {
                                    highResSrc = src.replace(/width=\\d+/, 'width=2000');
                                }
                                images.push(highResSrc);
                            }
                        });
                    }
                    
                    // 如果没有找到图片，尝试获取缩略图
                    if (images.length === 0) {
                        const thumbContainer = document.querySelector('[id^="ProductThumbs-"]');
                        if (thumbContainer) {
                            const thumbs = thumbContainer.querySelectorAll('li img');
                            thumbs.forEach(img => {
                                const src = img.src || img.dataset.src || '';
                                if (src) {
                                    let highResSrc = src;
                                    if (src.includes('width=')) {
                                        highResSrc = src.replace(/width=\\d+/, 'width=2000');
                                    }
                                    if (src.includes('_compact')) {
                                        highResSrc = src.replace('_compact', '');
                                    }
                                    images.push(highResSrc);
                                }
                            });
                        }
                    }
                    
                    // 如果仍然没有找到图片，从页面上所有图片中过滤
                    if (images.length === 0) {
                        const allImages = Array.from(document.querySelectorAll('img'));
                        // 根据URL中包含商品关键词或alt文本相关来筛选
                        const productImages = allImages.filter(img => {
                            const src = img.src || img.dataset.src || '';
                            const alt = img.alt || '';
                            
                            const matchesProductKey = 
                                productKey && 
                                ((src && src.toLowerCase().includes(productKey.toLowerCase())) || 
                                (alt && alt.toLowerCase().includes(productKey.toLowerCase())));
                                
                            const isProductImage = 
                                (src && src.includes('/products/')) && 
                                !src.includes('related-product') && 
                                !src.includes('recommendation');
                                
                            return matchesProductKey || isProductImage;
                        });
                        
                        productImages.forEach(img => {
                            const src = img.src || img.dataset.src || '';
                            if (src) {
                                let highResSrc = src;
                                if (src.includes('width=')) {
                                    highResSrc = src.replace(/width=\\d+/, 'width=2000');
                                }
                                images.push(highResSrc);
                            }
                        });
                    }
                    
                    return [...new Set(images)]; // 去重
                }
            """, product_key)
            
            if js_images and isinstance(js_images, list):
                for img_url in js_images:
                    if isinstance(img_url, str):
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif not img_url.startswith(('http://', 'https://')):
                            img_url = urljoin(BASE_URL, img_url)
                        
                        if img_url not in images:
                            images.append(img_url)
                            logger.info(f"从产品图库找到图片: {img_url}")
            
            # 2. 如果上述方法没有找到图片，尝试使用ProductThumbs选择器
            if not images:
                logger.info("尝试使用ProductThumbs-ID选择器提取图片")
                thumbs_id = await page.evaluate("""
                    () => {
                        const thumbsEl = document.querySelector('[id^="ProductThumbs-"]');
                        return thumbsEl ? thumbsEl.id : null;
                    }
                """)
                
                if thumbs_id:
                    logger.info(f"找到缩略图容器: {thumbs_id}")
                    thumb_elements = await page.query_selector_all(f"#{thumbs_id} li")
                    logger.info(f"找到 {len(thumb_elements)} 个缩略图元素")
                    
                    for thumb in thumb_elements:
                        img = await thumb.query_selector('img')
                        if img:
                            # 获取缩略图的数据源属性
                            data_src = await img.get_attribute('data-src') or await img.get_attribute('src')
                            if data_src:
                                # 转换缩略图URL为高分辨率图片URL
                                high_res_url = data_src.replace('_compact', '')
                                high_res_url = high_res_url.replace('width=160', 'width=2000')
                                
                                if high_res_url.startswith('//'):
                                    high_res_url = 'https:' + high_res_url
                                elif not high_res_url.startswith(('http://', 'https://')):
                                    high_res_url = urljoin(BASE_URL, high_res_url)
                                
                                if high_res_url not in images:
                                    images.append(high_res_url)
                                    logger.info(f"从ProductThumbs找到图片: {high_res_url}")
        
        except Exception as e:
            logger.warning(f"提取商品图片失败: {e}")
        
        # 3. 如果仍未找到图片，从JSON-LD结构化数据中提取
        if not images and 'image' in schema_data:
            image_data = schema_data['image']
            if isinstance(image_data, list):
                for img in image_data:
                    if isinstance(img, str):
                        images.append(img)
                    elif isinstance(img, dict) and 'url' in img:
                        images.append(img['url'])
            elif isinstance(image_data, str):
                images.append(image_data)
            elif isinstance(image_data, dict) and 'url' in image_data:
                images.append(image_data['url'])
        
        # 去除重复的图片URL并规范化
        clean_images = []
        local_images = []  # 保存本地图片路径
        
        # 为当前商品创建专属文件夹
        product_folder_name = re.sub(r'[^\w\-]', '_', product_key)  # 安全的文件夹名
        product_image_dir = os.path.join(IMAGES_DIR, product_folder_name)
        
        # 确保商品图片目录存在
        Path(product_image_dir).mkdir(exist_ok=True, parents=True)
        logger.info(f"创建商品图片目录: {product_image_dir}")
        
        for img_url in images:
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(BASE_URL, img_url)
            
            # 优化图片URL (去除宽度和不必要的参数)
            parsed_url = urlparse(img_url)
            path = parsed_url.path
            # 只保留v参数，去除width等其他参数
            if parsed_url.query:
                params = parsed_url.query.split('&')
                v_param = next((p for p in params if p.startswith('v=')), None)
                if v_param:
                    img_url = f"https://{parsed_url.netloc}{path}?{v_param}"
                else:
                    img_url = f"https://{parsed_url.netloc}{path}"
            
            # 保存图片到本地
            if img_url not in clean_images:
                clean_images.append(img_url)
                
                # 生成本地文件名
                filename = os.path.basename(path)
                local_path = os.path.join(product_folder_name, filename)  # 使用相对路径，不含IMAGES_DIR
                full_path = os.path.join(product_image_dir, filename)     # 实际保存时使用的完整路径
                
                try:
                    # 下载图片
                    response = requests.get(img_url, stream=True, timeout=30)
                    if response.status_code == 200:
                        with open(full_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        local_images.append(local_path)  # 保存相对路径，用于数据库记录
                        logger.info(f"图片已保存到本地: {full_path}")
                    else:
                        logger.warning(f"下载图片失败: {img_url}, 状态码: {response.status_code}")
                except Exception as e:
                    logger.warning(f"下载图片异常: {img_url}, 错误: {e}")
        
        images = clean_images
        logger.info(f"商品共找到 {len(images)} 张图片, 成功下载 {len(local_images)} 张到本地目录: {product_image_dir}")
        
        # 获取商品库存状态
        in_stock = False
        if 'offers' in schema_data and isinstance(schema_data['offers'], list) and len(schema_data['offers']) > 0:
            offer = schema_data['offers'][0]
            availability = offer.get('availability', '')
            in_stock = 'InStock' in availability
        
        # 创建商品对象
        product = {
            'title': title,
            'url': product_url,
            'price_original': price_myr,  # 原始价格
            'currency_original': currency,  # 原始货币
            'price_usd': price_usd,  # 转换为美元的价格
            'description': description,
            'sku': sku,
            'brand': brand,
            'in_stock': in_stock,
            'main_image': images[0] if images else '',
            'images': images,
            'local_images': local_images,  # 添加本地图片路径
            'category': category_name,
            'parent_category': parent_category_name,
            'scraped_at': datetime.now().isoformat()
        }
        
        logger.info(f"成功抓取商品详情: {title}")
        return product
    
    except Exception as e:
        logger.error(f"抓取商品详情失败: {product_url}, 错误: {e}")
        return None

async def scrape_products_in_category(page, category):
    """抓取单个分类中的所有商品"""
    category_name = category['name']
    category_url = category['url']
    parent_category_name = category.get('parent', '')
    logger.info(f"正在抓取分类 '{category_name}' 中的商品: {category_url}")
    
    products = []
    product_urls = []
    
    try:
        await page.goto(category_url, timeout=TIMEOUT)
        await page.wait_for_load_state('networkidle')
        
        # 修复：使用JavaScript提取所有商品链接，这样更可靠
        product_links = await page.evaluate("""
            () => {
                const links = [];
                
                // 尝试各种可能的选择器组合
                // 先查找所有商品项
                document.querySelectorAll('.grid__item, .grid-product, .product-item, .product-card, .product').forEach(item => {
                    // 在每个商品项中查找链接
                    const link = item.querySelector('a[href*="/products/"]');
                    if (link) {
                        const href = link.getAttribute('href');
                        // 确保链接是完整URL
                        const fullUrl = href.startsWith('/') ? window.location.origin + href : href;
                        links.push(fullUrl);
                    }
                });
                
                // 如果上面的方法没找到链接，尝试直接查找所有商品链接
                if (links.length === 0) {
                    document.querySelectorAll('a.grid-product__link, a.grid-view-item__link, a.product-card__link, a.product-link, a[href*="/products/"]').forEach(link => {
                        const href = link.getAttribute('href');
                        if (href && href.includes('/products/')) {
                            const fullUrl = href.startsWith('/') ? window.location.origin + href : href;
                            links.push(fullUrl);
                        }
                    });
                }
                
                return [...new Set(links)]; // 去重
            }
        """)
        
        logger.info(f"在分类 '{category_name}' 中找到 {len(product_links)} 个商品链接")
        print(f"📊 分类 '{category_name}' 中找到 {len(product_links)} 个商品链接")
        
        # 在测试模式下限制商品数量
        if TEST_MODE and MAX_PRODUCTS_PER_CATEGORY and len(product_links) > MAX_PRODUCTS_PER_CATEGORY:
            product_links = product_links[:MAX_PRODUCTS_PER_CATEGORY]
            logger.info(f"测试模式: 限制为前 {len(product_links)} 个商品")
        
        # 抓取每个商品详情
        for i, url in enumerate(product_links, 1):
            logger.info(f"正在抓取商品 {i}/{len(product_links)}: {url}")
            print(f"⏳ 正在抓取商品 {i}/{len(product_links)}: {url}")
            
            product_info = await scrape_product_details(page, url, category_name, parent_category_name)
            if product_info:
                products.append(product_info)
                logger.info(f"成功抓取商品: {product_info['title']}")
                print(f"  ✓ 成功: {product_info['title']}")
            else:
                logger.warning(f"抓取失败: {url}")
                print(f"  ✗ 失败: {url}")
            
            # 添加短暂延迟，避免请求过快
            await asyncio.sleep(1)
        
        return products
    
    except Exception as e:
        logger.error(f"抓取分类 '{category_name}' 中的商品失败: {e}")
        return []

async def main():
    """主函数: 抓取所有分类及其商品"""
    all_categories = []
    all_products = []
    start_time = datetime.now()
    
    logger.info("=== 开始采集任务 ===")
    logger.info(f"采集目标网站: {BASE_URL}")
    if TEST_MODE:
        logger.info("运行在测试模式，将仅采集有限的商品")
    logger.info(f"浏览器模式: {'无头模式' if HEADLESS_MODE else '可视模式'}")
    
    # 创建进度计数器
    products_counter = 0
    images_counter = 0
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS_MODE)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        # 抓取所有分类
        categories = await scrape_categories(page)
        all_categories = categories
        logger.info(f"共找到 {len(categories)} 个分类")
        print(f"📊 共找到 {len(categories)} 个分类")
        
        # 抓取每个分类中的商品
        for i, category in enumerate(categories, 1):
            logger.info(f"=== 开始采集第 {i}/{len(categories)} 个分类: {category['name']} ===")
            print(f"⏳ 正在采集分类 ({i}/{len(categories)}): {category['name']}")
            
            category_products = await scrape_products_in_category(page, category)
            all_products.extend(category_products)
            
            # 更新计数器
            products_counter += len(category_products)
            images_counter += sum(len(product.get('images', [])) for product in category_products)
            
            logger.info(f"=== 完成第 {i}/{len(categories)} 个分类采集，获取 {len(category_products)} 个商品 ===")
            print(f"✅ 完成分类 {category['name']}: 采集 {len(category_products)} 个商品, 累计 {products_counter} 个商品, {images_counter} 张图片")
            
            # 添加延迟，避免请求过快
            await asyncio.sleep(2)
        
        await browser.close()
    
    # 合并分类和商品数据
    result = {
        'categories': all_categories,
        'products': all_products,
        'total_categories': len(all_categories),
        'total_products': len(all_products),
        'scraped_at': datetime.now().isoformat()
    }
    
    # 保存结果到JSON文件
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== 采集任务完成! ===")
    logger.info(f"共采集 {len(all_categories)} 个分类, {len(all_products)} 个商品, {images_counter} 张图片")
    logger.info(f"耗时: {duration:.2f} 秒 (平均每个商品 {duration/max(1, len(all_products)):.2f} 秒)")
    logger.info(f"采集结果已保存到 {RESULTS_FILE}")
    
    print(f"\n🎉 采集任务完成!")
    print(f"📊 统计信息:")
    print(f"  - 共采集 {len(all_categories)} 个分类")
    print(f"  - 共采集 {len(all_products)} 个商品")
    print(f"  - 共采集 {images_counter} 张图片")
    print(f"  - 耗时: {duration//60} 分 {duration%60:.0f} 秒")
    print(f"  - 采集结果已保存到 {RESULTS_FILE}")
    
    return True

if __name__ == "__main__":
    asyncio.run(main()) 