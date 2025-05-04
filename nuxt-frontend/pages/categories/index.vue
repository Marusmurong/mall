<template>
  <div>
    <!-- Top categories navigation -->
    <div class="bg-white shadow-sm mb-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="overflow-x-auto py-4">
          <div class="flex space-x-4 min-w-max">
            <NuxtLink
              :to="`/categories`"
              :class="[
                'flex flex-col items-center p-4 bg-white rounded-lg shadow-sm transition-shadow',
                selectedCategory === null ? 'ring-2 ring-primary-500 shadow-md' : 'hover:shadow-md'
              ]"
            >
              <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-3 transition-all duration-300 hover:bg-primary-200">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-500 transition-all duration-300 transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
              </div>
              <span class="text-sm font-medium text-gray-900 text-center">All Products</span>
            </NuxtLink>

            <NuxtLink
              v-for="category in filteredCategories"
              :key="category.id"
              :to="`/categories/${category.id}`"
              :class="[
                'flex flex-col items-center p-4 bg-white rounded-lg shadow-sm transition-shadow',
                selectedCategory === category.id ? 'ring-2 ring-primary-500 shadow-md' : 'hover:shadow-md'
              ]"
            >
              <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-3 transition-all duration-300 hover:bg-primary-200">
                <img v-if="category.image" :src="category.image" :alt="category.name" class="w-10 h-10 object-contain">
                <svg v-else-if="getCategoryIcon(category.name)" :class="getCategoryIcon(category.name).class" class="h-8 w-8 text-primary-500 transition-all duration-300 transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getCategoryIcon(category.name).path" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
              <span class="text-sm font-medium text-gray-900 text-center">{{ category.name }}</span>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main content area -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
      <!-- Mobile filter button -->
      <div class="lg:hidden mb-4">
        <button 
          @click="mobileFilterOpen = true"
          class="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filter
        </button>
      </div>
      
      <div class="flex flex-col lg:flex-row gap-6">
        <!-- Filter sidebar - Desktop -->
        <div class="hidden lg:block w-64 flex-shrink-0">
          <div class="bg-white rounded-lg shadow-sm p-4 sticky top-4">
            <h3 class="font-medium text-gray-900 mb-4">Filter Options</h3>
            
            <!-- Price range -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Price Range</h4>
              <div class="flex items-center space-x-2">
                <input 
                  v-model="priceMin" 
                  type="number" 
                  placeholder="Min price" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
                <span>-</span>
                <input 
                  v-model="priceMax" 
                  type="number" 
                  placeholder="Max price" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
              </div>
              <button 
                @click="applyFilters"
                class="mt-2 w-full px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm rounded"
              >
                Apply Price
              </button>
            </div>
            
            <!-- Product attributes -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Product Attributes</h4>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterNew" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">New Arrivals</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterHot" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">Hot Sales</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">On Sale</span>
                </label>
              </div>
            </div>
            
            <!-- Subcategories -->
            <div v-if="selectedCategory && selectedCategory.children && selectedCategory.children.length" class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">{{ selectedCategory.name }} Categories</h4>
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
            
            <!-- Reset button -->
            <button 
              @click="resetFilters"
              class="w-full px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded"
            >
              Reset Filters
            </button>
          </div>
        </div>
        
        <!-- Products display area -->
        <div class="flex-grow">
          <!-- Sort options -->
          <div class="mb-4 flex justify-between items-center">
            <h1 class="text-xl font-bold">
              {{ selectedCategory ? selectedCategory.name : 'All Products' }}
              <span class="text-sm font-normal text-gray-500 ml-2">{{ filteredProducts.length }} products</span>
            </h1>
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2">Sort by:</span>
              <select v-model="sortBy" class="form-select rounded-md border-gray-300 text-sm">
                <option value="default">Default</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="newest">Newest</option>
                <option value="sales">Best Selling</option>
              </select>
            </div>
          </div>
          
          <!-- Product list -->
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
            <h3 class="mt-4 text-lg font-medium text-gray-900">No Products Found</h3>
            <p class="mt-1 text-gray-500">No products match your filter criteria. Please try different filters.</p>
          </div>
        </div>
      </div>
      
      <!-- Pagination -->
      <div v-if="totalPages > 1" class="mt-8">
        <!-- Page information -->
        <div class="text-center text-sm text-gray-600 mb-3">
          Page {{ currentPage }} of {{ totalPages }} (showing {{ products.length }} of {{ productsTotal }} products)
        </div>
        
        <div class="flex justify-center">
          <div class="flex space-x-2">
            <button 
              @click="changePage(currentPage - 1)" 
              :disabled="currentPage === 1"
              class="px-4 py-2 border rounded-md transition-colors"
              :class="currentPage === 1 ? 'bg-gray-100 cursor-not-allowed' : 'bg-white hover:bg-gray-50'"
            >
              Previous
            </button>
            
            <template v-for="page in visiblePages" :key="page">
              <span v-if="page === '...'" class="px-4 py-2">
                ...
              </span>
              <button
                v-else
                @click="changePage(page)"
                :class="[
                  'px-4 py-2 border rounded-md',
                  currentPage === page 
                    ? 'bg-primary-600 text-white border-primary-600' 
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
            </template>
            
            <button 
              @click="changePage(currentPage + 1)" 
              :disabled="currentPage === totalPages"
              class="px-4 py-2 border rounded-md transition-colors"
              :class="currentPage === totalPages ? 'bg-gray-100 cursor-not-allowed' : 'bg-white hover:bg-gray-50'"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Mobile filter sidebar -->
    <div 
      v-if="mobileFilterOpen" 
      class="fixed inset-0 flex z-40 lg:hidden"
      @click.self="mobileFilterOpen = false"
    >
      <div class="fixed inset-0 bg-black bg-opacity-25" aria-hidden="true"></div>
      
      <div class="relative max-w-xs w-full bg-white shadow-xl pb-12 flex flex-col h-full">
        <div class="px-4 py-5 flex items-center justify-between">
          <h2 class="text-lg font-medium text-gray-900">Filter Options</h2>
          <button 
            @click="mobileFilterOpen = false"
            class="-mr-2 w-10 h-10 bg-white p-2 rounded-md flex items-center justify-center text-gray-400 hover:bg-gray-50 focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <!-- Filter options - Mobile -->
        <div class="mt-4 border-t border-gray-200 overflow-y-auto h-full">
          <div class="px-4 py-6">
            <!-- Price range -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Price Range</h4>
              <div class="flex items-center space-x-2">
                <input 
                  v-model="priceMin" 
                  type="number" 
                  placeholder="Min price" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
                <span>-</span>
                <input 
                  v-model="priceMax" 
                  type="number" 
                  placeholder="Max price" 
                  class="form-input rounded-md border-gray-300 w-24 text-sm"
                >
              </div>
            </div>
            
            <!-- Product attributes -->
            <div class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Product Attributes</h4>
              <div class="space-y-2">
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterNew" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">New Arrivals</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterHot" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">Hot Sales</span>
                </label>
                <label class="flex items-center">
                  <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                  <span class="ml-2 text-sm text-gray-700">On Sale</span>
                </label>
              </div>
            </div>
            
            <!-- Subcategories -->
            <div v-if="selectedCategory && selectedCategory.children && selectedCategory.children.length" class="mb-6">
              <h4 class="text-sm font-medium text-gray-700 mb-2">{{ selectedCategory.name }} Categories</h4>
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
        
        <!-- Bottom buttons -->
        <div class="border-t border-gray-200 px-4 py-6 mt-auto">
          <div class="flex space-x-3">
            <button 
              @click="resetFilters"
              class="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Reset
            </button>
            <button 
              @click="applyFilters(); mobileFilterOpen = false"
              class="flex-1 px-4 py-2 bg-primary-600 border border-transparent rounded-md text-sm font-medium text-white hover:bg-primary-700"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Get API service
