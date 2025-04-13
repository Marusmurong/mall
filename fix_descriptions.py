#!/usr/bin/env python
import os
import sys
import json
import logging
from pathlib import Path
import django

# 设置Django环境
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
django.setup()

from goods.models import Goods
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_descriptions.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 配置
DATA_FILE = "drharness_all_products.json"

def fix_descriptions():
    """修复商品描述"""
    # 加载原始数据
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        logger.info(f"从文件加载了 {len(products_data)} 个商品数据")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"无法加载商品数据: {e}")
        return

    # 统计信息
    descriptions_updated = 0
    descriptions_missing = 0
    products_not_found = 0

    # 遍历所有商品数据
    for product_data in products_data:
        title = product_data.get('title', '')
        description = product_data.get('description', '')
        source_url = product_data.get('url', '')
        
        if not title:
            logger.warning(f"跳过没有标题的商品")
            continue

        # 清理HTML中的不必要标签
        if description:
            try:
                soup = BeautifulSoup(description, 'html.parser')
                # 移除脚本和样式
                for script in soup(["script", "style"]):
                    script.extract()
                # 保留有用的HTML标签，但清理掉不必要的属性
                for tag in soup.find_all(True):
                    allowed_attrs = ['href', 'src', 'alt']
                    for attr in list(tag.attrs):
                        if attr not in allowed_attrs:
                            del tag[attr]
                description = str(soup)
            except Exception as e:
                logger.error(f"清理商品 '{title}' 的描述HTML时出错: {e}")

        # 查找对应的商品并更新描述
        try:
            # 首先尝试通过URL查找
            if source_url:
                goods = Goods.objects.filter(source_url=source_url).first()
            else:
                goods = None

            # 如果找不到，尝试通过标题查找
            if not goods:
                goods = Goods.objects.filter(name=title).first()

            if goods:
                if description:
                    # 更新描述字段
                    goods.description = description
                    goods.goods_desc = description
                    goods.save(update_fields=['description', 'goods_desc'])
                    logger.info(f"更新了商品 '{title}' 的描述")
                    descriptions_updated += 1
                else:
                    logger.warning(f"商品 '{title}' 没有描述信息")
                    descriptions_missing += 1
            else:
                logger.warning(f"找不到匹配的商品: '{title}'")
                products_not_found += 1
        except Exception as e:
            logger.error(f"更新商品 '{title}' 的描述时出错: {e}")

    # 打印统计信息
    logger.info(f"==== 商品描述更新完成 ====")
    logger.info(f"- 更新商品描述: {descriptions_updated}")
    logger.info(f"- 缺少描述的商品: {descriptions_missing}")
    logger.info(f"- 找不到的商品: {products_not_found}")

def main():
    """主函数"""
    logger.info("=== 开始修复商品描述 ===")
    fix_descriptions()
    logger.info("=== 商品描述修复完成 ===")

if __name__ == "__main__":
    main() 