<template>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 返回按钮 -->
      <div class="mb-6">
        <NuxtLink to="/wishlist" class="flex items-center text-gray-600 hover:text-primary-600">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回心愿单列表
        </NuxtLink>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <!-- 心愿单详情 -->
      <div v-else-if="wishlist" class="bg-white rounded-lg shadow-sm overflow-hidden">
        <!-- 心愿单头部 -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex justify-between items-start">
            <div>
              <div class="flex items-center">
                <h1 class="text-2xl font-bold text-gray-900">{{ wishlist.name }}</h1>
                <span 
                  class="ml-3 px-2 py-1 text-xs font-medium rounded-full"
                  :class="wishlist.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                >
                  {{ wishlist.is_public ? '公开' : '私密' }}
                </span>
              </div>
              <p v-if="wishlist.description" class="mt-2 text-gray-600">{{ wishlist.description }}</p>
              <div class="mt-2 flex items-center text-sm text-gray-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <span>{{ stats?.views_count || 0 }} 次浏览</span>
                <span class="mx-2">•</span>
                <span>创建于 {{ formatDate(wishlist.created_at) }}</span>
              </div>
            </div>
            
            <div class="flex space-x-2">
              <button 
                v-if="wishlist.is_public"
                @click="showShareModal = true"
                class="btn btn-outline flex items-center"
                title="分享"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                </svg>
                分享
              </button>
              
              <button 
                @click="showEditModal = true"
                class="btn btn-outline flex items-center"
                title="编辑"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                编辑
              </button>
            </div>
          </div>
          
          <!-- 统计数据 -->
          <div class="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="stat-card">
              <div class="stat-title">商品数量</div>
              <div class="stat-value">{{ wishlist.items?.length || 0 }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-title">已购买</div>
              <div class="stat-value">{{ getCompletedItemsCount() }}</div>
              <div class="stat-desc">{{ Math.round((getCompletedItemsCount() / (wishlist.items?.length || 1)) * 100) }}%</div>
            </div>
            <div class="stat-card">
              <div class="stat-title">已付款</div>
              <div class="stat-value">{{ getPaymentCompletedCount() }}</div>
              <div class="stat-desc">金额: ¥{{ formatPrice(getPaymentCompletedAmount()) }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-title">未付款</div>
              <div class="stat-value">{{ getUnpaidCount() }}</div>
              <div class="stat-desc">金额: ¥{{ formatPrice(getUnpaidAmount()) }}</div>
            </div>
          </div>
          
          <!-- 进度指示器 -->
          <div v-if="wishlist.items && wishlist.items.length" class="mt-4">
            <div class="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                class="bg-primary-600 h-2.5 rounded-full" 
                :style="`width: ${(getCompletedItemsCount() / wishlist.items.length) * 100}%`"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- 心愿单内容 -->
        <div class="p-6">
          <!-- 无商品状态 -->
          <div v-if="!wishlist.items || !wishlist.items.length" class="text-center py-10">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">心愿单还是空的</h3>
            <p class="mt-1 text-gray-600">浏览商品并添加到心愿单中</p>
            <NuxtLink to="/products" class="mt-4 btn btn-primary inline-block">
              浏览商品
            </NuxtLink>
          </div>
          
          <!-- 商品列表 -->
          <div v-else class="space-y-6">
            <div 
              v-for="item in wishlist.items" 
              :key="item.id"
              class="flex flex-col md:flex-row border border-gray-200 rounded-lg overflow-hidden hover:shadow-sm transition-shadow"
              :class="{'opacity-75': item.purchased}"
            >
              <!-- 商品图片 -->
              <div class="w-full md:w-48 h-48 bg-gray-100 flex-shrink-0">
                <img 
                  v-if="item.image" 
                  :src="item.image" 
                  :alt="item.title" 
                  class="w-full h-full object-cover"
                >
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              
              <!-- 商品信息 -->
              <div class="flex-1 p-4 flex flex-col">
                <div class="flex-1">
                  <div class="flex justify-between">
                    <h3 class="text-lg font-medium text-gray-900">
                      <NuxtLink :to="`/products/${item.product_id}`" class="hover:text-primary-600">
                        {{ item.title }}
                      </NuxtLink>
                    </h3>
                    
                    <!-- 已购买标签 -->
                    <span 
                      v-if="item.purchased"
                      class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800"
                    >
                      已购买
                    </span>
                  </div>
                  
                  <p v-if="item.description" class="mt-1 text-sm text-gray-600 line-clamp-2">
                    {{ item.description }}
                  </p>
                  
                  <!-- 价格信息 -->
                  <div class="mt-2 flex items-baseline">
                    <span class="text-xl font-bold text-primary-600">¥{{ formatPrice(item.price) }}</span>
                    <span v-if="item.original_price" class="ml-2 text-sm text-gray-500 line-through">
                      ¥{{ formatPrice(item.original_price) }}
                    </span>
                  </div>
                  
                  <!-- 添加时间 -->
                  <div class="mt-2 text-xs text-gray-500">
                    添加于 {{ formatDate(item.added_at) }}
                  </div>
                  
                  <!-- 购买者信息 -->
                  <div v-if="item.purchased && item.purchased_by" class="mt-2 text-sm text-gray-600">
                    <span class="font-medium text-green-600">{{ item.purchased_by }}</span> 已为您购买此商品
                  </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="mt-4 flex justify-end space-x-2">
                  <button 
                    v-if="!item.purchased"
                    @click="addToCart(item)"
                    class="btn btn-primary py-2 text-sm"
                  >
                    加入购物车
                  </button>
                  
                  <button 
                    v-if="!item.purchased"
                    @click="removeFromWishlist(item)"
                    class="btn btn-outline py-2 text-sm"
                  >
                    移除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 未找到心愿单 -->
      <div v-else-if="!loading && !wishlist" class="bg-white rounded-lg shadow-sm p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">未找到心愿单</h3>
        <p class="mt-1 text-gray-600">该心愿单不存在或已被删除</p>
        <NuxtLink to="/wishlist" class="mt-4 btn btn-primary inline-block">
          返回心愿单列表
        </NuxtLink>
      </div>
      
      <!-- 编辑心愿单模态框 -->
      <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">编辑心愿单</h3>
          
          <div class="space-y-4">
            <div>
              <label for="wishlist-name" class="block text-sm font-medium text-gray-700 mb-1">名称</label>
              <input 
                id="wishlist-name"
                v-model="wishlistForm.name" 
                type="text" 
                class="input"
                placeholder="我的心愿单"
              >
            </div>
            
            <div>
              <label for="wishlist-description" class="block text-sm font-medium text-gray-700 mb-1">描述</label>
              <textarea 
                id="wishlist-description"
                v-model="wishlistForm.description" 
                class="input"
                rows="3"
                placeholder="描述您的心愿单..."
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
                公开心愿单（允许他人查看和购买）
              </label>
            </div>
          </div>
          
          <div class="mt-6 flex justify-end space-x-3">
            <button 
              @click="showEditModal = false"
              class="btn btn-outline"
            >
              取消
            </button>
            <button 
              @click="saveWishlist"
              class="btn btn-primary"
              :disabled="formSubmitting"
            >
              {{ formSubmitting ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 分享心愿单模态框 -->
      <div v-if="showShareModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">分享心愿单</h3>
          
          <p class="text-sm text-gray-600 mb-4">复制以下链接分享给您的朋友，让他们帮您实现愿望：</p>
          
          <div class="flex items-center mb-6">
            <input 
              type="text" 
              :value="getShareUrl()" 
              readonly 
              class="input flex-1"
            >
            <button 
              @click="copyShareUrl()"
              class="ml-2 p-2 bg-gray-100 rounded-md hover:bg-gray-200"
              title="复制链接"
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
              @click="showShareModal = false"
              class="btn btn-outline"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 路由参数
const route = useRoute()
const wishlistId = computed(() => route.params.id)

// 获取状态管理
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()
const cartStore = useCartStore()

// 状态
const loading = ref(true)
const wishlist = ref(null)
const stats = ref(null)
const showEditModal = ref(false)
const showShareModal = ref(false)
const formSubmitting = ref(false)

// 表单数据
const wishlistForm = ref({
  name: '',
  description: '',
  is_public: true
})

// 获取心愿单详情
const fetchWishlistDetail = async () => {
  loading.value = true
  try {
    // 使用直接的fetch API调用替代store方法
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase
    console.log('使用API基础URL:', baseUrl)
    
    const response = await fetch(`${baseUrl}/v1/wishlist/lists/${wishlistId.value}/?site=default`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`)
    }
    
    const data = await response.json()
    console.log('心愿单详情响应:', data)
    
    if (data && data.code === 0 && data.data) {
      wishlist.value = data.data
      
      // 初始化表单数据
      wishlistForm.value = {
        name: wishlist.value.name,
        description: wishlist.value.description || '',
        is_public: wishlist.value.is_public
      }
      
      // 记录浏览量
      await recordView()
      
      // 获取统计数据
      await fetchStats()
    } else {
      throw new Error(data.message || '获取心愿单详情失败')
    }
  } catch (error) {
    console.error('获取心愿单详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 记录浏览量
const recordView = async () => {
  try {
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase
    
    const response = await fetch(`${baseUrl}/v1/wishlist/lists/${wishlistId.value}/view/?site=default`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    const data = await response.json()
    console.log('记录浏览量响应:', data)
  } catch (error) {
    console.error('记录浏览量失败:', error)
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase
    
    const response = await fetch(`${baseUrl}/v1/wishlist/lists/${wishlistId.value}/stats/?site=default`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    const data = await response.json()
    console.log('获取统计数据响应:', data)
    
    if (data && data.code === 0 && data.data) {
      stats.value = data.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取已购买商品数量
const getCompletedItemsCount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items.filter(item => item.purchased).length
}

// 获取已付款商品数量
const getPaymentCompletedCount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items.filter(item => item.payment_completed).length
}

// 获取已付款商品金额
const getPaymentCompletedAmount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items
    .filter(item => item.payment_completed)
    .reduce((sum, item) => sum + parseFloat(item.price || 0), 0)
}

// 获取未付款商品数量
const getUnpaidCount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items.filter(item => !item.payment_completed).length
}

// 获取未付款商品金额
const getUnpaidAmount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items
    .filter(item => !item.payment_completed)
    .reduce((sum, item) => sum + parseFloat(item.price || 0), 0)
}

// 从心愿单移除商品
const removeFromWishlist = async (item) => {
  if (!confirm('确定要从心愿单中移除此商品吗？')) return
  
  try {
    await wishlistStore.removeItemFromWishlist(wishlist.value.id, item.id)
    // 重新获取心愿单详情
    fetchWishlistDetail()
  } catch (error) {
    console.error('移除商品失败:', error)
    alert('移除失败，请重试')
  }
}

// 添加到购物车
const addToCart = async (item) => {
  try {
    await cartStore.addToCart({
      product_id: item.product_id,
      quantity: 1,
      // 其他必要的商品信息
    })
    alert('已添加到购物车')
  } catch (error) {
    console.error('添加到购物车失败:', error)
    alert('添加失败，请重试')
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
    await wishlistStore.updateWishlist(wishlist.value.id, wishlistForm.value)
    // 更新本地数据
    wishlist.value = {
      ...wishlist.value,
      name: wishlistForm.value.name,
      description: wishlistForm.value.description,
      is_public: wishlistForm.value.is_public
    }
    showEditModal.value = false
  } catch (error) {
    console.error('保存心愿单失败:', error)
    alert('保存失败，请重试')
  } finally {
    formSubmitting.value = false
  }
}

// 获取分享链接
const getShareUrl = () => {
  if (!wishlist.value || !wishlist.value.share_code) return ''
  
  const baseUrl = window.location.origin
  return `${baseUrl}/wishlist/share/${wishlist.value.share_code}`
}

// 复制分享链接
const copyShareUrl = () => {
  const url = getShareUrl()
  navigator.clipboard.writeText(url)
    .then(() => {
      alert('链接已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制')
    })
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '0.00'
  return Number(price).toFixed(2)
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

// 记录心愿单浏览
const recordWishlistView = async () => {
  if (!wishlist.value?.id) return
  
  try {
    await api.wishlist.recordView(wishlist.value.id)
    // 更新统计数据
    fetchWishlistStats()
  } catch (error) {
    console.error('记录浏览失败:', error)
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchWishlistDetail()
  // 延迟一点记录浏览，确保wishlist已加载
  setTimeout(() => {
    recordWishlistView()
  }, 1000)
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
</style>