const api = useApi()
const route = useRoute()

// State
const categories = ref([])
const filteredCategories = ref([])
const products = ref([])
const loading = ref(true)
const error = ref(null)
const selectedCategory = ref(null)
const selectedSubcategories = ref([])
const mobileFilterOpen = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const visiblePages = ref([])
const productsTotal = ref(0)

// Filter and sort
const sortBy = ref('default')
const priceMin = ref('')
const priceMax = ref('')
const filterNew = ref(false)
const filterHot = ref(false)
const filterDiscount = ref(false)

// Get all categories
const fetchCategories = async () => {
  try {
    console.log('开始获取分类树')
    const response = await api.categories.getTree()
    console.log('分类树响应:', response)
    
    // 检查API响应格式，处理新的返回结构
    let categoriesData = []
    if (response && response.code === 0 && response.data) {
      // 处理新的API响应格式：{ code: 0, message: 'success', data: [...] }
      categoriesData = response.data
      console.log('已找到分类数据:', categoriesData.length)
    } else if (Array.isArray(response)) {
      // 处理旧的API响应格式：直接返回数组
      categoriesData = response
      console.log('已找到分类数据(旧格式):', categoriesData.length)
    } else {
      console.log('未找到有效的分类数据:', response)
      categoriesData = []
    }
    
    // 保存所有分类
    categories.value = categoriesData
    
    // 仅显示有产品的子分类
    const filtered = []
    if (Array.isArray(categories.value)) {
      categories.value.forEach(category => {
        if (category && category.level === 1 && Array.isArray(category.children)) {
          category.children.forEach(child => {
            if (child && (child.product_count > 0 || true)) { // 暂时显示所有子分类
              filtered.push(child)
            }
          })
        } else if (category && category.level === 2 && (category.product_count > 0 || true)) { // 暂时显示所有二级分类
          filtered.push(category)
        }
      })
    }
    
    // 按产品数量排序
    filtered.sort((a, b) => (b.product_count || 0) - (a.product_count || 0))
    filteredCategories.value = filtered
    console.log('过滤后的分类:', filteredCategories.value.length)
    
  } catch (err) {
    console.error('获取分类失败:', err)
    categories.value = []
    filteredCategories.value = []
  }
}

