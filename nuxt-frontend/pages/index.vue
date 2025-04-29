<template>
  <div>
    <!-- Homepage Carousel -->
    <section class="relative">
      <!-- Admin Mode Toggle -->
      <div v-if="isDev" class="absolute top-4 right-4 z-50 p-2 bg-gray-100 bg-opacity-80 rounded-md flex items-center justify-between">
        <span class="text-sm text-gray-700 mr-2">Admin Mode</span>
        <button 
          @click="adminModeEnabled = !adminModeEnabled" 
          class="px-3 py-1 text-xs rounded-full" 
          :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
        >
          {{ adminModeEnabled ? 'Enabled' : 'Disabled' }}
        </button>
      </div>

      <!-- Edit Slides Button -->
      <div v-if="adminModeEnabled" class="absolute top-4 left-4 z-50">
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
      
      <!-- Carousel Container -->
      <div class="carousel-container h-[500px] overflow-hidden relative">
        <!-- Carousel Content -->
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
      
      <!-- Carousel Indicators and Controls -->
      <div class="absolute bottom-5 left-0 right-0 flex justify-center space-x-2">
        <button 
          v-for="(slide, index) in carouselSlides" 
          :key="slide.id"
          @click="currentSlideIndex = index"
          class="w-3 h-3 rounded-full bg-white transition-opacity"
          :class="currentSlideIndex === index ? 'opacity-100' : 'opacity-50'"
        ></button>
      </div>

      <!-- Navigation Arrows -->
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
    
    <!-- Categories Navigation -->
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
            :to="`http://127.0.0.1:8000/api/v1/categories?category=${category.id}`"
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
          No categories available
        </div>
      </div>
    </section>
    
    <!-- Recommended Products -->
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
        
        <div v-else-if="recommendedProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
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
    
    <!-- Promotional Banner -->
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
    
    <!-- New Arrivals -->
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
        
        <div v-else-if="newProducts.length" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
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
    
    <!-- Wishlist Feature Promotion -->
    <section class="py-12 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div>
            <h2 class="text-3xl font-bold text-gray-900 mb-4">Create Your Wishlist</h2>
            <p class="text-lg text-gray-600 mb-6">Add your favorite products to a wishlist and share it with friends and family. Perfect for birthdays, holidays, or any special occasion!</p>
            <div class="space-y-4">
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p class="ml-3 text-gray-600">Create multiple wishlists for different occasions</p>
              </div>
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p class="ml-3 text-gray-600">Share your wishlist with a simple link</p>
              </div>
              <div class="flex items-start">
                <div class="flex-shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <p class="ml-3 text-gray-600">Track purchased items and receive notifications</p>
              </div>
            </div>
            <div class="mt-8">
              <NuxtLink to="/wishlist" class="btn btn-primary">
                Start Your Wishlist
              </NuxtLink>
            </div>
          </div>
          <div class="flex justify-center">
            <img src="/images/wishlist-promo.png" alt="Wishlist Feature" class="max-w-full h-auto rounded-lg shadow-lg">
          </div>
        </div>
      </div>
    </section>
    
    <!-- Slide Manager Modal -->
    <SlideManager 
      v-if="showSlideManager" 
      :show="showSlideManager" 
      :initial-slides="carouselSlides"
      @close="showSlideManager = false"
      @save="saveSlides"
    />
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import SlideManager from '~/components/SlideManager.vue'

// State
const isDev = process.env.NODE_ENV === 'development'
const adminModeEnabled = ref(false)
const categoriesLoading = ref(true)
const recommendedLoading = ref(true)
const newProductsLoading = ref(true)
const categories = ref([])
const recommendedProducts = ref([])
const newProducts = ref([])
const showSlideManager = ref(false)

// Carousel state
const currentSlideIndex = ref(0)
const carouselSlides = ref([])

// Fetch data
onMounted(async () => {
  try {
    // 尝试从API获取幻灯片数据
    const { data } = await useFetch('http://127.0.0.1:8000/api/v1/admin/settings/?site=default')
    
    if (data.value && data.value.code === 0 && data.value.data && data.value.data.homepage && data.value.data.homepage.carousel) {
      // 使用API返回的幻灯片数据
      const apiSlides = data.value.data.homepage.carousel;
      // 只显示启用的幻灯片
      const activeSlides = apiSlides.filter(slide => slide.active);
      // 按顺序排序
      activeSlides.sort((a, b) => a.order - b.order);
      
      if (activeSlides.length > 0) {
        carouselSlides.value = activeSlides;
      } else {
        // 如果没有启用的幻灯片，使用默认数据
        loadDefaultSlides();
      }
    } else {
      // API调用失败或返回格式不正确，使用默认数据
      loadDefaultSlides();
    }
    
    // 设置轮播间隔
    if (process.client && carouselSlides.value.length > 1) {
      const interval = setInterval(() => {
        nextSlide()
      }, 5000)
      
      // 组件卸载时清除间隔
      onUnmounted(() => {
        clearInterval(interval)
      })
    }
    
    // 获取分类
    await fetchCategories()
    
    // 获取推荐产品
    await fetchRecommendedProducts()
    
    // 获取新产品
    await fetchNewProducts()
  } catch (error) {
    console.error('Error initializing homepage:', error)
    // 出错时使用默认数据
    loadDefaultSlides();
  }
})

