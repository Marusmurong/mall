import { useAuthStore } from '~/stores/auth'

export default defineNuxtPlugin(async (nuxtApp) => {
  // 在应用启动时初始化认证状态
  const authStore = useAuthStore()
  
  // 调用初始化方法
  authStore.initAuth()
  
  // 提供一个全局方法来检查是否已认证
  nuxtApp.provide('isAuthenticated', () => authStore.isAuthenticated)
  
  // 添加全局导航守卫，处理需要认证的路由
  nuxtApp.hook('page:start', () => {
    // 可以在这里添加导航守卫逻辑
    // 例如，检查用户是否有权限访问某些页面
  })
})
