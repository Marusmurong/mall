import { defineEventHandler, getRequestURL, createError } from 'h3';

// 专门处理热门产品API的代理
export default defineEventHandler(async (event) => {
  const url = getRequestURL(event);
  const method = event.node.req.method;
  
  console.log(`[热门产品API] 收到${method}请求: ${url.pathname}${url.search || ''}`);
  
  // 构建目标URL - 明确指向Django 8000端口
  const targetUrl = `http://localhost:8000/api/v1/products/hot/${url.search || ''}`;
  console.log(`[热门产品API] 转发到: ${targetUrl}`);
  
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
    
    // 构造fetch选项
    const fetchOptions = {
      method,
      headers,
      redirect: 'follow',
    };
    
    // 发送请求到Django
    console.log(`[热门产品API] 开始请求Django服务器(8000端口): ${targetUrl}`);
    const response = await fetch(targetUrl, fetchOptions);
    console.log(`[热门产品API] 收到响应: ${response.status} ${response.statusText}`);
    
    // 处理响应
    if (response.ok) {
      // 解析JSON响应
      const data = await response.json();
      console.log(`[热门产品API] 成功获取数据`);
      return data;
    } else {
      console.error(`[热门产品API] 错误响应: ${response.status} ${response.statusText}`);
      throw createError({
        statusCode: response.status,
        statusMessage: `Django API错误: ${response.statusText}`,
      });
    }
  } catch (error) {
    console.error(`[热门产品API] 请求失败: ${error.message}`);
    throw createError({
      statusCode: 500,
      statusMessage: `热门产品API错误: ${error.message}`,
    });
  }
}); 