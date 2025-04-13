<template>
  <!-- Independent page without website header and footer -->
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-2">
    <div class="max-w-md mx-auto px-2">
      <NuxtLayout name="empty">
      
      <!-- Loading state -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <div class="relative">
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-gray-200"></div>
          <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-primary-500 absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-gray-600 animate-pulse">Loading wishlist...</p>
      </div>
      
      <!-- Wishlist details -->
      <div v-else-if="wishlist" class="bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-500 hover:shadow-2xl">
        <!-- 顶部装饰条 -->
        <div class="h-2 bg-gradient-to-r from-primary-400 via-primary-500 to-secondary-500"></div>
        
        <!-- 心愿单头部 - 使用浅色梦幻渐变 -->
        <div class="bg-gradient-to-r from-blue-100 via-purple-100 to-pink-100 p-4 text-center">
          <!-- 标题 -->
          <h1 class="text-2xl font-bold text-gray-800 mb-1">{{ wishlist.name === '我要钱' ? 'I Need Money' : wishlist.name }}</h1>
          
          <!-- 描述文字 -->
          <p v-if="wishlist.description" class="text-gray-600 text-sm italic mb-2">{{ wishlist.description }}</p>
        </div>
        
        <!-- Wishlist content -->
        <div class="p-8" ref="itemsSection">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Wishlist
            </h2>
            
            <div class="flex items-center text-sm text-gray-500">
              <span v-if="wishlist.items && wishlist.items.length > 0" class="bg-primary-50 text-primary-700 px-3 py-1 rounded-full font-medium">
                {{ wishlist.items.length }} items
              </span>
            </div>
          </div>
          
          <!-- Empty state -->
          <div v-if="!wishlist.items || !wishlist.items.length" class="text-center py-16 bg-gray-50 rounded-2xl border border-gray-100 shadow-inner">
            <div class="w-24 h-24 mx-auto bg-white rounded-full shadow-md flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900">Wishlist is empty</h3>
            <p class="mt-2 text-gray-600 max-w-md mx-auto">This wishlist has no items yet. Please check back later.</p>
          </div>
          
          <!-- Product carousel -->
          <div v-else class="relative">
            <!-- 移除了商品索引显示，将移动到商品卡片上 -->
            
            
            <!-- Carousel -->
            <div class="relative overflow-hidden rounded-2xl shadow-lg">
              <!-- 添加明显的左右箭头按钮 -->
              <button 
                v-if="wishlist.items.length > 1"
                @click="prevItem"
                class="absolute left-2 top-1/2 transform -translate-y-1/2 z-30 bg-white/80 rounded-full p-2 shadow-md hover:bg-white transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <button 
                v-if="wishlist.items.length > 1"
                @click="nextItem"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 z-30 bg-white/80 rounded-full p-2 shadow-md hover:bg-white transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <!-- Swipe indicators -->
              <div v-if="wishlist.items.length > 1" class="absolute bottom-2 left-0 right-0 z-20 flex justify-center space-x-2">
                <div 
                  v-for="(_, index) in wishlist.items" 
                  :key="index"
                  class="h-2 w-2 rounded-full transition-all duration-300"
                  :class="index === currentItemIndex ? 'bg-white scale-125' : 'bg-white/50'"
                ></div>
              </div>
              
              <!-- 移除了隐藏的左右点击区域，改用明显的按钮 -->
              
              <!-- 商品卡片 -->
              <div 
                v-for="(item, index) in wishlist.items" 
                :key="item.id"
                v-show="index === currentItemIndex"
                class="bg-white rounded-2xl overflow-hidden shadow-lg transition-all duration-300 relative"
                :class="{'opacity-90 bg-gray-50': item.purchased}"
              >
                <!-- 已实现标记 -->
                <div 
                  v-if="item.purchased" 
                  class="absolute top-0 right-0 z-30 w-full h-12 flex items-center justify-center bg-gradient-to-r from-green-500 to-green-600 text-white font-bold shadow-lg"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Fulfilled by {{ item.purchased_by || 'Anonymous' }}
                </div>
                
                <!-- 商品图片 - 竖构图 -->
                <div 
                  class="relative w-full overflow-hidden" 
                  style="height: 120vw; max-height: 500px; min-height: 400px; aspect-ratio: 5/6;"
                >
                  <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10"></div>
                  <img 
                    v-if="item.image" 
                    :src="item.image" 
                    :alt="item.title" 
                    class="w-full h-full object-cover object-center transition-transform duration-700 hover:scale-110"
                  >
                  <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  
                  <!-- 价格标签 - 移动到右上角 -->
                  <div class="absolute top-4 right-4 z-20 flex items-center">
                    <div class="bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full shadow-lg flex items-center">
                      <span class="text-base font-bold text-primary-600">¥{{ formatPrice(item.price) }}</span>
                      <span v-if="item.original_price && item.original_price !== item.price" class="text-xs text-gray-500 line-through ml-1">
                        ¥{{ formatPrice(item.original_price) }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- 商品索引显示 -->
                  <div 
                    v-if="wishlist.items.length > 1" 
                    class="absolute top-4 left-4 z-20 px-3 py-1 rounded-full shadow-md text-xs font-bold bg-gray-700/70 text-white"
                  >
                    {{ currentItemIndex + 1 }} / {{ wishlist.items.length }}
                  </div>
                  
                  <!-- 商品标题（图片上叠加） -->
                  <div class="absolute bottom-0 left-0 right-0 z-10 p-4 text-white">
                    <h3 class="text-lg font-bold line-clamp-2"><!-- 减小字体，允许显示两行 -->
                      {{ item.title }}
                    </h3>
                  </div>
                </div>
                
                <!-- 商品信息 -->
                <div class="p-5">
                  <!-- 商品描述 -->
                  <div v-if="item.description" class="mb-4">
                    <p class="text-gray-700 text-sm line-clamp-2">
                      {{ item.description }}
                    </p>
                  </div>
                  
                  <!-- 商品属性 -->
                  <div class="flex items-center justify-between text-xs text-gray-500 mb-4">
                    <div class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Added on {{ formatDate(item.added_at) }}
                    </div>
                    
                    <div class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                      {{ wishlist.owner_name }}'s wish
                    </div>
                  </div>
                  
                  <!-- 总金额和按钮区域 -->
                  <div v-if="!item.purchased" class="mt-4">
                    <!-- 总金额显示 - 放在一排 -->
                    <div class="mb-3 flex items-center justify-between px-1">
                      <div class="text-xs text-gray-500">Total Amount:</div>
                      <div class="text-lg font-bold text-primary-600">${{ formatPrice(getTotalAmount()) }}</div>
                    </div>
                    
                    <button 
                      @click="purchaseDirectly(item)"
                      class="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-bold py-3 px-4 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Fulfill This Wish
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 帮助提示文字，放在商品轮播下方 -->
            <div class="text-center mt-6 mb-2 px-4">
              <p class="text-sm font-medium text-gray-700 mb-1">Help <span class="font-semibold text-primary-600">{{ wishlist.owner_name }}</span> fulfill wishes</p>
              <p class="text-xs text-gray-500">Your support will help them realize their wishes</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 未找到心愿单 -->
      <div v-else-if="!loading && !wishlist" class="bg-white rounded-lg shadow-sm p-8 text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Wishlist Not Found</h3>
        <p class="mt-1 text-gray-600">This wishlist doesn't exist or has been deleted</p>
        <NuxtLink to="/" class="mt-4 btn btn-primary inline-block">
          Back to Home
        </NuxtLink>
      </div>
      
      <!-- 购买确认模态框 -->
      <div v-if="purchasingItem" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Confirm Purchase</h3>
          
          <p class="text-gray-600 mb-6">
            Are you sure you want to purchase "{{ purchasingItem.title }}" for {{ wishlist?.owner_name }}?
          </p>
          
          <div class="mb-6">
            <label for="buyer-name" class="block text-sm font-medium text-gray-700 mb-1">Your Name</label>
            <input 
              id="buyer-name"
              v-model="buyerName" 
              type="text" 
              class="input"
              placeholder="Enter your name (will be shown to the wishlist owner)"
            >
          </div>
          
          <div class="flex justify-end space-x-3">
            <button 
              @click="purchasingItem = null"
              class="btn btn-outline"
            >
              Cancel
            </button>
            <button 
              @click="confirmPurchase"
              class="btn btn-primary"
              :disabled="formSubmitting || !buyerName"
            >
              {{ formSubmitting ? 'Processing...' : 'Confirm Purchase' }}
            </button>
          </div>
        </div>
      </div>
      </NuxtLayout>
    </div>
  </div>
</template>

<script setup>
// 路由参数
const route = useRoute()
const shareCode = computed(() => route.params.code)

// 获取状态管理
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()
const cartStore = useCartStore()

// 状态
const loading = ref(true)
const wishlist = ref(null)
const stats = ref(null)
const showShareModal = ref(false)
const purchasingItem = ref(null)
const formSubmitting = ref(false)
const buyerName = ref('')
const currentItemIndex = ref(0) // 当前轮播商品索引

// 触摸滑动相关状态
const touchStartX = ref(0)
const touchEndX = ref(0)

// 获取心愿单详情
const fetchSharedWishlist = async () => {
  try {
    loading.value = true
    await wishlistStore.fetchWishlistByShareCode(shareCode.value)
    wishlist.value = wishlistStore.sharedWishlist
    
    // 记录浏览
    if (wishlist.value) {
      recordView()
      fetchStats()
    }
  } catch (error) {
    console.error('获取心愿单失败:', error)
  } finally {
    loading.value = false
  }
}

// 记录浏览量
const recordView = async () => {
  try {
    const api = useApi()
    await api.wishlist.recordShareView(shareCode.value)
  } catch (error) {
    console.error('记录浏览量失败:', error)
  }
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const api = useApi()
    const response = await api.wishlist.getShareStats(shareCode.value)
    stats.value = response.data
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

// 获取心愿单总金额
const getTotalAmount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items
    .reduce((sum, item) => sum + parseFloat(item.price || 0), 0)
}

// 轮播控制函数 - 上一个商品
const prevItem = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return
  if (currentItemIndex.value <= 0) {
    currentItemIndex.value = wishlist.value.items.length - 1
  } else {
    currentItemIndex.value--
  }
}

