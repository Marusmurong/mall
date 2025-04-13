#!/usr/bin/env python
"""
调试脚本：检查网站结构
"""
import os
import asyncio
from playwright.async_api import async_playwright

# 要检查的URL
TARGET_URL = "https://houseofsxn.com/collections/fetish-wear"

async def main():
    """主函数：检查网站结构"""
    print(f"正在检查网站: {TARGET_URL}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器窗口以观察
        page = await browser.new_page()
        
        # 访问目标网站
        await page.goto(TARGET_URL)
        await page.wait_for_load_state('networkidle')
        
        # 保存页面HTML
        html_content = await page.content()
        with open("page_content.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"页面HTML已保存到: page_content.html")
        
        # 查找商品链接
        print("\n检查商品链接选择器:")
        
        # 尝试不同的选择器
        selectors = [
            '.product-card__link',
            '.grid-product__link',
            'a[href*="/products/"]',
            '.product-item a',
            '.product a'
        ]
        
        for selector in selectors:
            elements = await page.query_selector_all(selector)
            print(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
            
            # 如果找到元素，打印前3个元素的href属性
            if elements:
                print("  前几个链接:")
                for i, element in enumerate(elements[:3]):
                    href = await element.get_attribute('href')
                    print(f"  {i+1}. {href}")
        
        # 尝试获取页面上所有链接
        all_links = await page.query_selector_all('a')
        product_links = []
        
        print(f"\n页面上共有 {len(all_links)} 个链接")
        print("检查包含'/products/'的链接:")
        
        for link in all_links:
            href = await link.get_attribute('href')
            if href and '/products/' in href:
                product_links.append(href)
        
        print(f"找到 {len(product_links)} 个可能的商品链接")
        for i, link in enumerate(product_links[:5]):
            print(f"{i+1}. {link}")
        
        # 截图
        await page.screenshot(path="page_screenshot.png")
        print("页面截图已保存到: page_screenshot.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())