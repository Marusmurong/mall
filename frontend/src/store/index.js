import { createStore } from 'vuex'
import api from '../api/alokai'

export default createStore({
  state: {
    site: {
      config: null,
      loading: true
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
    async fetchSiteConfig({ commit }) {
      try {
        const config = await api.getSiteConfig()
        commit('setSiteConfig', config)
      } catch (error) {
        console.error('获取站点配置失败:', error)
      }
    },
    async fetchUser({ commit }) {
      try {
        const user = await api.getUser()
        commit('setUser', user)
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },
    async addToCart({ commit }, product) {
      try {
        const result = await api.addToCart(product)
        commit('updateCart', result)
      } catch (error) {
        console.error('添加到购物车失败:', error)
      }
    },
    async addToWishlist({ commit }, product) {
      try {
        const result = await api.addToWishlist(product)
        commit('updateWishlist', result)
      } catch (error) {
        console.error('添加到心愿单失败:', error)
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
