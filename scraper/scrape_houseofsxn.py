#!/usr/bin/env python
"""
采集脚本：从houseofsxn.com网站采集商品信息
采集内容：商品名称、介绍、价格、多张商品图片
"""
import os
import time
import json
import logging
import asyncio
from urllib.parse import urljoin
import requests
from PIL import Image
from io import BytesIO
from playwright.async_api import async_playwright
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 基础配置
BASE_URL = "https://houseofsxn.com"
CATEGORIES = [
    "/collections/fetish-wear",
    "/collections/floggers-whips",
    "/collections/impact",
    "/collections/collars-gags",
    "/collections/restraint-cuff-sets",
    "/collections/hoods-masks-and-blindfolds",
    "/collections/gloves",
    "/collections/leashes-locks-and-accessories",
]

# 测试模式配置
TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() in ('true', '1', 't')
if TEST_MODE:
    logger.info("=== 运行在测试模式 ===")
    # 在测试模式下，只抓取第一个分类的前几个商品
    CATEGORIES = [CATEGORIES[0]]
    MAX_PRODUCTS_PER_CATEGORY = 3  # 每个分类最多抓取的商品数量
    MAX_PAGES = 1  # 最多翻页数
else:
    MAX_PRODUCTS_PER_CATEGORY = None  # 不限制
    MAX_PAGES = 5  # 正常模式下最多翻5页

IMAGE_DIR = "scraped_images"  # 保存图片的目录
RESULTS_FILE = "scraped_products.json"  # 结果JSON文件
TIMEOUT = 60000  # 超时设置(ms)

# 确保图片目录存在
os.makedirs(IMAGE_DIR, exist_ok=True)

# 下载图片并保存到本地
def download_image(url, product_id, index):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # 从URL中获取文件扩展名
            file_ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
            # 创建文件名
            filename = f"{product_id}_{index}{file_ext}"
            file_path = os.path.join(IMAGE_DIR, filename)
            
            # 保存图片
            img = Image.open(BytesIO(response.content))
            img.save(file_path)
            logger.info(f"已保存图片: {file_path}")
            return filename
        else:
            logger.error(f"下载图片失败, 状态码: {response.status_code}, URL: {url}")
            return None
    except Exception as e:
        logger.error(f"下载图片异常: {e}, URL: {url}")
        return None

