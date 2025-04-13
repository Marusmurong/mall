#!/usr/bin/env python
"""
一键运行脚本：执行采集和导入过程
"""
import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scrape_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 将项目根目录添加到Python路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def print_header(text):
    """打印美观的标题头"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80 + "\n")

def ask_yes_no(question):
    """询问用户是/否问题"""
    while True:
        response = input(f"{question} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("请输入 'y' 或 'n'.")

async def run_scraper(test_mode=False, headless=True):
    """运行采集脚本"""
    print_header("开始采集商品数据")
    
    # 设置测试模式环境变量
    if test_mode:
        os.environ['TEST_MODE'] = 'True'
        logger.info("启用测试模式 - 每个分类将只采集少量商品")
    else:
        os.environ['TEST_MODE'] = 'False'
        logger.info("启用完整采集模式 - 将采集所有分类和商品")
    
    # 设置无头模式环境变量
    os.environ['HEADLESS_MODE'] = 'True' if headless else 'False'
    logger.info(f"浏览器采集模式: {'无头模式' if headless else '可视模式'}")
    
    try:
        # 导入采集脚本
        from scraper.scrape_direct import main as scraper_main
        
        # 运行采集
        logger.info("开始运行采集脚本...")
        await scraper_main()
        
        return True
    except Exception as e:
        logger.error(f"采集过程中出错: {e}")
        return False

def run_import():
    """运行导入脚本"""
    print_header("开始导入数据到数据库")
    
    try:
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mall.settings')
        import django
        django.setup()
        
        # 导入导入脚本
        from scraper.import_categories_products import import_data
        
        # 检查采集的数据文件
        from scraper.scrape_direct import RESULTS_FILE
        
        if not os.path.exists(RESULTS_FILE):
            logger.error(f"采集数据文件不存在: {RESULTS_FILE}")
            return False
        
        # 加载采集的数据
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        # 运行导入
        logger.info("开始导入数据...")
        import_data(scraped_data)
        
        return True
    except Exception as e:
        logger.error(f"导入过程中出错: {e}")
        return False

async def main():
    """主函数：交互式运行采集和导入过程"""
    print_header("商品采集与导入系统")
    print("这个脚本将帮助你完成从网站采集商品数据并导入到数据库的过程。\n")
    
    # 询问测试模式
    test_mode = ask_yes_no("是否使用测试模式运行? (测试模式下只采集少量商品)")
    
    # 询问无头模式
    headless = ask_yes_no("是否使用无头模式运行? (无头模式下不会显示浏览器窗口)")
    
    # 运行采集
    scrape_success = await run_scraper(test_mode, headless)
    if not scrape_success:
        print("\n❌ 采集过程出错，请检查日志文件获取详细信息。")
        return
    
    print("\n✅ 采集完成!")
    
    # 显示采集结果统计
    try:
        # 从文件加载采集的数据
        from scraper.scrape_direct import RESULTS_FILE
        
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
                
            categories_count = len(scraped_data.get('categories', []))
            products_count = len(scraped_data.get('products', []))
            
            print("\n📊 采集统计:")
            print(f"  - 总计采集了 {categories_count} 个商品类目")
            print(f"  - 总计采集了 {products_count} 个商品")
            
            # 统计每个类目的商品数量
            category_stats = {}
            for product in scraped_data.get('products', []):
                category = product.get('category', '未分类')
                category_stats[category] = category_stats.get(category, 0) + 1
            
            print("\n📊 各类目商品数量:")
            for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {category}: {count} 个商品")
                
            # 统计图片数量
            total_images = sum(len(product.get('images', [])) for product in scraped_data.get('products', []))
            print(f"\n📊 总计采集了 {total_images} 张商品图片")
    except Exception as e:
        logger.error(f"统计采集结果时出错: {e}")
    
    # 询问是否继续导入
    if ask_yes_no("\n是否将采集的数据导入到数据库?"):
        import_success = run_import()
        if import_success:
            print("\n✅ 导入完成! 数据已成功导入到数据库。")
        else:
            print("\n❌ 导入过程出错，请检查日志文件获取详细信息。")
    else:
        print("\n⏹️ 已跳过导入步骤。采集的数据已保存到JSON文件。")
    
    print("\n感谢使用商品采集与导入系统!")

if __name__ == "__main__":
    asyncio.run(main()) 