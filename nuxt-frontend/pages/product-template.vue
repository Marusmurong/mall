<template>
  <div class="container mx-auto px-4 py-8">
    <!-- 加载状态 -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <div class="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="error" class="text-center py-12">
      <h2 class="text-2xl font-bold text-red-600 mb-4">{{ $t('product.error_loading') }}</h2>
      <p class="text-gray-600">{{ error }}</p>
      <button @click="fetchProduct" class="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
        {{ $t('common.retry') }}
      </button>
    </div>

    <div v-else-if="product" class="pb-16">
      <!-- 商品基本信息区域 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <!-- 左侧商品图片区域 -->
        <div>
          <!-- 主图展示区 -->
          <div class="mb-4 border rounded-lg overflow-hidden bg-gray-50 flex items-center justify-center" style="height: 400px;">
            <img 
              :src="currentImage || '/images/placeholder.png'" 
              :alt="product.name" 
              class="object-contain h-full w-full"
            >
          </div>
          
          <!-- 缩略图选择区 -->
          <div v-if="product.images && product.images.length > 0" class="grid grid-cols-5 gap-2">
            <button 
              v-for="(image, index) in product.images" 
              :key="index"
              @click="currentImage = image"
              class="border rounded overflow-hidden h-20 flex items-center justify-center" 
              :class="{'ring-2 ring-primary-600': currentImage === image}"
            >
              <img :src="image" :alt="`${product.name} - ${index + 1}`" class="object-contain h-full">
            </button>
          </div>
        </div>
        
        <!-- 右侧商品信息区域 -->
        <div>
          <h1 class="text-3xl font-bold text-gray-900">{{ product.name }}</h1>
          
          <!-- 商品标签 -->
          <div class="flex flex-wrap gap-2 mt-2">
            <span v-if="product.is_new" class="px-2 py-1 bg-blue-500 text-white text-xs font-semibold rounded">
              {{ $t('product.new') }}
            </span>
            <span v-if="product.is_hot" class="px-2 py-1 bg-red-500 text-white text-xs font-semibold rounded">
              {{ $t('product.hot') }}
            </span>
            <span v-if="product.is_recommended" class="px-2 py-1 bg-green-500 text-white text-xs font-semibold rounded">
              {{ $t('product.recommended') }}
            </span>
          </div>
          
          <!-- 商品分类 -->
          <div class="mt-4 text-sm text-gray-500">
            {{ $t('product.category') }}: {{ product.category }}
          </div>
          
          <!-- 价格信息 -->
          <div class="mt-4 flex items-baseline">
            <span class="text-2xl font-bold text-primary-600">${{ formatPrice(product.price) }}</span>
            <span v-if="product.original_price && product.original_price > product.price" class="ml-2 text-lg text-gray-500 line-through">
              ${{ formatPrice(product.original_price) }}
            </span>
            <span v-if="product.original_price && product.original_price > product.price" class="ml-3 px-2 py-1 text-xs font-semibold text-white bg-red-500 rounded">
              {{ calculateDiscount(product.price, product.original_price) }}% OFF
            </span>
          </div>
          
          <!-- 库存信息 -->
          <div class="mt-4 text-sm">
            <span class="font-medium">{{ $t('product.stock') }}: </span>
            <span :class="product.stock > 0 ? 'text-green-600' : 'text-red-600'">
              {{ product.stock > 0 ? product.stock : $t('product.out_of_stock') }}
            </span>
          </div>
          
          <!-- 销量信息 -->
          <div v-if="product.sales" class="mt-2 text-sm text-gray-500">
            {{ $t('product.sales') }}: {{ product.sales }}
          </div>
          
          <!-- 简短描述 -->
          <div class="mt-4 text-gray-600">
            {{ product.description }}
          </div>
          
          <!-- 数量选择 -->
          <div class="mt-8">
            <label for="quantity" class="block text-sm font-medium text-gray-700">{{ $t('product.quantity') }}</label>
            <div class="mt-1 flex">
              <button 
                class="px-3 py-2 border border-r-0 rounded-l-md bg-gray-100 text-gray-600" 
                @click="quantity > 1 ? quantity-- : null"
                :disabled="quantity <= 1"
              >
                -
              </button>
              <input 
                id="quantity" 
                type="number" 
                v-model.number="quantity" 
                min="1" 
                :max="product.stock" 
                class="w-16 border text-center" 
              />
              <button 
                class="px-3 py-2 border border-l-0 rounded-r-md bg-gray-100 text-gray-600" 
                @click="quantity < product.stock ? quantity++ : null"
                :disabled="quantity >= product.stock"
              >
                +
              </button>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="mt-8 flex flex-col gap-3">
            <button 
              @click="addToWishlist"
              class="flex items-center justify-center px-6 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              {{ $t('product.add_to_wishlist') }}
            </button>
            
            <button 
              @click="buyNow"
              :disabled="product.stock <= 0"
              class="flex items-center justify-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              {{ $t('product.buy_now') }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 商品详情区域 -->
      <div class="border-t pt-8">
        <h2 class="text-2xl font-bold mb-6">{{ $t('product.details') }}</h2>
        
        <!-- 详细描述 -->
        <div class="mb-12 prose prose-lg max-w-none" v-html="product.detail_description"></div>
        
        <!-- 商品图片展示 -->
        <div v-if="product.images && product.images.length > 0">
          <h3 class="text-xl font-bold mb-4">{{ $t('product.product_images') }}</h3>
          <div class="grid grid-cols-1 gap-6">
            <div v-for="(image, index) in product.images" :key="index" class="flex justify-center">
              <img :src="image" :alt="`${product.name} - ${$t('product.image')} ${index + 1}`" class="max-w-full h-auto rounded-lg shadow-md">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNuxtApp } from '#app'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const product = ref(null)