async def scrape_product_details(page, url):
    """抓取单个商品的详细信息"""
    logger.info(f"正在抓取商品: {url}")
    
    try:
        await page.goto(url, timeout=TIMEOUT)
        await page.wait_for_load_state('networkidle')
        
        # 获取商品标题
        title_element = await page.query_selector('h1.product__title')
        title = await title_element.inner_text() if title_element else "未知商品"
        
        # 生成商品ID (使用标题的简化版本)
        product_id = "".join(c if c.isalnum() else "_" for c in title.lower())
        
        # 获取商品价格
        price_element = await page.query_selector('span.price-item--regular')
        price_text = await price_element.inner_text() if price_element else "$0.00"
        price = price_text.replace('$', '').strip()
        
        # 获取商品描述
        description_element = await page.query_selector('.product__description')
        description = await description_element.inner_text() if description_element else ""
        
        # 获取所有商品图片
        image_elements = await page.query_selector_all('.product-single__media img')
        image_urls = []
        
        for img in image_elements:
            src = await img.get_attribute('src')
            if src:
                # 确保是完整URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif not src.startswith(('http://', 'https://')):
                    src = urljoin(BASE_URL, src)
                image_urls.append(src)
        
        # 下载所有图片
        images = []
        for i, img_url in enumerate(image_urls):
            filename = download_image(img_url, product_id, i)
            if filename:
                images.append(filename)
        
        # 返回完整的商品信息
        return {
            "id": product_id,
            "title": title,
            "price": price,
            "description": description,
            "images": images,
            "source_url": url,
            "scraped_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"抓取商品失败: {url}, 错误: {e}")
        return None

async def scrape_category(page, category_url):
    """抓取单个分类的所有商品"""
    products = []
    full_url = urljoin(BASE_URL, category_url)
    logger.info(f"正在抓取分类: {full_url}")
    
    try:
        await page.goto(full_url, timeout=TIMEOUT)
        await page.wait_for_load_state('networkidle')
        
        # 处理第一页数据
        product_links = await page.query_selector_all('.product-card__link')
        page_products = []
        
        # 获取本页所有商品链接
        for link in product_links:
            href = await link.get_attribute('href')
            if href:
                page_products.append(urljoin(BASE_URL, href))
        
        logger.info(f"在分类 {category_url} 找到 {len(page_products)} 个商品")
        
        # 在测试模式下限制商品数量
        if TEST_MODE and MAX_PRODUCTS_PER_CATEGORY:
            page_products = page_products[:MAX_PRODUCTS_PER_CATEGORY]
            logger.info(f"测试模式: 限制为前 {len(page_products)} 个商品")
        
        # 抓取每个商品的详细信息
        for product_url in page_products:
            product_info = await scrape_product_details(page, product_url)
            if product_info:
                products.append(product_info)
                logger.info(f"成功采集商品: {product_info['title']}")
            # 添加短暂延迟，避免请求过快
            await asyncio.sleep(1)
            
            # 在测试模式下，检查是否已达到最大商品数
            if TEST_MODE and MAX_PRODUCTS_PER_CATEGORY and len(products) >= MAX_PRODUCTS_PER_CATEGORY:
                logger.info(f"测试模式: 已达到最大商品数 {MAX_PRODUCTS_PER_CATEGORY}，停止采集")
                break
        
        # 检查是否需要翻页 - 如果首页商品数量较少，可能有更多页面
        if len(page_products) >= 10 and not TEST_MODE:  # 测试模式不翻页
            logger.info(f"商品数量较多，尝试检查是否有下一页...")
            # 处理翻页 - 根据URL中的page参数来处理
            page_num = 2
            while True:
                # 构建下一页URL
                next_page_url = f"{full_url}?page={page_num}" if "?" not in full_url else f"{full_url}&page={page_num}"
                logger.info(f"尝试翻到第 {page_num} 页: {next_page_url}")
                
                # 导航到下一页
                await page.goto(next_page_url, timeout=TIMEOUT)
                await page.wait_for_load_state('networkidle')
                
                # 检查是否还有商品
                product_links = await page.query_selector_all('.product-card__link')
                
                if not product_links:
                    logger.info(f"没有更多页面，结束翻页")
                    break
                    
                page_products = []
                
                for link in product_links:
                    href = await link.get_attribute('href')
                    if href:
                        page_products.append(urljoin(BASE_URL, href))
                
                logger.info(f"在分类 {category_url} 第 {page_num} 页找到 {len(page_products)} 个商品")
                
                # 如果这一页没有找到商品，可能是最后一页
                if not page_products:
                    break
                    
                # 抓取这一页每个商品的详细信息
                for product_url in page_products:
                    product_info = await scrape_product_details(page, product_url)
                    if product_info:
                        products.append(product_info)
                        logger.info(f"成功采集商品: {product_info['title']}")
                    # 添加短暂延迟，避免请求过快
                    await asyncio.sleep(1)
                    
                    # 在测试模式下，检查是否已达到最大商品数
                    if TEST_MODE and MAX_PRODUCTS_PER_CATEGORY and len(products) >= MAX_PRODUCTS_PER_CATEGORY:
                        logger.info(f"测试模式: 已达到最大商品数 {MAX_PRODUCTS_PER_CATEGORY}，停止采集")
                        break
                
                # 继续下一页
                page_num += 1
                
                # 限制页数，避免无限抓取
                if page_num > MAX_PAGES:
                    logger.info(f"达到最大页数限制({MAX_PAGES}页)，停止翻页")
                    break
                    
                # 在测试模式下，检查是否已达到最大商品数
                if TEST_MODE and MAX_PRODUCTS_PER_CATEGORY and len(products) >= MAX_PRODUCTS_PER_CATEGORY:
                    logger.info(f"测试模式: 已达到最大商品数 {MAX_PRODUCTS_PER_CATEGORY}，停止采集")
                    break
        else:
            logger.info(f"商品数量较少或测试模式，无需检查翻页")
        
        logger.info(f"分类 {category_url} 采集完成，共采集 {len(products)} 个商品")
        return products
    
    except Exception as e:
        logger.error(f"抓取分类失败: {category_url}, 错误: {e}")
        return []

async def main():
    """主函数: 抓取所有分类的所有商品"""
    all_products = []
    start_time = datetime.now()
    
    logger.info("=== 开始采集任务 ===")
    logger.info(f"采集目标网站: {BASE_URL}")
    logger.info(f"计划采集分类数: {len(CATEGORIES)}")
    if TEST_MODE:
        logger.info("运行在测试模式，将仅采集有限的商品")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not TEST_MODE)  # 测试模式下显示浏览器窗口
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        # 抓取每个分类
        for i, category in enumerate(CATEGORIES, 1):
            logger.info(f"=== 开始采集第 {i}/{len(CATEGORIES)} 个分类: {category} ===")
            category_products = await scrape_category(page, category)
            all_products.extend(category_products)
            logger.info(f"=== 完成第 {i}/{len(CATEGORIES)} 个分类采集，获取 {len(category_products)} 个商品 ===")
            # 添加延迟，避免请求过快
            await asyncio.sleep(2)
        
        await browser.close()
    
    # 保存所有商品数据到JSON文件
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=== 采集任务完成! ===")
    logger.info(f"共采集 {len(CATEGORIES)} 个分类, {len(all_products)} 个商品")
    logger.info(f"耗时: {duration:.2f} 秒 (平均每个商品 {duration/max(1, len(all_products)):.2f} 秒)")
    logger.info(f"采集结果已保存到 {RESULTS_FILE}")
    logger.info(f"商品图片已保存到 {IMAGE_DIR} 目录")

if __name__ == "__main__":
    asyncio.run(main()) 