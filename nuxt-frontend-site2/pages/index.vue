<template>
  <div>
    <!-- 首页轮播图 -->
    <section class="relative">
      <!-- 管理员模式开关 -->
      <div v-if="isDev" class="absolute top-4 right-4 z-50 p-2 bg-gray-100 bg-opacity-80 rounded-md flex items-center justify-between">
        <span class="text-sm text-gray-700 mr-2">管理员模式</span>
        <button 
          @click="adminModeEnabled = !adminModeEnabled" 
          class="px-3 py-1 text-xs rounded-full" 
          :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
        >
          {{ adminModeEnabled ? '已启用' : '未启用' }}
        </button>
      </div>

      <!-- 编辑幕布幕按钮 -->
      <div v-if="adminModeEnabled" class="absolute top-4 left-4 z-50">
        <button 
          @click="openSlideManager"
          class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          编辑幕布幕
        </button>
      </div>
      
      <!-- 轮播图容器 -->
      <div class="carousel-container h-[500px] overflow-hidden relative">
        <!-- 轮播图内容 -->
        <div 
          v-for="(slide, index) in carouselSlides" 
          :key="slide.id"
          class="carousel-slide h-full flex items-center absolute inset-0 transition-opacity duration-500"
          :class="{
            'opacity-100 z-10': currentSlideIndex === index,
            'opacity-0 z-0': currentSlideIndex !== index
          }"
          :style="getSlideStyle(slide)"
        >
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-white relative z-10">
            <div class="max-w-2xl">
              <h1 class="text-4xl font-extrabold tracking-tight sm:text-5xl lg:text-6xl">
                {{ slide.title }}
              </h1>
              <p class="mt-6 text-xl">
                {{ slide.subtitle }}
              </p>
              <div class="mt-10">
                <NuxtLink :to="slide.buttonLink" class="btn btn-primary px-8 py-3 text-lg">
                  {{ slide.buttonText }}
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 轮播图指示器和控制按钮 -->
      <div class="absolute bottom-5 left-0 right-0 flex justify-center space-x-2">
        <button 
          v-for="(slide, index) in carouselSlides" 
          :key="slide.id"
          @click="currentSlideIndex = index"
          class="w-3 h-3 rounded-full bg-white transition-opacity"
          :class="currentSlideIndex === index ? 'opacity-100' : 'opacity-50'"
        ></button>
      </div>

      <!-- 左右切换按钮 -->
      <button 
        v-if="carouselSlides.length > 1"
        @click="prevSlide"
        class="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-30 hover:bg-opacity-50 text-white rounded-full p-2 z-20"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <button 
        v-if="carouselSlides.length > 1"
        @click="nextSlide"
        class="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-30 hover:bg-opacity-50 text-white rounded-full p-2 z-20"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </section>
    
    <!-- 分类导航 -->
    <section class="py-12 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-8">热门分类</h2>
        
        <div v-if="categoriesLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="categories.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <NuxtLink 
            v-for="category in categories.slice(0, 6)" 
            :key="category.id" 
            :to="`/categories/${category.id}`"
            class="flex flex-col items-center p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
          >
            <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-3">
              <img v-if="category.image" :src="category.image" :alt="category.name" class="w-10 h-10 object-contain">
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-900 text-center">{{ category.name }}</span>
          </NuxtLink>
        </div>
        
        <div v-else class="text-center py-10 text-gray-500">
          暂无分类数据
        </div>
      </div>
    </section>
    
    <!-- 推荐商品 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">推荐商品</h2>
          <NuxtLink to="/products?recommended=true" class="text-primary-600 hover:text-primary-500">
            查看全部 <span aria-hidden="true">→</span>
          </NuxtLink>
        </div>
        
        <div v-if="recommendedLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="recommendedProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <ProductCard 
            v-for="product in recommendedProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <div v-else class="text-center py-10 text-gray-500">
          暂无推荐商品
        </div>
      </div>
    </section>
    
    <!-- 促销广告条 -->
    <section class="bg-secondary-600 py-12 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row items-center justify-between">
          <div class="mb-6 md:mb-0">
            <h2 class="text-2xl font-bold">限时优惠活动</h2>
            <p class="mt-2">全场商品8折起，还有更多惊喜等你发现！</p>
          </div>
          <NuxtLink to="/products" class="btn bg-white text-secondary-600 hover:bg-gray-100">
            立即抢购
          </NuxtLink>
        </div>
      </div>
    </section>
    
    <!-- 新品上市 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">新品上市</h2>
          <NuxtLink to="/products?new=true" class="text-primary-600 hover:text-primary-500">
            查看全部 <span aria-hidden="true">→</span>
          </NuxtLink>
        </div>
        
        <div v-if="newProductsLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="newProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <ProductCard 
            v-for="product in newProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <div v-else class="text-center py-10 text-gray-500">
          暂无新品
        </div>
      </div>
    </section>
    
    <!-- 心愿单功能宣传 -->
    <section class="py-12 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-4">创建并分享您的心愿单</h2>
            <p class="text-lg text-gray-600 mb-6">
              将您喜爱的商品添加到心愿单，与朋友分享您的购物愿望，让购物体验更加社交化。
            </p>
            <div class="flex space-x-4">
              <NuxtLink to="/wishlist" class="btn btn-primary">
                创建心愿单
              </NuxtLink>
              <NuxtLink to="/wishlist/public" class="btn btn-outline">
                探索公开心愿单
              </NuxtLink>
            </div>
          </div>
          <div class="relative h-64 md:h-80 lg:h-96 rounded-lg overflow-hidden shadow-lg bg-gray-200 flex items-center justify-center">
            <div class="text-gray-500 text-center p-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <p class="text-lg font-medium">心愿单功能预览</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 热门商品 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">热门商品</h2>
          <NuxtLink to="/products?hot=true" class="text-primary-600 hover:text-primary-500">
            查看全部 <span aria-hidden="true">→</span>
          </NuxtLink>
        </div>
        
        <div v-if="hotProductsLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="hotProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <ProductCard 
            v-for="product in hotProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <div v-else-if="hotProductsError" class="text-center py-10 text-red-500">
          <p>获取热门商品失败:</p>
          <pre class="mt-2 bg-red-50 p-4 rounded text-left overflow-auto">{{ hotProductsError }}</pre>
        </div>
        <div v-else class="text-center py-10 text-gray-500">
          暂无热门商品
        </div>
      </div>
    </section>
  </div>

  <!-- 幕布幕管理器 -->
  <SlideManager 
    :show="showSlideManager" 
    :initial-slides="carouselSlides"
    @close="showSlideManager = false"
    @save="handleSlidesSave"
  />
