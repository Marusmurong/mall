<template>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <template v-else-if="product">
        <!-- 面包屑导航 -->
        <nav class="flex mb-8" aria-label="Breadcrumb">
          <ol class="inline-flex items-center space-x-1 md:space-x-3">
            <li class="inline-flex items-center">
              <NuxtLink to="/" class="text-gray-500 hover:text-gray-700">
                首页
              </NuxtLink>
            </li>
            <li>
              <div class="flex items-center">
                <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                </svg>
                <NuxtLink to="/categories" class="ml-1 text-gray-500 hover:text-gray-700 md:ml-2">
                  分类
                </NuxtLink>
              </div>
            </li>
            <li v-if="product.category">
              <div class="flex items-center">
                <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                </svg>
                <NuxtLink :to="`/categories/${product.category.id}`" class="ml-1 text-gray-500 hover:text-gray-700 md:ml-2">
                  {{ product.category.name }}
                </NuxtLink>
              </div>
            </li>
            <li aria-current="page">
              <div class="flex items-center">
                <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span class="ml-1 text-gray-500 md:ml-2 font-medium line-clamp-1">{{ product.name }}</span>
              </div>
            </li>
          </ol>
        </nav>
        
        <!-- 商品详情 -->
        <div class="bg-white rounded-lg shadow-sm overflow-hidden">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 p-6">
            <!-- 商品图片 -->
            <div>
              <!-- 主图 -->
              <div class="aspect-square bg-gray-100 rounded-lg overflow-hidden mb-4">
                <img 
                  :src="currentImage" 
                  :alt="product.name" 
                  class="w-full h-full object-contain"
                >
              </div>
              
              <!-- 缩略图 -->
              <div v-if="productImages.length > 1" class="grid grid-cols-5 gap-2">
                <button 
                  v-for="(image, index) in productImages" 
                  :key="index"
                  @click="currentImageIndex = index"
                  class="aspect-square bg-gray-100 rounded-md overflow-hidden border-2"
                  :class="currentImageIndex === index ? 'border-primary-500' : 'border-transparent'"
                >
                  <img 
                    :src="image" 
                    :alt="`${product.name} - 图片 ${index + 1}`" 
                    class="w-full h-full object-contain"
                  >
                </button>
              </div>
            </div>
            
            <!-- 商品信息 -->
            <div>
              <!-- 商品标题 -->
              <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
              
              <!-- 评分 -->
              <div v-if="product.rating" class="flex items-center mb-4">
                <div class="flex">
                  <template v-for="i in 5" :key="i">
                    <svg 
                      :class="[i <= Math.round(product.rating) ? 'text-yellow-400' : 'text-gray-300']"
                      xmlns="http://www.w3.org/2000/svg" 
                      class="h-5 w-5" 
                      viewBox="0 0 20 20" 
                      fill="currentColor"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </template>
                </div>
                <span class="text-sm text-gray-500 ml-2">{{ product.rating }} ({{ product.rating_count || 0 }}条评价)</span>
              </div>
              
              <!-- 价格 -->
              <div class="mb-6">
                <div class="flex items-baseline">
                  <span v-if="product.discount_price" class="text-2xl font-bold text-red-600">¥{{ product.discount_price }}</span>
                  <span 
                    :class="[product.discount_price ? 'text-lg text-gray-500 line-through ml-2' : 'text-2xl font-bold text-gray-900']"
                  >
                    ¥{{ product.price }}
                  </span>
                  <span v-if="product.discount_price" class="ml-2 px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">
                    {{ Math.round((1 - product.discount_price / product.price) * 100) }}% 折扣
                  </span>
                </div>
                <p v-if="product.stock > 0 && product.stock < 10" class="text-sm text-orange-600 mt-1">
                  库存紧张，仅剩 {{ product.stock }} 件
                </p>
              </div>
              
              <!-- 规格选择 -->
              <div v-if="product.variants && product.variants.length" class="mb-6">
                <h3 class="text-sm font-medium text-gray-900 mb-2">规格</h3>
                <div class="flex flex-wrap gap-2">
                  <button 
                    v-for="variant in product.variants" 
                    :key="variant.id"
                    @click="selectedVariant = variant"
                    class="px-3 py-1 border rounded-md text-sm"
                    :class="selectedVariant && selectedVariant.id === variant.id ? 'border-primary-500 bg-primary-50 text-primary-700' : 'border-gray-300 text-gray-700 hover:border-gray-400'"
                  >
                    {{ variant.name }}
                  </button>
                </div>
              </div>
              
              <!-- 数量选择 -->
              <div class="mb-6">
                <h3 class="text-sm font-medium text-gray-900 mb-2">数量</h3>
                <div class="flex items-center">
                  <button 
                    @click="quantity > 1 ? quantity-- : null"
                    class="p-2 border border-gray-300 rounded-l-md text-gray-600 hover:bg-gray-50"
                    :disabled="quantity <= 1"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                    </svg>
                  </button>
                  <input 
                    v-model="quantity" 
                    type="number" 
                    min="1" 
                    :max="product.stock || 99"
                    class="w-16 text-center border-t border-b border-gray-300 py-2 focus:outline-none focus:ring-0 focus:border-gray-300"
                  >
                  <button 
                    @click="quantity < (product.stock || 99) ? quantity++ : null"
                    class="p-2 border border-gray-300 rounded-r-md text-gray-600 hover:bg-gray-50"
                    :disabled="product.stock && quantity >= product.stock"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="flex flex-wrap gap-4 mb-6">
                <button 
                  @click="addToCart"
                  class="flex-1 btn btn-primary py-3 flex items-center justify-center"
                  :disabled="product.stock === 0"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  加入购物车
                </button>
                <button 
                  @click="toggleWishlist"
                  class="flex-1 btn btn-outline py-3 flex items-center justify-center"
                >
                  <svg v-if="isInWishlist" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-secondary-600" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  {{ isInWishlist ? '已加入心愿单' : '加入心愿单' }}
                </button>
              </div>
              
              <!-- 商品标签 -->
              <div class="flex flex-wrap gap-2 mb-6">
                <span v-if="product.is_new" class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">新品</span>
                <span v-if="product.is_hot" class="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded">热销</span>
                <span v-if="product.is_recommended" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">推荐</span>
                <span v-if="product.stock === 0" class="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded">缺货</span>
              </div>
              
              <!-- 商品简介 -->
              <div class="border-t border-gray-200 pt-4">
                <h3 class="text-sm font-medium text-gray-900 mb-2">商品简介</h3>
                <p class="text-sm text-gray-600">{{ product.brief || '暂无简介' }}</p>
              </div>
            </div>
          </div>
          
          <!-- 商品详情标签页 -->
          <div class="border-t border-gray-200">
            <div class="border-b border-gray-200">
              <nav class="-mb-px flex">
                <button 
                  @click="activeTab = 'description'"
                  class="py-4 px-6 text-sm font-medium"
                  :class="activeTab === 'description' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                >
                  商品详情
                </button>
                <button 
                  @click="activeTab = 'specs'"
                  class="py-4 px-6 text-sm font-medium"
                  :class="activeTab === 'specs' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                >
                  规格参数
                </button>
                <button 
                  @click="activeTab = 'reviews'"
                  class="py-4 px-6 text-sm font-medium"
                  :class="activeTab === 'reviews' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                >
                  用户评价
                </button>
              </nav>
            </div>
            
            <!-- 标签页内容 -->
            <div class="p-6">
              <!-- 商品详情 -->
              <div v-if="activeTab === 'description'" class="prose max-w-none">
                <div v-if="product.description" v-html="product.description"></div>
                <p v-else class="text-gray-500">暂无详细描述</p>
              </div>
              
              <!-- 规格参数 -->
              <div v-else-if="activeTab === 'specs'">
                <div v-if="product.specifications && product.specifications.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    v-for="(spec, index) in product.specifications" 
                    :key="index"
                    class="flex border-b border-gray-200 py-2"
                  >
                    <span class="w-1/3 text-sm text-gray-500">{{ spec.name }}</span>
                    <span class="w-2/3 text-sm text-gray-900">{{ spec.value }}</span>
                  </div>
                </div>
                <p v-else class="text-gray-500">暂无规格参数</p>
              </div>
              
              <!-- 用户评价 -->
              <div v-else-if="activeTab === 'reviews'">
                <div v-if="product.reviews && product.reviews.length">
                  <div 
                    v-for="(review, index) in product.reviews" 
                    :key="index"
                    class="border-b border-gray-200 py-4 last:border-b-0"
                  >
                    <div class="flex items-center mb-2">
                      <div class="flex">
                        <template v-for="i in 5" :key="i">
                          <svg 
                            :class="[i <= review.rating ? 'text-yellow-400' : 'text-gray-300']"
                            xmlns="http://www.w3.org/2000/svg" 
                            class="h-4 w-4" 
                            viewBox="0 0 20 20" 
                            fill="currentColor"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        </template>
                      </div>
                      <span class="text-sm font-medium text-gray-900 ml-2">{{ review.user_name }}</span>
                      <span class="text-xs text-gray-500 ml-2">{{ review.created_at }}</span>
                    </div>
                    <p class="text-sm text-gray-600">{{ review.content }}</p>
                  </div>
                </div>
                <p v-else class="text-gray-500">暂无评价</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 相关商品 -->
        <div v-if="relatedProducts.length" class="mt-12">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">相关商品</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <ProductCard 
              v-for="relatedProduct in relatedProducts" 
              :key="relatedProduct.id" 
              :product="relatedProduct"
            />
          </div>
        </div>
      </template>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">获取商品失败</h3>
        <p class="mt-1 text-gray-500">{{ error }}</p>
        <button 
          @click="fetchProductData"
          class="mt-4 btn btn-primary"
        >
          重试
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// 获取路由参数
const route = useRoute()
const productId = route.params.id

