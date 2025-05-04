// 全局API代理，处理所有API请求
import { defineEventHandler, getRequestURL, readBody, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const url = getRequestURL(event);
  const method = event.node.req.method;
  
  console.log(`[API代理] 收到${method}请求: ${url.pathname}`);
  
  // 只代理API请求
  if (url.pathname.startsWith('/api/')) {
    // 修改目标URL逻辑，确保正确路径映射
    let targetPath = url.pathname;
    
    // 调试: 显示原始路径
    console.log(`[API代理] 原始请求路径: ${targetPath}`);
    
    // 修正API路径，确保有v1版本
    // 确保所有/api/前缀的路径都被映射到/api/v1/
    if (!targetPath.includes('/api/v1/') && targetPath.startsWith('/api/')) {
      targetPath = targetPath.replace('/api/', '/api/v1/');
    }
    
    // 调试: 显示修正后的路径
    console.log(`[API代理] 修正后路径: ${targetPath}`);
    
    const targetUrl = `http://localhost:8000${targetPath}${url.search || ''}`;
    console.log(`[API代理] 转发到Django: ${targetUrl}`);
    
    try {
      // 显示请求头
      console.log(`[API代理] 请求头:`, event.node.req.headers);
      
      // 复制请求头
      const headers = Object.fromEntries(Object.entries(event.node.req.headers)
        .filter(([key]) => !['host', 'connection'].includes(key.toLowerCase())));
      
      // 获取请求体
      const body = method !== 'GET' && method !== 'HEAD' 
        ? await readBody(event).catch(() => null) 
        : null;
      
      // 如果有请求体，显示
      if (body) {
        console.log(`[API代理] 请求体:`, body);
      }
      
      // 构造fetch选项
      const fetchOptions = {
        method,
        headers,
        redirect: 'follow',
      };
      
      if (body) {
        fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
      }
      
      // 显示完整请求选项
      console.log(`[API代理] 请求选项:`, {
        method: fetchOptions.method,
        headers: fetchOptions.headers,
        hasBody: !!fetchOptions.body
      });
      
      // 发送请求到本地Django
      console.log(`[API代理] 开始请求 ${targetUrl}`);
      const response = await fetch(targetUrl, fetchOptions);
      console.log(`[API代理] 请求完成，状态: ${response.status}`);
      
      // 调试响应
      console.log(`[API代理] 收到响应状态: ${response.status} ${response.statusText}`);
      console.log(`[API代理] 响应头:`, Object.fromEntries([...response.headers.entries()]));
      
      // 设置响应状态
      event.node.res.statusCode = response.status;
      
      // 复制响应头
      for (const [key, value] of response.headers.entries()) {
        event.node.res.setHeader(key, value);
      }
      
      // 处理响应体
      let responseData;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
        console.log(`[API代理] 响应JSON数据:`, responseData);
      } else {
        responseData = await response.text();
        console.log(`[API代理] 响应文本数据 (前100字符):`, responseData.substring(0, 100));
      }
      
      return responseData;
    } catch (error) {
      console.error(`[API代理] 错误: ${error.message}`);
      console.error(error.stack);
      throw createError({
        statusCode: 500,
        statusMessage: `API代理错误: ${error.message}`,
      });
    }
  }
  
  // 非API请求，让后续处理器处理
  return;
}); 