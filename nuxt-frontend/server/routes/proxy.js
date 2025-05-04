// 创建图片代理中间件，用于加载远程图片
export default defineEventHandler(async (event) => {
  const query = getQuery(event);
  const url = query.url;
  
  if (!url) {
    throw createError({
      statusCode: 400,
      statusMessage: '缺少url参数',
    });
  }
  
  console.log(`[图片代理] 代理请求: ${url}`);
  
  try {
    // 发送请求到目标URL
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
      },
    });
    
    if (!response.ok) {
      throw new Error(`图片请求失败: ${response.status} ${response.statusText}`);
    }
    
    // 获取内容类型
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('image')) {
      throw new Error(`返回的不是图片: ${contentType}`);
    }
    
    // 设置响应头
    event.node.res.setHeader('Content-Type', contentType);
    event.node.res.setHeader('Cache-Control', 'public, max-age=86400');
    
    // 获取并返回图片数据
    const buffer = await response.arrayBuffer();
    return Buffer.from(buffer);
  } catch (error) {
    console.error(`[图片代理] 错误: ${error.message}`);
    throw createError({
      statusCode: 500,
      statusMessage: `图片代理错误: ${error.message}`,
    });
  }
}); 