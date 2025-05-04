<template>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面标题 -->
      <div class="flex justify-between items-center mb-8">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">我的心愿单</h1>
          <p class="mt-2 text-gray-600">创建心愿单并与朋友分享，帮助实现你的愿望</p>
        </div>
        
        <button 
          v-if="isAuthenticated"
          @click="showCreateModal = true"
          class="btn btn-primary flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          创建心愿单
        </button>
      </div>
      
      <!-- 未登录状态 -->
      <div v-if="!isAuthenticated" class="bg-white rounded-lg shadow-sm p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <h2 class="mt-4 text-lg font-medium text-gray-900">Please Login First</h2>
        <p class="mt-2 text-gray-600">Login to create and manage your wishlists</p>
        <div class="mt-6">
          <NuxtLink to="/login" class="btn btn-primary">
            Login
          </NuxtLink>
          <NuxtLink to="/register" class="btn btn-outline ml-4">
            Register
          </NuxtLink>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-else-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <!-- 统计数据 -->
      <div v-if="isAuthenticated && allStats" class="bg-white rounded-lg shadow-sm p-6 mb-8">
        <h2 class="text-xl font-bold text-gray-900 mb-4">统计概览</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="stat-card">
            <div class="stat-title">心愿单数量</div>
            <div class="stat-value">{{ allStats.wishlists_count || 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-title">总浏览量</div>
            <div class="stat-value">{{ allStats.views_count || 0 }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-title">已购买商品</div>
            <div class="stat-value">{{ allStats.purchased?.count || 0 }}</div>
            <div class="stat-desc">金额: ${{ formatPrice(allStats.purchased?.amount || 0) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-title">未购买商品</div>
            <div class="stat-value">{{ allStats.unpurchased?.count || 0 }}</div>
            <div class="stat-desc">金额: ${{ formatPrice(allStats.unpurchased?.amount || 0) }}</div>
          </div>
        </div>
      </div>
      
      
      <!-- 心愿单列表 -->
      <div v-if="wishlists && wishlists.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="wishlist in wishlists" 
          :key="wishlist.id"
          class="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow"
        >
          <!-- 心愿单头部 -->
          <div class="p-4 border-b border-gray-200">
            <div class="flex justify-between items-start">
              <div>
                <h2 class="text-xl font-bold text-gray-900 mb-1">{{ wishlist.name }}</h2>
                <p v-if="wishlist.description" class="text-sm text-gray-600 line-clamp-2">{{ wishlist.description }}</p>
              </div>
              
              <!-- 公开/私密标签 -->
              <span 
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="wishlist.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ wishlist.is_public ? '公开' : '私密' }}
              </span>
            </div>
            
            <!-- 浏览量和创建时间 -->
            <div class="mt-2 flex items-center text-xs text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>{{ wishlistStats[wishlist.id]?.views_count || 0 }} 次浏览</span>
              <span class="mx-2">•</span>
              <span>创建于 {{ formatDate(wishlist.created_at) }}</span>
            </div>
          </div>
          
          <!-- 心愿单内容预览 -->
          <div class="p-4">
            <div class="grid grid-cols-2 gap-2 mb-3">
              <div class="stat-mini">
                <div class="stat-mini-title">商品</div>
                <div class="stat-mini-value">{{ wishlist.items?.length || 0 }}</div>
              </div>
              <div class="stat-mini">
                <div class="stat-mini-title">已购买</div>
                <div class="stat-mini-value text-green-600">{{ getCompletedItemsCount(wishlist) }}</div>
              </div>
              <div class="stat-mini">
                <div class="stat-mini-title">已付款</div>
                <div class="stat-mini-value text-blue-600">{{ getPaymentCompletedCount(wishlist) }}</div>
              </div>
              <div class="stat-mini">
                <div class="stat-mini-label">总金额</div>
                <div class="stat-mini-value">${{ formatPrice(getTotalAmount(wishlist)) }}</div>
              </div>
            </div>
            
            <!-- 商品预览 -->
            <div v-if="wishlist.items && wishlist.items.length" class="grid grid-cols-4 gap-2 mb-4">
              <div 
                v-for="(item, index) in wishlist.items.slice(0, 4)" 
                :key="item.id"
                class="aspect-square bg-gray-100 rounded overflow-hidden relative"
              >
                <img 
                  v-if="item.image" 
                  :src="item.image" 
                  :alt="item.title" 
                  class="w-full h-full object-cover"
                >
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                
                <!-- 已购买标记 -->
                <div 
                  v-if="item.purchased"
                  class="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                
                <!-- 更多商品提示 -->
                <div 
                  v-if="index === 3 && wishlist.items.length > 4"
                  class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center text-white font-medium"
                >
                  +{{ wishlist.items.length - 4 }}
                </div>
              </div>
            </div>
            
            <div v-else class="text-sm text-gray-500 mb-4">
              暂无商品，快去添加吧
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex space-x-2">
              <NuxtLink 
                to="/categories"
                class="flex-1 btn btn-success py-2 text-sm flex items-center justify-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                添加商品
              </NuxtLink>
              
              <NuxtLink 
                :to="`/wishlist/${wishlist.id}`"
                class="flex-1 btn btn-primary py-2 text-sm"
              >
                View Details
              </NuxtLink>
              
              <button 
                v-if="wishlist.is_public"
                @click="showShareModal(wishlist)"
                class="p-2 bg-gray-100 rounded hover:bg-gray-200"
                title="分享"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
              </button>
              
              <button 
                @click="showEditModal(wishlist)"
                class="p-2 bg-gray-100 rounded hover:bg-gray-200"
                title="编辑"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              
              <button 
                @click="confirmDeleteWishlist(wishlist)"
                class="p-2 bg-gray-100 rounded hover:bg-gray-200"
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 无心愿单状态 -->
      <div v-else-if="!loading && isAuthenticated && !wishlists.length" class="bg-white rounded-lg shadow-sm p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">You haven't created any wishlists yet</h3>
        <p class="mt-1 text-gray-600">Create a wishlist, add items you like, and share with friends</p>
        <button 
          @click="showCreateModal = true"
          class="mt-4 btn btn-primary"
        >
          创建心愿单
        </button>
      </div>
      
      <!-- 创建/编辑心愿单模态框 -->
      <div v-if="showCreateModal || editingWishlist" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingWishlist ? 'Edit Wishlist' : 'Create Wishlist' }}
          </h3>
          
          <div class="space-y-4">
            <div>
              <label for="wishlist-name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input 
                id="wishlist-name"
                v-model="wishlistForm.name" 
                type="text" 
                class="input"
                placeholder="My Wishlist"
              >
            </div>
            
            <div>
              <label for="wishlist-description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea 
                id="wishlist-description"
                v-model="wishlistForm.description" 
                class="input"
                rows="3"
                placeholder="Describe your wishlist..."
              ></textarea>
            </div>
            
            <div class="flex items-center">
              <input 
                id="wishlist-public"
                v-model="wishlistForm.is_public" 
                type="checkbox" 
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              >
              <label for="wishlist-public" class="ml-2 block text-sm text-gray-900">
                Public wishlist (allow others to view and purchase)
              </label>
            </div>
          </div>
          
          <div class="mt-6 flex justify-end space-x-3">
            <button 
              @click="cancelEdit"
              class="btn btn-outline"
            >
              取消
            </button>
            <button 
              @click="saveWishlist"
              class="btn btn-primary"
              :disabled="formSubmitting"
            >
              {{ formSubmitting ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分享心愿单模态框 -->
      <div v-if="sharingWishlist" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Share Wishlist</h3>
          
          <p class="text-sm text-gray-600 mb-4">Copy the link below to share with your friends and let them help fulfill your wishes:</p>
          
          <div class="flex items-center mb-6">
            <input 
              type="text" 
              :value="getShareUrl(sharingWishlist)" 
              readonly 
              class="input flex-1"
            >
            <button 
              @click="copyShareUrl(sharingWishlist)"
              class="ml-2 p-2 bg-gray-100 rounded-md hover:bg-gray-200"
              title="Copy Link"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
          
          <div class="flex justify-center space-x-4 mb-6">
            <!-- 社交分享按钮 -->
            <button class="p-2 bg-blue-500 text-white rounded-full hover:bg-blue-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            </button>
            <button class="p-2 bg-blue-400 text-white rounded-full hover:bg-blue-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723 10.054 10.054 0 01-3.127 1.184 4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
            </button>
            <button class="p-2 bg-green-500 text-white rounded-full hover:bg-green-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/>
              </svg>
            </button>
          </div>
          
          <div class="mt-2 flex justify-end">
            <button 
              @click="sharingWishlist = null"
              class="btn btn-outline"
            >
              Close
            </button>
          </div>
        </div>
      </div>
      
      <!-- 删除确认模态框 -->
      <div v-if="deletingWishlist" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Confirm Delete</h3>
          
          <p class="text-gray-600 mb-6">
            Are you sure you want to delete the wishlist "{{ deletingWishlist.name }}"? This action cannot be undone, and all items in the wishlist will also be deleted.
          </p>
          
          <div class="flex justify-end space-x-3">
            <button 
              @click="deletingWishlist = null"
              class="btn btn-outline"
            >
              取消
            </button>
            <button 
              @click="deleteWishlist"
              class="btn bg-red-600 text-white hover:bg-red-700"
              :disabled="formSubmitting"
            >
              {{ formSubmitting ? 'Deleting...' : 'Confirm Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 获取状态管理
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()
const api = useApi()

// 状态
const loading = ref(false)
const showCreateModal = ref(false)
const editingWishlist = ref(null)
const sharingWishlist = ref(null)
const deletingWishlist = ref(null)
const formSubmitting = ref(false)
const wishlistStats = ref({})
const allStats = ref(null)
const userWishlists = ref([])

// 计算属性
const isAuthenticated = computed(() => authStore.isAuthenticated)
// 直接使用本地状态而不是从 store 获取
const wishlists = computed(() => userWishlists.value)

// 表单数据
const wishlistForm = ref({
  name: '',
  description: '',
  is_public: true
})

// 获取心愿单数据
const fetchWishlists = async () => {
  loading.value = true
  try {
    // 检查认证状态
    console.log('认证状态:', authStore.isAuthenticated)
    console.log('认证令牌:', authStore.token)
    
    if (!authStore.isAuthenticated) {
      console.error('用户未登录')
      return
    }
    
    // 清除现有数据
    userWishlists.value = []
    wishlistStats.value = {}
    allStats.value = null
    
    // 获取心愿单列表
    console.log('开始获取心愿单列表...')
    let wishlistResponse;
    try {
      // 使用相对路径而不是硬编码的URL
      const runtimeConfig = useRuntimeConfig()
      const baseUrl = runtimeConfig.public.apiBaseUrl
      console.log('使用API基础URL:', baseUrl)
      
      wishlistResponse = await fetch(`${baseUrl}/wishlist/lists/?site=default`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'include' // 包含cookie
      })
      console.log('心愿单列表响应状态:', wishlistResponse.status)
    } catch (error) {
      console.error('获取心愿单列表错误:', error)
      throw error
    }
    
    const wishlistData = await wishlistResponse.json()
    console.log('直接获取心愿单列表响应:', wishlistData)
    
    // 处理响应数据
    if (wishlistData && wishlistData.code === 0 && wishlistData.data && wishlistData.data.results) {
      // 直接设置心愿单列表
      userWishlists.value = wishlistData.data.results
      console.log('设置心愿单列表:', userWishlists.value)
    }
    
    // 获取统计数据
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBaseUrl
    const statsResponse = await fetch(`${baseUrl}/wishlist/stats/?site=default`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    const statsData = await statsResponse.json()
    console.log('直接获取统计数据响应:', statsData)
    
    if (statsData && statsData.code === 0 && statsData.data) {
      allStats.value = statsData.data
      console.log('设置统计数据:', allStats.value)
    }
    
    // 强制刷新视图
    nextTick(() => {
      console.log('刷新视图后的心愿单列表:', wishlists.value)
      console.log('刷新视图后的统计数据:', allStats.value)
      
      // 获取各个心愿单的浏览统计数据
      fetchWishlistStats()
    })
  } catch (error) {
    console.error('获取心愿单失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取所有心愿单统计数据
const fetchAllStats = async () => {
  try {
    const result = await wishlistStore.fetchAllWishlistStats()
    if (result.success) {
      allStats.value = result.stats
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取各个心愿单的统计数据
const fetchWishlistStats = async () => {
  try {
    const stats = {}
    for (const wishlist of wishlists.value) {
      const result = await wishlistStore.fetchWishlistStats(wishlist.id)
      if (result.success) {
        stats[wishlist.id] = result.stats
      }
    }
    wishlistStats.value = stats
  } catch (error) {
    console.error('获取心愿单统计数据失败:', error)
  }
}

// 显示编辑模态框
const showEditModal = (wishlist) => {
  editingWishlist.value = wishlist
  wishlistForm.value = {
    name: wishlist.name,
    description: wishlist.description || '',
    is_public: wishlist.is_public
  }
}

// 显示分享模态框
const showShareModal = (wishlist) => {
  sharingWishlist.value = wishlist
}

// 确认删除心愿单
const confirmDeleteWishlist = (wishlist) => {
  deletingWishlist.value = wishlist
}

// 取消编辑
const cancelEdit = () => {
  showCreateModal.value = false
  editingWishlist.value = null
  wishlistForm.value = {
    name: '',
    description: '',
    is_public: true
  }
}

// 保存心愿单
const saveWishlist = async () => {
  if (!wishlistForm.value.name) {
    alert('请输入心愿单名称')
    return
  }
  
  formSubmitting.value = true
  
  try {
    // 确保所有必要字段都存在并有默认值
    const wishlistData = {
      name: wishlistForm.value.name || `我的心愿单`,
      description: wishlistForm.value.description || '',
      is_public: typeof wishlistForm.value.is_public === 'boolean' ? wishlistForm.value.is_public : true
    }
    
    console.log('准备创建心愿单，数据:', wishlistData)
    
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBaseUrl
    
    let response;
    if (editingWishlist.value) {
      // 更新心愿单
      response = await fetch(`${baseUrl}/wishlist/lists/${editingWishlist.value.id}/?site=default`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(wishlistData)
      })
    } else {
      // 创建心愿单
      response = await fetch(`${baseUrl}/wishlist/lists/?site=default`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(wishlistData)
      })
    }
    
    const result = await response.json()
    console.log('心愿单保存响应:', result)
    
    // 关闭模态框
    cancelEdit()
    
    // 重新获取心愿单列表数据
    await fetchWishlists()
    
    // 显示成功消息
    if (result && result.code === 0) {
      alert('心愿单保存成功')
    } else {
      alert(result.message || '保存失败，请重试')
    }
  } catch (error) {
    console.error('保存心愿单失败:', error)
    alert('保存失败，请重试')
  } finally {
    formSubmitting.value = false
  }
}

// 删除心愿单
const deleteWishlist = async () => {
  if (!deletingWishlist.value) return
  
  formSubmitting.value = true
  
  try {
    await wishlistStore.deleteWishlist(deletingWishlist.value.id)
    deletingWishlist.value = null
    
    // 重新获取心愿单列表数据
    await fetchWishlists()
  } catch (error) {
    console.error('删除心愿单失败:', error)
    alert('删除失败，请重试')
  } finally {
    formSubmitting.value = false
  }
}

// 获取已购买商品数量
const getCompletedItemsCount = (wishlist) => {
  if (!wishlist.items || !wishlist.items.length) return 0
  return wishlist.items.filter(item => item.purchased).length
}

// 获取已付款商品数量
const getPaymentCompletedCount = (wishlist) => {
  if (!wishlist.items || !wishlist.items.length) return 0
  return wishlist.items.filter(item => item.payment_completed).length
}

// 获取心愿单总金额
const getTotalAmount = (wishlist) => {
  if (!wishlist.items || !wishlist.items.length) return 0
  return wishlist.items.reduce((sum, item) => sum + (parseFloat(item.price) || 0), 0)
}

// 获取分享链接
const getShareUrl = (wishlist) => {
  if (!wishlist || !wishlist.share_code) return ''
  
  // 使用客户端专用的方式获取域名
  const baseUrl = process.client ? window.location.origin : ''
  return `${baseUrl}/wishlist/share/${wishlist.share_code}`
}

// 复制分享链接
const copyShareUrl = (wishlist) => {
  const url = getShareUrl(wishlist)
  navigator.clipboard.writeText(url)
    .then(() => {
      alert('链接已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制')
    })
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// 格式化价格
const formatPrice = (price) => {
  return parseFloat(price).toFixed(2)
}

// 页面加载时获取数据
onMounted(() => {
  if (isAuthenticated.value) {
    fetchWishlists()
  }
})

// 监听认证状态变化
watch(() => isAuthenticated.value, (newValue) => {
  if (newValue) {
    fetchWishlists()
  }
})
</script>

<style scoped>
.stat-card {
  background-color: #f9fafb;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stat-title {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.stat-desc {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.stat-mini {
  background-color: #f9fafb;
  border-radius: 0.375rem;
  padding: 0.5rem;
}

.stat-mini-title {
  font-size: 0.75rem;
  color: #6b7280;
}

.stat-mini-value {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}
</style>
