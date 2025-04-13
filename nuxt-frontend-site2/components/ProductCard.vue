<template>
  <div class="card group">
    <!-- 商品图片 -->
    <div class="relative overflow-hidden aspect-square">
      <NuxtLink :to="`/products/${product.id}`">
        <img 
          :src="productImage" 
          :alt="product.name" 
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        >
      </NuxtLink>
      
      <!-- 快速操作按钮 -->
      <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100">
        <div class="flex space-x-2">
          <!-- 添加到购物车 -->
          <button 
            @click="addToCart"
            class="p-2 bg-white rounded-full shadow-md hover:bg-primary-50 transition-colors"
            title="添加到购物车"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </button>
          
          <!-- 添加到心愿单 -->
          <button 
            @click="toggleWishlist"
            class="p-2 bg-white rounded-full shadow-md hover:bg-primary-50 transition-colors"
            :title="isInWishlist ? '从心愿单移除' : '添加到心愿单'"
            :disabled="isCheckingWishlists"
            :class="{'opacity-50 cursor-wait': isCheckingWishlists}"
          >
            <svg v-if="isInWishlist" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          
          <!-- 快速查看 -->
          <NuxtLink 
            :to="`/products/${product.id}`"
            class="p-2 bg-white rounded-full shadow-md hover:bg-primary-50 transition-colors"
            title="查看详情"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </NuxtLink>
        </div>
      </div>
      
      <!-- 标签 -->
      <div class="absolute top-2 left-2 flex flex-col space-y-1">
        <span v-if="product.is_new" class="px-2 py-1 bg-green-500 text-white text-xs font-medium rounded">新品</span>
        <span v-if="product.is_hot" class="px-2 py-1 bg-red-500 text-white text-xs font-medium rounded">热销</span>
        <span v-if="hasDiscount" class="px-2 py-1 bg-orange-500 text-white text-xs font-medium rounded">
          {{ discountPercentage }}% 折扣
        </span>
      </div>
    </div>
    
    <!-- 商品信息 -->
    <div class="p-4">
      <!-- 分类 -->
      <div class="text-xs text-gray-500 mb-1">{{ product.category?.name || '未分类' }}</div>
      
      <!-- 商品名称 -->
      <h3 class="text-sm font-medium text-gray-900 mb-1 line-clamp-2">
        <NuxtLink :to="`/products/${product.id}`">{{ product.name }}</NuxtLink>
      </h3>
      
      <!-- 价格 -->
      <div class="flex items-center space-x-2">
        <span v-if="discountPrice" class="text-sm font-medium text-gray-900">¥{{ discountPrice }}</span>
        <span :class="[discountPrice ? 'text-xs text-gray-500 line-through' : 'text-sm font-medium text-gray-900']">
          ¥{{ product.price }}
        </span>
      </div>
      
      <!-- 评分 -->
      <div v-if="product.rating" class="flex items-center mt-1">
        <div class="flex">
          <template v-for="i in 5" :key="i">
            <svg 
              :class="[i <= Math.round(product.rating) ? 'text-yellow-400' : 'text-gray-300']"
              xmlns="http://www.w3.org/2000/svg" 
              class="h-4 w-4" 
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </template>
        </div>
        <span class="text-xs text-gray-500 ml-1">{{ product.rating_count || 0 }}评</span>
      </div>
    </div>
  </div>
  
  <!-- 心愿单选择弹窗 -->
  <WishlistSelectModal 
    :show="showWishlistModal" 
    :product="props.product" 
    @close="showWishlistModal = false"
    @added="handleWishlistAdded"
  />
</template>

<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

// 导入心愿单选择弹窗组件
import WishlistSelectModal from './WishlistSelectModal.vue'

// 获取状态管理
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const authStore = useAuthStore()

