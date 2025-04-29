import axios from 'axios'

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 处理未授权的情况
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // 用户相关
  async login(credentials) {
    return api.post('/auth/login', credentials)
      .then(response => {
        localStorage.setItem('auth_token', response.data.token)
        return response.data
      })
  },

  async getUser() {
    return api.get('/user').then(response => response.data)
  },

  // 商品相关
  async getProducts(params) {
    return api.get('/products', { params }).then(response => response.data)
  },

  async getProduct(id) {
    return api.get(`/products/${id}`).then(response => response.data)
  },

  // 购物车相关
  async addToCart(product) {
    return api.post('/cart', product).then(response => response.data)
  },

  async getCart() {
    return api.get('/cart').then(response => response.data)
  },

  // 心愿单相关
  async addToWishlist(product) {
    return api.post('/wishlist', product).then(response => response.data)
  },

  async getWishlist() {
    return api.get('/wishlist').then(response => response.data)
  }
}
