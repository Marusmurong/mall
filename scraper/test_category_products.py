#!/usr/bin/env python
"""
测试脚本：调试类目商品采集问题
"""
import asyncio
import logging
from playwright.async_api import async_playwright

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 测试URL
BASE_URL = "https://houseofsxn.com"
TEST_CATEGORY_URL = "https://houseofsxn.com/collections/leather-fetish-wear"

async def test_category_products():
    """测试分类商品采集"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 使用有头模式观察
        page = await browser.new_page(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        logger.info(f"正在加载分类页面: {TEST_CATEGORY_URL}")
        await page.goto(TEST_CATEGORY_URL)
        await page.wait_for_load_state('networkidle')
        
        # 保存截图
        await page.screenshot(path="category_page.png", full_page=True)
        logger.info("已保存页面截图: category_page.png")
        
        # 1. 检查商品项目选择器
        logger.info("测试不同的商品项目选择器...")
        selectors = [
            '.grid__item',
            '.product-item',
            '.product-card',
            '.product',
            '.grid-product',
            '.collection-grid-item',
            '.grid-view-item',
            '.product-grid-item'
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            logger.info(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
        
        # 2. 检查商品链接选择器
        logger.info("\n测试不同的商品链接选择器...")
        link_selectors = [
            'a.grid-product__link',
            'a.grid-view-item__link',
            'a.product-card__link',
            'a.product-link',
            '.grid__item a',
            '.product-item a'
        ]
        
        for selector in link_selectors:
            elements = await page.query_selector_all(selector)
            logger.info(f"链接选择器 '{selector}' 找到 {len(elements)} 个元素")
            
            if elements:
                for i, elem in enumerate(elements[:3]):  # 只显示前3个
                    href = await elem.get_attribute('href')
                    text = await elem.text_content()
                    logger.info(f"  - 链接 {i+1}: href={href}, text={text}")
        
        # 3. 使用JavaScript提取所有商品
        logger.info("\n使用JavaScript提取商品...")
        product_items = await page.evaluate("""
            () => {
                const products = [];
                
                // 尝试各种可能的元素选择器
                document.querySelectorAll('.grid__item, .product-item, .product-card, .product').forEach(item => {
                    const linkElem = item.querySelector('a[href*="/products/"]');
                    if (linkElem) {
                        const href = linkElem.getAttribute('href');
                        const fullUrl = href.startsWith('/') ? window.location.origin + href : href;
                        
                        // 提取价格信息
                        let price = '';
                        const priceElem = item.querySelector('.price, .product-price, .product__price');
                        if (priceElem) {
                            price = priceElem.textContent.trim();
                        }
                        
                        // 提取标题
                        let title = '';
                        const titleElem = item.querySelector('.product-title, .product-name, .product-card__title, .grid-product__title');
                        if (titleElem) {
                            title = titleElem.textContent.trim();
                        } else if (linkElem.title) {
                            title = linkElem.title;
                        }
                        
                        products.push({
                            url: fullUrl,
                            title: title,
                            price: price
                        });
                    }
                });
                
                return products;
            }
        """)
        
        logger.info(f"通过JavaScript找到 {len(product_items)} 个商品")
        for i, product in enumerate(product_items[:10]):  # 只显示前10个
            logger.info(f"  - 商品 {i+1}: {product['title']} - {product['price']} - {product['url']}")
        
        # 4. 提取HTML结构分析
        logger.info("\n提取页面HTML结构进行分析...")
        page_structure = await page.evaluate("""
            () => {
                // 找到可能包含商品的容器元素
                const containers = document.querySelectorAll('.grid, .collection-grid, .product-grid, .collection__products');
                
                const containerInfo = [];
                containers.forEach((container, i) => {
                    const childrenInfo = [];
                    container.childNodes.forEach((child, j) => {
                        if (child.nodeType === 1) { // 元素节点
                            childrenInfo.push({
                                tag: child.tagName,
                                id: child.id,
                                className: child.className,
                                childCount: child.childNodes.length
                            });
                        }
                    });
                    
                    containerInfo.push({
                        index: i,
                        id: container.id,
                        className: container.className,
                        childrenCount: container.childNodes.length,
                        children: childrenInfo.slice(0, 5) // 只返回前5个子元素信息
                    });
                });
                
                return containerInfo;
            }
        """)
        
        logger.info(f"找到 {len(page_structure)} 个可能的商品容器")
        for i, container in enumerate(page_structure):
            logger.info(f"容器 {i+1}: className={container['className']}, 子元素数量={container['childrenCount']}")
            for j, child in enumerate(container['children']):
                logger.info(f"  - 子元素 {j+1}: tag={child['tag']}, className={child['className']}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_category_products()) 