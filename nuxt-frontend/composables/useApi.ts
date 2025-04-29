import { $fetch, FetchOptions } from 'ofetch'
import type { RuntimeConfig } from 'nuxt/schema'

// Declare global types for TypeScript to recognize these composable APIs
declare global {
  const useRuntimeConfig: () => RuntimeConfig
  const useCookie: any
}

export const useApi = () => {
  // Get runtime configuration
  const config = useRuntimeConfig()
  const { apiBase, currentSite } = config.public as {
    apiBase: string
    authBase: string
    currentSite: string
  }
  
  // Create fetch instance with basic configuration
  const apiFetch = $fetch.create({
    baseURL: apiBase,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    credentials: 'include',
  })
  
  // Generic request method
  const isPublicApi = (url: string) => {
    return (
      url.includes('/categories') ||
      url.includes('/products') ||
      url.includes('/v1/wishlist/lists/list_public')
      // 可扩展其它允许匿名访问的API
    )
  }

  const clearAuth = () => {
    try {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      document.cookie = 'sessionid=;expires=Thu, 01 Jan 1970 00:00:01 GMT;path=/'
    } catch (e) {}
  }

  const request = async (endpoint: string, options: FetchOptions = {}) => {
    try {
      // Add site identifier to URL parameters
      let urlStr = endpoint;
      if (!urlStr.includes('?')) {
        urlStr += `?site=${currentSite}`;
      } else {
        urlStr += `&site=${currentSite}`;
      }
      
      // Build complete URL
      if (!urlStr.startsWith('http')) {
        urlStr = `${apiBase}${urlStr}`;
      }
      
      console.log('API Request to:', urlStr);
      console.log('API Base URL:', apiBase);
      console.log('Runtime Config:', config.public);
      
      // Get authentication token (if available)
      // First try to get token from localStorage
      let token: string | null = null;
      if (typeof window !== 'undefined') {
        token = localStorage.getItem('token');
      }
      
      // If not in localStorage, try to get from cookie
      if (!token) {
        const tokenCookie = useCookie('auth_token');
        token = tokenCookie.value;
      }
      
      console.log('Authentication token used:', token);
      
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers as HeadersInit
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      // Prepare request options
      const fetchOptions: RequestInit = {
        method: options.method || 'GET',
        headers,
        credentials: 'include'
      };
      
      // Add request body to options if present
      if (options.body) {
        fetchOptions.body = JSON.stringify(options.body);
      }
      
      let response, responseText;
      try {
        response = await fetch(urlStr, fetchOptions);
        responseText = await response.text();
      } catch (fetchError) {
        throw fetchError;
      }
      
      // 检查403且为公开API，自动清除token并重试一次
      if (response && response.status === 403 && isPublicApi(urlStr)) {
        clearAuth();
        // 再次匿名请求
        const retryOptions: RequestInit = {
          method: options.method || 'GET',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          }
        };
        
        // 正确处理body字段
        if (options.body) {
          retryOptions.body = typeof options.body === 'string' 
            ? options.body 
            : JSON.stringify(options.body);
        }
        
        response = await fetch(urlStr, retryOptions);
        responseText = await response.text();
      }
      
      // Check response status
      if (!response.ok) {
        console.error(`API Error: ${response.status} ${response.statusText}`);
        console.error('Error response:', responseText);
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }
      
      console.log(`API Response from ${urlStr}:`, responseText);
      
      // Return empty object if response is empty
      if (!responseText.trim()) {
        return {};
      }
      
      // Parse response
      try {
        const data = JSON.parse(responseText);
        
        // Handle different API response formats
        if (data.code !== undefined) {
          // Handle {code, message, data} format
          if (data.code === 0) {
            return data.data || {};
          } else {
            console.error('API Error:', data.message);
            throw new Error(data.message || 'API request failed');
          }
        } else {
          // Return data directly
          return data;
        }
      } catch (parseError) {
        console.error('Failed to parse API response:', parseError);
        // Return raw text if cannot parse as JSON
        return responseText;
      }
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }
  
  // Various API methods
  return {
    // Categories related APIs
    categories: {
      // Get all categories
      getAll: () => request('/v1/categories/'),
      // Get category tree
      getTree: () => request('/v1/categories/tree/'),
      // Get category details
      getById: (id: string) => request(`/v1/categories/${id}/`),
      // Get products in category
      getProducts: (id: string) => request(`/v1/categories/${id}/products/`)
    },
    
    // Products related APIs
    products: {
      // Get product list
      getAll: (params = {}) => request('/v1/products/', { params }),
      // Get product details
      getById: (id: string) => request(`/v1/products/${id}/`),
      // Get recommended products
      getRecommended: () => request('/v1/products/recommended/'),
      // Get hot products
      getHot: () => request('/v1/products/hot/'),
      // Get new products
      getNew: () => request('/v1/products/new/'),
      // Search products
      search: (keyword: string) => request('/v1/products/', { params: { keyword } })
    },
    
    // Wishlist related APIs
    wishlist: {
      // Get all user wishlists
      getUserWishlists: () => request('/v1/wishlist/lists/'),
      // Get current user's default wishlist
      getCurrent: () => request('/v1/wishlist/lists/current/'),
      // Add item to wishlist (Django API)
      addItem: (data: any) => request('/v1/wishlist/items/', { method: 'POST', body: data }),
      // Remove item from wishlist
      removeItem: (id: string) => request(`/v1/wishlist/items/${id}/`, { method: 'DELETE' }),
      // Update wishlist item
      updateItem: (id: string, data: any) => request(`/v1/wishlist/items/${id}/`, { method: 'PATCH', body: data }),
      // Get wishlist by share code
      getByShareCode: (shareCode: string) => request(`/v1/wishlist/lists/share/${shareCode}/`),
      // Get public wishlist list
      getPublic: () => request('/v1/wishlist/lists/list_public/'),
      // Create wishlist
      create: (data: any) => request('/v1/wishlist/lists/', { method: 'POST', body: data }),
      // Update wishlist
      update: (id: string, data: any) => request(`/v1/wishlist/lists/${id}/`, { method: 'PATCH', body: data }),
      // Delete wishlist
      delete: (id: string) => request(`/v1/wishlist/lists/${id}/`, { method: 'DELETE' }),
      // Mark item as purchased
      purchaseItem: (id: string, data: any = {}) => request(`/v1/wishlist/items/${id}/purchase/`, { method: 'POST', body: data }),
      // Purchase full wishlist (all unpurchased items)
      purchaseFullWishlist: (data: any) => request(`/v1/wishlist/lists/${data.wishlist_id}/purchase_all/`, { method: 'POST', body: data }),
      // Record wishlist view
      recordView: (id: string) => request(`/v1/wishlist/lists/${id}/view/`, { method: 'POST' }),
      // Get wishlist statistics
      getStats: (id: string) => request(`/v1/wishlist/lists/${id}/stats/`),
      // Get summary statistics for all wishlists
      getAllStats: () => request('/v1/wishlist/stats/'),
      // Get wishlist share link
      getShareLink: (id: string) => request(`/v1/wishlist/lists/${id}/share-link/`),
      // Check if product is in wishlist
      checkProductInWishlist: (productId: string) => request(`/v1/wishlist/check-product/${productId}/`),
      // Get user's wishlist items
      getUserItems: () => request('/v1/wishlist/user-items/')
    },
    
    // User authentication related APIs
    auth: {
      // Login
      login: async (credentials: { username: string, password: string }) => {
        // Add site identifier to URL parameters
        const urlStr = `${config.public.authBase}/token/?site=${currentSite}`
        
        console.log('Sending login request to:', urlStr)
        console.log('With credentials:', credentials)
        
        try {
          // Send request using FormData format
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
            // Handle API response format
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
      // Refresh token
      refreshToken: async (refreshToken: string) => {
        // Add site identifier to URL parameters
        const urlStr = `${config.public.authBase}/token/refresh/?site=${currentSite}`
        
        try {
          // Construct request body according to test page format
          const formData = new FormData()
          formData.append('refresh', refreshToken)
          
          // Send request
          const response = await fetch(urlStr, {
            method: 'POST',
            credentials: 'include',
            body: formData
          })
          
          const responseText = await response.text()
          console.log('Token refresh API response:', responseText)
          
          try {
            const data = JSON.parse(responseText)
            // Handle API response format
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
    
    // Payments related APIs
    payments: {
      // Get payment methods
      getMethods: () => request('/v1/payments/methods/'),
      // Create payment
      create: (data: any) => request('/v1/payments/', { method: 'POST', body: data }),
      // Get payment details
      getById: (id: string) => request(`/v1/payments/${id}/`),
      // Create payment for wishlist item
      createForWishlistItem: (itemId: string, options: any = {}) => 
        request(`/v1/payments/wishlist-item/${itemId}/`, { 
          method: 'POST', 
          body: { 
            ...options,
            notify_telegram: true,            // 成功时通知
            notify_telegram_on_failure: true  // 失败时也通知
          } 
        }),
      // Check payment status
      checkStatus: (id: string) => request(`/v1/payments/${id}/status/`),
      // Cancel payment
      cancel: (id: string) => request(`/v1/payments/${id}/cancel/`, { method: 'POST' }),
    },
    
    // User related APIs
    user: {
      // Get user profile
      getProfile: () => request('/v1/user/profile/'),
      // Update user profile
      updateProfile: (data: any) => request('/v1/user/profile/', { method: 'PATCH', body: data }),
      // Register
      register: (data: any) => {
        // Ensure invite code parameter is correctly passed
        const registerData = {
          ...data,
          // Use invite_code if it exists, otherwise use inviteCode
          invite_code: data.invite_code || data.inviteCode
        };
        return request('/v1/user/register/', { method: 'POST', body: registerData });
      },
      // Generate Telegram connection token
      generateTelegramToken: () => request('/v1/user/telegram/token/', { method: 'POST' }),
      // Get Telegram connection status
      getTelegramStatus: () => request('/v1/user/telegram/status/'),
      // Disconnect Telegram
      disconnectTelegram: () => request('/v1/user/telegram/disconnect/', { method: 'POST' })
    }
  }
}