// 轮播控制函数 - 下一个商品
const nextItem = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return
  if (currentItemIndex.value >= wishlist.value.items.length - 1) {
    currentItemIndex.value = 0
  } else {
    currentItemIndex.value++
  }
}

// 触摸滑动处理函数
const handleTouchStart = (event) => {
  event.stopPropagation() // 阻止事件冒泡
  touchStartX.value = event.touches[0].clientX
  console.log('Touch start:', touchStartX.value) // 添加日志
}

const handleTouchEnd = (event) => {
  event.stopPropagation() // 阻止事件冒泡
  touchEndX.value = event.changedTouches[0].clientX
  console.log('Touch end:', touchEndX.value) // 添加日志
  handleSwipe()
}

const handleSwipe = () => {
  // 设置最小滑动距离以触发切换
  const minSwipeDistance = 30 // 减小最小滑动距离要求
  const swipeDistance = touchEndX.value - touchStartX.value
  
  console.log('Swipe distance:', swipeDistance) // 添加日志以便调试
  
  if (swipeDistance > minSwipeDistance) {
    // 向右滑动，显示上一个商品
    prevItem()
  } else if (swipeDistance < -minSwipeDistance) {
    // 向左滑动，显示下一个商品
    nextItem()
  }
}

// 添加到购物车
const addToCart = async (item) => {
  try {
    await cartStore.addToCart({
      product_id: item.product_id,
      quantity: 1,
      wishlist_item_id: item.id, // 添加心愿单商品ID，用于标记这是为他人购买
      wishlist_id: wishlist.value.id,
      // 其他必要的商品信息
    })
    alert('已添加到购物车')
  } catch (error) {
    console.error('添加到购物车失败:', error)
    alert('添加失败，请重试')
  }
}

