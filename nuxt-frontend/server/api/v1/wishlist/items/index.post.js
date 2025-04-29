export default defineEventHandler(async (event) => {
  try {
    // 解析请求体
    const body = await readBody(event)
    console.log('添加商品到心愿单请求体:', body)
    
    // 模拟响应
    return {
      code: 0,
      message: 'Success',
      data: {
        id: Math.floor(Math.random() * 10000).toString(),
        wishlist: body.wishlist,
        product_id: body.product_id,
        title: 'Product Title',
        description: body.description || '',
        price: 99.99,
        currency: 'USD',
        image: '/images/product-placeholder.jpg',
        priority: body.priority || 'medium',
        purchased: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('添加商品到心愿单出错:', error)
    
    return {
      code: 500,
      message: '服务器内部错误',
      error: error.message
    }
  }
}) 