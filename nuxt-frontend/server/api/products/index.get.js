export default defineEventHandler(async (event) => {
  // 获取URL参数
  const query = getQuery(event);
  const page = parseInt(query.page) || 1;
  const pageSize = parseInt(query.limit) || 40; // 默认每页40个产品
  const offset = (page - 1) * pageSize;
  
  // 获取筛选参数
  const minPrice = query.min_price ? parseFloat(query.min_price) : null;
  const maxPrice = query.max_price ? parseFloat(query.max_price) : null;
  const isNew = query.is_new === 'true';
  const isHot = query.is_hot === 'true';
  const isDiscount = query.is_discount === 'true';
  const sort = query.sort || null;
  const categoryId = query.category || null;
  
  // 创建模拟数据 - 为了演示，创建2000个产品
  const generateProducts = () => {
    return Array.from({ length: 2000 }, (_, i) => {
      const categoryId = Math.floor(Math.random() * 10) + 1;
      return {
        id: i + 1,
        name: `Product ${i + 1}`,
        description: `This is product ${i + 1}.`,
        price: Math.floor(Math.random() * 10000) / 100,
        image: `https://images.unsplash.com/photo-${1570000000000 + i * 1000}?w=500&q=80`,
        category: { id: categoryId, name: `Category ${categoryId}` },
        categories: [{ id: categoryId, name: `Category ${categoryId}` }],
        rating: (Math.random() * 5).toFixed(1),
        reviews_count: Math.floor(Math.random() * 100),
        is_in_stock: Math.random() > 0.2,
        is_new: i < 200,
        is_hot: i % 3 === 0,
        discount_price: i % 5 === 0 ? (Math.floor(Math.random() * 10000) / 100) * 0.8 : null,
        original_price: i % 5 === 0 ? Math.floor(Math.random() * 10000) / 100 : null,
        created_at: new Date(Date.now() - i * 86400000).toISOString(),
        sales: Math.floor(Math.random() * 1000)
      };
    });
  };
  
  // 生成所有商品
  let allProducts = generateProducts();
  
  // 应用筛选条件
  if (categoryId) {
    allProducts = allProducts.filter(product => 
      product.category.id === parseInt(categoryId) || 
      product.categories.some(cat => cat.id === parseInt(categoryId))
    );
  }
  
  if (minPrice !== null) {
    allProducts = allProducts.filter(product => {
      const price = product.discount_price || product.price;
      return price >= minPrice;
    });
  }
  
  if (maxPrice !== null) {
    allProducts = allProducts.filter(product => {
      const price = product.discount_price || product.price;
      return price <= maxPrice;
    });
  }
  
  if (isNew) {
    allProducts = allProducts.filter(product => product.is_new);
  }
  
  if (isHot) {
    allProducts = allProducts.filter(product => product.is_hot);
  }
  
  if (isDiscount) {
    allProducts = allProducts.filter(product => product.discount_price !== null);
  }
  
  // 应用排序
  if (sort) {
    switch (sort) {
      case 'price_asc':
        allProducts.sort((a, b) => {
          const priceA = a.discount_price || a.price;
          const priceB = b.discount_price || b.price;
          return priceA - priceB;
        });
        break;
      case 'price_desc':
        allProducts.sort((a, b) => {
          const priceA = a.discount_price || a.price;
          const priceB = b.discount_price || b.price;
          return priceB - priceA;
        });
        break;
      case 'newest':
        allProducts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
      case 'sales':
        allProducts.sort((a, b) => b.sales - a.sales);
        break;
    }
  }
  
  // 分页处理
  const totalCount = allProducts.length;
  const results = allProducts.slice(offset, offset + pageSize);
  
  // 生成上一页和下一页链接
  const baseUrl = `http://0.0.0.0:8000/api/v1/products/`;
  const buildUrl = (p) => `${baseUrl}?page=${p}&limit=${pageSize}`;
  
  // 返回响应
  return {
    code: 0,
    message: "success",
    data: {
      count: totalCount,
      next: page * pageSize < totalCount ? buildUrl(page + 1) : null,
      previous: page > 1 ? buildUrl(page - 1) : null,
      results: results
    }
  };
}); 