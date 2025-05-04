import { defineEventHandler, getRequestURL, readBody, sendError, createError } from 'h3';

export default defineEventHandler(async (event) => {
  const url = getRequestURL(event);
  const method = event.node.req.method;
  const path = url.pathname;
  const search = url.search || '';
  
  // 只处理API请求
  if (!path.startsWith('/api/')) {
    return;
  }
  
  // 日志记录
  console.log(`[直接代理] 收到${method}请求: ${path}${search}`);
  
  // 始终添加v1前缀
  let targetPath = path;
  if (!path.includes('/api/v1/') && path.startsWith('/api/')) {
    targetPath = path.replace('/api/', '/api/v1/');
  }
  
  // 构建目标URL - 确保指向端口8000
  const targetUrl = `http://localhost:8000${targetPath}${search}`;
  console.log(`[直接代理] 转发到Django(8000端口): ${targetUrl}`);
  
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
    console.log(`[直接代理] 开始请求: ${targetUrl}`);
    const response = await fetch(targetUrl, fetchOptions);
    console.log(`[直接代理] 请求完成，状态: ${response.status} ${response.statusText}`);
    
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
        console.log(`[直接代理] 返回JSON数据`);
        return responseData;
      } else {
        const responseText = await response.text();
        console.log(`[直接代理] 返回文本数据 (长度: ${responseText.length})`);
        return responseText;
      }
    } else {
      console.error(`[直接代理] 错误响应: ${response.status} ${response.statusText}`);
      // 返回错误响应
      return {
        statusCode: response.status,
        statusMessage: response.statusText,
        error: await response.text()
      };
    }
  } catch (error) {
    console.error(`[直接代理] 错误: ${error.message}`);
    console.error(error.stack);
    return sendError(event, createError({
      statusCode: 500,
      statusMessage: `代理错误: ${error.message}`
    }));
  }
}); 