// 获取API服务
const api = useApi()

// 获取状态管理
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const authStore = useAuthStore()

// 状态
const product = ref(null)
const relatedProducts = ref([])
const loading = ref(true)
const error = ref(null)

// 商品详情UI状态
const quantity = ref(1)
const activeTab = ref('description')
const selectedVariant = ref(null)
const currentImageIndex = ref(0)

// 计算属性
const productImages = computed(() => {
  if (!product.value) return []
  
  if (product.value.images && product.value.images.length) {
    return product.value.images.map(img => img.image)
  }
  
  if (product.value.image) {
    return [product.value.image]
  }
  
  return ['/images/product-placeholder.jpg']
})

const currentImage = computed(() => {
  return productImages.value[currentImageIndex.value] || '/images/product-placeholder.jpg'
})

// 是否在心愿单中
const isInWishlist = computed(() => {
  return wishlistStore.isInAnyWishlist(productId)
})

// 获取商品详情
const fetchProductData = async () => {
  try {
    loading.value = true
    error.value = null
    
    // 获取商品详情
    const productData = await api.products.getById(productId)
    product.value = productData
    
    // 设置默认变体
    if (product.value.variants && product.value.variants.length) {
      selectedVariant.value = product.value.variants[0]
    }
    
    // 获取相关商品
    // 这里简化处理，实际可能需要调用专门的API
    if (product.value.category) {
      const categoryProducts = await api.categories.getProducts(product.value.category.id)
      relatedProducts.value = categoryProducts
        .filter(p => p.id !== productId)
        .slice(0, 5)
    }
  } catch (err) {
    console.error('获取商品数据失败:', err)
    error.value = err.message || '获取商品数据失败'
  } finally {
    loading.value = false
  }
}

