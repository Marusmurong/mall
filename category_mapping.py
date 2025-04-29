"""
亚马逊商品分类与系统分类的映射关系
用于导入脚本自动分配商品到正确的分类
"""

# 分类映射配置
# 格式: "亚马逊分类": ["顶级分类", "二级分类", "三级分类(可选)"]
CATEGORY_MAPPING = {
    # 情绪疗愈类目
    "刻字马克杯": ["Home Life", "Mugs & Cups", "Coffee Mugs"],
    "照片水晶球": ["Gifts & Decor", "Home Decor", "Figurines"],
    "泡澡球礼盒": ["Home Life", "Bathroom", "Bath Accessories"],
    "香氛蜡烛": ["Gifts & Decor", "Home Decor", "Candles"],
    "按摩器": ["Home Life", "Bathroom", "Bath Accessories"],
    
    # 居家便利类目
    "烘焙模具": ["Home Life", "Kitchen", "Bakeware"],
    "空气炸锅": ["Home Life", "Kitchen", "Cookware"],
    "定制砧板": ["Home Life", "Kitchen", "Kitchen Tools"],
    "香薰机": ["Gifts & Decor", "Home Decor"],
    
    # 仪式感礼物类目
    "定制名字项链": ["Fashion", "Accessories", "Jewelry"],
    "女性香水": ["Fashion", "Accessories"],
    "花束礼盒（永生花）": ["Gifts & Decor", "Home Decor"],
    "巧克力礼盒": ["Gifts & Decor", "Personalized Gifts"],
    "蛋糕礼物": ["Gifts & Decor", "Personalized Gifts"],
    "零食礼物包": ["Gifts & Decor", "Personalized Gifts"],
    "香氛护理包": ["Gifts & Decor", "Personalized Gifts"],
    
    # 亲子情感礼物类
    "母女手链": ["Fashion", "Accessories", "Jewelry"],
    "智能手表": ["Electronics", "Mobile Accessories"],
    "Kindle 阅读器": ["Electronics", "Computers", "Accessories"],
    "励志书籍": ["Gifts & Decor", "Personalized Gifts"],
    "家庭关系书": ["Gifts & Decor", "Personalized Gifts"],
    "女童芭比娃娃": ["Gifts & Decor", "Personalized Gifts"],
    "女童手工DIY": ["Gifts & Decor", "Personalized Gifts"],
    "STEM科学玩具": ["Gifts & Decor", "Personalized Gifts"],
    "女童生日礼盒": ["Gifts & Decor", "Personalized Gifts"],
    "女童画画套装": ["Gifts & Decor", "Personalized Gifts"],
    
    # 情趣/孤独补偿类
    "家居睡衣": ["Home Life", "Bedding"],
    "瑜伽运动套装": ["Fashion", "Women's Clothing", "Tops"],
    "塑形内衣": ["Fashion", "Women's Clothing"],
    "情趣按摩器": ["Fashion", "Accessories"],
    "情趣浪漫香氛油": ["Gifts & Decor", "Home Decor"],
    "女性性感内衣": ["Fashion", "Women's Clothing"],
    "女性自慰情趣玩具": ["Fashion", "Accessories"],
    
    # 电子消费类
    "手机及配件": ["Electronics", "Mobile Accessories"],
    "电脑及配件": ["Electronics", "Computers", "Accessories"],
    "礼品卡": ["Gifts & Decor", "Personalized Gifts"],
}

# 批次文件映射 - 可以根据文件名前缀指定默认分类
BATCH_MAPPING = {
    # 文件名前缀: ["顶级分类", "二级分类", "三级分类(可选)"]
    "mugs_": ["Home Life", "Mugs & Cups", "Coffee Mugs"],
    "jewelry_": ["Fashion", "Accessories", "Jewelry"],
    "kitchen_": ["Home Life", "Kitchen"],
    "electronics_": ["Electronics"],
    "gift_": ["Gifts & Decor", "Personalized Gifts"],
    "beauty_": ["Fashion", "Accessories"],
    "home_": ["Home Life"],
    "intimate_": ["Fashion", "Women's Clothing"],
    # 添加批次85的映射
    "85": ["Fashion", "Accessories", "Jewelry"],
}

