export default defineEventHandler(async (event) => {
  // 模拟商品数据
  const products = Array.from({ length: 20 }, (_, i) => ({
    id: i + 1,
    name: `Product ${i + 1}`,
    description: `This is a description for product ${i + 1}`,
    price: Math.floor(Math.random() * 10000) / 100,
    image: `/images/products/product-${(i % 6) + 1}.jpg`,
    category: {
      id: Math.floor(Math.random() * 5) + 1,
      name: `Category ${Math.floor(Math.random() * 5) + 1}`
    },
    rating: (Math.random() * 5).toFixed(1),
    reviews_count: Math.floor(Math.random() * 100),
    is_in_stock: Math.random() > 0.2,
    discount_percentage: Math.random() > 0.7 ? Math.floor(Math.random() * 30) + 10 : 0
  }));

  // 获取查询参数
  const query = getQuery(event);
  const limit = parseInt(query.limit) || 10;
  
  // 根据查询参数过滤商品
  let filteredProducts = [...products];
  
  if (query.recommended === 'true') {
    // 模拟推荐商品逻辑
    filteredProducts = filteredProducts.filter(p => p.rating > 4);
  }
  
  if (query.new === 'true') {
    // 模拟新品逻辑
    filteredProducts = filteredProducts.sort(() => Math.random() - 0.5).slice(0, limit);
  }
  
  // 限制返回数量
  const results = filteredProducts.slice(0, limit);
  
  return {
    count: filteredProducts.length,
    results: results
  };
});
