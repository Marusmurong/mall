import { defineEventHandler, getRequestURL, readBody, createError } from 'h3'

export default defineEventHandler(async (event) => {
  const url = getRequestURL(event);
  const method = event.node.req.method;
  
  console.log(`[全局API代理] 收到${method}请求: ${url.pathname}`);
  
  // 修改目标URL逻辑
  let targetPath = url.pathname;
  
  // 添加v1前缀，如果路径不包含v1
  if (!targetPath.includes('/api/v1/') && targetPath.startsWith('/api/')) {
    targetPath = targetPath.replace('/api/', '/api/v1/');
  }
  
  console.log(`[全局API代理] 转发路径: ${targetPath}`);
  
  const targetUrl = `http://localhost:8000${targetPath}${url.search || ''}`;
  console.log(`[全局API代理] 转发到Django: ${targetUrl}`);
  
  try {
    // 复制请求头
    const headerEntries = Object.entries(event.node.req.headers)
      .filter(([key]) => !['host', 'connection'].includes(key.toLowerCase()));
    
    // 创建Headers对象
    const headers = new Headers();
    for (const [key, value] of headerEntries) {
      if (value !== undefined) {
        headers.append(key, Array.isArray(value) ? value.join(', ') : value);
      }
    }
    
    // 获取请求体
    const body = method !== 'GET' && method !== 'HEAD' 
      ? await readBody(event).catch(() => null) 
      : null;
    
    // 构造fetch选项
    const fetchOptions: RequestInit = {
      method,
      headers,
      redirect: 'follow',
    };
    
    if (body) {
      fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
    }
    
    // 发送请求到Django
    const response = await fetch(targetUrl, fetchOptions);
    console.log(`[全局API代理] 请求完成，状态: ${response.status}`);
    
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
    } else {
      responseData = await response.text();
    }
    
    return responseData;
  } catch (error) {
    console.error(`[全局API代理] 错误: ${error.message}`);
    console.error(error.stack);
    throw createError({
      statusCode: 500,
      statusMessage: `API代理错误: ${error.message}`,
    });
  }
}); 