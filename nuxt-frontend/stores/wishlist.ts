import { defineStore } from 'pinia'
import { useApi } from '../composables/useApi'
import { useAuthStore } from './auth'

interface WishlistItem {
  id: string
  title: string
  description: string
  price: number
  currency: string
  image: string
  priority: string
  purchased: boolean
  purchased_at: string | null
  purchased_by: any | null
  product: any | null
  [key: string]: any
}

interface Wishlist {
  id: string
  name: string
  description: string
  is_public: boolean
  share_code: string
  created_at: string
  updated_at: string
  items: WishlistItem[]
  [key: string]: any
}

interface WishlistStats {
  views_count: number
  purchased: {
    count: number
    amount: number
  }
  unpurchased: {
    count: number
    amount: number
  }
  payment_completed: {
    count: number
    amount: number
  }
}

interface WishlistState {
  userWishlists: Wishlist[]
  currentWishlistId: string | null
  publicWishlists: Wishlist[]
  sharedWishlist: Wishlist | null
  currentStats: WishlistStats | null
  allStats: WishlistStats | null
  loading: boolean
  error: string | null
}

export const useWishlistStore = defineStore('wishlist', {
  state: (): WishlistState => ({
    userWishlists: [],
    currentWishlistId: null,
    publicWishlists: [],
    sharedWishlist: null,
    currentStats: null,
    allStats: null,
    loading: false,
    error: null
  }),
  
  getters: {
    // 获取用户的所有心愿单
    getUserWishlists: (state) => state.userWishlists,
    
    // 获取当前选中的心愿单
    getCurrentWishlist: (state) => {
      if (!state.currentWishlistId) return null
      return state.userWishlists.find(w => w.id === state.currentWishlistId) || null
    },
    
    // 获取当前心愿单中的商品
    getWishlistItems: (state) => {
      const currentWishlist = state.userWishlists.find(w => w.id === state.currentWishlistId)
      return currentWishlist?.items || []
    },
    
    // 获取公开的心愿单列表
    getPublicWishlists: (state) => state.publicWishlists,
    
    // 获取通过分享链接访问的心愿单
    getSharedWishlist: (state) => state.sharedWishlist,
    
    // 获取当前心愿单的统计数据
    getCurrentStats: (state) => state.currentStats,
    
    // 获取所有心愿单的统计数据
    getAllStats: (state) => state.allStats,
    
    // 检查商品是否在当前心愿单中
    isInCurrentWishlist: (state) => (productId: string) => {
      const currentWishlist = state.userWishlists.find(w => w.id === state.currentWishlistId)
      return currentWishlist?.items.some(item => item.product?.id === productId) || false
    },
    
    // 检查商品是否在任何心愿单中
    isInAnyWishlist: (state) => (productId: string) => {
      return state.userWishlists.some(wishlist => 
        wishlist.items.some(item => item.product?.id === productId)
      )
    },
    
    // 获取商品所在的所有心愿单
    getWishlistsContainingProduct: (state) => (productId: string) => {
      return state.userWishlists.filter(wishlist => 
        wishlist.items.some(item => item.product?.id === productId)
      )
    }
  },
  
  actions: {
    // 获取用户的所有心愿单
    async fetchUserWishlists() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = '请先登录'
        console.error('获取心愿单失败: 用户未登录')
        return { success: false, error: '请先登录' }
      }
      
      console.log('开始获取心愿单列表, 认证状态:', authStore.isAuthenticated, '令牌:', authStore.token)
      
      this.loading = true
      this.error = null
      
      try {
        // 使用封装的API调用
        const response = await api.wishlist.getUserWishlists()
        console.log('获取心愿单数据:', response)
        
        // 正确处理分页格式的响应
        let wishlists: Wishlist[] = []
        
        if (response && response.data && Array.isArray(response.data.results)) {
          // API返回的是分页格式的数据 {code: 0, message: "success", data: {results: [...]}}
          wishlists = response.data.results as Wishlist[]
          console.log('从分页格式中提取心愿单列表:', wishlists)
        } else if (response && Array.isArray(response.results)) {
          // API直接返回分页格式 {results: [...]}
          wishlists = response.results as Wishlist[]
          console.log('从results字段提取心愿单列表:', wishlists)
        } else if (Array.isArray(response)) {
          // API直接返回数组格式
          wishlists = response as Wishlist[]
          console.log('API直接返回数组格式:', wishlists)
        } else if (response && typeof response === 'object') {
          // 尝试查找可能的心愿单数据
          console.log('尝试从其他响应格式中找到心愿单数据')
          if (response.data && Array.isArray(response.data)) {
            wishlists = response.data as Wishlist[]
          } else if (response.wishlists && Array.isArray(response.wishlists)) {
            wishlists = response.wishlists as Wishlist[]
          }
        }
        
        console.log('解析后的心愿单列表:', wishlists)
        
        // 更新心愿单列表
        this.userWishlists = wishlists
        
        // 强制触发响应式更新
        this.userWishlists = [...this.userWishlists]
        
        // 如果有心愿单但没有选中当前心愿单，则选择第一个
        if (this.userWishlists.length > 0 && !this.currentWishlistId) {
          this.currentWishlistId = this.userWishlists[0].id
        }
        
        return { success: true, wishlists: this.userWishlists }
      } catch (error: any) {
        console.error('获取心愿单失败:', error)
        this.error = error.message || '获取心愿单失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 设置当前选中的心愿单
    setCurrentWishlist(wishlistId: string) {
      if (this.userWishlists.some(w => w.id === wishlistId)) {
        this.currentWishlistId = wishlistId
      }
    },
    
    // 获取公开的心愿单列表
    async fetchPublicWishlists() {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const wishlists = await api.wishlist.getPublic()
        this.publicWishlists = wishlists
      } catch (error: any) {
        console.error('获取公开心愿单失败:', error)
        this.error = error.message || '获取公开心愿单失败'
      } finally {
        this.loading = false
      }
    },
    
    // 通过分享码获取心愿单
    async fetchWishlistByShareCode(shareCode: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        console.log('开始从API获取分享心愿单，分享码:', shareCode)
        const response = await api.wishlist.getByShareCode(shareCode)
        console.log('API响应:', response)
        
        // 处理API响应格式
        if (response && response.code === 0 && response.data) {
          // 标准API封装格式 {code: 0, message: "success", data: {...}}
          console.log('使用标准API响应格式中的data字段:', response.data)
          this.sharedWishlist = response.data
        } else {
          // 直接使用响应
          console.log('使用直接API响应:', response)
          this.sharedWishlist = response
        }
        
        console.log('分享心愿单数据设置完成:', this.sharedWishlist)
      } catch (error: any) {
        console.error('获取分享心愿单失败:', error)
        this.error = error.message || '获取分享心愿单失败'
      } finally {
        this.loading = false
      }
    },
    
    // 添加商品到心愿单
    async addToWishlist(product: any, wishlistId: string | null = null, customData = {}) {
      const api = useApi()
      const authStore = useAuthStore()
      
      // 验证商品数据
      if (!product || !product.id) {
        console.error('添加到心愿单失败: 无效的商品数据')
        this.error = '无效的商品数据'
        return { success: false, error: '无效的商品数据' }
      }
      
      // 确保用户已登录
      if (!authStore.isAuthenticated) {
        console.error('添加到心愿单失败: 用户未登录')
        this.error = '请先登录'
        return { success: false, error: '请先登录' }
      }
      
      // 必须提供心愿单ID
      if (!wishlistId) {
        console.error('添加到心愿单失败: 未指定心愿单')
        this.error = '请选择要添加到的心愿单'
        return { success: false, error: '请选择要添加到的心愿单' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        // 准备添加商品的数据
        const itemData = {
          wishlist: wishlistId,
          product_id: product.id,
          description: product.description || '',
          priority: 'medium',
          ...customData
        }
        
        // 添加到心愿单
        console.log('添加商品到心愿单，数据:', itemData)
        const response = await api.wishlist.addItem(itemData)
        console.log('添加商品到心愿单响应:', response)
        
        // 重新获取心愿单以更新数据
        await this.fetchUserWishlists()
        
        return { success: true, wishlistId: wishlistId }
      } catch (error: any) {
        console.error('添加到心愿单失败:', error)
        this.error = error.message || '添加到心愿单失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 从心愿单中移除商品
    async removeFromWishlist(itemId: string, wishlistId: string | null = null) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        await api.wishlist.removeItem(itemId)
        
        // 更新本地心愿单数据
        const targetWishlistId = wishlistId || this.currentWishlistId
        if (targetWishlistId) {
          const wishlistIndex = this.userWishlists.findIndex(w => w.id === targetWishlistId)
          if (wishlistIndex !== -1) {
            this.userWishlists[wishlistIndex].items = this.userWishlists[wishlistIndex].items.filter(item => item.id !== itemId)
          }
        }
        
        return { success: true }
      } catch (error: any) {
        console.error('从心愿单移除失败:', error)
        this.error = error.message || '从心愿单移除失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 创建心愿单
    async createWishlist(data: { name: string, description: string, is_public: boolean }) {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = '请先登录'
        return { success: false, error: '请先登录' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        // 确保所有必要字段都存在并有默认值
        const wishlistData = {
          name: data.name || `我的心愿单`,
          description: data.description || '',
          is_public: typeof data.is_public === 'boolean' ? data.is_public : true
        }
        
        console.log('开始创建心愿单, 数据格式:', wishlistData)
        
        const newWishlist = await api.wishlist.create(wishlistData)
        console.log('创建心愿单响应:', newWishlist)
        
        // 更新本地数据
        if (newWishlist && newWishlist.id) {
          // 添加到心愿单列表
          this.userWishlists.push(newWishlist)
          this.currentWishlistId = newWishlist.id
          
          // 强制触发响应式更新
          this.userWishlists = [...this.userWishlists]
        }
        
        return { success: true, wishlist: newWishlist }
      } catch (error: any) {
        console.error('创建心愿单失败:', error)
        this.error = error.message || '创建心愿单失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 更新心愿单设置
    async updateWishlist(wishlistId: string, data: any) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const updatedWishlist = await api.wishlist.update(wishlistId, data)
        
        // 更新本地数据
        const wishlistIndex = this.userWishlists.findIndex(w => w.id === wishlistId)
        if (wishlistIndex !== -1) {
          this.userWishlists[wishlistIndex] = { ...this.userWishlists[wishlistIndex], ...updatedWishlist }
        }
        
        return { success: true, wishlist: updatedWishlist }
      } catch (error: any) {
        console.error('更新心愿单失败:', error)
        this.error = error.message || '更新心愿单失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 删除心愿单
    async deleteWishlist(wishlistId: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        await api.wishlist.delete(wishlistId)
        
        // 更新本地数据
        this.userWishlists = this.userWishlists.filter(w => w.id !== wishlistId)
        
        // 如果删除的是当前选中的心愿单，重置选中状态
        if (this.currentWishlistId === wishlistId) {
          this.currentWishlistId = this.userWishlists.length > 0 ? this.userWishlists[0].id : null
        }
        
        return { success: true }
      } catch (error: any) {
        console.error('删除心愿单失败:', error)
        this.error = error.message || '删除心愿单失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 标记心愿单商品为已购买
    async purchaseWishlistItem(itemId: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const updatedItem = await api.wishlist.purchaseItem(itemId)
        
        // 更新本地数据 - 在所有心愿单中查找并更新
        for (let i = 0; i < this.userWishlists.length; i++) {
          const itemIndex = this.userWishlists[i].items.findIndex(item => item.id === itemId)
          if (itemIndex !== -1) {
            this.userWishlists[i].items[itemIndex] = updatedItem
          }
        }
        
        // 更新共享心愿单中的商品状态
        if (this.sharedWishlist) {
          const itemIndex = this.sharedWishlist.items.findIndex(item => item.id === itemId)
          if (itemIndex !== -1) {
            this.sharedWishlist.items[itemIndex] = updatedItem
          }
        }
        
        return { success: true, item: updatedItem }
      } catch (error: any) {
        console.error('标记为已购买失败:', error)
        this.error = error.message || '标记为已购买失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 对WishlistItem创建支付
    async createPaymentForItem(itemId: string) {
      const api = useApi()
      
      try {
        // 调用支付API创建支付
        const payment = await api.payments.createPayment({
          wishlist_item: itemId,
          payment_method: 'standard'
        })
        
        return { success: true, payment }
      } catch (error: any) {
        console.error('创建支付失败:', error)
        return { success: false, error: error.message || '创建支付失败' }
      }
    },
    
    // 记录心愿单浏览量
    async recordWishlistView(wishlistId: string) {
      const api = useApi()
      
      try {
        const result = await api.wishlist.recordView(wishlistId)
        return { success: true, views: result.views }
      } catch (error: any) {
        console.error('记录浏览量失败:', error)
        return { success: false, error: error.message || '记录浏览量失败' }
      }
    },
    
    // 获取心愿单统计数据
    async fetchWishlistStats(wishlistId: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const stats = await api.wishlist.getStats(wishlistId)
        this.currentStats = stats
        return { success: true, stats }
      } catch (error: any) {
        console.error('获取心愿单统计数据失败:', error)
        this.error = error.message || '获取心愿单统计数据失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 获取所有心愿单的统计数据
    async fetchAllWishlistStats() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = '请先登录'
        return { success: false, error: this.error }
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await api.wishlist.getAllStats()
        console.log('获取所有心愿单统计数据响应:', response)
        
        // 正确处理API响应格式
        const stats = response && response.data ? response.data : response
        this.allStats = stats
        return { success: true, stats }
      } catch (error: any) {
        console.error('获取所有心愿单统计数据失败:', error)
        this.error = error.message || '获取所有心愿单统计数据失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 获取心愿单分享链接
    async getWishlistShareLink(wishlistId: string) {
      const api = useApi()
      
      try {
        const result = await api.wishlist.getShareLink(wishlistId)
        return { success: true, shareLink: result.share_url, shareCode: result.share_code }
      } catch (error: any) {
        console.error('获取分享链接失败:', error)
        return { success: false, error: error.message || '获取分享链接失败' }
      }
    },
    
    // 检查商品是否在任何心愿单中
    async checkProductInWishlist(productId: string) {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        return { inWishlist: false }
      }
      
      try {
        const result = await api.wishlist.checkProductInWishlist(productId)
        return result
      } catch (error: any) {
        console.error('检查商品是否在心愿单中失败:', error)
        return { inWishlist: false, error: error.message }
      }
    },
    
    // 清除心愿单状态
    clearWishlistState() {
      this.userWishlists = []
      this.currentWishlistId = null
      this.sharedWishlist = null
      this.currentStats = null
      this.allStats = null
      this.error = null
    }
  }
})
