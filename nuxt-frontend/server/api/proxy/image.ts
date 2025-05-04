import { defineEventHandler, getQuery, createError, sendRedirect } from 'h3'
import { resolve } from 'path'

// 允许的域名白名单，设置为通配符，允许所有域名（仅用于开发环境）
const ALLOWED_DOMAINS = [
  // 允许所有域名，生产环境应该设置为具体的可信域名列表
  '.*'
]

export default defineEventHandler(async (event) => {
  // 获取URL参数
  const query = getQuery(event)
  const imageUrl = query.url as string

  if (!imageUrl) {
    throw createError({
      statusCode: 400,
      message: '缺少图片URL参数'
    })
  }

  try {
    // 将远程URL转换为本地直接访问URL
    // 例如: http://localhost:8000/media/goods/images/amazon_123.jpg
    // 因为我们现在直接使用本地API，可以直接返回重定向到原始URL
    return sendRedirect(event, imageUrl, 302)
  } catch (error) {
    console.error('图片代理失败:', error)
    throw createError({
      statusCode: 500,
      message: `图片代理失败: ${error.message || '未知错误'}`
    })
  }
}) 