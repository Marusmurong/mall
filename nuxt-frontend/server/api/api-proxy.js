import { defineEventHandler, getRequestURL, readBody, createError } from 'h3';

// 通用API代理 - 将所有请求转发到Django后端
export default defineEventHandler(async (event) => {
  const url = getRequestURL(event);
  const method = event.node.req.method;
  const path = url.pathname;
  const search = url.search || '';
  
  // 只处理/api/开头的请求
  if (!path.startsWith('/api/')) {
    return; // 非API请求不处理
  }
  
  console.log(`[API代理] 收到${method}请求: ${path}${search}`);
  
  // 构建目标URL - 指向Django 8000端口
  let targetPath = path;
  
  // 处理非v1路径
  if (!path.includes('/v1/') && path.startsWith('/api/')) {
    targetPath = path.replace('/api/', '/api/v1/');
  }
  
  const targetUrl = `http://localhost:8000${targetPath}${search}`;
  console.log(`[API代理] 转发到Django: ${targetUrl}`);
  
  try {
    // 准备请求头
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
    const fetchOptions = {
      method,
      headers,
      redirect: 'follow',
    };
    
    if (body) {
      fetchOptions.body = typeof body === 'string' ? body : JSON.stringify(body);
    }
    
    // 发送请求到Django
    console.log(`[API代理] 开始请求: ${targetUrl}`);
    const response = await fetch(targetUrl, fetchOptions);
    console.log(`[API代理] 请求完成，状态: ${response.status} ${response.statusText}`);
    
    // 设置响应状态
    event.node.res.statusCode = response.status;
    
    // 复制响应头
    for (const [key, value] of response.headers.entries()) {
      event.node.res.setHeader(key, value);
    }
    
    // 处理响应体
    if (response.ok) {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const responseData = await response.json();
        console.log(`[API代理] 返回JSON数据`);
        return responseData;
      } else {
        const responseText = await response.text();
        console.log(`[API代理] 返回文本数据 (长度: ${responseText.length})`);
        return responseText;
      }
    } else {
      console.error(`[API代理] 错误响应: ${response.status} ${response.statusText}`);
      // 返回错误响应
      throw createError({
        statusCode: response.status,
        statusMessage: response.statusText,
        data: await response.text()
      });
    }
  } catch (error) {
    console.error(`[API代理] 错误: ${error.message}`);
    console.error(error.stack);
    throw createError({
      statusCode: 500,
      statusMessage: `API代理错误: ${error.message}`
    });
  }
}); 