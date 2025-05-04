<template>
  <div>
    <!-- 首页轮播图 -->
    <section class="relative">
      <!-- 管理员模式组件 -->
      <div class="absolute top-4 right-4 z-50">
        <AdminModeSwitch @update:adminMode="adminModeEnabled = $event" />
      </div>

      <!-- 编辑幕布幕按钮 -->
      <div v-if="isAdmin && adminModeEnabled" class="absolute top-4 left-4 z-50">
        <button 
          @click="openSlideManager"
          class="px-3 py-1 bg-blue-600 text-white text-sm rounded-md flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
          Edit Slides
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
        <h2 class="text-2xl font-bold text-gray-900 mb-8">Popular Categories</h2>
        
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
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" :class="getCategoryIcon(category.name).class" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getCategoryIcon(category.name).path" />
              </svg>
            </div>
            <span class="text-sm font-medium text-gray-900 text-center">{{ category.name }}</span>
          </NuxtLink>
        </div>
        
        <div v-else class="text-center py-10 text-gray-500">
          No categories available
        </div>
      </div>
    </section>
    
    <!-- 推荐商品 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">Recommended Products</h2>
          <NuxtLink to="/products?recommended=true" class="text-primary-600 hover:text-primary-500">
            View All <span aria-hidden="true">→</span>
          </NuxtLink>
        </div>
        
        <div v-if="recommendedLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="recommendedProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <ProductCard 
            v-for="product in recommendedProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <div v-else class="text-center py-10 text-gray-500">
          No recommended products available
        </div>
      </div>
    </section>
    
    <!-- 促销广告条 -->
    <section class="bg-secondary-600 py-12 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row items-center justify-between">
          <div class="mb-6 md:mb-0">
            <h2 class="text-2xl font-bold">Limited Time Offer</h2>
            <p class="mt-2">All products starting at 20% off, with more surprises waiting for you!</p>
          </div>
          <NuxtLink to="/products" class="btn bg-white text-secondary-600 hover:bg-gray-100">
            Shop Now
          </NuxtLink>
        </div>
      </div>
    </section>
    
    <!-- 新品上市 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">New Arrivals</h2>
          <NuxtLink to="/products?new=true" class="text-primary-600 hover:text-primary-500">
            View All <span aria-hidden="true">→</span>
          </NuxtLink>
        </div>
        
        <div v-if="newProductsLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="newProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <ProductCard 
            v-for="product in newProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <div v-else class="text-center py-10 text-gray-500">
          No new products available
        </div>
      </div>
    </section>
    
    <!-- 心愿单功能宣传 -->
    <section class="py-12 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-4">Create and Share Your Wishlist</h2>
            <p class="text-lg text-gray-600 mb-6">
              Add your favorite products to your wishlist, share your shopping wishes with friends, and make shopping more social.
            </p>
            <div class="flex space-x-4">
              <NuxtLink to="/wishlist" class="btn btn-primary">
                Create Wishlist
              </NuxtLink>
              <NuxtLink to="/wishlist/public" class="btn btn-outline">
                Explore Public Wishlists
              </NuxtLink>
            </div>
          </div>
          <div class="relative h-64 md:h-80 lg:h-96 rounded-lg overflow-hidden shadow-lg bg-gray-200 flex items-center justify-center">
            <div class="text-gray-500 text-center p-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              <p class="text-lg font-medium">Wishlist Feature Preview</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- 热门商品 -->
    <section class="py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900">Hot Products</h2>
          <NuxtLink to="/products?hot=true" class="text-primary-600 hover:text-primary-500">
            View All <span aria-hidden="true">→</span>
          </NuxtLink>
        </div>
        
        <div v-if="hotProductsLoading" class="flex justify-center py-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-else-if="hotProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
          <ProductCard 
            v-for="product in hotProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <div v-else-if="hotProductsError" class="text-center py-10 text-red-500">
          <p>Failed to fetch hot products:</p>
          <pre class="mt-2 bg-red-50 p-4 rounded text-left overflow-auto">{{ hotProductsError }}</pre>
        </div>
        <div v-else class="text-center py-10 text-gray-500">
          No hot products available
        </div>
      </div>
    </section>
    
    <!-- 幕布幕管理器 -->
    <SlideManager 
      :show="showSlideManager" 
      :initial-slides="carouselSlides"
      @close="showSlideManager = false"
      @save="handleSlidesSave"
    />
  </div>
</template>

<script setup>
// 导入幕布幕管理器组件
import SlideManager from '~/components/SlideManager.vue'
import { useAuthStore } from '~/stores/auth'
import AdminModeSwitch from '~/components/AdminModeSwitch.vue'

// 获取API服务
const api = useApi()

// 获取认证状态
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

// 检查是否是管理员
const isAdmin = computed(() => {
  return authStore.user?.is_staff || authStore.user?.is_superuser || false
})

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

