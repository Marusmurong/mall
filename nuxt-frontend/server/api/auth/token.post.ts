import { defineEventHandler, readBody, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  try {
    // 获取请求体和查询参数
    const body = await readBody(event)
    const query = getQuery(event)
    
    // 获取站点名称
    const site = query.site || 'default'
    
    console.log('收到登录请求:', { site, username: body.username })
    
    // 构建请求URL
    const apiUrl = `https://cartitop.com/api/v1/auth/token/`
    
    // 构建请求体
    const requestBody = {
      username: body.username,
      password: body.password,
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
      console.error('登录API错误:', responseData)
      return {
        code: 1,
        message: responseData.detail || '登录失败',
        status: response.status
      }
    }
    
    // 返回成功响应
    return {
      code: 0,
      message: '登录成功',
      data: responseData
    }
  } catch (error) {
    console.error('登录API异常:', error)
    return {
      code: 1,
      message: error.message || '处理登录请求时发生错误',
      error: String(error)
    }
  }
}) 