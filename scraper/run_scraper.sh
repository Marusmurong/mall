#!/bin/bash
# 运行商品采集和导入流程

# 确保脚本退出时清理
trap 'echo "脚本被中断"; exit 1' INT TERM

# 设置工作目录
cd "$(dirname "$0")"

# 创建日志目录
mkdir -p logs

# 设置时间变量用于日志文件名
timestamp=$(date +"%Y%m%d_%H%M%S")
log_file="logs/scrape_${timestamp}.log"

echo "=== 开始采集商品数据 ($(date)) ===" | tee -a "$log_file"

# 检查是否已安装所需的Python依赖
if ! pip list | grep -q "playwright"; then
    echo "正在安装Playwright..." | tee -a "$log_file"
    pip install playwright | tee -a "$log_file"
    playwright install | tee -a "$log_file"
fi

if ! pip list | grep -q "pillow"; then
    echo "正在安装Pillow..." | tee -a "$log_file"
    pip install pillow | tee -a "$log_file"
fi

# 运行采集脚本
echo "正在运行采集脚本..." | tee -a "$log_file"
python scrape_houseofsxn.py | tee -a "$log_file"

# 检查采集脚本是否成功
if [ $? -ne 0 ]; then
    echo "采集脚本执行失败，终止流程。" | tee -a "$log_file"
    exit 1
fi

# 运行导入脚本
echo "" | tee -a "$log_file"
echo "=== 开始导入商品数据 ($(date)) ===" | tee -a "$log_file"
python import_products.py | tee -a "$log_file"

# 检查导入脚本是否成功
if [ $? -ne 0 ]; then
    echo "导入脚本执行失败。" | tee -a "$log_file"
    exit 1
fi

echo "" | tee -a "$log_file"
echo "=== 采集和导入流程完成 ($(date)) ===" | tee -a "$log_file"
echo "完整日志请查看: $log_file"

# 备份已采集的数据
backup_dir="backup_${timestamp}"
mkdir -p "$backup_dir"
cp scraped_products.json "$backup_dir/"
cp -r scraped_images "$backup_dir/"

echo "数据已备份到: $backup_dir" | tee -a "$log_file" 