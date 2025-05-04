/**
 * 图片URL处理工具
 * 统一处理图片URL格式，修复重复域名等问题
 */
export function useImageUrl() {
  const baseUrl = 'http://localhost:8000'
  
  /**
   * 格式化图片URL，确保URL格式正确
   * @param url 原始图片URL
   * @returns 格式化后的URL
   */
  const formatImageUrl = (url: string): string => {
    // 如果URL为空，返回空字符串而不是占位图
    if (!url) {
      return ''
    }
    
    // 修复重复域名问题
    if (url.includes(`${baseUrl}/${baseUrl}`)) {
      url = url.replace(`${baseUrl}/${baseUrl}`, baseUrl)
    }
    if (url.includes(`${baseUrl}${baseUrl}`)) {
      url = url.replace(`${baseUrl}${baseUrl}`, baseUrl)
    }
    
    // 处理各种URL格式
    if (url.startsWith('http://localhost') || url.startsWith('https://localhost')) {
      // 本地URL直接返回
      return url
    }
    
    if (url.startsWith('/media/')) {
      // 相对URL添加域名
      return `${baseUrl}${url}`
    }
    
    if (url.includes('media/') && !url.startsWith('/')) {
      // 没有前导斜杠的相对URL
      return `${baseUrl}/${url}`
    }
    
    if (url.startsWith('http')) {
      // 远程URL通过代理加载
      return `/api/proxy/image?url=${encodeURIComponent(url)}`
    }
    
    // 其他情况直接返回
    return url
  }
  
  return {
    formatImageUrl
  }
} 