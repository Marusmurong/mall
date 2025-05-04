// 全局API代理，处理所有API请求
import { defineEventHandler } from 'h3'
import directProxy from './direct-proxy'

export default defineEventHandler(async (event) => {
  // 使用直接代理处理请求
  return directProxy(event);
}); 