</template>

<script setup>
// 导入幕布幕管理器组件
import SlideManager from '~/components/SlideManager.vue'

// 获取API服务
const api = useApi()

// 分类数据
const categories = ref([])
const categoriesLoading = ref(true)

// 推荐商品
const recommendedProducts = ref([])
const recommendedLoading = ref(true)

// 新品
const newProducts = ref([])
const newProductsLoading = ref(true)

// 热门商品
const hotProducts = ref([])
const hotProductsLoading = ref(true)
const hotProductsError = ref('')

// 轮播图相关数据
const carouselSlides = ref([])
const currentSlideIndex = ref(0)
const slidesLoading = ref(true)

// 幕布管理器
const showSlideManager = ref(false)

// 管理员模式（开发环境临时功能）
const adminModeEnabled = ref(false)
const isDev = process.env.NODE_ENV === 'development'

// 获取分类数据
const fetchCategories = async () => {
  try {
    categoriesLoading.value = true
    const response = await api.categories.getTree()
    console.log('分类数据响应:', response)
    // API响应已经在useApi中处理过，直接使用响应数据
    categories.value = response || []
  } catch (error) {
    console.error('获取分类失败:', error)
  } finally {
    categoriesLoading.value = false
  }
}

// 获取推荐商品
const fetchRecommendedProducts = async () => {
  try {
    recommendedLoading.value = true
    const response = await api.products.getRecommended()
    console.log('推荐商品响应:', response)
    // API响应已经在useApi中处理过，直接使用响应数据
    recommendedProducts.value = response || []
  } catch (error) {
    console.error('获取推荐商品失败:', error)
  } finally {
    recommendedLoading.value = false
  }
}