// 立即购买
const purchaseDirectly = (item) => {
  // 如果用户已登录，直接显示购买确认框
  if (authStore.isAuthenticated) {
    purchasingItem.value = item
    // 默认使用用户昵称
    buyerName.value = authStore.user?.nickname || ''
  } else {
    // 未登录则先跳转到登录页
    navigateTo(`/login?redirect=${encodeURIComponent(route.fullPath)}`)
  }
}

// 确认购买
const confirmPurchase = async () => {
  if (!buyerName.value) {
    alert('请输入您的名字')
    return
  }
  
  formSubmitting.value = true
  
  try {
    await wishlistStore.purchaseWishlistItem({
      wishlist_id: wishlist.value.id,
      item_id: purchasingItem.value.id,
      buyer_name: buyerName.value
    })
    
    // 更新本地数据
    const itemIndex = wishlist.value.items.findIndex(item => item.id === purchasingItem.value.id)
    if (itemIndex !== -1) {
      wishlist.value.items[itemIndex] = {
        ...wishlist.value.items[itemIndex],
        purchased: true,
        purchased_by: buyerName.value
      }
    }
    
    purchasingItem.value = null
    alert('购买成功！感谢您帮助实现心愿')
  } catch (error) {
    console.error('购买失败:', error)
    alert('购买失败，请重试')
  } finally {
    formSubmitting.value = false
  }
}

// 获取当前页面URL
const getCurrentUrl = () => {
  return window.location.href
}

// 复制当前页面URL
const copyCurrentUrl = () => {
  navigator.clipboard.writeText(getCurrentUrl())
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

// 页面加载时获取数据
onMounted(() => {
  fetchSharedWishlist()
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
