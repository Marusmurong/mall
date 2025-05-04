import { defineStore } from 'pinia'

// 导入Nuxt的composables
const useApi = () => {
  // 使用动态导入确保在Nuxt环境中运行
  return import('../composables/useApi').then(module => module.useApi())
}

// 安全地访问localStorage
const useLocalStorage = () => {
  const isClient = typeof window !== 'undefined'
  
  return {
    getItem: (key: string): string | null => {
      if (!isClient) return null
      return localStorage.getItem(key)
    },
    setItem: (key: string, value: string): void => {
      if (!isClient) return
      localStorage.setItem(key, value)
    },
    removeItem: (key: string): void => {
      if (!isClient) return
      localStorage.removeItem(key)
    }
  }
}

// 使用Nuxt的useCookie
const useCookie = (name: string) => {
  const storage = useLocalStorage()
  
  return {
    get value() {
      return storage.getItem(name)
    },
    set value(newValue: string | null) {
      if (newValue === null) {
        storage.removeItem(name)
      } else {
        storage.setItem(name, newValue)
      }
    }
  }
}

interface User {
  id: number
  username: string
  email: string
  [key: string]: any
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false
  }),
  
  getters: {
    getUser: (state) => state.user,
    getToken: (state) => state.token,
    getIsAuthenticated: (state) => state.isAuthenticated
  },
  
  actions: {
    async login(username: string, password: string) {
      try {
        // 获取API实例
        const api = await useApi()
        const response = await api.auth.login({ username, password })
        
        // 处理新的API响应格式: { code: 0, message: 'success', data: { refresh, access } }
        let tokenData
        if (response && response.code === 0 && response.data) {
          // 新的API响应格式
          tokenData = response.data
        } else {
          // 旧的API响应格式，直接使用
          tokenData = response
        }
        
        this.token = tokenData.access
        this.refreshToken = tokenData.refresh
        this.isAuthenticated = true
        
        // 存储token到localStorage
        const storage = useLocalStorage()
        storage.setItem('token', tokenData.access)
        storage.setItem('refresh_token', tokenData.refresh)
        
        // 为兼容性保留这些代码
        const tokenCookie = useCookie('auth_token')
        tokenCookie.value = tokenData.access
        
        const refreshTokenCookie = useCookie('refresh_token')
        refreshTokenCookie.value = tokenData.refresh
        
        // 获取用户信息
        await this.fetchUserProfile()
        
        return { success: true }
      } catch (error) {
        console.error('登录失败:', error)
        return { success: false, error }
      }
    },
    
    async fetchUserProfile() {
      if (!this.isAuthenticated) return
      
      try {
        const api = await useApi()
        const userProfile = await api.user.getProfile()
        this.user = userProfile
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },
    
    async refreshAccessToken() {
      if (!this.refreshToken) return false
      
      try {
        const api = await useApi()
        const response = await api.auth.refreshToken(this.refreshToken)
        
        // 处理新的API响应格式
        let tokenData
        if (response && response.code === 0 && response.data) {
          // 新的API响应格式
          tokenData = response.data
        } else {
          // 旧的API响应格式，直接使用
          tokenData = response
        }
        
        this.token = tokenData.access
        
        // 更新localStorage中的token
        const tokenCookie = useCookie('auth_token')
        tokenCookie.value = tokenData.access
        
        return true
      } catch (error) {
        console.error('刷新token失败:', error)
        this.logout()
        return false
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      this.isAuthenticated = false
      
      // 清除localStorage中的token
      const storage = useLocalStorage()
      storage.removeItem('token')
      storage.removeItem('refresh_token')
      
      // 为兼容性保留这些代码
      const tokenCookie = useCookie('auth_token')
      tokenCookie.value = null
      
      const refreshTokenCookie = useCookie('refresh_token')
      refreshTokenCookie.value = null
    },
    
    async register(username: string, email: string, password: string, inviteCode: string, confirmPassword: string) {
      try {
        if (!username || !email || !password) {
          console.error('注册失败: 用户名、邮箱和密码不能为空')
          return { success: false, error: '用户名、邮箱和密码不能为空' }
        }
        
        // 基本验证
        if (password.length < 8) {
          console.error('注册失败: 密码长度不能小于8位')
          return { success: false, error: '密码长度不能小于8位' }
        }
        
        console.log('准备注册用户:', { username, email, invite_code: inviteCode })
        
        const api = await useApi()
        const response = await api.user.register({ 
          username, 
          email, 
          password,
          password2: password,
          invite_code: inviteCode 
        })
        
        console.log('注册响应:', response)
        
        // 检查API响应格式
        if (response && response.code !== undefined) {
          // 新的API响应格式
          if (response.code === 0) {
            // 成功
            return { success: true }
          } else {
            // 失败，服务器返回了错误信息
            console.error('注册失败:', response.message)
            return { 
              success: false, 
              error: response.message || '注册失败'
            }
          }
        } else {
          // 旧的API响应格式或其他响应
          return { success: true }
        }
      } catch (error) {
        console.error('注册失败:', error)
        return { 
          success: false, 
          error: error instanceof Error ? error.message : '注册失败，请稍后再试'
        }
      }
    },
    
    // 初始化认证状态 (从localStorage恢复)
    initAuth() {
      // 检查是否在客户端环境
      if (typeof window === 'undefined') {
        console.log('在服务器端，跳过认证初始化')
        return false
      }
      
      // 优先从localStorage获取token
      const storage = useLocalStorage()
      let token = storage.getItem('token')
      let refreshToken = storage.getItem('refresh_token')
      
      // 如果localStorage中没有，尝试从cookie获取
      if (!token) {
        const tokenCookie = useCookie('auth_token')
        const refreshTokenCookie = useCookie('refresh_token')
        
        if (tokenCookie.value) {
          token = tokenCookie.value
          refreshToken = refreshTokenCookie.value
          
          // 将cookie中的token同步到localStorage
          if (token) {
            storage.setItem('token', token)
          }
          if (refreshToken) {
            storage.setItem('refresh_token', refreshToken)
          }
        }
      }
      
      if (token) {
        this.token = token
        this.refreshToken = refreshToken
        this.isAuthenticated = true
        this.fetchUserProfile()
        
        console.log('用户登录状态恢复成功')
        return true
      }
      
      return false
    }
  }
})
