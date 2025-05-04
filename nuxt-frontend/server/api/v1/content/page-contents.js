import { defineEventHandler, getRequestURL, createError, readBody } from 'h3';

// 专门处理content页面内容的API代理
export default defineEventHandler(async (event) => {
  const url = getRequestURL(event);
  const method = event.node.req.method;
  const search = url.search || '';
  
  console.log(`[内容API] 收到${method}请求: ${url.pathname}${search}`);
  
  // 构建目标URL - 明确指向Django 8000端口
  const targetUrl = `http://localhost:8000/api/v1/content/page-contents${search}`;
  console.log(`[内容API] 转发到: ${targetUrl}`);
  
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
    console.log(`[内容API] 开始请求: ${targetUrl}`);
    const response = await fetch(targetUrl, fetchOptions);
    console.log(`[内容API] 收到响应: ${response.status} ${response.statusText}`);
    
    // 处理响应
    if (response.ok) {
      // 解析JSON响应
      const data = await response.json();
      console.log(`[内容API] 成功获取数据`);
      return data;
    } else {
      console.error(`[内容API] 错误响应: ${response.status} ${response.statusText}`);
      throw createError({
        statusCode: response.status,
        statusMessage: `Django API错误: ${response.statusText}`,
      });
    }
  } catch (error) {
    console.error(`[内容API] 请求失败: ${error.message}`);
    throw createError({
      statusCode: 500,
      statusMessage: `内容API错误: ${error.message}`,
    });
  }
}); 