// Get products
const fetchProducts = async (categoryId = null, page = 1, filterParams = {}) => {
  try {
    loading.value = true
    error.value = null
    
    const pageSize = 40 // Products per page - 修改为每页40个商品
    console.log('获取商品, 分类ID:', categoryId, '页码:', page)
    
    let productsData
    let apiResponse
    
    if (categoryId) {
      // 确保将页码作为query参数正确传递
      apiResponse = await api.categories.getProducts(categoryId, page, pageSize, filterParams)
      console.log('分类商品响应:', apiResponse)
    } else {
      // 确保将页码作为query参数正确传递
      apiResponse = await api.products.getAll(page, pageSize, filterParams)
      console.log('所有商品响应:', apiResponse)
    }
    
    // 处理新的API响应格式
    if (apiResponse && apiResponse.code === 0 && apiResponse.data) {
      // 新的API响应格式: { code: 0, message: 'success', data: {...} }
      productsData = apiResponse.data
      console.log('从API响应中提取数据:', productsData)
    } else {
      // 旧的API响应格式，直接使用
      productsData = apiResponse
    }
    
    // 确保正确提取数据，处理不同的API响应格式
    if (productsData && productsData.data) {
      // 直接使用data字段
      products.value = productsData.data
      totalPages.value = productsData.totalPages || 1
      productsTotal.value = productsData.total || products.value.length
    } else if (productsData && productsData.results) {
      // 使用results字段(Django REST Framework格式)
      products.value = productsData.results
      totalPages.value = Math.ceil((productsData.count || 0) / pageSize)
      productsTotal.value = productsData.count || 0
    } else if (Array.isArray(productsData)) {
      // 直接数组
      products.value = productsData
      totalPages.value = 1
      productsTotal.value = productsData.length
    } else {
      products.value = []
      totalPages.value = 1
      productsTotal.value = 0
    }
    
    currentPage.value = page
    visiblePages.value = getVisiblePages()
    
    console.log('加载的商品数:', products.value.length)
    console.log('商品总数:', productsTotal.value)
    console.log('总页数:', totalPages.value)
    console.log('当前页码:', currentPage.value)
  } catch (err) {
    console.error('获取商品失败:', err)
    error.value = err.message || '获取商品数据失败'
    products.value = []
    totalPages.value = 1
    productsTotal.value = 0
  } finally {
    loading.value = false
  }
}

// Select category
const selectCategory = async (category) => {
  selectedCategory.value = category
  selectedSubcategories.value = []
  currentPage.value = 1 // Reset to first page
  await fetchProducts(category.id, 1)
}

