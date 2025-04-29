<template>
  <div class="container mx-auto px-4 py-8">
    <div>
      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <!-- Product Details -->
      <template v-else-if="product">
        <!-- Breadcrumb -->
        <nav class="flex mb-6" aria-label="Breadcrumb">
          <ol class="inline-flex items-center space-x-1 md:space-x-3">
            <li class="inline-flex items-center">
              <NuxtLink to="/" class="text-sm text-gray-700 hover:text-primary-600">
                Home
              </NuxtLink>
            </li>
            <li>
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                </svg>
                <NuxtLink v-if="product.category" :to="`/categories/${product.category.id}`" class="text-sm text-gray-700 hover:text-primary-600">
                  {{ product.category.name }}
                </NuxtLink>
                <span v-else class="text-sm text-gray-500">Categories</span>
              </div>
            </li>
            <li aria-current="page">
              <div class="flex items-center">
                <svg class="w-3 h-3 text-gray-400 mx-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-sm text-gray-500 md:ml-2">{{ product.name }}</span>
              </div>
            </li>
          </ol>
        </nav>
        
        <!-- Product -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
            <!-- Product Images -->
            <div>
              <!-- Main Image -->
              <div class="mb-4 relative">
                <img :src="currentImage" :alt="product.name" class="w-full h-auto object-contain rounded-lg border border-gray-200 bg-white" style="max-height: 400px;">
                
                <!-- Image Controls -->
                <button 
                  v-if="productImages.length > 1" 
                  @click="currentImageIndex = (currentImageIndex - 1 + productImages.length) % productImages.length"
                  class="absolute left-2 top-1/2 -translate-y-1/2 bg-white bg-opacity-75 p-2 rounded-full"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button 
                  v-if="productImages.length > 1" 
                  @click="currentImageIndex = (currentImageIndex + 1) % productImages.length"
                  class="absolute right-2 top-1/2 -translate-y-1/2 bg-white bg-opacity-75 p-2 rounded-full"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
              
              <!-- Thumbnail Images -->
              <div v-if="productImages.length > 1" class="flex space-x-2 overflow-x-auto">
                <button 
                  v-for="(image, index) in productImages" 
                  :key="index"
                  @click="currentImageIndex = index"
                  class="w-16 h-16 rounded border"
                  :class="currentImageIndex === index ? 'border-primary-500' : 'border-gray-200'"
                >
                  <img :src="image" :alt="`${product.name} ${index + 1}`" class="w-full h-full object-cover rounded">
                </button>
              </div>
            </div>
            
            <!-- Product Info -->
            <div>
              <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
              
              <!-- Rating -->
              <div class="flex items-center mb-4" v-if="product.rating">
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
                <span class="text-sm text-gray-500 ml-2">{{ product.rating }} ({{ product.reviews?.length || 0 }} Reviews)</span>
              </div>
              
              <!-- Price -->
              <div class="flex items-end mb-4">
                <span class="text-2xl font-bold text-gray-900">${{ product.price }}</span>
                <span v-if="product.original_price && product.original_price > product.price" class="text-lg text-gray-500 line-through ml-2">${{ product.original_price }}</span>
              </div>
              
              <!-- Stock Status -->
              <div class="mb-4">
                <p v-if="product.stock > 0" class="text-sm text-green-600">
                  <span class="inline-block w-2 h-2 bg-green-500 rounded-full mr-1"></span>
                  In Stock ({{ product.stock }})
                </p>
                <p v-else class="text-sm text-red-600">
                  <span class="inline-block w-2 h-2 bg-red-500 rounded-full mr-1"></span>
                  Out of Stock
                </p>
              </div>
              
              <!-- Variants Selection -->
              <div v-if="product.variants && product.variants.length" class="mb-4">
                <h3 class="text-sm font-medium text-gray-900 mb-2">Variants</h3>
                <div class="flex flex-wrap gap-2">
                  <button 
                    v-for="variant in product.variants" 
                    :key="variant.id"
                    @click="selectedVariant = variant"
                    class="px-3 py-1 border rounded-md text-sm"
                    :class="selectedVariant && selectedVariant.id === variant.id 
                      ? 'border-primary-500 bg-primary-50 text-primary-700' 
                      : 'border-gray-300 text-gray-700 hover:border-gray-400'"
                  >
                    {{ variant.name }}
                  </button>
                </div>
              </div>
              
              <!-- Quantity -->
              <div class="mb-6">
                <h3 class="text-sm font-medium text-gray-900 mb-2">Quantity</h3>
                <div class="flex items-center">
                  <button 
                    @click="quantity > 1 ? quantity-- : quantity"
                    class="w-10 h-10 border border-gray-300 flex items-center justify-center rounded-l-md"
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
                    :max="product.stock"
                    class="w-16 h-10 border-t border-b border-gray-300 text-center"
                  />
                  <button 
                    @click="quantity < product.stock ? quantity++ : quantity"
                    class="w-10 h-10 border border-gray-300 flex items-center justify-center rounded-r-md"
                    :disabled="quantity >= product.stock"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- Action Buttons -->
              <div class="flex flex-wrap gap-3 mb-6">
                <button 
                  @click="addToCart"
                  class="btn btn-primary flex-1"
                  :disabled="product.stock === 0"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  Add to Cart
                </button>
                <button 
                  @click="toggleWishlist"
                  class="btn btn-outline flex items-center justify-center px-4"
                >
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    class="h-5 w-5" 
                    :fill="isInWishlist ? 'currentColor' : 'none'"
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </button>
              </div>
              
              <!-- Tags -->
              <div class="flex flex-wrap gap-2 mb-4">
                <span v-if="product.is_recommended" class="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">Recommended</span>
                <span v-if="product.stock === 0" class="px-2 py-1 bg-gray-100 text-gray-800 text-xs font-medium rounded">Out of Stock</span>
              </div>
              
              <!-- Product Brief -->
              <div class="border-t border-gray-200 pt-4">
                <h3 class="text-sm font-medium text-gray-900 mb-2">Product Brief</h3>
                <p class="text-sm text-gray-600">{{ product.brief || 'No brief available' }}</p>
              </div>
            </div>
          </div>
          
          <!-- Product Detail Tabs -->
          <div class="border-t border-gray-200">
            <div class="border-b border-gray-200">
              <nav class="-mb-px flex">
                <button 
                  @click="activeTab = 'description'"
                  class="py-4 px-6 text-sm font-medium"
                  :class="activeTab === 'description' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                >
                  Product Details
                </button>
                <button 
                  @click="activeTab = 'specs'"
                  class="py-4 px-6 text-sm font-medium"
                  :class="activeTab === 'specs' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                >
                  Specifications
                </button>
                <button 
                  @click="activeTab = 'reviews'"
                  class="py-4 px-6 text-sm font-medium"
                  :class="activeTab === 'reviews' ? 'border-b-2 border-primary-500 text-primary-600' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                >
                  Reviews
                </button>
              </nav>
            </div>
            
            <!-- Tab Contents -->
            <div class="p-6">
              <!-- Product Details -->
              <div v-if="activeTab === 'description'" class="prose max-w-none">
                <div v-if="product.description" v-html="product.description"></div>
                <p v-else class="text-gray-500">No detailed description available</p>
              </div>
              
              <!-- Specifications -->
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
                <p v-else class="text-gray-500">No specifications available</p>
              </div>
              
              <!-- Reviews -->
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
                <p v-else class="text-gray-500">No reviews available</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Related Products -->
        <div v-if="relatedProducts.length" class="mt-12">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Related Products</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            <ProductCard 
              v-for="relatedProduct in relatedProducts" 
              :key="relatedProduct.id" 
              :product="relatedProduct"
            />
          </div>
        </div>
      </template>
      
      <!-- Error State -->
      <div v-else-if="error" class="text-center py-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Failed to load product</h3>
        <p class="mt-1 text-gray-500">{{ error }}</p>
        <button 
          @click="fetchProductData"
          class="mt-4 btn btn-primary"
        >
          Retry
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
    console.error('Failed to fetch product data:', err)
    error.value = err.message || 'Failed to fetch product data'
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
    alert(`Added ${quantity.value} ${product.value.name} to cart`)
  }
}

// 添加/移除心愿单
const toggleWishlist = async () => {
  // 检查用户是否已登录
  if (!authStore.isAuthenticated) {
    alert('Please login first')
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
        alert('Removed from wishlist')
      } else {
        alert(result.error || 'Operation failed')
      }
    }
  } else {
    // 添加到心愿单
    const result = await wishlistStore.addToWishlist(product.value)
    if (result.success) {
      alert('Added to wishlist')
    } else {
      alert(result.error || 'Operation failed')
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
