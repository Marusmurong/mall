#!/usr/bin/env python
"""
从DrHarness网站获取商品描述并更新到数据库（同步版本）
"""
import os
import sys
import logging
import json
import django
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

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
TEST_MODE = os.environ.get('TEST_MODE', 'false').lower() == 'true'
MAX_PRODUCTS = int(os.environ.get('MAX_PRODUCTS', '0')) if os.environ.get('MAX_PRODUCTS') else None
BASE_URL = "https://drharness.co"

# 用户代理，防止被网站屏蔽
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

def get_product_description(url):
    """获取商品描述（同步版本）"""
    try:
        logger.info(f"正在访问商品页面: {url}")
        
        # 发送HTTP请求获取页面内容
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()  # 如果请求失败，抛出异常
        
        # 解析HTML内容
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. 尝试常见的商品描述容器
        desc_selectors = [
            '.product-single__description', '.product-description', '#product-description',
            '.product-single__content-text', '[itemprop="description"]', '.product__description',
            '.product-content', '.product-detail__description', '.product-detail-text'
        ]
        
        for selector in desc_selectors:
            desc_element = soup.select_one(selector)
            if desc_element and len(desc_element.text.strip()) > 20:
                return str(desc_element)
        
        # 2. 如果找不到明确的描述容器，尝试查找商品内容区域的所有段落
        product_content_selectors = [
            '.product-single__content', '.product-content', '.product-detail',
            '.product-container', '.product-main', '#shopify-section-product'
        ]
        
        for selector in product_content_selectors:
            product_content = soup.select_one(selector)
            if product_content:
                paragraphs = product_content.find_all('p')
                desc_paragraphs = []
                
                for p in paragraphs:
                    text = p.text.strip()
                    # 忽略太短的段落和明显不是描述的段落（如配送、退款说明等）
                    if len(text) > 20 and 'shipping' not in text.lower() and 'refund' not in text.lower() and 'return' not in text.lower():
                        desc_paragraphs.append(str(p))
                
                if desc_paragraphs:
                    return ''.join(desc_paragraphs)
        
        # 3. 最后的备选方案：尝试从页面中找出所有类似描述的内容
        description_classes = ['rte', 'description', 'desc']
        for cls in description_classes:
            elements = soup.find_all(class_=lambda c: c and cls in c.lower())
            if elements:
                desc_texts = []
                for el in elements:
                    # 忽略页脚和页眉中的元素
                    if not el.find_parent('footer') and not el.find_parent('header'):
                        desc_texts.append(str(el))
                if desc_texts:
                    return ''.join(desc_texts)
        
        # 4. 尝试查找所有较长的段落
        content_paragraphs = soup.find_all('p')
        if content_paragraphs:
            desc_texts = []
            for p in content_paragraphs:
                text = p.text.strip()
                if len(text) > 50 and not p.find_parent('footer') and not p.find_parent('header'):
                    if 'shipping' not in text.lower() and 'refund' not in text.lower() and 'return' not in text.lower():
                        desc_texts.append(str(p))
            if desc_texts:
                return ''.join(desc_texts)
        
        logger.warning(f"无法找到商品描述: {url}")
        return ""
    except Exception as e:
        logger.error(f"获取商品描述失败: {url}, 错误: {e}")
        return ""

def update_product_descriptions():
    """更新商品描述"""
    # 获取需要更新描述的商品
    products = Goods.objects.filter(
        source_url__contains='drharness.co'
    ).order_by('id')
    
    logger.info(f"找到 {products.count()} 个DrHarness商品")
    
    # 如果为空，检查是否有描述为空的商品
    if not products.exists():
        logger.warning("没有找到任何DrHarness商品")
        return 0
    
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
            if not product.source_url:
                logger.warning(f"商品 '{product.name}' 没有源URL，跳过")
                continue
                
            description = get_product_description(product.source_url)
            
            if description:
                # 清理HTML内容
                try:
                    soup = BeautifulSoup(description, 'html.parser')
                    # 移除脚本和样式
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    # 保留有用的HTML标签，但清理掉不必要的属性
                    for tag in soup.find_all(True):
                        allowed_attrs = ['href', 'src', 'alt']
                        for attr in list(tag.attrs):
                            if attr not in allowed_attrs:
                                del tag[attr]
                    clean_description = str(soup)
                except Exception as e:
                    logger.error(f"清理商品 '{product.name}' 的描述HTML时出错: {e}")
                    clean_description = description
                
                # 更新商品描述
                product.description = clean_description
                product.goods_desc = clean_description
                product.save(update_fields=['description', 'goods_desc'])
                logger.info(f"成功更新商品 '{product.name}' 的描述")
                descriptions_updated += 1
            else:
                logger.warning(f"无法获取商品 '{product.name}' 的描述")
        except Exception as e:
            logger.error(f"更新商品 '{product.name}' 描述失败: {e}")
    
    logger.info(f"完成描述更新，共更新了 {descriptions_updated}/{products.count()} 个商品的描述")
    return descriptions_updated

def main():
    """主函数"""
    logger.info("=== 开始更新DrHarness商品描述 ===")
    updated_count = update_product_descriptions()
    logger.info(f"=== 完成更新 {updated_count} 个商品描述 ===")

if __name__ == "__main__":
    main() 