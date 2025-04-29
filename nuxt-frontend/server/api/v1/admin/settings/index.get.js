export default defineEventHandler(async (event) => {
  // 在实际应用中，这里应该从数据库或配置文件中获取管理员设置
  // 现在我们返回一些模拟数据
  return {
    code: 0,
    message: 'Success',
    data: {
      site: {
        name: 'Multi-site E-commerce System',
        logo: '/images/logo.png',
        favicon: '/favicon.ico',
        description: 'Multi-site E-commerce System - Based on Nuxt 3 and Tailwind CSS',
        keywords: 'e-commerce, online shop, multi-site',
        copyright: '© 2025 Multi-site E-commerce System',
        contactEmail: 'support@mall.com',
        contactPhone: '400-123-4567',
        address: '123 E-commerce Street, Tech City'
      },
      homepage: {
        carousel: [
          {
            id: '1',
            title: 'Welcome to Our Online Store',
            subtitle: 'Discover amazing products with great prices',
            buttonText: 'Shop Now',
            buttonLink: '/products',
            backgroundColor: 'bg-gradient-to-r from-blue-700 to-indigo-900',
            backgroundImage: '/images/hero-1.jpg',
            active: true,
            order: 1
          },
          {
            id: '2',
            title: 'Summer Collection',
            subtitle: 'Explore our new arrivals for the season',
            buttonText: 'View Collection',
            buttonLink: '/products?new=true',
            backgroundColor: 'bg-gradient-to-r from-orange-500 to-pink-600',
            backgroundImage: '/images/hero-2.jpg',
            active: true,
            order: 2
          },
          {
            id: '3',
            title: 'Special Offers',
            subtitle: 'Limited time discounts on selected items',
            buttonText: 'See Offers',
            buttonLink: '/products?discount=true',
            backgroundColor: 'bg-gradient-to-r from-green-600 to-teal-500',
            backgroundImage: '/images/hero-3.jpg',
            active: false,
            order: 3
          }
        ],
        featuredCategories: 6, // 首页显示的分类数量
        recommendedProductsCount: 8, // 推荐产品显示数量
        newProductsCount: 8 // 新产品显示数量
      },
      features: {
        wishlist: true,
        reviews: true,
        comparison: false,
        recentlyViewed: true
      },
      currency: {
        default: 'USD',
        symbol: '$',
        position: 'before', // 'before' 或 'after'
        showCode: false, // 是否显示货币代码，如 USD
        decimals: 2 // 小数位数
      },
      pagination: {
        productsPerPage: 20,
        categoriesPerPage: 20
      }
    }
  }
})
