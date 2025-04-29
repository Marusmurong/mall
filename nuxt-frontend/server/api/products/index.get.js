export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const page = parseInt(query.page) || 1;
  const limit = parseInt(query.limit) || 28;
  const offset = (page - 1) * limit;
  
  // 真实商品数据
  const products = [
    {
      id: 1,
      name: "MacBook Pro 14-inch",
      description: "Apple M3 Pro chip with 11‑core CPU, 14‑core GPU, 18GB unified memory, 512GB SSD",
      price: 1999.00,
      image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
      category: { id: 1, name: "Laptops" },
      rating: 4.8,
      reviews_count: 128,
      is_in_stock: true,
      is_new: true,
      is_hot: true,
      discount_price: null,
      original_price: 1999.00,
      created_at: "2025-04-20T00:00:00Z",
      sales: 256
    },
    {
      id: 2,
      name: "iPhone 15 Pro",
      description: "6.1-inch display, A17 Pro chip, 256GB storage, Titanium design",
      price: 1099.00,
      image: "https://images.unsplash.com/photo-1592750475338-74b7b21a0193?w=800&q=80",
      category: { id: 2, name: "Smartphones" },
      rating: 4.9,
      reviews_count: 256,
      is_in_stock: true,
      is_new: true,
      is_hot: true,
      discount_price: 999.00,
      original_price: 1099.00,
      created_at: "2025-04-15T00:00:00Z",
      sales: 512
    },
    {
      id: 3,
      name: "Sony WH-1000XM5",
      description: "Wireless noise cancelling headphones with up to 30-hour battery life",
      price: 399.00,
      image: "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=800&q=80",
      category: { id: 3, name: "Audio" },
      rating: 4.7,
      reviews_count: 89,
      is_in_stock: true,
      is_new: false,
      is_hot: true,
      discount_price: 349.00,
      original_price: 399.00,
      created_at: "2025-03-01T00:00:00Z",
      sales: 178
    },
    {
      id: 4,
      name: "iPad Air",
      description: "10.9-inch Liquid Retina display, M1 chip, 256GB storage",
      price: 749.00,
      image: "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=800&q=80",
      category: { id: 4, name: "Tablets" },
      rating: 4.6,
      reviews_count: 67,
      is_in_stock: true,
      is_new: false,
      is_hot: false,
      discount_price: null,
      original_price: 749.00,
      created_at: "2025-02-15T00:00:00Z",
      sales: 145
    },
    {
      id: 5,
      name: "Samsung 49\" Odyssey G9",
      description: "49-inch QLED Gaming Monitor, 240Hz, 1000R Curved Screen",
      price: 1299.00,
      image: "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&q=80",
      category: { id: 5, name: "Monitors" },
      rating: 4.5,
      reviews_count: 45,
      is_in_stock: true,
      is_new: true,
      is_hot: false,
      discount_price: 1199.00,
      original_price: 1299.00,
      created_at: "2025-04-10T00:00:00Z",
      sales: 89
    },
    {
      id: 6,
      name: "DJI Air 3",
      description: "4K/60fps HDR Video, 3-Axis Gimbal, 46 Minutes Flight Time",
      price: 1099.00,
      image: "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800&q=80",
      category: { id: 6, name: "Drones" },
      rating: 4.4,
      reviews_count: 34,
      is_in_stock: true,
      is_new: true,
      is_hot: false,
      discount_price: null,
      original_price: 1099.00,
      created_at: "2025-04-05T00:00:00Z",
      sales: 67
    },
    {
      id: 7,
      name: "Canon EOS R5",
      description: "45MP Full-Frame Mirrorless Camera, 8K Video Recording",
      price: 3899.00,
      image: "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=800&q=80",
      category: { id: 7, name: "Cameras" },
      rating: 4.8,
      reviews_count: 56,
      is_in_stock: true,
      is_new: false,
      is_hot: true,
      discount_price: 3599.00,
      original_price: 3899.00,
      created_at: "2025-03-20T00:00:00Z",
      sales: 112
    },
    {
      id: 8,
      name: "Nintendo Switch OLED",
      description: "7-inch OLED screen, Enhanced Audio, 64GB Storage",
      price: 349.00,
      image: "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=800&q=80",
      category: { id: 8, name: "Gaming" },
      rating: 4.7,
      reviews_count: 89,
      is_in_stock: true,
      is_new: false,
      is_hot: true,
      discount_price: 329.00,
      original_price: 349.00,
      created_at: "2025-02-28T00:00:00Z",
      sales: 234
    }
  ];

  // 根据查询参数过滤商品
  let filteredProducts = [...products];
  
  // 分类过滤
  if (query.category) {
    filteredProducts = filteredProducts.filter(p => p.category.id === parseInt(query.category));
  }

  // 返回分页数据
  const totalCount = filteredProducts.length;
  const results = filteredProducts.slice(offset, offset + limit);
  
  return {
    total: totalCount,
    page,
    limit,
    total_pages: Math.ceil(totalCount / limit),
    results
  };
});