// Apply filters
const applyFilters = async () => {
  loading.value = true
  try {
    // 使用API重新获取带筛选条件的数据，而不是在前端筛选
    const pageSize = 40 // Products per page - 修改为每页40个商品
    
    // 构建筛选参数对象
    const filterParams = {
      page: 1, // 重置为第一页
      limit: pageSize,
      min_price: priceMin.value || undefined,
      max_price: priceMax.value || undefined,
      is_new: filterNew.value || undefined,
      is_hot: filterHot.value || undefined,
      is_discount: filterDiscount.value || undefined,
      sort: sortBy.value !== 'default' ? sortBy.value : undefined,
      subcategories: selectedSubcategories.value.length > 0 ? selectedSubcategories.value.join(',') : undefined
    }
    
    console.log('应用筛选条件:', filterParams)
    
    let apiResponse
    if (selectedCategory.value) {
      // 获取选定分类的筛选商品
      apiResponse = await api.categories.getProducts(
        selectedCategory.value.id,
        1, // 重置为第一页
        pageSize,
        filterParams
      )
      console.log('分类筛选商品响应:', apiResponse)
    } else {
      // 获取所有商品的筛选结果
      apiResponse = await api.products.getAll(1, pageSize, filterParams)
      console.log('所有商品筛选响应:', apiResponse)
    }
    
    // 处理API响应
    let productsData
    if (apiResponse && apiResponse.code === 0 && apiResponse.data) {
      // 新的API响应格式
      productsData = apiResponse.data
    } else {
      // 旧的API响应格式
      productsData = apiResponse
    }
    
    // 更新数据
    if (productsData && productsData.data) {
      products.value = productsData.data
      totalPages.value = productsData.totalPages || 1
      productsTotal.value = productsData.total || products.value.length
    } else if (productsData && productsData.results) {
      products.value = productsData.results
      totalPages.value = Math.ceil((productsData.count || 0) / pageSize)
      productsTotal.value = productsData.count || 0
    } else if (Array.isArray(productsData)) {
      products.value = productsData
      totalPages.value = 1
      productsTotal.value = productsData.length
    } else {
      products.value = []
      totalPages.value = 1
      productsTotal.value = 0
    }
    
    // 重置页码和可见页面
    currentPage.value = 1
    visiblePages.value = getVisiblePages()
    
    console.log('筛选后商品数:', products.value.length)
    console.log('筛选后总商品数:', productsTotal.value)
    console.log('筛选后总页数:', totalPages.value)
    
    // 在移动设备上关闭筛选侧边栏
    if (mobileFilterOpen.value) {
      mobileFilterOpen.value = false
    }
  } catch (err) {
    console.error('应用筛选条件失败:', err)
    error.value = err.message || '应用筛选条件失败'
  } finally {
    loading.value = false
  }
}

// Reset filters
const resetFilters = () => {
  priceMin.value = ''
  priceMax.value = ''
  filterNew.value = false
  filterHot.value = false
  filterDiscount.value = false
  selectedSubcategories.value = []
}

