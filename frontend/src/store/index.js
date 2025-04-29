import { createStore } from 'vuex'
import api from '../api/api'

export default createStore({
  state: {
    site: {
      config: {
        name: 'Default Mall',
        theme: 'default',
        features: {
          wishlist: true,
          cart: true,
          user_profile: true
        }
      },
      loading: false
    },
    user: {
      isAuthenticated: false,
      profile: null
    },
    cart: {
      items: [],
      total: 0
    },
    wishlist: {
      items: [],
      total: 0
    }
  },
  mutations: {
    setSiteConfig(state, config) {
      state.site.config = config
      state.site.loading = false
    },
    setUser(state, user) {
      state.user.isAuthenticated = !!user
      state.user.profile = user
    },
    updateCart(state, { items, total }) {
      state.cart.items = items
      state.cart.total = total
    },
    updateWishlist(state, { items, total }) {
      state.wishlist.items = items
      state.wishlist.total = total
    }
  },
  actions: {
    async fetchUser({ commit }) {
      try {
        const user = await api.getUser()
        commit('setUser', user)
      } catch (error) {
        console.error('Failed to get user info:', error)
      }
    },
    async addToCart({ commit }, product) {
      try {
        const result = await api.addToCart(product)
        commit('updateCart', result)
      } catch (error) {
        console.error('Failed to add to cart:', error)
      }
    },
    async addToWishlist({ commit }, product) {
      try {
        const result = await api.addToWishlist(product)
        commit('updateWishlist', result)
      } catch (error) {
        console.error('Failed to add to wishlist:', error)
      }
    }
  },
  getters: {
    isSiteReady: state => !state.site.loading,
    isAuthenticated: state => state.user.isAuthenticated,
    cartItemCount: state => state.cart.items.length,
    wishlistItemCount: state => state.wishlist.items.length
  }
})