# 关键词映射 - 根据商品标题中的关键词匹配分类
KEYWORD_MAPPING = {
    # 关键词: ["顶级分类", "二级分类", "三级分类(可选)"]
    # 母女手链相关关键词
    "mom and daughter": ["Fashion", "Accessories", "Jewelry"],
    "mother daughter": ["Fashion", "Accessories", "Jewelry"],
    "mom daughter": ["Fashion", "Accessories", "Jewelry"],
    "infinity heart": ["Fashion", "Accessories", "Jewelry"],
    "bracelet": ["Fashion", "Accessories", "Jewelry"],
    "bracelets": ["Fashion", "Accessories", "Jewelry"],
    "mama": ["Fashion", "Accessories", "Jewelry"],
    
    # 智能手表相关关键词
    "smart watch": ["Electronics", "Mobile Accessories"],
    "smartwatch": ["Electronics", "Mobile Accessories"],
    "watch": ["Electronics", "Mobile Accessories"],
    "fitness tracker": ["Electronics", "Mobile Accessories"],
    "fitpolo": ["Electronics", "Mobile Accessories"],
    "alexa": ["Electronics", "Mobile Accessories"],
    
    # 其他常见商品关键词
    "mug": ["Home Life", "Mugs & Cups", "Coffee Mugs"],
    "cup": ["Home Life", "Mugs & Cups"],
    "necklace": ["Fashion", "Accessories", "Jewelry"],
    "pendant": ["Fashion", "Accessories", "Jewelry"],
    "kindle": ["Electronics", "Computers", "Accessories"],
    "candle": ["Gifts & Decor", "Home Decor", "Candles"],
    "massage": ["Home Life", "Bathroom", "Bath Accessories"],
    "baking": ["Home Life", "Kitchen", "Bakeware"],
    "fryer": ["Home Life", "Kitchen", "Cookware"],
    "lingerie": ["Fashion", "Women's Clothing"],
    "yoga": ["Fashion", "Women's Clothing", "Tops"],
    "phone": ["Electronics", "Mobile Accessories"],
    "computer": ["Electronics", "Computers"],
    "laptop": ["Electronics", "Computers", "Laptops"],
    "toy": ["Gifts & Decor", "Personalized Gifts"],
    "doll": ["Gifts & Decor", "Personalized Gifts"],
    "chocolate": ["Gifts & Decor", "Personalized Gifts"],
    "gift": ["Gifts & Decor", "Personalized Gifts"],
    "flower": ["Gifts & Decor", "Home Decor"],
    "book": ["Gifts & Decor", "Personalized Gifts"],
}

def get_category_by_name(category_name):
    """
    根据亚马逊分类名称获取系统分类
    """
    return CATEGORY_MAPPING.get(category_name, ["Home Life"])

def get_category_by_batch(batch_filename):
    """
    根据批次文件名获取系统分类
    """
    # 先尝试精确匹配
    for prefix, category in BATCH_MAPPING.items():
        if batch_filename.startswith(prefix):
            return category

    # 尝试提取批次号
    import re
    match = re.search(r'batch_(\d+)', batch_filename)
    if match:
        batch_num = match.group(1)
        if batch_num in BATCH_MAPPING:
            return BATCH_MAPPING[batch_num]

    return ["Home Life"]

def get_category_by_keywords(product_title):
    """
    根据商品标题中的关键词获取系统分类
    """
    if not product_title:
        return ["Home Life"]
        
    title_lower = product_title.lower()
    
    # 按优先级检查关键词
    for keyword, category in KEYWORD_MAPPING.items():
        if keyword.lower() in title_lower:
            return category
    
    # 默认分类
    return ["Home Life"]

def determine_category(product_title, category_name=None, batch_filename=None):
    """
    根据多种因素综合判断商品应该属于哪个分类
    优先级: 显式分类名称 > 标题关键词 > 批次文件名 > 默认分类
    
    Args:
        product_title: 商品标题
        category_name: 亚马逊分类名称
        batch_filename: 批次文件名
    
    Returns:
        list: [顶级分类, 二级分类, 三级分类(可选)]
    """
    # 优先使用显式分类名称
    if category_name and category_name in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[category_name]
    
    # 其次使用标题关键词
    if product_title:
        keyword_category = get_category_by_keywords(product_title)
        if keyword_category and keyword_category[0] != "Home Life":  # 如果不是默认分类
            return keyword_category
    
    # 然后尝试批次文件名
    if batch_filename:
        batch_category = get_category_by_batch(batch_filename)
        if batch_category:
            return batch_category
    
    # 最后使用默认分类
    return ["Home Life"] 