// 获取分类数据
const fetchCategories = async () => {
  try {
    categoriesLoading.value = true
    const response = await api.categories.getTree()
    console.log('分类数据响应:', response)
    
    // 检查API返回结构
    if (response && response.code === 0 && response.data) {
      // 如果是 { code: 0, message: 'success', data: [...] } 结构
      categories.value = response.data
    } else {
      // 如果直接返回数组
      categories.value = response || []
    }
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
    
    // 检查API返回结构
    if (response && response.code === 0 && response.data) {
      // 如果是 { code: 0, message: 'success', data: [...] } 结构
      recommendedProducts.value = response.data
    } else {
      // 如果直接返回数组
      recommendedProducts.value = response || []
    }
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
    
    // 检查API返回结构
    if (response && response.code === 0 && response.data) {
      // 如果是 { code: 0, message: 'success', data: [...] } 结构
      newProducts.value = response.data
    } else {
      // 如果直接返回数组
      newProducts.value = response || []
    }
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
    
    // 为热门商品添加额外的错误处理和重试逻辑
    let retries = 0;
    const maxRetries = 2;
    let success = false;
    let response;
    
    while (!success && retries <= maxRetries) {
      try {
        response = await api.products.getHot();
        success = true;
      } catch (retryError) {
        retries++;
        console.warn(`获取热门商品失败，尝试重试 ${retries}/${maxRetries}:`, retryError);
        if (retries > maxRetries) throw retryError;
        // 等待短暂时间后重试
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    console.log('热门商品响应:', response)
    
    // 检查API返回结构
    if (response && response.code === 0 && response.data) {
      // 如果是 { code: 0, message: 'success', data: [...] } 结构
      hotProducts.value = response.data
    } else {
      // 如果直接返回数组
      hotProducts.value = response || []
    }
  } catch (error) {
    console.error('获取热门商品失败:', error)
    hotProductsError.value = `错误: ${error.message || JSON.stringify(error) || '未知错误'}`
    // 出错时设置为空数组而不是undefined
    hotProducts.value = []
  } finally {
    hotProductsLoading.value = false
  }
}

// 获取轮播图数据
const fetchSlides = async () => {
  try {
    slidesLoading.value = true
    
    // 尝试从API获取幻灯片数据
    const response = await api.banners.getList()
    console.log('轮播图API响应:', response)
    
    // 检查API返回结构
    if (response && response.results && response.results.length > 0) {
      // 将API返回的数据转换为前端需要的格式
      carouselSlides.value = response.results.map(banner => ({
        id: banner.id.toString(),
        title: banner.title || '优质商品，精选推荐',
        subtitle: banner.subtitle || '为您提供高品质的精选商品，满足您的一站式购物需求。',
        buttonText: banner.button_text || '开始购物',
        buttonLink: banner.link || '/categories',
        backgroundColor: 'bg-gradient-to-r from-primary-700 to-primary-900',
        backgroundImage: banner.image_url || ''
      }))
      
      // 同步到localStorage作为缓存
      localStorage.setItem('carouselSlides', JSON.stringify(carouselSlides.value))
    } else {
      // 如果API没有返回数据，尝试从localStorage获取
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
        localStorage.setItem('carouselSlides', JSON.stringify(carouselSlides.value))
      }
    }
  } catch (error) {
    console.error('获取幕布幕数据失败:', error)
    
    // 出错时尝试从localStorage获取
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
    }
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

// 根据分类名称返回对应的图标
const getCategoryIcon = (categoryName) => {
  // 转换为小写并去除多余空格便于匹配
  const name = categoryName?.toLowerCase().trim() || '';
  
  // 分类名称与图标路径的映射
  const iconMap = {
    'inspirational books': {
      path: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
      class: 'text-blue-600'
    },
    'chocolate gift box': {
      path: 'M21 15.546c-.523 0-1.046.151-1.5.454a2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.701 2.701 0 00-1.5-.454M9 6v2m3-2v2m3-2v2M9 3h.01M12 3h.01M15 3h.01M21 21v-7a2 2 0 00-2-2H5a2 2 0 00-2 2v7h18zm-3-9v-2a2 2 0 00-2-2H8a2 2 0 00-2 2v2h12z',
      class: 'text-yellow-700'
    },
    'bouquet gift box': {
      path: 'M12 6v6m0 0v6m0-6h6m-6 0H6',
      class: 'text-pink-500'
    },
    'home pajamas': {
      path: 'M3 12l2-2m0 0l7-7 7 7m-7-7v14',
      class: 'text-indigo-500'
    },
    'customized cutting board': {
      path: 'M4 6h16M4 10h16M4 14h16M4 18h16',
      class: 'text-yellow-800'
    },
    'handmade diy for girls': {
      path: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z',
      class: 'text-pink-600'
    },
    'customized name necklace': {
      path: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z',
      class: 'text-yellow-500'
    },
    'mother and daughter bracelet': {
      path: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9',
      class: 'text-purple-500'
    },
    // 添加通用分类图标
    'clothing': {
      path: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4',
      class: 'text-blue-500'
    },
    'jewelry': {
      path: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-.553.894L15 18M5 18l-4.553-2.276A1 1 0 010 14.618V7.854a1 1 0 01.553-.894L5 5M9.364 5H5.5M9.364 5a4.5 4.5 0 105.872 0M9.364 5L15.5 5M20 12V8h-8a4 4 0 11-8 0H0v4a4 4 0 004 4h16a4 4 0 004-4z',
      class: 'text-yellow-500'
    },
    'electronics': {
      path: 'M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18',
      class: 'text-indigo-500'
    },
    'books': {
      path: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
      class: 'text-blue-600'
    },
  };
  
  // 尝试直接匹配
  if (iconMap[name]) {
    return iconMap[name];
  }
  
  // 如果没有直接匹配，尝试部分匹配
  for (const key in iconMap) {
    if (name.includes(key) || key.includes(name)) {
      return iconMap[key];
    }
  }
  
  // 返回默认图标
  return {
    path: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4',
    class: 'text-primary-500'
  };
};
</script>
