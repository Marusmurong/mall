#!/usr/bin/env python
"""
测试脚本：运行采集和导入
"""
import os
import sys
import logging
import asyncio
import subprocess
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_scrape.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 采集脚本
SCRAPER_SCRIPT = os.path.join(BASE_DIR, "scraper", "scrape_houseofsxn.py")
# 导入脚本
IMPORT_SCRIPT = os.path.join(BASE_DIR, "scraper", "test_import_products.py")

def main():
    """主函数: 运行测试采集和导入"""
    try:
        logger.info("=== 开始测试采集和导入流程 ===")
        
        # 检查脚本是否存在
        if not os.path.exists(SCRAPER_SCRIPT):
            logger.error(f"采集脚本不存在: {SCRAPER_SCRIPT}")
            return
        
        if not os.path.exists(IMPORT_SCRIPT):
            logger.error(f"导入脚本不存在: {IMPORT_SCRIPT}")
            return
        
        # 运行采集脚本 - 只采集一个分类作为测试
        logger.info("=== 开始测试采集 ===")
        
        # 修改采集脚本的CATEGORIES变量，仅采集一个分类
        # 这里简化处理，通过环境变量传递测试标志
        env = os.environ.copy()
        env['TEST_MODE'] = 'True'  # 在采集脚本中可以检测这个环境变量来限制采集范围
        
        # 运行采集脚本
        result = subprocess.run([sys.executable, SCRAPER_SCRIPT], 
                                env=env, 
                                capture_output=True, 
                                text=True)
        
        if result.returncode == 0:
            logger.info("采集脚本运行成功")
            logger.info(f"采集脚本输出: {result.stdout}")
        else:
            logger.error(f"采集脚本运行失败: {result.stderr}")
            return
        
        # 运行导入脚本
        logger.info("=== 开始测试导入 ===")
        result = subprocess.run([sys.executable, IMPORT_SCRIPT], 
                                capture_output=True, 
                                text=True)
        
        if result.returncode == 0:
            logger.info("导入脚本运行成功")
            logger.info(f"导入脚本输出: {result.stdout}")
        else:
            logger.error(f"导入脚本运行失败: {result.stderr}")
            return
        
        logger.info("=== 测试采集和导入流程完成 ===")
    
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    main() 