// Filtered product list
const filteredProducts = computed(() => {
  let result = Array.isArray(products.value) ? [...products.value] : []
  
  // Apply subcategory filter
  if (selectedSubcategories.value.length > 0) {
    result = result.filter(product => 
      product.categories && product.categories.some(cat => 
        selectedSubcategories.value.includes(cat.id)
      )
    )
  }
  
  // Apply product attribute filter
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
  
  // Apply price filter
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
  
  // Apply sorting
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

// Change page
const changePage = (page) => {
  // 保持当前筛选条件不变，仅改变页码
  const filterParams = {
    min_price: priceMin.value || undefined,
    max_price: priceMax.value || undefined,
    is_new: filterNew.value || undefined,
    is_hot: filterHot.value || undefined,
    is_discount: filterDiscount.value || undefined,
    sort: sortBy.value !== 'default' ? sortBy.value : undefined,
    subcategories: selectedSubcategories.value.length > 0 ? selectedSubcategories.value.join(',') : undefined
  }
  
  console.log('翻页并保持筛选条件:', filterParams, '页码:', page)
  
  currentPage.value = page
  
  if (selectedCategory.value) {
    fetchProducts(selectedCategory.value.id, page, filterParams)
  } else {
    fetchProducts(null, page, filterParams)
  }
}

// Get visible pages
const getVisiblePages = () => {
  const pages = []
  const maxVisiblePages = 7 // Maximum page buttons to show
  
  if (totalPages.value <= maxVisiblePages) {
    // If not many pages, show all
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    // Always show first page
    pages.push(1)
    
    // Calculate middle page range start and end
    let startPage = Math.max(2, currentPage.value - 2)
    let endPage = Math.min(totalPages.value - 1, currentPage.value + 2)
    
    // Adjust display range to avoid bias to one side
    if (currentPage.value <= 4) {
      // Near start
      endPage = Math.min(6, totalPages.value - 1)
    } else if (currentPage.value >= totalPages.value - 3) {
      // Near end
      startPage = Math.max(totalPages.value - 5, 2)
    }
    
    // Add first ellipsis
    if (startPage > 2) {
      pages.push('...')
    }
    
    // Add middle pages
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }
    
    // Add second ellipsis
    if (endPage < totalPages.value - 1) {
      pages.push('...')
    }
    
    // Always show last page
    pages.push(totalPages.value)
  }
  
  return pages
}

// Load data when page loads
onMounted(async () => {
  await fetchCategories()
  
  // Check URL for category ID
  if (route.query.category) {
    const categoryId = route.query.category
    // First look in subcategories
    let category = filteredCategories.value.find(c => c.id === categoryId)
    if (!category) {
      // Then try to find in all categories
      category = categories.value.find(c => c.id === categoryId)
    }
    
    if (category) {
      await selectCategory(category)
    } else {
      await fetchProducts()
    }
  } else {
    await fetchProducts()
  }
})

// Define page metadata
definePageMeta({
  layout: 'default',
  title: 'Product Categories',
  description: 'Browse our entire product catalog and find products you love'
})

// 根据分类名称返回对应的图标
const getCategoryIcon = (categoryName) => {
  // 转换为小写并去除多余空格便于匹配
  const name = categoryName.toLowerCase().trim();
  
  // 分类名称与图标路径的映射
  const iconMap = {
    'inspirational books': {
      path: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
      class: 'text-blue-600'
    },
    'chocolate gift box': {
      path: 'M21 15.546c-.523 0-1.046.151-1.5.454a2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.701 2.701 0 00-1.5-.454M9 6v2m3-2v2m3-2v2M9 3h.01M12 3h.01M15 3h.01M21 21v-7a2 2 0 00-2-2H5a2 2 0 00-2 2v7h18zm-3-9v-2a2 2 0 00-2-2H8a2 2 0 00-2 2v2h12z',
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
      path: 'M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9',
      class: 'text-purple-500'
    },
    'girls barbie dolls': {
      path: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
      class: 'text-pink-500'
    },
    'women\'s perfume': {
      path: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
      class: 'text-purple-400'
    },
    'family relationship book': {
      path: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
      class: 'text-blue-500'
    },
    'smart watch': {
      path: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
      class: 'text-gray-700'
    },
    'kindle reader': {
      path: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
      class: 'text-blue-600'
    },
    'cake gift': {
      path: 'M21 15.546c-.523 0-1.046.151-1.5.454a2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.704 2.704 0 00-3 0 2.704 2.704 0 01-3 0 2.701 2.701 0 00-1.5-.454M9 6v2m3-2v2m3-2v2M9 3h.01M12 3h.01M15 3h.01M21 21v-7a2 2 0 00-2-2H5a2 2 0 00-2 2v7h18zm-3-9v-2a2 2 0 00-2-2H8a2 2 0 00-2 2v2h12z',
      class: 'text-yellow-700'
    },
    'air fryer': {
      path: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
      class: 'text-gray-600'
    },
    'gift card': {
      path: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
      class: 'text-green-500'
    },
    'snack gift pack': {
      path: 'M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14',
      class: 'text-yellow-600'
    },
    'photo crystal ball': {
      path: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      class: 'text-blue-400'
    },
    'lettering mug': {
      path: 'M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z',
      class: 'text-teal-600'
    },
    'massager': {
      path: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
      class: 'text-green-600'
    },
    'scented candle': {
      path: 'M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z',
      class: 'text-orange-500'
    },
    'bath ball gift box': {
      path: 'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12',
      class: 'text-blue-500'
    },
    'yoga': {
      path: 'M14 11h6m-6 4h4m-10 4h10M4 12a1 1 0 110-2h1a1 1 0 110 2H4zm12-4a1 1 0 110 2h1a1 1 0 110-2h-1zm-8 12a1 1 0 110-2h1a1 1 0 110 2H8zm16-8a1 1 0 01-1 1H4.062a1 1 0 010-2H19a1 1 0 011 1z',
      class: 'text-purple-600'
    },
    'sculpture': {
      path: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
      class: 'text-indigo-500'
    },
    'mobile': {
      path: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
      class: 'text-gray-800'
    },
    'baking': {
      path: 'M9 13h6m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
      class: 'text-yellow-600'
    },
    'girls': {
      path: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
      class: 'text-pink-500'
    }
  };
  
  // 尝试精确匹配
  if (iconMap[name]) {
    return iconMap[name];
  }
  
  // 尝试部分匹配
  for (const key in iconMap) {
    if (name.includes(key) || key.includes(name)) {
      return iconMap[key];
    }
  }
  
  // 如果没有匹配，返回null，将使用默认图标
  return null;
};
</script>

<style scoped>
/* Custom scrollbar styles */
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
