<template>
  <div>
    <!-- 顶部分类导航 -->
    <div class="bg-white shadow-sm mb-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="overflow-x-auto py-4">
          <div class="flex space-x-4 min-w-max">
            <button 
              @click="selectedCategory = null; fetchProducts()"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors',
                !selectedCategory ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              ]"
            >
              全部商品
            </button>
            <button 
              v-for="category in categories" 
              :key="category.id"
              @click="selectCategory(category)"
              :class="[
                'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors',
                selectedCategory && selectedCategory.id === category.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              ]"
            >
              {{ category.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
      <!-- 移动端筛选按钮 -->
      <div class="lg:hidden mb-4">
        <button 
          @click="mobileFilterOpen = true"
          class="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          筛选
        </button>
      </div>
      
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- 筛选侧边栏 - 桌面版 -->
        <div class="hidden lg:block w-64 flex-shrink-0">
          <div class="bg-white rounded-lg shadow-sm p-4 sticky top-4">
            <h3 class="font-medium text-gray-900 mb-4">筛选选项</h3>
            
            <!-- 价格区间 -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">价格区间</h4>
              <div class="flex items-center space-x-2">
                <input 
                  v-model="priceMin" 
                  type="number" 
                  placeholder="最低价" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
                <span>-</span>
                <input 
                  v-model="priceMax" 
                  type="number" 
                  placeholder="最高价" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
              </div>
              <button 
                @click="applyFilters"
                class="mt-2 w-full px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm rounded"
              >
                应用价格
              </button>
            </div>
            
            <!-- 商品属性 -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">商品属性</h4>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterNew" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">新品</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterHot" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">热销</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">特价</span>
                </label>
              </div>
            </div>
            
            <!-- 子分类 -->
            <div v-if="selectedCategory && selectedCategory.children && selectedCategory.children.length" class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">{{ selectedCategory.name }}分类</h4>
              <div class="space-y-2">
                <label 
                  v-for="child in selectedCategory.children" 
                  :key="child.id"
                  class="flex items-center"
                >
                  <input 
                    type="checkbox" 
                    v-model="selectedSubcategories" 
                    :value="child.id"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  >
                  <span class="ml-2 text-sm text-gray-700">{{ child.name }}</span>
                </label>
              </div>
            </div>
            
            <!-- 重置按钮 -->
            <button 
              @click="resetFilters"
              class="w-full px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded"
            >
              重置筛选
            </button>
          </div>
        </div>
        
        <!-- 商品展示区域 -->
        <div class="flex-grow">
          <!-- 排序选项 -->
          <div class="mb-4 flex justify-between items-center">
            <h1 class="text-xl font-bold">
              {{ selectedCategory ? selectedCategory.name : '所有商品' }}
              <span class="text-sm font-normal text-gray-500 ml-2">{{ filteredProducts.length }} 件商品</span>
            </h1>
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2">排序:</span>
              <select v-model="sortBy" class="form-select rounded-md border-gray-300 text-sm">
                <option value="default">默认排序</option>
                <option value="price_asc">价格从低到高</option>
                <option value="price_desc">价格从高到低</option>
                <option value="newest">最新上架</option>
                <option value="sales">销量优先</option>
              </select>
            </div>
          </div>
          
          <!-- 商品列表 -->
          <div v-if="loading" class="flex justify-center py-10">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
          
          <div v-else-if="filteredProducts.length" class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            <ProductCard 
              v-for="product in filteredProducts" 
              :key="product.id"
              :product="product"
            />
          </div>
          
          <div v-else class="text-center py-10 bg-white rounded-lg shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">暂无商品</h3>
            <p class="mt-1 text-gray-500">没有找到符合条件的商品，请尝试其他筛选条件。</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 移动端筛选侧边栏 -->
    <div 
      v-if="mobileFilterOpen" 
      class="fixed inset-0 flex z-40 lg:hidden"
      @click.self="mobileFilterOpen = false"
    >
      <div class="fixed inset-0 bg-black bg-opacity-25" aria-hidden="true"></div>
      
      <div class="relative max-w-xs w-full bg-white shadow-xl pb-12 flex flex-col h-full">
        <div class="px-4 py-5 flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">筛选选项</h2>
          <button 
            @click="mobileFilterOpen = false"
            class="-mr-2 w-10 h-10 bg-white p-2 rounded-md flex items-center justify-center text-gray-400 hover:bg-gray-50 focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- 筛选选项 - 移动端 -->
        <div class="mt-4 border-t border-gray-200 overflow-y-auto h-full">
          <div class="px-4 py-6">
            <!-- 价格区间 -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">价格区间</h4>
              <div class="flex items-center space-x-2">
                <input 
                  v-model="priceMin" 
                  type="number" 
                  placeholder="最低价" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
                <span>-</span>
                <input 
                  v-model="priceMax" 
                  type="number" 
                  placeholder="最高价" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
              </div>
            </div>
            
            <!-- 商品属性 -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">商品属性</h4>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterNew" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">新品</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterHot" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">热销</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">特价</span>
                </label>
              </div>
            </div>
            
            <!-- 子分类 -->
            <div v-if="selectedCategory && selectedCategory.children && selectedCategory.children.length" class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">{{ selectedCategory.name }}分类</h4>
              <div class="space-y-2">
                <label 
                  v-for="child in selectedCategory.children" 
                  :key="child.id"
                  class="flex items-center"
                >
                  <input 
                    type="checkbox" 
                    v-model="selectedSubcategories" 
                    :value="child.id"
                    class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  >
                  <span class="ml-2 text-sm text-gray-700">{{ child.name }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部按钮 -->
        <div class="border-t border-gray-200 px-4 py-6 mt-auto">
          <div class="flex space-x-3">
            <button 
              @click="resetFilters"
              class="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              重置
            </button>
            <button 
              @click="applyFilters(); mobileFilterOpen = false"
              class="flex-1 px-4 py-2 bg-primary-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700"
            >
              应用筛选
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 获取API服务
const api = useApi()
const route = useRoute()

// 状态
const categories = ref([])
const products = ref([])
const loading = ref(true)
const error = ref(null)
const selectedCategory = ref(null)
const selectedSubcategories = ref([])
const mobileFilterOpen = ref(false)

// 筛选和排序
const sortBy = ref('default')
const priceMin = ref('')
const priceMax = ref('')
const filterNew = ref(false)
const filterHot = ref(false)
const filterDiscount = ref(false)

// 获取所有分类
const fetchCategories = async () => {
  try {
    const response = await api.categories.getTree()
    categories.value = response || []
  } catch (err) {
    console.error('获取分类失败:', err)
  }
}

// 获取商品
const fetchProducts = async (categoryId = null) => {
  try {
    loading.value = true
    error.value = null
    
    let productsData
    if (categoryId) {
      productsData = await api.categories.getProducts(categoryId)
    } else {
      productsData = await api.products.getAll()
    }
    
    products.value = productsData || []
  } catch (err) {
    console.error('获取商品失败:', err)
    error.value = err.message || '获取商品数据失败'
  } finally {
    loading.value = false
  }
}

// 选择分类
const selectCategory = async (category) => {
  selectedCategory.value = category
  selectedSubcategories.value = []
  await fetchProducts(category.id)
}

// 应用筛选
const applyFilters = () => {
  // 触发计算属性重新计算
}

// 重置筛选
const resetFilters = () => {
  priceMin.value = ''
  priceMax.value = ''
  filterNew.value = false
  filterHot.value = false
  filterDiscount.value = false
  selectedSubcategories.value = []
}

// 筛选后的商品列表
const filteredProducts = computed(() => {
  let result = [...products.value]
  
  // 应用子分类筛选
  if (selectedSubcategories.value.length > 0) {
    result = result.filter(product => 
      product.categories && product.categories.some(cat => 
        selectedSubcategories.value.includes(cat.id)
      )
    )
  }
  
  // 应用商品属性筛选
  if (filterNew.value) {
    result = result.filter(product => product.is_new)
  }
  
  if (filterHot.value) {
    result = result.filter(product => product.is_hot)
  }
  
  if (filterDiscount.value) {
    result = result.filter(product => {
      return product.discount_price || 
        (product.original_price && product.original_price !== product.price)
    })
  }
  
  // 应用价格筛选
  if (priceMin.value) {
    result = result.filter(product => {
      const price = product.discount_price || product.price
      return parseFloat(price) >= Number(priceMin.value)
    })
  }
  
  if (priceMax.value) {
    result = result.filter(product => {
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
  }
  
  return result
})

// 页面加载时获取数据
onMounted(async () => {
  await fetchCategories()
  
  // 检查URL中是否有分类ID
  if (route.query.category) {
    const categoryId = route.query.category
    const category = categories.value.find(c => c.id === categoryId)
    if (category) {
      await selectCategory(category)
    } else {
      await fetchProducts()
    }
  } else {
    await fetchProducts()
  }
})

// 定义页面元数据
definePageMeta({
  layout: 'default',
  title: '商品分类',
  description: '浏览我们的全部商品，找到您喜爱的产品'
})
</script>

<style scoped>
/* 自定义滚动条样式 */
.overflow-x-auto {
  scrollbar-width: thin;
  scrollbar-color: #e5e7eb #f9fafb;
}

.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f9fafb;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background-color: #d1d5db;
}
</style>
