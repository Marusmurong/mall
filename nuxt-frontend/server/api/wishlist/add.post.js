export default defineEventHandler(async (event) => {
  try {
    // 解析请求体
    const body = await readBody(event)
    
    console.log('添加到心愿单请求:', body)
    
    // 获取当前用户信息（如果有）
    // 这里模拟用户已登录
    const mockUserId = 1
    
    // 检查必要参数
    if (!body.product_id) {
      return {
        statusCode: 400,
        success: false,
        message: 'Product ID is required'
      }
    }
    
    // 模拟返回成功响应
    return {
      statusCode: 200,
      success: true,
      message: 'Product added to wishlist successfully',
      data: {
        id: Math.floor(Math.random() * 1000), // 随机生成的心愿单项目ID
        product_id: body.product_id,
        user_id: mockUserId,
        created_at: new Date().toISOString()
      }
    }
  } catch (error) {
    console.error('添加到心愿单错误:', error)
    
    // 返回错误响应
    return {
      statusCode: 500,
      success: false,
      message: 'Failed to add product to wishlist',
      error: error.message
    }
  }
}) 