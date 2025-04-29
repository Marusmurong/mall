export default defineEventHandler(async (event) => {
  try {
    // 模拟响应
    return {
      code: 0,
      message: 'Success',
      data: [
        {
          id: '1',
          name: 'My First Wishlist',
          description: 'This is a default wishlist',
          is_public: true,
          share_code: 'abc123',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          items: []
        }
      ]
    }
  } catch (error) {
    console.error('获取心愿单列表出错:', error)
    
    return {
      code: 500,
      message: '服务器内部错误',
      error: error.message
    }
  }
}) 