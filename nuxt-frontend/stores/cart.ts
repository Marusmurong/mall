import { defineStore } from 'pinia'

interface CartItem {
  id: string
  name: string
  price: number
  image: string
  quantity: number
  [key: string]: any
}

interface CartState {
  items: CartItem[]
  loading: boolean
}

export const useCartStore = defineStore('cart', {
  state: (): CartState => ({
    items: [],
    loading: false
  }),
  
  getters: {
    cartItems: (state) => state.items,
    
    cartCount: (state) => {
      return state.items.reduce((total, item) => total + item.quantity, 0)
    },
    
    cartTotal: (state) => {
      return state.items.reduce((total, item) => total + (item.price * item.quantity), 0)
    },
    
    isCartEmpty: (state) => state.items.length === 0
  },
  
  actions: {
    addToCart(product: any, quantity = 1) {
      const existingItem = this.items.find(item => item.id === product.id)
      
      if (existingItem) {
        // 如果商品已在购物车中，增加数量
        existingItem.quantity += quantity
      } else {
        // 否则添加新商品到购物车
        this.items.push({
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image || product.images?.[0]?.image || '',
          quantity
        })
      }
      
      // 保存到本地存储
      this.saveCart()
    },
    
    updateQuantity(productId: string, quantity: number) {
      const item = this.items.find(item => item.id === productId)
      
      if (item) {
        if (quantity > 0) {
          item.quantity = quantity
        } else {
          // 如果数量为0或负数，从购物车中移除
          this.removeFromCart(productId)
          return
        }
        
        // 保存到本地存储
        this.saveCart()
      }
    },
    
    removeFromCart(productId: string) {
      const index = this.items.findIndex(item => item.id === productId)
      
      if (index !== -1) {
        this.items.splice(index, 1)
        
        // 保存到本地存储
        this.saveCart()
      }
    },
    
    clearCart() {
      this.items = []
      
      // 保存到本地存储
      this.saveCart()
    },
    
    // 保存购物车到本地存储
    saveCart() {
      if (process.client) {
        localStorage.setItem('cart', JSON.stringify(this.items))
      }
    },
    
    // 从本地存储加载购物车
    loadCart() {
      if (process.client) {
        const savedCart = localStorage.getItem('cart')
        
        if (savedCart) {
          try {
            this.items = JSON.parse(savedCart)
          } catch (error) {
            console.error('加载购物车失败:', error)
            this.items = []
          }
        }
      }
    }
  }
})
