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
  telegramConnected: boolean
  telegramUsername: string
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
    error: null,
    telegramConnected: false,
    telegramUsername: ''
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
    },
    
    // Get Telegram connection status
    getTelegramStatus: (state) => {
      return {
        connected: state.telegramConnected,
        username: state.telegramUsername
      }
    }
  },
  
  actions: {
    // 获取用户的所有心愿单
    async fetchUserWishlists() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        console.error('Failed to fetch wishlists: User not logged in')
        return { success: false, error: 'Please log in first' }
      }
      
      console.log('Starting to fetch wishlist list, authentication status:', authStore.isAuthenticated, 'token:', authStore.token)
      
      this.loading = true
      this.error = null
      
      try {
        // Use the wrapped API call
        const response = await api.wishlist.getUserWishlists()
        console.log('Wishlist data:', response)
        
        // Correctly handle paginated response format
        let wishlists: Wishlist[] = []
        if (response && response.data && response.data.results) {
          // API returns paginated data
          wishlists = response.data.results as Wishlist[]
        } else if (Array.isArray(response)) {
          // Compatible with direct array return
          wishlists = response as Wishlist[]
        }
        
        console.log('Parsed wishlist list:', wishlists)
        
        // Update wishlist list
        this.userWishlists = wishlists
        
        // Force reactive update
        this.userWishlists = [...this.userWishlists]
        
        // If there are wishlists but no current wishlist selected, select the first one
        if (this.userWishlists.length > 0 && !this.currentWishlistId) {
          this.currentWishlistId = this.userWishlists[0].id
        }
        
        return { success: true, wishlists: this.userWishlists }
      } catch (error: any) {
        console.error('Failed to fetch wishlists:', error)
        this.error = error.message || 'Failed to fetch wishlists'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Set current selected wishlist
    setCurrentWishlist(wishlistId: string) {
      if (this.userWishlists.some(w => w.id === wishlistId)) {
        this.currentWishlistId = wishlistId
      }
    },
    
    // Get public wishlist list
    async fetchPublicWishlists() {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const wishlists = await api.wishlist.getPublic()
        this.publicWishlists = wishlists
      } catch (error: any) {
        console.error('Failed to fetch public wishlists:', error)
        this.error = error.message || 'Failed to fetch public wishlists'
      } finally {
        this.loading = false
      }
    },
    
    // Get wishlist by share code
    async fetchWishlistByShareCode(shareCode: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const wishlist = await api.wishlist.getByShareCode(shareCode)
        this.sharedWishlist = wishlist
      } catch (error: any) {
        console.error('Failed to fetch shared wishlist:', error)
        this.error = error.message || 'Failed to fetch shared wishlist'
      } finally {
        this.loading = false
      }
    },
    
    // Add product to specified wishlist
    async addToWishlist(product: any, wishlistId: string | null = null, customData = {}) {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        return { success: false, error: 'Please log in first' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        // If no wishlist ID is provided, use the current selected wishlist
        let finalWishlistId = wishlistId || this.currentWishlistId
        
        // If no wishlist ID, first get or create one
        if (!finalWishlistId) {
          // First check if user already has a wishlist
          if (this.userWishlists.length === 0) {
            // If no wishlist, first get user's wishlist
            await this.fetchUserWishlists()
          }
          
          // Again check if user has wishlists
          if (this.userWishlists.length > 0) {
            // If yes, use the first wishlist
            finalWishlistId = this.userWishlists[0].id
            this.currentWishlistId = finalWishlistId
            console.log('Using existing wishlist:', finalWishlistId)
          } else {
            // If no, create new wishlist
            console.log('No wishlist, creating new wishlist')
            const result = await this.createWishlist({
              name: `My Wishlist`,
              description: '',
              is_public: true
            })
            
            if (!result.success || !result.wishlist) {
              throw new Error('Failed to create wishlist')
            }
            
            finalWishlistId = result.wishlist.id
            this.currentWishlistId = finalWishlistId
            console.log('New wishlist created successfully:', finalWishlistId)
          }
        }
        
        // Again check if there is a valid wishlist ID
        if (!finalWishlistId) {
          throw new Error('Unable to determine which wishlist to add to')
        }
        
        // Prepare data to add to wishlist
        const itemData = {
          wishlist: finalWishlistId, // Specify wishlist ID
          product_id: product.id,
          description: product.description || '',
          priority: 'medium',
          ...customData
        }
        
        // Add to wishlist
        console.log('Adding product to wishlist, data:', itemData)
        const response = await api.wishlist.addItem(itemData)
        console.log('Adding product to wishlist response:', response)
        
        // Re-fetch wishlist to update data
        await this.fetchUserWishlists()
        
        return { success: true, wishlistId: finalWishlistId }
      } catch (error: any) {
        console.error('Failed to add to wishlist:', error)
        this.error = error.message || 'Failed to add to wishlist'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Remove product from wishlist
    async removeFromWishlist(itemId: string, wishlistId: string | null = null) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        await api.wishlist.removeItem(itemId)
        
        // Update local wishlist data
        const targetWishlistId = wishlistId || this.currentWishlistId
        if (targetWishlistId) {
          const wishlistIndex = this.userWishlists.findIndex(w => w.id === targetWishlistId)
          if (wishlistIndex !== -1) {
            this.userWishlists[wishlistIndex].items = this.userWishlists[wishlistIndex].items.filter(item => item.id !== itemId)
          }
        }
        
        return { success: true }
      } catch (error: any) {
        console.error('Failed to remove from wishlist:', error)
        this.error = error.message || 'Failed to remove from wishlist'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Get or create wishlist
    async createWishlist(data: { name: string, description: string, is_public: boolean }) {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        return { success: false, error: 'Please log in first' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        // First try to get user's current wishlist
        try {
          console.log('Trying to get user current wishlist')
          const currentWishlist = await api.wishlist.getCurrent()
          console.log('Get current wishlist response:', currentWishlist)
          
          if (currentWishlist && currentWishlist.id) {
            // Update local data
            const existingIndex = this.userWishlists.findIndex(w => w.id === currentWishlist.id)
            if (existingIndex >= 0) {
              // If exists, replace
              this.userWishlists[existingIndex] = currentWishlist
            } else {
              // If not exists, add
              this.userWishlists.push(currentWishlist)
            }
            this.currentWishlistId = currentWishlist.id
            
            // Force reactive update
            this.userWishlists = [...this.userWishlists]
            
            return { success: true, wishlist: currentWishlist }
          }
        } catch (err) {
          console.log('Failed to get current wishlist, trying to create new wishlist:', err)
        }
        
        // If no existing wishlist, try to create new
        // Ensure all necessary fields exist and have default values
        const wishlistData = {
          name: data.name || `My Wishlist`,
          description: data.description || '',
          is_public: typeof data.is_public === 'boolean' ? data.is_public : true
        }
        
        console.log('Starting to create wishlist, data format:', wishlistData)
        console.log('Authentication status:', authStore.isAuthenticated, 'token:', authStore.token)
        
        const newWishlist = await api.wishlist.create(wishlistData)
        console.log('Create wishlist response:', newWishlist)
        
        // Update local data
        if (newWishlist && newWishlist.id) {
          // First check if exists
          const existingIndex = this.userWishlists.findIndex(w => w.id === newWishlist.id)
          if (existingIndex >= 0) {
            // If exists, replace
            this.userWishlists[existingIndex] = newWishlist
          } else {
            // If not exists, add
            this.userWishlists.push(newWishlist)
          }
          this.currentWishlistId = newWishlist.id
          
          // Force reactive update
          this.userWishlists = [...this.userWishlists]
        }
        
        return { success: true, wishlist: newWishlist }
      } catch (error: any) {
        console.error('Failed to get or create wishlist:', error)
        this.error = error.message || 'Failed to get or create wishlist'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Update wishlist settings
    async updateWishlist(wishlistId: string, data: any) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const updatedWishlist = await api.wishlist.update(wishlistId, data)
        
        // Update local data
        const wishlistIndex = this.userWishlists.findIndex(w => w.id === wishlistId)
        if (wishlistIndex !== -1) {
          this.userWishlists[wishlistIndex] = { ...this.userWishlists[wishlistIndex], ...updatedWishlist }
        }
        
        return { success: true, wishlist: updatedWishlist }
      } catch (error: any) {
        console.error('Failed to update wishlist:', error)
        this.error = error.message || 'Failed to update wishlist'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Delete wishlist
    async deleteWishlist(wishlistId: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        await api.wishlist.delete(wishlistId)
        
        // Update local data
        this.userWishlists = this.userWishlists.filter(w => w.id !== wishlistId)
        
        // If the deleted wishlist is currently selected, reset the selection
        if (this.currentWishlistId === wishlistId) {
          this.currentWishlistId = this.userWishlists.length > 0 ? this.userWishlists[0].id : null
        }
        
        return { success: true }
      } catch (error: any) {
        console.error('Failed to delete wishlist:', error)
        this.error = error.message || 'Failed to delete wishlist'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Mark wishlist item as purchased
    async purchaseWishlistItem(data: any) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        // 如果是整个心愿单购买
        if (data.is_full_wishlist) {
          // 构建API请求数据
          const requestData: any = {
            wishlist_id: data.wishlist_id,
            buyer_name: data.buyer_name,
            payment_method: data.payment_method,
            transaction_id: data.transaction_id,
            is_full_wishlist: true
          }
          
          // 添加支付方式特定数据
          if (data.transaction_hash) {
            requestData.transaction_hash = data.transaction_hash
          }
          if (data.card_type) {
            requestData.card_type = data.card_type
          }
          if (data.last_four) {
            requestData.last_four = data.last_four
          }
          if (data.paypal_order_id) {
            requestData.paypal_order_id = data.paypal_order_id
          }
          if (data.charge_id) {
            requestData.charge_id = data.charge_id
          }
          
          // 调用API购买整个心愿单
          const result = await api.wishlist.purchaseFullWishlist(requestData)
          return { success: true, data: result }
        } else {
          // 单个商品购买
          const result = await api.wishlist.purchaseItem(data.item_id, {
            buyer_name: data.buyer_name,
            payment_method: data.payment_method,
            transaction_id: data.transaction_id,
            transaction_hash: data.transaction_hash,
            card_type: data.card_type,
            last_four: data.last_four,
            paypal_order_id: data.paypal_order_id,
            charge_id: data.charge_id
          })
          return { success: true, data: result }
        }
      } catch (error: any) {
        console.error('Failed to purchase wishlist item:', error)
        this.error = error.message || 'Failed to purchase wishlist item'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Purchase full wishlist (all unpurchased items)
    async purchaseFullWishlist(data: any) {
      return this.purchaseWishlistItem({ ...data, is_full_wishlist: true })
    },
    
    // Create payment for wishlist item
    async createPaymentForItem(itemId: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        // Call payment API to create payment - include notify flag for Telegram notification
        const payment = await api.payments.createForWishlistItem(itemId, { notify_telegram: true })
        
        return { success: true, payment }
      } catch (error: any) {
        console.error('Failed to create payment:', error)
        this.error = error.message || 'Failed to create payment'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Record wishlist view
    async recordWishlistView(wishlistId: string) {
      const api = useApi()
      
      try {
        const result = await api.wishlist.recordView(wishlistId)
        return { success: true, views: result.views }
      } catch (error: any) {
        console.error('Failed to record view:', error)
        return { success: false, error: error.message || 'Failed to record view' }
      }
    },
    
    // Get wishlist statistics
    async fetchWishlistStats(wishlistId: string) {
      const api = useApi()
      
      this.loading = true
      this.error = null
      
      try {
        const stats = await api.wishlist.getStats(wishlistId)
        this.currentStats = stats
        return { success: true, stats }
      } catch (error: any) {
        console.error('Failed to get wishlist statistics:', error)
        this.error = error.message || 'Failed to get wishlist statistics'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Get statistics for all wishlists
    async fetchAllWishlistStats() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        return { success: false, error: this.error }
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await api.wishlist.getAllStats()
        console.log('All wishlist statistics response:', response)
        
        // Correctly handle API response format
        const stats = response && response.data ? response.data : response
        this.allStats = stats
        return { success: true, stats }
      } catch (error: any) {
        console.error('Failed to get all wishlist statistics:', error)
        this.error = error.message || 'Failed to get all wishlist statistics'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Get wishlist share link
    async getWishlistShareLink(wishlistId: string) {
      const api = useApi()
      
      try {
        const result = await api.wishlist.getShareLink(wishlistId)
        return { success: true, shareLink: result.share_url, shareCode: result.share_code }
      } catch (error: any) {
        console.error('Failed to get share link:', error)
        return { success: false, error: error.message || 'Failed to get share link' }
      }
    },
    
    // Check if product is in any wishlist
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
        console.error('Failed to check if product is in wishlist:', error)
        return { inWishlist: false, error: error.message }
      }
    },
    
    // Generate Telegram connection token
    async generateTelegramToken() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        return { success: false, error: 'Please log in first' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await api.user.generateTelegramToken()
        return { success: true, token: response.token }
      } catch (error: any) {
        console.error('Failed to generate Telegram token:', error)
        this.error = error.message || 'Failed to generate Telegram token'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Check Telegram connection status
    async checkTelegramConnection() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        return { success: false, error: 'Please log in first' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await api.user.getTelegramStatus()
        this.telegramConnected = response.connected
        this.telegramUsername = response.username || ''
        return { 
          success: true, 
          connected: response.connected,
          username: response.username
        }
      } catch (error: any) {
        // 兼容后端未实现接口时，降级处理
        console.warn('Telegram status API error，降级为未连接:', error)
        this.telegramConnected = false
        this.telegramUsername = ''
        // 不弹窗报错，返回未连接
        return { success: true, connected: false, username: '' }
      } finally {
        this.loading = false
      }
    },
    
    // Disconnect Telegram
    async disconnectTelegram() {
      const api = useApi()
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.error = 'Please log in first'
        return { success: false, error: 'Please log in first' }
      }
      
      this.loading = true
      this.error = null
      
      try {
        await api.user.disconnectTelegram()
        this.telegramConnected = false
        this.telegramUsername = ''
        return { success: true }
      } catch (error: any) {
        console.error('Failed to disconnect Telegram:', error)
        this.error = error.message || 'Failed to disconnect Telegram'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // Clear wishlist state
    clearWishlistState() {
      this.userWishlists = []
      this.currentWishlistId = null
      this.sharedWishlist = null
      this.currentStats = null
      this.allStats = null
      this.error = null
      // Do not clear Telegram status on logout
    }
  }
})
