import { defineEventHandler, proxyRequest } from 'h3'

export default defineEventHandler(async (event) => {
  const path = event.path || ''
  
  // 代理所有API请求到外部API
  if (path.startsWith('/api/')) {
    console.log('代理API请求到cartitop.com:', path)
    return proxyRequest(event, 'https://cartitop.com')
  }
}) 