// 商品图片
const productImage = computed(() => {
  // 直接使用API返回的image字段
  if (props.product.image) return props.product.image
  // 兼容可能的其他格式
  if (props.product.images && props.product.images.length > 0) {
    if (typeof props.product.images[0] === 'string') return props.product.images[0]
    if (props.product.images[0].image) return props.product.images[0].image
  }
  return '/images/product-placeholder.jpg'
})

// 折扣价格
const discountPrice = computed(() => {
  // 如果有discount_price字段，直接使用
  if (props.product.discount_price) return props.product.discount_price
  // 如果original_price与price不同，说明有折扣
  if (props.product.original_price && props.product.original_price !== props.product.price) {
    return props.product.price
  }
  return null
})

// 是否在心愿单中
const isInWishlist = computed(() => {
  return wishlistStore.isInAnyWishlist(props.product.id)
})

// 是否有折扣
const hasDiscount = computed(() => {
  return !!discountPrice.value
})

// 折扣百分比
const discountPercentage = computed(() => {
  if (!hasDiscount.value) return 0
  
  // 如果有original_price，使用它计算折扣
  if (props.product.original_price) {
    return Math.round((1 - parseFloat(props.product.price) / parseFloat(props.product.original_price)) * 100)
  }
  
  // 如果有discount_price，使用它计算折扣
  if (props.product.discount_price) {
    return Math.round((1 - parseFloat(props.product.discount_price) / parseFloat(props.product.price)) * 100)
  }
  
  return 0
})

// 添加到购物车
const addToCart = () => {
  cartStore.addToCart(props.product)
  
  // 显示提示信息
  // 这里可以使用toast通知组件
  alert('已添加到购物车')
}

// 显示/隐藏心愿单选择弹窗
const showWishlistModal = ref(false)
// 正在检查心愿单状态
const isCheckingWishlists = ref(false)

// 处理心愿单添加结果
const handleWishlistAdded = (result) => {
  if (result.success) {
    alert(result.message || '已添加到心愿单')
  } else {
    alert(result.message || '操作失败')
  }
}

// 添加/移除心愿单
const toggleWishlist = async () => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    const confirmed = confirm('请先登录才能添加到心愿单。\n是否前往登录页面？')
    if (confirmed) {
      navigateTo(`/login?redirect=${encodeURIComponent(window.location.pathname)}`)
    }
    return
  }
  
  if (isInWishlist.value) {
    // 从心愿单中移除
    // 需要获取心愿单中的商品ID
    const wishlistItem = wishlistStore.getWishlistItems.find(item => item.product?.id === props.product.id)
    if (wishlistItem) {
      const result = await wishlistStore.removeFromWishlist(wishlistItem.id)
      if (result.success) {
        alert('已从心愿单移除')
      } else {
        alert(result.error || '操作失败')
      }
    }
  } else {
    // 检查是否有心愿单，如果没有则先创建一个默认心愿单
    isCheckingWishlists.value = true
    
    try {
      // 先获取用户的心愿单列表
      await wishlistStore.fetchUserWishlists()
      
      // 如果用户没有心愿单，直接创建并添加商品
      if (wishlistStore.getUserWishlists.length === 0) {
        const confirmed = confirm('您还没有心愿单，是否创建一个新的心愿单？')
        
        if (confirmed) {
          const createResult = await wishlistStore.createWishlist({
            name: '我的心愿单',
            description: '',
            is_public: true
          })
          
          if (createResult.success && createResult.wishlist) {
            // 创建成功后直接添加商品
            const addResult = await wishlistStore.addToWishlist(props.product, createResult.wishlist.id)
            
            if (addResult.success) {
              alert('已添加到新创建的心愿单')
            } else {
              alert(addResult.error || '添加失败')
            }
          } else {
            alert(createResult.error || '创建心愿单失败')
          }
        }
      } else {
        // 如果用户有心愿单，显示选择弹窗
        showWishlistModal.value = true
      }
    } catch (error) {
      console.error('检查心愿单失败:', error)
      alert('操作失败，请重试')
    } finally {
      isCheckingWishlists.value = false
    }
  }
}
</script>