// 添加到购物车
const addToCart = () => {
  if (product.value) {
    // 如果有选中的变体，使用变体信息
    const productToAdd = selectedVariant.value 
      ? { ...product.value, ...selectedVariant.value }
      : product.value
      
    cartStore.addToCart(productToAdd, quantity.value)
    
    // 显示提示信息
    // 这里可以使用toast通知组件
    alert(`已将 ${quantity.value} 件 ${product.value.name} 添加到购物车`)
  }
}

// 添加/移除心愿单
const toggleWishlist = async () => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    alert('请先登录')
    // 可以重定向到登录页面
    // navigateTo('/login')
    return
  }
  
  if (isInWishlist.value) {
    // 从心愿单中移除
    // 需要获取心愿单中的商品ID
    const wishlistItem = wishlistStore.getWishlistItems.find(item => item.product?.id === productId)
    if (wishlistItem) {
      const result = await wishlistStore.removeFromWishlist(wishlistItem.id)
      if (result.success) {
        alert('已从心愿单移除')
      } else {
        alert(result.error || '操作失败')
      }
    }
  } else {
    // 添加到心愿单
    const result = await wishlistStore.addToWishlist(product.value)
    if (result.success) {
      alert('已添加到心愿单')
    } else {
      alert(result.error || '操作失败')
    }
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchProductData()
})

// 监听路由变化，重新获取数据
watch(() => route.params.id, (newId) => {
  if (newId) {
    currentImageIndex.value = 0
    quantity.value = 1
    selectedVariant.value = null
    fetchProductData()
  }
})

// 定义页面元数据，指定使用默认布局
definePageMeta({
  layout: 'default'
})
</script>