// 加载默认幻灯片数据
const loadDefaultSlides = () => {
  // 首先尝试从本地存储加载
  if (process.client && localStorage.getItem('carouselSlides')) {
    try {
      const savedSlides = JSON.parse(localStorage.getItem('carouselSlides'))
      if (Array.isArray(savedSlides) && savedSlides.length > 0) {
        carouselSlides.value = savedSlides
        return;
      }
    } catch (error) {
      console.error('Failed to parse saved slides:', error)
    }
  }
  
  // 如果本地存储没有数据，使用硬编码的默认数据
  carouselSlides.value = [
  {
    id: '1',
    title: 'Welcome to Our Online Store',
    subtitle: 'Discover amazing products with great prices',
    buttonText: 'Shop Now',
    buttonLink: '/products',
    backgroundColor: 'bg-gradient-to-r from-blue-700 to-indigo-900',
    backgroundImage: '/images/hero-1.jpg'
  },
  {
    id: '2',
    title: 'Summer Collection',
    subtitle: 'Explore our new arrivals for the season',
    buttonText: 'View Collection',
    buttonLink: '/products?new=true',
    backgroundColor: 'bg-gradient-to-r from-orange-500 to-pink-600',
    backgroundImage: '/images/hero-2.jpg'
  }
  ]
}

// Carousel navigation
const nextSlide = () => {
  currentSlideIndex.value = (currentSlideIndex.value + 1) % carouselSlides.value.length
}

const prevSlide = () => {
  currentSlideIndex.value = (currentSlideIndex.value - 1 + carouselSlides.value.length) % carouselSlides.value.length
}

// Get slide style based on slide data
const getSlideStyle = (slide) => {
  let style = `background-color: var(--color-primary-700);`
  
  if (slide.backgroundColor) {
    // If the background color is a Tailwind class, we need to handle it differently
    if (slide.backgroundColor.startsWith('bg-')) {
      // We'll keep the class and apply it directly to the element
    } else {
      style = `background-color: ${slide.backgroundColor};`
    }
  }
  
  if (slide.backgroundImage) {
    style += ` background-image: url(${slide.backgroundImage}); background-size: cover; background-position: center;`
  }
  
  return style
}

// Open slide manager
const openSlideManager = () => {
  showSlideManager.value = true
}

// Save slides
const saveSlides = (slides) => {
  carouselSlides.value = slides
  
  // Save to local storage in development
  if (process.client) {
    try {
      localStorage.setItem('carouselSlides', JSON.stringify(slides))
    } catch (error) {
      console.error('Failed to save slides to local storage:', error)
    }
  }
}

// Fetch categories
const fetchCategories = async () => {
  try {
    categoriesLoading.value = true
    const { data } = await useFetch('http://127.0.0.1:8000/api/v1/categories/?site=default')
    if (data.value && data.value.code === 0 && data.value.data) {
      categories.value = data.value.data.results || []
    } else {
      categories.value = []
    }
  } catch (error) {
    console.error('Failed to fetch categories:', error)
    categories.value = []
  } finally {
    categoriesLoading.value = false
  }
}

// Fetch recommended products
const fetchRecommendedProducts = async () => {
  try {
    recommendedLoading.value = true
    const { data } = await useFetch('http://127.0.0.1:8000/api/v1/products/?recommended=true&limit=8&site=default')
    if (data.value && data.value.code === 0 && data.value.data) {
      recommendedProducts.value = data.value.data.results || []
    } else {
      recommendedProducts.value = []
    }
  } catch (error) {
    console.error('Failed to fetch recommended products:', error)
    recommendedProducts.value = []
  } finally {
    recommendedLoading.value = false
  }
}

// Fetch new products
const fetchNewProducts = async () => {
  try {
    newProductsLoading.value = true
    const { data } = await useFetch('http://127.0.0.1:8000/api/v1/products/?new=true&limit=8&site=default')
    if (data.value && data.value.code === 0 && data.value.data) {
      newProducts.value = data.value.data.results || []
    } else {
      newProducts.value = []
    }
  } catch (error) {
    console.error('Failed to fetch new products:', error)
    newProducts.value = []
  } finally {
    newProductsLoading.value = false
  }
}
</script>
