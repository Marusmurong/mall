<template>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <template v-else-if="category">
        <!-- 分类信息 -->
        <div class="mb-8">
          <!-- 面包屑导航 -->
          <nav class="flex mb-4" aria-label="Breadcrumb">
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
              <li v-if="category.parent" aria-current="page">
                <div class="flex items-center">
                  <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  <NuxtLink :to="`/categories/${category.parent.id}`" class="ml-1 text-gray-500 hover:text-gray-700 md:ml-2">
                    {{ category.parent.name }}
                  </NuxtLink>
                </div>
              </li>
              <li aria-current="page">
                <div class="flex items-center">
                  <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  <span class="ml-1 text-gray-500 md:ml-2 font-medium">{{ category.name }}</span>
                </div>
              </li>
            </ol>
          </nav>
          
          <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ category.name }}</h1>
              <p v-if="category.description" class="mt-2 text-gray-600">{{ category.description }}</p>
            </div>
            
            <!-- 商品数量 -->
            <div class="mt-4 md:mt-0">
              <span class="text-gray-500">{{ products.length }} 件商品</span>
            </div>
          </div>
        </div>
        
        <!-- 子分类选项卡 -->
        <div v-if="category.children && category.children.length" class="mb-8">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8">
              <NuxtLink 
                :to="`/categories/${category.id}`"
                class="border-primary-500 text-primary-600 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                aria-current="page"
              >
                全部
              </NuxtLink>
              
              <NuxtLink 
                v-for="child in category.children" 
                :key="child.id"
                :to="`/categories/${child.id}`"
                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
              >
                {{ child.name }}
              </NuxtLink>
            </nav>
          </div>
        </div>
        
        <!-- 筛选器 -->
        <div class="mb-8 bg-white shadow-sm rounded-lg p-4">
          <div class="flex flex-wrap items-center gap-4">
            <!-- 排序 -->
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2">排序:</span>
              <select v-model="sortBy" class="text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500">
                <option value="default">默认</option>
                <option value="price_asc">价格从低到高</option>
                <option value="price_desc">价格从高到低</option>
                <option value="newest">最新上架</option>
                <option value="sales">销量优先</option>
              </select>
            </div>
            
            <!-- 价格区间 -->
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2">价格:</span>
              <div class="flex items-center">
                <input 
                  v-model="priceMin" 
                  type="number" 
                  placeholder="最低" 
                  class="w-20 text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                >
                <span class="mx-2">-</span>
                <input 
                  v-model="priceMax" 
                  type="number" 
                  placeholder="最高" 
                  class="w-20 text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                >
                <button 
                  @click="applyPriceFilter"
                  class="ml-2 px-2 py-1 bg-primary-600 text-white text-sm rounded hover:bg-primary-700"
                >
                  确定
                </button>
              </div>
            </div>
            
            <!-- 筛选选项 -->
            <div class="flex items-center space-x-4">
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterNew" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">新品</span>
              </label>
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterHot" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">热销</span>
              </label>
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">特价</span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- 商品列表 -->
        <div v-if="filteredProducts.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 md:gap-6">
          <ProductCard 
            v-for="product in filteredProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        
        <!-- 无商品状态 -->
        <div v-else class="text-center py-10">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">暂无商品</h3>
          <p class="mt-1 text-gray-500">该分类下暂时没有商品，请查看其他分类。</p>
        </div>
        
        <!-- 分页 -->
        <div v-if="filteredProducts.length" class="mt-8 flex justify-center">
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <a href="#" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              <span class="sr-only">上一页</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
            </a>
            <a href="#" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              1
            </a>
            <a href="#" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-primary-50 text-sm font-medium text-primary-600 hover:bg-primary-100">
              2
            </a>
            <a href="#" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              3
            </a>
            <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
              ...
            </span>
            <a href="#" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              8
            </a>
            <a href="#" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              9
            </a>
            <a href="#" class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              10
            </a>
            <a href="#" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              <span class="sr-only">下一页</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </a>
          </nav>
        </div>
      </template>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">获取分类失败</h3>
        <p class="mt-1 text-gray-500">{{ error }}</p>
        <button 
          @click="fetchCategoryData"
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
const categoryId = route.params.id

// 获取API服务
const api = useApi()

// 状态
const category = ref(null)
const products = ref([])
const loading = ref(true)
const error = ref(null)

// 筛选和排序
const sortBy = ref('default')
const priceMin = ref('')
const priceMax = ref('')
const filterNew = ref(false)
const filterHot = ref(false)
const filterDiscount = ref(false)

// 获取分类详情和商品
const fetchCategoryData = async () => {
  try {
    loading.value = true
    error.value = null
    
    console.log('开始获取分类详情, ID:', categoryId)
    
    // 获取分类详情
    try {
      const categoryData = await api.categories.getById(categoryId)
      console.log('分类详情响应:', categoryData)
      category.value = categoryData || null
    } catch (categoryErr) {
      console.error('获取分类详情失败:', categoryErr)
      error.value = categoryErr.message || '获取分类详情失败'
    }
    
    // 获取分类下的商品
    try {
      console.log('开始获取分类商品, ID:', categoryId)
      const productsData = await api.categories.getProducts(categoryId)
      console.log('分类商品响应:', productsData)
      products.value = productsData || []
    } catch (productsErr) {
      console.error('获取分类商品失败:', productsErr)
      // 如果分类详情成功但商品失败，仍然显示分类信息
      if (!error.value) {
        error.value = productsErr.message || '获取分类商品失败'
      }
    }
  } catch (err) {
    console.error('获取分类数据失败:', err)
    error.value = err.message || '获取分类数据失败'
  } finally {
    loading.value = false
  }
}

// 应用价格筛选
const applyPriceFilter = () => {
  // 这里可以添加价格验证逻辑
}

// 筛选后的商品列表
const filteredProducts = computed(() => {
  let result = [...products.value]
  
  // 应用筛选条件
  if (filterNew.value) {
    result = result.filter(product => product.is_new)
  }
  
  if (filterHot.value) {
    result = result.filter(product => product.is_hot)
  }
  
  if (filterDiscount.value) {
    // 支持两种折扣格式：discount_price或original_price
    result = result.filter(product => {
      return product.discount_price || 
        (product.original_price && product.original_price !== product.price)
    })
  }
  
  // 应用价格筛选
  if (priceMin.value) {
    result = result.filter(product => {
      // 获取实际销售价格，支持两种折扣格式
      const price = product.discount_price || product.price
      return parseFloat(price) >= Number(priceMin.value)
    })
  }
  
  if (priceMax.value) {
    result = result.filter(product => {
      // 获取实际销售价格，支持两种折扣格式
      const price = product.discount_price || product.price
      return parseFloat(price) <= Number(priceMax.value)
    })
  }
  
  // 应用排序
  switch (sortBy.value) {
    case 'price_asc':
      result.sort((a, b) => {
        const priceA = parseFloat(a.discount_price || a.price)
        const priceB = parseFloat(b.discount_price || b.price)
        return priceA - priceB
      })
      break
    case 'price_desc':
      result.sort((a, b) => {
        const priceA = parseFloat(a.discount_price || a.price)
        const priceB = parseFloat(b.discount_price || b.price)
        return priceB - priceA
      })
      break
    case 'newest':
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'sales':
      result.sort((a, b) => (b.sales || 0) - (a.sales || 0))
      break
    default:
      // 默认排序，保持原顺序
      break
  }
  
  return result
})

// 页面加载时获取数据
onMounted(() => {
  fetchCategoryData()
})

// 监听路由变化，重新获取数据
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchCategoryData()
  }
})
</script>