// 获取新品
const fetchNewProducts = async () => {
  try {
    newProductsLoading.value = true
    const response = await api.products.getNew()
    console.log('新品响应:', response)
    // API响应已经在useApi中处理过，直接使用响应数据
    newProducts.value = response || []
  } catch (error) {
    console.error('获取新品失败:', error)
  } finally {
    newProductsLoading.value = false
  }
}

// 获取热门商品
const fetchHotProducts = async () => {
  try {
    hotProductsLoading.value = true
    hotProductsError.value = ''
    console.log('发送热门商品请求...')
    const response = await api.products.getHot()
    console.log('热门商品响应:', response)
    // API响应已经在useApi中处理过，直接使用响应数据
    hotProducts.value = response || []
  } catch (error) {
    console.error('获取热门商品失败:', error)
    hotProductsError.value = `错误: ${error.message || error}`
  } finally {
    hotProductsLoading.value = false
  }
}

// 获取轮播图数据
const fetchSlides = () => {
  try {
    slidesLoading.value = true
    
    // 从 localStorage 中获取幕布幕数据
    const savedSlides = localStorage.getItem('carouselSlides')
    
    if (savedSlides) {
      carouselSlides.value = JSON.parse(savedSlides)
    } else {
      // 设置默认幕布幕
      carouselSlides.value = [{
        id: '1',
        title: '优质商品，精选推荐',
        subtitle: '为您提供高品质的精选商品，满足您的一站式购物需求。',
        buttonText: '开始购物',
        buttonLink: '/categories',
        backgroundColor: 'bg-gradient-to-r from-primary-700 to-primary-900',
        backgroundImage: ''
      }]
      
      // 将默认幕布幕保存到 localStorage
      localStorage.setItem('carouselSlides', JSON.stringify(carouselSlides.value))
    }
  } catch (error) {
    console.error('获取幕布幕数据失败:', error)
    // 设置默认幕布幕
    carouselSlides.value = [{
      id: '1',
      title: '优质商品，精选推荐',
      subtitle: '为您提供高品质的精选商品，满足您的一站式购物需求。',
      buttonText: '开始购物',
      buttonLink: '/categories',
      backgroundColor: 'bg-gradient-to-r from-primary-700 to-primary-900',
      backgroundImage: ''
    }]
  } finally {
    slidesLoading.value = false
  }
}

// 开启幕布幕管理器
const openSlideManager = () => {
  showSlideManager.value = true
}

// 处理幕布幕保存
const handleSlidesSave = (slides) => {
  carouselSlides.value = slides
  // 同步到localStorage
  localStorage.setItem('carouselSlides', JSON.stringify(slides))
}

// 上一张幕布幕
const prevSlide = () => {
  if (currentSlideIndex.value > 0) {
    currentSlideIndex.value--
  } else {
    currentSlideIndex.value = carouselSlides.value.length - 1
  }
}

// 下一张幕布幕
const nextSlide = () => {
  if (currentSlideIndex.value < carouselSlides.value.length - 1) {
    currentSlideIndex.value++
  } else {
    currentSlideIndex.value = 0
  }
}

// 获取幕布幕样式
const getSlideStyle = (slide) => {
  const style = {}
  
  // 如果有背景图片，优先使用背景图片
  if (slide.backgroundImage) {
    style.backgroundImage = `url(${slide.backgroundImage})`
    style.backgroundSize = 'cover'
    style.backgroundPosition = 'center'
    // 添加半透明黑色遮罩，使文字更清晰
    style.backgroundColor = 'rgba(0, 0, 0, 0.4)'
  }
  
  return style
}

// 自动轮播
let autoplayInterval
const startAutoplay = () => {
  autoplayInterval = setInterval(() => {
    nextSlide()
  }, 5000) // 5秒切换一次
}

// 页面加载时获取数据
onMounted(() => {
  fetchCategories()
  fetchRecommendedProducts()
  fetchNewProducts()
  fetchHotProducts()
  fetchSlides()
  
  // 启动自动轮播
  startAutoplay()
})

// 页面卸载时清除定时器
onBeforeUnmount(() => {
  if (autoplayInterval) {
    clearInterval(autoplayInterval)
  }
})

// 定义页面元数据，指定使用默认布局
definePageMeta({
  layout: 'default'
})
</script>
