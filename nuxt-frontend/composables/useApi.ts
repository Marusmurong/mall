import { useFetch as baseUseFetch, UseFetchOptions } from 'nuxt/app'
import { useAuthStore } from '../stores/auth'
import { ref } from 'vue'
import type { FetchError } from 'ofetch'
import axios from 'axios'
import { useNuxtApp } from 'nuxt/app'

// Declare global types for TypeScript to recognize these composable APIs
declare global {
  const useRuntimeConfig: any
  const useCookie: any
}

// 请求选项接口定义
interface RequestOptions {
  method?: string;
  headers?: HeadersInit;
  body?: any;
  params?: Record<string, any>;
}

// API响应类型
interface ApiResponse<T> {
  data: T
}

// 产品类型
interface Product {
  id: string
  name: string
  description: string
  price: number
  image: string
  [key: string]: any
}

// 扩展UseFetchOptions类型以匹配useFetch的期望
type ExtendedUseFetchOptions<T> = UseFetchOptions<any, any, any, any, any, any>

// API基础URL获取函数
const getApiBase = () => {
  // 获取本地配置还是线上配置
  const config = useRuntimeConfig()
  // 使用环境变量或默认值
  let base = config.public.apiBaseUrl || 'http://localhost:8000/api/v1'
  
  // 确保URL格式正确（没有多余的斜杠）
  if (base.endsWith('/')) {
    base = base.slice(0, -1)
  }
  
  return base
}

// 添加API错误处理辅助函数
const handleApiError = (error: any) => {
  console.error('API错误处理:', error);
  
  // 如果是Axios错误
  if (error.response && error.response.data) {
    return { 
      message: error.response.data.message || error.response.data || '请求处理失败' 
    };
  }
  
  // 其他错误
  return { 
    message: error.message || '未知错误' 
  };
};

