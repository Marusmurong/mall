<template>
  <div class="min-h-screen flex flex-col">
    <!-- 顶部导航栏 -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- 左侧Logo和导航链接 -->
          <div class="flex">
            <div class="flex-shrink-0 flex items-center relative">
              <!-- 网站LOGO -->
              <NuxtLink to="/" class="flex items-center">
                <img v-if="siteLogo" :src="siteLogo" alt="Mall Logo" class="h-8 w-auto" />
                <span v-else class="text-2xl font-bold text-primary-600">Mall</span>
              </NuxtLink>
              
              <!-- 管理员模式开关 (仅在开发环境显示) -->
              <div v-if="isDev" class="absolute -top-4 -right-4 z-10">
                <button 
                  @click="adminModeEnabled = !adminModeEnabled" 
                  class="px-2 py-0.5 text-xs rounded-full" 
                  :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
                >
                  {{ adminModeEnabled ? '管理' : '普通' }}
                </button>
              </div>
              
              <!-- LOGO上传按钮 -->
              <div v-if="adminModeEnabled" class="absolute top-full left-0 mt-1 bg-white shadow-md rounded-md p-2 z-50">
                <button 
                  @click="showLogoUpload = true"
                  class="text-xs px-2 py-1 bg-blue-500 text-white rounded flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  更换LOGO
                </button>
              </div>
              
              <!-- LOGO上传弹窗 -->
              <div v-if="showLogoUpload" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
                  <h3 class="text-lg font-bold mb-4">上传网站LOGO</h3>
                  
                  <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">选择图片</label>
                    <input 
                      type="file" 
                      accept="image/*" 
                      @change="handleLogoFileChange"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                  </div>
                  
                  <!-- 预览 -->
                  <div v-if="logoPreview" class="mb-4 p-4 border border-gray-200 rounded-md">
                    <p class="text-sm text-gray-500 mb-2">预览:</p>
                    <img :src="logoPreview" alt="Logo Preview" class="h-12 w-auto mx-auto">
                  </div>
                  
                  <div class="flex justify-end space-x-2">
                    <button 
                      @click="showLogoUpload = false" 
                      class="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700"
                    >
                      取消
                    </button>
                    <button 
                      @click="saveLogo"
                      class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm"
                      :disabled="!logoFile || isUploading"
                    >
                      {{ isUploading ? '上传中...' : '保存' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <nav class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <NuxtLink to="/" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                首页
              </NuxtLink>
              <NuxtLink to="/categories" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                分类
              </NuxtLink>
              <NuxtLink to="/wishlist" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                心愿单
              </NuxtLink>
            </nav>
          </div>
          
          <!-- 右侧用户菜单和购物车 -->
          <div class="flex items-center">
            <!-- 搜索框 -->
            <div class="hidden md:block">
              <div class="relative">
                <input type="text" placeholder="搜索商品..." class="input w-64" />
              </div>
            </div>
            
            <!-- 购物车图标 -->
            <NuxtLink to="/cart" class="ml-4 p-2 text-gray-500 hover:text-gray-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </NuxtLink>
            
            <!-- 用户菜单 -->
            <div class="ml-4 relative flex-shrink-0" ref="userMenuContainer">
              <!-- 未登录时显示登录按钮 -->
              <button v-if="!isLoggedIn" @click="showAuthModal = true" class="flex items-center text-sm rounded-full focus:outline-none">
                <span class="sr-only">用户登录</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </button>
              
              <!-- 已登录时显示用户信息和退出按钮 -->
              <div v-else class="flex items-center">
                <span class="text-sm text-gray-700 mr-2">您好，{{ authStore.user?.username || '用户' }}</span>
                <button @click="logout" class="text-sm text-red-500 hover:text-red-700">退出</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 移动端导航菜单 -->
      <div class="sm:hidden">
        <div class="pt-2 pb-3 space-y-1">
          <NuxtLink to="/" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
            首页
          </NuxtLink>
          <NuxtLink to="/categories" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
            分类
          </NuxtLink>
          <NuxtLink to="/wishlist" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
            心愿单
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex-grow">
      <slot />
    </main>

    <!-- 页脚 -->
    <footer class="bg-gray-800 text-white">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- 公司信息 -->
          <div>
            <h3 class="text-lg font-semibold mb-4">关于我们</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/about/company" class="text-gray-300 hover:text-white">公司简介</NuxtLink></li>
              <li><NuxtLink to="/info/about/contact" class="text-gray-300 hover:text-white">联系我们</NuxtLink></li>
              <li><NuxtLink to="/info/about/join" class="text-gray-300 hover:text-white">加入我们</NuxtLink></li>
            </ul>
          </div>
          
          <!-- 购物指南 -->
          <div>
            <h3 class="text-lg font-semibold mb-4">购物指南</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/shopping/process" class="text-gray-300 hover:text-white">购物流程</NuxtLink></li>
              <li><NuxtLink to="/info/shopping/payment" class="text-gray-300 hover:text-white">支付方式</NuxtLink></li>
              <li><NuxtLink to="/info/shopping/delivery" class="text-gray-300 hover:text-white">配送方式</NuxtLink></li>
            </ul>
          </div>
          
          <!-- 售后服务 -->
          <div>
            <h3 class="text-lg font-semibold mb-4">售后服务</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/service/return" class="text-gray-300 hover:text-white">退换货政策</NuxtLink></li>
              <li><NuxtLink to="/info/service/warranty" class="text-gray-300 hover:text-white">保修条款</NuxtLink></li>
              <li><NuxtLink to="/info/service/faq" class="text-gray-300 hover:text-white">常见问题</NuxtLink></li>
            </ul>
          </div>
          
          <!-- 联系方式 -->
          <div>
            <h3 class="text-lg font-semibold mb-4">联系方式</h3>
            <ul class="space-y-2">
              <li class="flex items-center text-gray-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                400-123-4567
              </li>
              <li class="flex items-center text-gray-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                support@mall.com
              </li>
            </ul>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
          <p>© {{ new Date().getFullYear() }} Mall多站点电商系统. 保留所有权利.</p>
        </div>
      </div>
    </footer>
    <!-- 登录/注册弹窗 -->
    <AuthModal 
      :show="showAuthModal" 
      @close="showAuthModal = false" 
      @login-success="handleLoginSuccess" 
      @register-success="handleRegisterSuccess" 
    />
  </div>
</template>

<script setup>
// 默认布局组件
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import AuthModal from '~/components/AuthModal.vue'

// 使用auth store
const authStore = useAuthStore()

// 控制登录弹窗显示
const showAuthModal = ref(false)

// 网站LOGO相关状态
const siteLogo = ref('')
const showLogoUpload = ref(false)
const logoFile = ref(null)
const logoPreview = ref('')
const isUploading = ref(false)

// 管理员模式（开发环境临时功能）
const adminModeEnabled = ref(false)
const isDev = process.env.NODE_ENV === 'development'

// 使用计算属性获取登录状态
const isLoggedIn = computed(() => authStore.isAuthenticated)

// 登录成功处理
const handleLoginSuccess = () => {
  // 登录成功后关闭弹窗
  showAuthModal.value = false
  // 可以添加其他逻辑，如显示欢迎信息等
}

// 注册成功处理
const handleRegisterSuccess = () => {
  // 注册成功后切换到登录标签
  // 可以添加注册成功后的逻辑
}

// 退出登录
const logout = () => {
  authStore.logout()
}

// 处理LOGO文件选择
const handleLogoFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  logoFile.value = file
  
  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    logoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// 保存LOGO
const saveLogo = () => {
  if (!logoFile.value) return
  
  try {
    isUploading.value = true
    
    // 直接使用预览中的Base64数据
    siteLogo.value = logoPreview.value
    
    // 保存Base64数据到localStorage，以便页面刷新后仍能显示
    localStorage.setItem('siteLogoUrl', logoPreview.value)
    
    // 关闭上传弹窗
    showLogoUpload.value = false
    
    // 提示用户
    alert('LOGO已更新')
    
    // 重置上传状态
    setTimeout(() => {
      isUploading.value = false
    }, 500)
  } catch (error) {
    console.error('处理LOGO失败:', error)
    alert('处理失败，请重试')
    isUploading.value = false
  }
}

onMounted(() => {
  // 初始化认证状态
  authStore.initAuth()
  
  // 从localStorage加载LOGO URL
  const savedLogoUrl = localStorage.getItem('siteLogoUrl')
  if (savedLogoUrl) {
    siteLogo.value = savedLogoUrl
  }
})

// 监听登录状态变化
watch(isLoggedIn, (newValue) => {
  if (newValue) {
    // 用户登录后的逻辑
    console.log('用户已登录')
  } else {
    // 用户退出后的逻辑
    console.log('用户未登录')
  }
})
</script>

<style scoped>
/* 可以添加一些样式 */
</style>
