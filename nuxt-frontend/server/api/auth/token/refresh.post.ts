import { defineEventHandler, readBody, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  try {
    // 获取请求体和查询参数
    const body = await readBody(event)
    const query = getQuery(event)
    
    // 获取站点名称
    const site = query.site || 'default'
    
    console.log('收到刷新令牌请求:', { site })
    
    // 构建请求URL
    const apiUrl = `https://cartitop.com/api/v1/auth/token/refresh/`
    
    // 构建请求体
    const requestBody = {
      refresh: body.refresh,
      site
    }
    
    // 发送请求到实际API
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    // 获取响应数据
    const responseData = await response.json()
    
    // 检查响应状态
    if (!response.ok) {
      console.error('刷新令牌API错误:', responseData)
      return {
        code: 1,
        message: responseData.detail || '刷新令牌失败',
        status: response.status
      }
    }
    
    // 返回成功响应
    return {
      code: 0,
      message: '刷新令牌成功',
      data: responseData
    }
  } catch (error) {
    console.error('刷新令牌API异常:', error)
    return {
      code: 1,
      message: error.message || '处理刷新令牌请求时发生错误',
      error: String(error)
    }
  }
}) 