const loading = ref(true)
const error = ref(null)
const quantity = ref(1)
const currentImage = ref('')

// 格式化价格
const formatPrice = (price) => {
  return Number(price).toFixed(2)
}

// 计算折扣百分比
const calculateDiscount = (price, originalPrice) => {
  if (!price || !originalPrice || originalPrice <= price) return 0
  return Math.round(((originalPrice - price) / originalPrice) * 100)
}

// 获取商品信息
const fetchProduct = async () => {
  try {
    loading.value = true
    error.value = null
    
    // 使用路由参数获取商品ID
    const productId = route.params.id || 'template'
    
    // 从API获取数据 - 实际项目中会启用下面的代码
    const { $axios } = useNuxtApp()
    // const response = await $axios.get(`/api/products/${productId}`)
    // product.value = response.data
    
    // 演示数据 - 实际项目中删除这段代码
    // 这里使用模拟数据避免构建错误
    setTimeout(() => {
      product.value = {
        id: 1,
        name: 'Homeweeks 300ml Essential Oil Diffuser',
        category: 'Home Life',
        price: 14.59,
        original_price: 17.51,
        stock: 100,
        sales: 0,
        is_new: true,
        is_recommended: true,
        is_hot: false,
        description: 'Wood',
        detail_description: `<hr aria-hidden="true" class="a-divider-normal"><h1 class="a-size-base-plus a-text-bold"> About this item </h1><ul class="a-unordered-list a-vertical a-spacing-mini"> <li class="a-spacing-mini"><span class="a-list-item"> Wood </span></li> <li class="a-spacing-mini"><span class="a-list-item"> HUMIDIFIER &amp;AROMATHERAPY &amp;NIGHT LIGHT: Besides its functions as a humidifier and uses in aromatherapy, this essential oil diffuser also gives off good light that can easily function as a night light. It's great to fit for the room, home, office and everywhere you want to put it, and it is the best present for your family or friends </span></li> <li class="a-spacing-mini"><span class="a-list-item"> IMPROVE AIR QUALITY AND FEEL RELAXING: The oil diffuser with some aroma will add the amount of moisture to the room to improve your home's air quality and cover the smell of pets or smoking. The 8 color lights are adjustable between bright and dim modes, perfectfor creating a romantic, relaxed and sweet atmosphere</span></li></ul>`,
        images: [
          '/goods/images/amazon_1745655084_0.jpg',
          '/goods/images/amazon_1745655084_1.jpg',
          '/goods/images/amazon_1745655084_2.jpg'
        ]
      }
      
      // 设置默认显示的图片
      if (product.value && product.value.images && product.value.images.length > 0) {
        currentImage.value = product.value.images[0]
      }
      
      loading.value = false
    }, 500)
    
  } catch (err) {
    console.error('Error fetching product:', err)
    error.value = t('product.error_message')
  } finally {
    loading.value = false
  }
}

// 添加到心愿单
const addToWishlist = () => {
  // 实现添加到心愿单的逻辑
  alert(t('product.added_to_wishlist'))
}

// 立即购买
const buyNow = () => {
  if (product.value.stock <= 0) {
    alert(t('product.out_of_stock'))
    return
  }
  
  // 准备购买参数
  const purchaseParams = {
    product_id: product.value.id,
    quantity: quantity.value
  }
  
  // 跳转到支付页面
  router.push({
    path: '/payment',
    query: { direct: 'true' },
    state: { purchaseParams }
  })
}

// 页面加载时获取商品数据
onMounted(() => {
  fetchProduct()
})
</script>

<style scoped>
/* 可以添加自定义样式 */
</style> 