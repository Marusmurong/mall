export default defineEventHandler(async (event) => {
  // 模拟分类数据
  const categories = [
    {
      id: 1,
      name: 'Electronics',
      image: '/images/categories/electronics.jpg',
      description: 'Electronic devices and gadgets'
    },
    {
      id: 2,
      name: 'Clothing',
      image: '/images/categories/clothing.jpg',
      description: 'Fashion and apparel'
    },
    {
      id: 3,
      name: 'Home & Garden',
      image: '/images/categories/home.jpg',
      description: 'Products for your home and garden'
    },
    {
      id: 4,
      name: 'Sports',
      image: '/images/categories/sports.jpg',
      description: 'Sports equipment and accessories'
    },
    {
      id: 5,
      name: 'Beauty',
      image: '/images/categories/beauty.jpg',
      description: 'Beauty and personal care products'
    },
    {
      id: 6,
      name: 'Books',
      image: '/images/categories/books.jpg',
      description: 'Books and publications'
    }
  ];
  
  return categories;
});
