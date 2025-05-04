import { defineNuxtPlugin } from 'nuxt/app'
import { createApp } from 'vue'
import Toast, { PluginOptions, POSITION, useToast } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

export default defineNuxtPlugin((nuxtApp) => {
  const options: PluginOptions = {
    position: POSITION.TOP_RIGHT,
    timeout: 3000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: 'button',
    icon: true,
    rtl: false,
    maxToasts: 3,
    transition: 'Vue-Toastification__fade'
  }

  // 将 Toast 插件添加到 Nuxt 应用
  nuxtApp.vueApp.use(Toast, options)
  
  // 提供辅助方法来在组件中使用
  return {
    provide: {
      toast: {
        success: (message: string) => {
          // 使用 window.alert 作为备选方案，确保消息始终能够显示
          window.alert(message)
        },
        error: (message: string) => {
          window.alert(`错误: ${message}`)
        },
        info: (message: string) => {
          window.alert(`提示: ${message}`)
        },
        warning: (message: string) => {
          window.alert(`警告: ${message}`)
        }
      }
    }
  }
}) 