export const useApi = () => {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()
  
  // 获取环境API基础URL
  const apiBase = getApiBase()
  
  // 日志函数
  const logRequest = (method: string, url: string, data?: any) => {
    if (config.public.debug) {
      console.log(`[API] ${method} 请求: ${url}`, data ? JSON.stringify(data) : '无数据')
    }
  }

  // 日志函数-响应
  const logResponse = (url: string, response: any) => {
    if (config.public.debug) {
      console.log(`[API] 响应: ${url}`, response)
    }
  }

  // 日志函数-错误
  const logError = (url: string, error: any) => {
    console.error(`[API] 错误: ${url}`, error)
  }

  // 加载状态
  const loading = ref(false)
  // 错误状态
  const error = ref<string | null>(null)

  /**
   * 通用GET请求
   * @param url - 请求URL
   * @param options - fetch选项
   * @returns 响应数据
   */
  const get = async <T>(url: string, options: any = {}) => {
    try {
      // 处理URL参数
      let queryParams = '';
      if (options.params && Object.keys(options.params).length > 0) {
        const searchParams = new URLSearchParams();
        for (const key in options.params) {
          if (options.params[key] !== undefined && options.params[key] !== null) {
            searchParams.append(key, options.params[key].toString());
          }
        }
        queryParams = searchParams.toString();
        if (queryParams) {
          // 如果URL已经包含查询参数，则使用&添加，否则使用?添加
          url += url.includes('?') ? `&${queryParams}` : `?${queryParams}`;
        }
      }
      
      // 如果URL是完整URL，直接使用；否则拼接apiBase
      const base = getApiBase();
      const fullUrl = url.startsWith('http') 
        ? url 
        : url.startsWith('/') 
          ? `${base}${url}` 
          : `${base}/${url}`;
      
      // 修复所有双斜杠问题（除了http://）
      const cleanedUrl = fullUrl.replace(/([^:]\/)\/+/g, "$1");
      
      console.log(`[API GET] ${cleanedUrl}`, options.params || {})
      
      // 构建请求头，包含认证令牌
      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      };
      
      // 添加认证令牌
      if (authStore.token) {
        headers['Authorization'] = `Bearer ${authStore.token}`;
      }
      
      // 直接使用fetch，避免与Nuxt的生命周期冲突
      const response = await fetch(cleanedUrl, {
        headers
      });
      
      if (!response.ok) {
        throw new Error(`请求失败: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`[API] 响应数据:`, data);
      
      // 检查是否需要保留原始响应格式
      if (options.preserveResponse) {
        console.log('[API] 保留原始响应格式')
        return data
      }
      
      // 检查是否符合标准API响应格式
      if (data && typeof data === 'object' && 'code' in data && data.code === 0 && 'data' in data) {
        console.log('[API] 检测到标准响应格式，返回data字段');
        return data.data;
      }
      
      return data;
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }

  /**
   * 通用POST请求
   * @param url - 请求URL
   * @param payload - 请求数据
   * @param options - fetch选项
   * @returns 响应数据
   */
  const post = async <T>(url: string, payload: any, options: any = {}) => {
    try {
      // 如果URL是完整URL，直接使用；否则拼接apiBase
      const base = getApiBase();
      const fullUrl = url.startsWith('http') 
        ? url 
        : url.startsWith('/') 
          ? `${base}${url}` 
          : `${base}/${url}`;
      
      // 修复双斜杠问题
      const cleanedUrl = fullUrl.replace(/([^:]\/)\/+/g, "$1");
      
      console.log(`[API POST] ${cleanedUrl}`, payload)
      
      // 构建请求头，包含认证令牌
      const headers: HeadersInit = {
        'Content-Type': 'application/json'
      };
      
      // 添加认证令牌
      if (authStore.token) {
        headers['Authorization'] = `Bearer ${authStore.token}`;
      }
      
      // 直接使用fetch，避免与Nuxt的生命周期冲突
      const response = await fetch(cleanedUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
      });
      
      // 获取响应的状态码
      const statusCode = response.status;
      
      if (!response.ok) {
        // 尝试读取响应内容，可能包含详细错误信息
        let errorDetail = '';
        try {
          const errorResponse = await response.json();
          console.error('API错误详情:', errorResponse);
          errorDetail = errorResponse ? `: ${JSON.stringify(errorResponse)}` : '';
        } catch (readError) {
          console.error('无法读取错误响应内容', readError);
        }
        
        throw new Error(`请求失败: ${response.status} ${response.statusText}${errorDetail}`);
      }
      
      // 尝试解析JSON响应
      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        // 如果响应不是JSON，读取为文本
        data = await response.text();
      }
      
      console.log(`[API] 响应数据 [${statusCode}]:`, data);
      
      // 判断是否是标准API响应格式，如果是则提取data字段
      if (data && typeof data === 'object' && 'code' in data && data.code === 0 && 'data' in data) {
        console.log('[API] 检测到标准响应格式，返回data字段');
        return data.data;
      }
      
      return data;
    } catch (error) {
      console.error('API call failed:', error)
      throw error
    }
  }

  /**
   * 通用请求函数
   * @param url 请求地址
   * @param options 请求选项
   * @returns 请求结果
   */
  const request = async <T>(url: string, options: UseFetchOptions<T> = {}) => {
    loading.value = true
    error.value = null

    try {
      // 确保URL是绝对路径或使用本地API路径
      let fullUrl: string;
      
      // 判断是否已经是完整URL
      if (url.startsWith('http')) {
        fullUrl = url;
      } else if (url.startsWith('/api/')) {
        // 已经以/api开头的，直接转发到本地代理
        fullUrl = url;
      } else {
        // 不是以上情况，使用getApiBase，去掉开头的斜杠，构造完整路径
        const base = getApiBase();
        
        // 避免双斜杠问题
        if (url.startsWith('/')) {
          fullUrl = `${base}${url}`;
        } else {
          fullUrl = `${base}/${url}`;
        }
        
        // 修复所有双斜杠问题（除了http://）
        fullUrl = fullUrl.replace(/([^:]\/)\/+/g, "$1");
      }
      
      console.log(`[API] 请求: [${options.method || 'GET'}] "${fullUrl}"`);
      
      // 构建请求选项
      const fetchOptions: UseFetchOptions<T> = {
        ...options,
        // 使用本地代理，所以不需要添加baseURL
      }

      const { data, error: fetchError } = await baseUseFetch<T>(fullUrl, fetchOptions as any)

      // 处理错误
      if (fetchError.value) {
        const errorMessage = fetchError.value.message || '未知错误'
        console.error(`[API] 错误: ${fullUrl} ${errorMessage}`)
        throw new Error(`API错误: ${errorMessage}`)
      }

      return data.value as T
    } catch (err: any) {
      console.error(`[API] 错误: ${url}`, err)
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * GET请求
   * @param url 请求地址
   * @param options 请求选项
   * @returns 请求结果
   */
  const getRequest = <T>(url: string, options: UseFetchOptions<T> = {}) => {
    return request<T>(url, { ...options, method: 'GET' })
  }

  /**
   * POST请求
   * @param url 请求地址
   * @param options 请求选项
   * @returns 请求结果
   */
  const postRequest = <T>(url: string, options: UseFetchOptions<T> = {}) => {
    return request<T>(url, { ...options, method: 'POST' })
  }

  /**
   * PUT请求
   * @param url 请求地址
   * @param options 请求选项
   * @returns 请求结果
   */
  const put = <T>(url: string, options: UseFetchOptions<T> = {}) => {
    return request<T>(url, { ...options, method: 'PUT' })
  }

  /**
   * PATCH请求
   * @param url 请求地址
   * @param options 请求选项
   * @returns 请求结果
   */
  const patch = <T>(url: string, options: UseFetchOptions<T> = {}) => {
    return request<T>(url, { ...options, method: 'PATCH' })
  }

  /**
   * DELETE请求
   * @param url 请求地址
   * @param options 请求选项
   * @returns 请求结果
   */
  const del = <T>(url: string, options: UseFetchOptions<T> = {}) => {
    return request<T>(url, { ...options, method: 'DELETE' })
  }

  // 内容相关API
  const content = {
    /**
     * 获取页面内容
     * @param category 分类
     * @returns 页面内容
     */
    getPageContent: async (category: string) => {
      const url = `content/page-contents/?category=${category}`;
      console.log(`[Content API] 请求内容: ${url}`);
      return get(url);
    },
    /**
     * 获取页面详情
     * @param id 页面ID
     * @returns 页面详情
     */
    getPageContentDetail: async (id: string) => {
      const url = `content/page-contents/${id}/`;
      console.log(`[Content API] 请求详情: ${url}`);
      return get(url);
    },
    /**
     * 根据分类和slug获取内容
     * @param category 分类
     * @param slug slug
     * @returns 页面内容
     */
    getPageContentBySlug: async (category: string, slug: string) => {
      const url = `content/page-contents/by_category_slug/?category=${category}&slug=${slug}`;
      console.log(`[Content API] 根据slug请求内容: ${url}`);
      return get(url);
    }
  }

  // Various API methods
  return {
    loading,
    error,
    // Categories related APIs
    categories: {
      // Get all categories
      getAll: () => get('/categories/'),
      // Get category tree
      getTree: () => get('/categories/tree/'),
      // Get category details
      getById: (id: string) => get(`/categories/${id}/`),
      // Get products in category
      getProducts: (id: string, page = 1, pageSize = 40, filters = {}) => 
        get(`/categories/${id}/products/`, { 
          params: { 
            page, 
            limit: pageSize,
            ...filters  // 添加所有筛选参数
          } 
        }),
      getDetail: (id: string) => get(`/categories/${id}/`)
    },
    
    // Products related APIs
    products: {
      // Get product list
      getAll: (page = 1, pageSize = 40, filters = {}) => 
        get('/products/', { 
          params: { 
            page, 
            limit: pageSize,
            ...filters  // 添加所有筛选参数
          } 
        }),
      // Get product details
      getById: (id: string) => get(`/products/${id}/`),
      // Get recommended products
      getRecommended: () => get('/products/recommended/'),
      /**
       * 获取热门商品列表
       * @param limit 限制数量，默认20
       * @returns 热门商品列表
       */
      getHot: async (limit = 20): Promise<Product[]> => {
        try {
          console.log(`[API] 请求热门商品: limit=${limit}`);
          // 使用直接路径访问
          const response = await get<Product[]>(`/products/hot/?limit=${limit}`);
          return response;
        } catch (error) {
          console.error(`[API] 获取热门商品失败:`, error);
          // 失败时返回空数组而不是抛出错误
          return [];
        }
      },
      // Get new products
      getNew: () => get('/products/new/'),
      // Search products
      search: (query: string) => get(`/products/search/?q=${query}`),
      // Get products by category
      getByCategory: (categoryId: string) => get(`/products/category/${categoryId}/`),
      getList: (params = {}) => get('/products/list/', { params }),
      getDetail: (id: string) => get(`/products/${id}/`),
      getProducts: (params: any = {}) => {
        return get('/products/', params)
      },
      getCategories: () => {
        return get('/categories/')
      }
    },
    
    // Wishlist related APIs
    wishlist: {
      // Get wishlist
      getCurrent: () => {
        console.log('获取当前心愿单')
        return get('/wishlist/lists/current/')
          .catch(error => {
            console.error('获取当前心愿单失败:', error)
            
            // 如果错误是由于找不到心愿单，尝试创建一个
            if (error.message.includes('not found')) {
              console.log('尝试创建新的心愿单')
              return post('/wishlist/lists/', { 
                method: 'POST', 
                body: { 
                  name: `${useAuthStore().user?.username || 'User'}'s Wishlist`,
                  is_public: true,
                  site: (useRuntimeConfig().public as any).currentSite
                } 
              }).catch(error => {
                console.error('创建心愿单失败:', error)
                throw error; // 如果获取失败，抛出原始错误
              })
            }
            
            throw error; // 抛出原始错误
          })
      },
      // Get all wishlists
      getLists: () => get('/wishlist/lists/'),
      // Get wishlist by ID
      getList: (id: string) => get(`/wishlist/lists/${id}/`),
      // Add item to wishlist
      addItem: (data: any) => post('/wishlist/items/', data),
      // 从心愿单中移除商品
      removeItem: (id: string) => del(`/wishlist/items/${id}/`, { method: 'DELETE' }),
      // 更新心愿单商品
      updateItem: (id: string, data: any) => post(`/wishlist/items/${id}/`, { method: 'PATCH', body: data }),
      // 通过分享码获取心愿单
      getByShareCode: (shareCode: string) => {
        console.log('通过分享码获取心愿单:', shareCode)
        return get(`/wishlist/lists/share/${shareCode}/`)
          .then(response => {
            console.log('分享码获取心愿单响应:', response)
            
            // 检查响应格式是否是标准API格式 {code: 0, message: "success", data: {...}}
            if (response && typeof response.code !== 'undefined' && response.message) {
              return response; // 已经是标准格式，直接返回
            } else {
              // 包装成标准格式
              return {
                code: 0,
                message: 'success',
                data: response
              }
            }
          })
          .catch(error => {
            console.error('通过分享码获取心愿单失败:', error)
            throw error
          })
      },
      // 获取公开的心愿单列表
      getPublic: () => get('/wishlist/lists/list_public/'),
      // 创建心愿单
      create: (data: any) => {
        console.log('调用API: 创建心愿单', data)
        
        // 确保site参数存在
        const requestData = { 
          ...data,
          // 确保发送site参数
          site: (useRuntimeConfig().public as any).currentSite
        }
        
        // 确保name参数存在
        if (!requestData.name) {
          console.error('创建心愿单错误: 缺少name参数')
          return Promise.reject(new Error('缺少必要参数: name'))
        }
        
        return post('/wishlist/lists/', { 
          method: 'POST', 
          body: requestData
        }).catch(error => {
          console.error('创建心愿单API错误:', error)
          throw error
        })
      },
      // Update wishlist
      update: (id: string, data: any) => post(`/wishlist/lists/${id}/`, { method: 'PATCH', body: data }),
      // Delete wishlist
      delete: (id: string) => del(`/wishlist/lists/${id}/`, { method: 'DELETE' }),
      // Mark item as purchased
      purchaseItem: (id: string, data: any = {}) => post(`/wishlist/items/${id}/purchase/`, { method: 'POST', body: data }),
      // Purchase full wishlist (all unpurchased items)
      purchaseFullWishlist: (data: any) => post(`/wishlist/lists/${data.wishlist_id}/purchase_all/`, { method: 'POST', body: data }),
      // Record wishlist view
      recordView: (id: string) => post(`/wishlist/lists/${id}/view/`, { method: 'POST' }),
      // Record share view
      recordShareView: (shareCode: string) => get(`/wishlist/lists/share/${shareCode}/`),
      // Get wishlist stats
      getStats: (id: string) => get(`/wishlist/lists/${id}/stats/`),
      // Get share stats - using share_code instead of ID
      getShareStats: (shareCode: string) => get(`/wishlist/lists/share/${shareCode}/`),
      // Get all wishlist stats
      getAllStats: () => get('/wishlist/stats/'),
      // Get wishlist share link
      getShareLink: (id: string) => get(`/wishlist/lists/${id}/share-link/`),
      // Check if product is in wishlist
      checkProductInWishlist: (productId: string) => get(`/wishlist/check-product/${productId}/`),
      // Get user wishlist items
      getUserItems: () => get('/wishlist/user-items/'),
      // Get user wishlists
      getUserWishlists: () => {
        console.log('调用getUserWishlists API')
        // 使用保留原始响应格式的方式调用API
        return get('/wishlist/lists/', { 
          preserveResponse: true // 添加标志，表示需要保留原始响应格式
        })
      }
    },
    
    // Cart related APIs
    cart: {
      // Get cart
      get: () => get('/cart/'),
      // Add item to cart
      addItem: (data: any) => post('/cart/items/', { 
        method: 'POST',
        body: data
      }),
      // Update cart item
      updateItem: (id: string, data: any) => put(`/cart/items/${id}/`, {
        method: 'PUT',
        body: data
      }),
      // Remove cart item
      removeItem: (id: string) => del(`/cart/items/${id}/`),
      // Clear cart
      clear: () => del('/cart/clear/'),
      getCart: () => {
        return get('/cart/')
      },
      addToCart: (productId: string, quantity: number) => {
        return post('/cart/add/', { product_id: productId, quantity })
      },
      updateCart: (itemId: string, quantity: number) => {
        return post('/cart/update/', { item_id: itemId, quantity })
      },
      removeFromCart: (itemId: string) => {
        return post('/cart/remove/', { item_id: itemId })
      }
    },
    
    // Order related APIs
    orders: {
      // Get order list
      getList: () => get('/orders/'),
      // Get order details
      getDetail: (id: string) => get(`/orders/${id}/`),
      // Create order
      create: (data: any) => post('/orders/', {
        method: 'POST',
        body: data
      }),
      // Cancel order
      cancel: (id: string) => post(`/orders/${id}/cancel/`, { method: 'POST' }),
      getOrders: () => {
        return get('/orders/')
      },
      getOrderDetail: (id: string) => {
        return get(`/orders/${id}/`)
      },
      createOrder: (orderData: any) => {
        return post('/orders/create/', orderData)
      }
    },
    
    // Authentication related APIs
    auth: {
      // Login
      login: (credentials: { username: string, password: string }) => 
        post('/auth/token/', credentials),
      // Register
      register: async (
        username: string,
        email: string,
        password: string,
        password2: string,
        inviteCode: string
      ): Promise<any> => {
        try {
          // 不再使用toast，改为alert
          const { data } = await axios.post('/api/v1/user/register/', {
            username,
            email,
            password,
            password2,
            invite_code: inviteCode
          });
          
          // 注册成功后直接保存登录信息
          if (data) {
            // 直接设置store属性，而不是调用方法
            authStore.user = data.user;
            authStore.token = data.access;
            authStore.refreshToken = data.refresh;
            authStore.isAuthenticated = true;
            
            // 保存到本地存储
            localStorage.setItem('user', JSON.stringify(data.user));
            localStorage.setItem('token', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            
            // 使用alert而不是toast
            alert('注册成功！欢迎加入我们的社区。');
            return data;
          }
          return null;
        } catch (error) {
          console.error('注册失败:', error);
          const errorResponse = handleApiError(error);
          
          // 格式化并返回API错误信息
          if (errorResponse?.message) {
            let errorMsg = '';
            
            // 处理不同字段的错误信息
            if (typeof errorResponse.message === 'object') {
              // 针对不同字段的错误提示
              if (errorResponse.message.username) {
                errorMsg += `用户名: ${errorResponse.message.username} `;
              }
              if (errorResponse.message.email) {
                errorMsg += `邮箱: ${errorResponse.message.email} `;
              }
              if (errorResponse.message.password) {
                errorMsg += `密码: ${errorResponse.message.password} `;
              }
              if (errorResponse.message.invite_code) {
                errorMsg += `邀请码: ${errorResponse.message.invite_code} `;
              }
            } else {
              errorMsg = errorResponse.message;
            }
            
            // 使用alert而不是toast
            alert(errorMsg || '注册失败，请重试');
          } else {
            alert('注册失败，请重试');
          }
          throw error;
        }
      },
      // Logout
      logout: () => 
        post('/auth/logout/', { 
          method: 'POST' 
        }),
      // Refresh token
      refreshToken: (refreshToken: string) => 
        post('/auth/token/refresh/', { 
          method: 'POST', 
          body: { refresh: refreshToken } 
        }),
      profile: () => {
        return get('/auth/profile/')
      }
    },
    
    // Payment related APIs
    payments: {
      // Get available payment methods
      getMethods: () => get('/payments/methods/'),
      // Create payment record
      createPayment: (data: any) => {
        // 确保数据完整且格式正确
        console.log('准备发送支付请求，参数:', data);
        
        const paymentData = {
          ...data,
          is_anonymous: true,
          payer_email: data.payer_email || 'anonymous@example.com'
        };
        
        // 确保ID是字符串，payment_method_id是数字
        if (paymentData.wishlist_item_id && typeof paymentData.wishlist_item_id !== 'string') {
          paymentData.wishlist_item_id = String(paymentData.wishlist_item_id);
        }
        
        if (paymentData.payment_method_id && typeof paymentData.payment_method_id !== 'number') {
          paymentData.payment_method_id = Number(paymentData.payment_method_id);
        }
        
        if (paymentData.amount && typeof paymentData.amount !== 'string') {
          paymentData.amount = String(paymentData.amount);
        }
        
        console.log('最终发送的支付数据:', paymentData);
        
        // 直接将数据作为post的参数，而不是嵌套在body中
        return post('/payments/list/', paymentData)
          .then(response => {
            console.log('支付API原始响应:', response);
            
            // 处理嵌套响应结构
            let responseData = response;
            
            // 如果响应是标准格式 {code: 0, message: "success", data: {...}}
            if (response && response.code === 0 && response.data) {
              console.log('检测到标准API响应格式，获取data字段');
              responseData = response.data;
            }
            
            console.log('支付API处理后响应:', responseData);
            
            // 检查是否有payment_link
            if (responseData && responseData.payment_link) {
              console.log('直接在响应中找到payment_link:', responseData.payment_link);
            }
            // 检查是否有checkout_url，如果有，设置为payment_link
            else if (responseData && responseData.payment_data && responseData.payment_data.checkout_url) {
              responseData.payment_link = responseData.payment_data.checkout_url;
              console.log('找到checkout_url，设置为payment_link:', responseData.payment_link);
            }
            // 检查Coinbase支付详情
            else if (responseData && responseData.coinbase_details && responseData.coinbase_details.hosted_url) {
              responseData.payment_link = responseData.coinbase_details.hosted_url;
              console.log('找到coinbase托管URL，设置为payment_link:', responseData.payment_link);
            }
            // 检查PayPal支付详情
            else if (responseData && responseData.paypal_details && responseData.paypal_details.payment_link) {
              responseData.payment_link = responseData.paypal_details.payment_link;
              console.log('找到PayPal支付链接，设置为payment_link:', responseData.payment_link);
            }
            
            if (responseData && responseData.payment_link) {
              console.log('最终支付链接:', responseData.payment_link);
            } else {
              console.warn('支付API响应中没有找到支付链接!');
            }
            
            return responseData;
          });
      },
      // Create PayPal payment
      createPaypalPayment: (data: any) => post('/payments/paypal/', data),
      // Create Coinbase payment
      createCoinbasePayment: (data: any) => post('/payments/coinbase/', data),
      // Create Stripe payment
      createStripePayment: (data: any) => post('/payments/stripe/', data)
    },
    
    // User related APIs
    user: {
      // Get user profile
      getProfile: () => get('/user/profile/'),
      // Update user profile
      updateProfile: (data: any) => post('/user/profile/', { 
        method: 'PATCH', 
        body: data 
      }),
      // 注册新用户
      register: (userData: { username: string; email: string; password: string; password2?: string; invite_code: string }) => {
        // 确保有password2字段，如果没有则使用password的值
        const registerData = {
          ...userData,
          password2: userData.password2 || userData.password,
          // 确保发送site参数
          site: (useRuntimeConfig().public as any).currentSite
        }
        console.log('注册用户, 数据:', registerData)
        return post('/user/register/', registerData)
      }
    },
    
    // 内容相关API
    content,
    
    // 轮播图/横幅
    banners: {
      getList: () => get('/banners/')
    },
    
    request,
    getRequest,
    postRequest,
    put,
    patch,
    delete: del
  }
}