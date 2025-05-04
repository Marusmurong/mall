import os
import json
from pathlib import Path
from googletrans import Translator

def extract_and_translate_categories_in_dir(data_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    all_category_types = set()
    all_category_names = set()
    json_files = list(Path(data_dir).glob('*.json'))
    # 第一次遍历所有文件，收集所有分类
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        products = data.get('products') if isinstance(data, dict) else data
        if products is None:
            products = []
        for product in products:
            if 'category_type' in product:
                all_category_types.add(product['category_type'])
            if 'category_name' in product:
                all_category_names.add(product['category_name'])
    print('所有顶级分类:')
    for t in sorted(all_category_types):
        print(t)
    print('\n所有二级分类:')
    for n in sorted(all_category_names):
        print(n)
    # 翻译
    translator = Translator()
    type_map = {t: translator.translate(t, src='zh-cn', dest='en').text.strip() for t in all_category_types}
    name_map = {n: translator.translate(n, src='zh-cn', dest='en').text.strip() for n in all_category_names}
    print('\n顶级分类中英文映射:')
    for zh, en in type_map.items():
        print(f'{zh} -> {en}')
    print('\n二级分类中英文映射:')
    for zh, en in name_map.items():
        print(f'{zh} -> {en}')
    # 第二次遍历所有文件，替换并输出新文件
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        products = data.get('products') if isinstance(data, dict) else data
        if products is None:
            products = []
        for product in products:
            if 'category_type' in product:
                product['category_type'] = type_map.get(product['category_type'], product['category_type'])
            if 'category_name' in product:
                product['category_name'] = name_map.get(product['category_name'], product['category_name'])
        # 写回
        if isinstance(data, dict) and 'products' in data:
            data['products'] = products
        elif isinstance(data, list):
            data = products
        out_path = Path(output_dir) / json_file.name.replace('.json', '_en.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"已生成: {out_path}")

if __name__ == '__main__':
    DATA_DIR = '/Users/jimmu/mall/scraped_data/amazon'
    OUTPUT_DIR = '/Users/jimmu/mall/scraped_data/amazon_en'
    extract_and_translate_categories_in_dir(DATA_DIR, OUTPUT_DIR)
