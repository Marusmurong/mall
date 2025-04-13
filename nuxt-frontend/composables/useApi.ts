import { $fetch, FetchOptions } from 'ofetch'
import type { RuntimeConfig } from 'nuxt/schema'

// 声明全局类型，让TypeScript识别这些组合式API
declare global {
  const useRuntimeConfig: () => RuntimeConfig
  const useCookie: any
}

export const useApi = () => {
  // 获取运行时配置
  const config = useRuntimeConfig()
  const { apiBase, currentSite } = config.public as {
    apiBase: string
    authBase: string
    currentSite: string
  }
  
  // 创建带有基本配置的fetch实例
  const apiFetch = $fetch.create({
    baseURL: apiBase,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    credentials: 'include',
  })
  
  // 通用请求方法
  const request = async (endpoint: string, options: FetchOptions = {}) => {
    try {
      // 添加站点标识到URL参数
      let urlStr = endpoint;
      if (!urlStr.includes('?')) {
        urlStr += `?site=${currentSite}`;
      } else {
        urlStr += `&site=${currentSite}`;
      }
      
      // 构建完整URL
      if (!urlStr.startsWith('http')) {
        urlStr = `${apiBase}${urlStr}`;
      }
      
      console.log('API Request to:', urlStr);
      console.log('API Base URL:', apiBase);
      console.log('Runtime Config:', config.public);
      
      // 获取认证token (如果有)
      // 首先从localStorage获取token
      let token: string | null = null;
      if (typeof window !== 'undefined') {
        token = localStorage.getItem('token');
      }
      
      // 如果localStorage中没有，尝试从cookie获取
      if (!token) {
        const tokenCookie = useCookie('auth_token');
        token = tokenCookie.value;
      }
      
      console.log('使用的认证令牌:', token);
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers as HeadersInit
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // 准备请求选项
      const fetchOptions: RequestInit = {
        method: options.method || 'GET',
        headers,
        credentials: 'include'
      };
      
      // 如果有请求体，添加到选项中
      if (options.body) {
        fetchOptions.body = JSON.stringify(options.body);
      }
      
      // 发送请求
      console.log('Fetch options:', fetchOptions);
      const response = await fetch(urlStr, fetchOptions);
      
      // 检查响应状态
      if (!response.ok) {
        console.error(`API Error: ${response.status} ${response.statusText}`);
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      const responseText = await response.text();
      console.log(`API Response from ${urlStr}:`, responseText);
      
      // 如果响应为空，返回空对象
      if (!responseText.trim()) {
        return {};
      }
      
      // 解析响应
      try {
        const data = JSON.parse(responseText);
        
        // 处理不同的API响应格式
        if (data.code !== undefined) {
          // 处理 {code, message, data} 格式
          if (data.code === 0) {
            return data.data || {};
          } else {
            console.error('API Error:', data.message);
            throw new Error(data.message || 'API request failed');
          }
        } else {
          // 直接返回数据
          return data;
        }
      } catch (parseError) {
        console.error('Failed to parse API response:', parseError);
        // 如果无法解析为JSON，返回原始文本
        return responseText;
      }
    } catch (error) {
      console.error('API请求错误:', error);
      throw error;
    }
  }
  
  // 各种API方法
  return {
    // 分类相关API
    categories: {
      // 获取所有分类
      getAll: () => request('/v1/categories/'),
      // 获取分类树
      getTree: () => request('/v1/categories/tree/'),
      // 获取分类详情
      getById: (id: string) => request(`/v1/categories/${id}/`),
      // 获取分类下的商品
      getProducts: (id: string) => request(`/v1/categories/${id}/products/`)
    },
    
    // 商品相关API
    products: {
      // 获取商品列表
      getAll: (params = {}) => request('/v1/products/', { params }),
      // 获取商品详情
      getById: (id: string) => request(`/v1/products/${id}/`),
      // 获取推荐商品
      getRecommended: () => request('/v1/products/recommended/'),
      // 获取热门商品
      getHot: () => request('/v1/products/hot/'),
      // 获取新品
      getNew: () => request('/v1/products/new/'),
      // 搜索商品
      search: (keyword: string) => request('/v1/products/', { params: { keyword } })
    },
    
    // 心愿单相关API
    wishlist: {
      // 获取用户的所有心愿单
      getUserWishlists: () => request('/v1/wishlist/lists/'),
      // 获取当前用户的默认心愿单
      getCurrent: () => request('/v1/wishlist/lists/current/'),
      // 获取指定心愿单详情
      getById: (id: string) => request(`/v1/wishlist/lists/${id}/`),
      // 通过分享码获取心愿单
      getByShareCode: (shareCode: string) => request(`/v1/wishlist/lists/share/${shareCode}/`),
      // 获取公开的心愿单列表
      getPublic: () => request('/v1/wishlist/lists/list_public/'),
      // 创建心愿单
      create: (data: any) => request('/v1/wishlist/lists/', { method: 'POST', body: data }),
      // 更新心愿单
      update: (id: string, data: any) => request(`/v1/wishlist/lists/${id}/`, { method: 'PATCH', body: data }),
      // 删除心愿单
      delete: (id: string) => request(`/v1/wishlist/lists/${id}/`, { method: 'DELETE' }),
      // 添加商品到心愿单
      addItem: (data: any) => request('/v1/wishlist/items/', { method: 'POST', body: data }),
      // 更新心愿单商品
      updateItem: (id: string, data: any) => request(`/v1/wishlist/items/${id}/`, { method: 'PATCH', body: data }),
      // 删除心愿单商品
      removeItem: (id: string) => request(`/v1/wishlist/items/${id}/`, { method: 'DELETE' }),
      // 标记商品为已购买
      purchaseItem: (id: string) => request(`/v1/wishlist/items/${id}/purchase/`, { method: 'POST' }),
      // 记录心愿单浏览量
      recordView: (id: string) => request(`/v1/wishlist/lists/${id}/view/`, { method: 'POST' }),
      // 获取心愿单统计数据
      getStats: (id: string) => request(`/v1/wishlist/lists/${id}/stats/`),
      // 获取所有心愿单的汇总统计数据
      getAllStats: () => request('/v1/wishlist/stats/'),
      // 获取心愿单分享链接
      getShareLink: (id: string) => request(`/v1/wishlist/lists/${id}/share-link/`),
      // 检查商品是否已在心愿单中
      checkProductInWishlist: (productId: string) => request(`/v1/wishlist/check-product/${productId}/`),
      // 获取用户的心愿单商品列表
      getUserItems: () => request('/v1/wishlist/user-items/')
    },
    
    // 用户认证相关API
    auth: {
      // 登录
      login: async (credentials: { username: string, password: string }) => {
        // 添加站点标识符到URL参数
        const urlStr = `${config.public.authBase}/token/?site=${currentSite}`
        
        console.log('Sending login request to:', urlStr)
        console.log('With credentials:', credentials)
        
        try {
          // 使用FormData格式发送请求
          const formData = new FormData()
          formData.append('username', credentials.username)
          formData.append('password', credentials.password)
          formData.append('site', currentSite)
          
          const response = await fetch(urlStr, {
            method: 'POST',
            credentials: 'include',
            body: formData
          })
          
          const responseText = await response.text()
          console.log('Login API response:', responseText)
          
          try {
            const data = JSON.parse(responseText)
            // 处理API响应格式
            if (data.code === 0 && data.data) {
              return data.data
            } else {
              throw new Error(data.message || 'Login failed')
            }
          } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError)
            throw new Error('Invalid response format')
          }
        } catch (fetchError) {
          console.error('Fetch error:', fetchError)
          throw fetchError
        }
      },
      // 刷新token
      refreshToken: async (refreshToken: string) => {
        // 添加站点标识符到URL参数
        const urlStr = `${config.public.authBase}/token/refresh/?site=${currentSite}`
        
        try {
          // 按照测试页面的格式构造请求体
          const formData = new FormData()
          formData.append('refresh', refreshToken)
          
          // 发送请求
          const response = await fetch(urlStr, {
            method: 'POST',
            credentials: 'include',
            body: formData
          })
          
          const responseText = await response.text()
          console.log('Token refresh API response:', responseText)
          
          try {
            const data = JSON.parse(responseText)
            // 处理API响应格式
            if (data.code === 0 && data.data) {
              return data.data
            } else {
              throw new Error(data.message || 'Token refresh failed')
            }
          } catch (parseError) {
            console.error('Failed to parse JSON response:', parseError)
            throw new Error('Invalid response format')
          }
        } catch (fetchError) {
          console.error('Fetch error:', fetchError)
          throw fetchError
        }
      }
    },
    
    // 支付相关API
    payments: {
      // 获取支付方式列表
      getMethods: () => request('/v1/payments/methods/'),
      // 创建支付
      create: (data: any) => request('/v1/payments/', { method: 'POST', body: data }),
      // 获取支付详情
      getById: (id: string) => request(`/v1/payments/${id}/`),
      // 为心愿单商品创建支付
      createForWishlistItem: (itemId: string) => request(`/v1/payments/wishlist-item/${itemId}/`, { method: 'POST' }),
      // 查询支付状态
      checkStatus: (id: string) => request(`/v1/payments/${id}/status/`),
      // 取消支付
      cancel: (id: string) => request(`/v1/payments/${id}/cancel/`, { method: 'POST' }),
    },
    
    // 用户相关API
    user: {
      // 获取用户信息
      getProfile: () => request('/v1/user/profile/'),
      // 更新用户信息
      updateProfile: (data: any) => request('/v1/user/profile/', { method: 'PATCH', body: data }),
      // 注册
      register: (data: any) => {
        // 确保邀请码参数正确传递
        const registerData = {
          ...data,
          // 如果已经有invite_code就使用它，否则使用inviteCode
          invite_code: data.invite_code || data.inviteCode
        };
        return request('/v1/user/register/', { method: 'POST', body: registerData });
      }
    }
  }
}
