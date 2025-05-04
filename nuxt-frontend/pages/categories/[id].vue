<template>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <template v-else-if="category">
        <!-- Category information -->
        <div class="container mx-auto px-4 py-6">
          <!-- Breadcrumb navigation -->
          <nav class="flex mb-4" aria-label="Breadcrumb">
            <ol class="inline-flex items-center space-x-1 md:space-x-3">
              <li class="inline-flex items-center">
                <NuxtLink to="/" class="text-gray-500 hover:text-gray-700">
                  Home
                </NuxtLink>
              </li>
              <li>
                <div class="flex items-center">
                  <svg class="w-6 h-6 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                  </svg>
                  <NuxtLink to="/categories" class="ml-1 text-gray-500 hover:text-gray-700 md:ml-2">
                    Categories
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

          <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
            <div class="flex items-center">
              <div v-if="category.image" class="mr-4 w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                <img :src="category.image" :alt="category.name" class="w-10 h-10 object-contain">
              </div>
              <div v-else class="mr-4 w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center transition-all duration-300 hover:bg-primary-200">
                <svg v-if="getCategoryIcon(category.name)" :class="getCategoryIcon(category.name).class" class="h-8 w-8 text-primary-500 transition-all duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="getCategoryIcon(category.name).path" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                </svg>
              </div>
              <div>
                <h1 class="text-2xl md:text-3xl font-bold text-gray-900">{{ category.name }}</h1>
                <p v-if="category.description" class="mt-2 text-gray-600">{{ category.description }}</p>
                <span class="text-gray-500 mt-1 block">{{ sortedAndFilteredProducts.length }} products</span>
              </div>
            </div>

            <div class="mt-4 md:mt-0 hidden">
              <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-2">
                  <span class="text-gray-700">Sort by:</span>
                  <select v-model="sortBy" class="text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500">
                    <option value="default">Default</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="newest">Newest</option>
                  </select>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-gray-700">Price:</span>
                  <input 
                    v-model="priceMin" 
                    type="number" 
                    placeholder="Min" 
                    class="form-input rounded-md border-gray-300 w-20 text-sm"
                  >
                  <span>-</span>
                  <input 
                    v-model="priceMax" 
                    type="number" 
                    placeholder="Max" 
                    class="form-input rounded-md border-gray-300 w-20 text-sm"
                  >
                  <button 
                    @click="applyPriceFilter"
                    class="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm rounded"
                  >
                    Apply
                  </button>
                  <button 
                    @click="resetFilters"
                    class="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm rounded"
                  >
                    Reset
                  </button>
                </div>
                <div class="flex items-center space-x-2">
                  <span class="text-gray-700">Filter:</span>
                  <select v-model="filter" class="rounded border border-gray-300 p-2">
                    <option value="all">All</option>
                    <option value="on-sale">On Sale</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Product count -->
          <div class="mt-4 md:mt-0 hidden">
            <span class="text-gray-500">{{ products.length }} products</span>
          </div>
        </div>
        
        <!-- Subcategory tabs -->
        <div v-if="category.children && category.children.length" class="mb-8">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8">
              <NuxtLink 
                :to="`/categories/${category.id}`"
                class="border-primary-500 text-primary-600 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
                aria-current="page"
              >
                All
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
        
        <!-- Filters -->
        <div class="mb-8 bg-white shadow-sm rounded-lg p-4">
          <div class="flex flex-wrap items-center gap-4">
            <!-- Sort -->
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2">Sort by:</span>
              <select v-model="sortBy" class="text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500">
                <option value="default">Default</option>
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
                <option value="newest">Newest</option>
              </select>
            </div>
            
            <!-- Price filter -->
            <div class="flex items-center space-x-2">
              <span class="text-sm text-gray-700">Price:</span>
              <input 
                v-model="priceMin" 
                type="number" 
                placeholder="Min" 
                class="form-input rounded-md border-gray-300 w-20 text-sm"
              >
              <span>-</span>
              <input 
                v-model="priceMax" 
                type="number" 
                placeholder="Max" 
                class="form-input rounded-md border-gray-300 w-20 text-sm"
              >
              <button 
                @click="applyPriceFilter"
                class="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm rounded"
              >
                Apply
              </button>
              <button 
                @click="resetFilters"
                class="px-2 py-1 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm rounded"
              >
                Reset
              </button>
            </div>
            
            <!-- Filter options -->
            <div class="flex items-center space-x-4">
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">On Sale</span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- Products Grid -->
        <div v-if="sortedAndFilteredProducts.length > 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
          <ProductCard 
            v-for="product in sortedAndFilteredProducts" 
            :key="product.id" 
            :product="product" 
          />
        </div>
        
        <!-- No products state -->
        <div v-else class="text-center py-10">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No Products</h3>
          <p class="mt-1 text-gray-500">There are no products in this category. Please check other categories.</p>
        </div>
        
        <!-- Pagination -->
        <div v-if="totalPages > 1" class="mt-8">
          <!-- Page info -->
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
      </template>
      
      <!-- Error state -->
      <div v-else-if="error" class="text-center py-10">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 class="mt-4 text-lg font-medium text-gray-900">Error Loading Category</h3>
        <p class="mt-1 text-gray-500">{{ error }}</p>
        <button @click="fetchData" class="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
          Try Again
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Get route parameters
const route = useRoute()
const categoryId = route.params.id

// Get API service
const api = useApi()

// State
const category = ref(null)
const products = ref([])
const loading = ref(true)
const error = ref(null)

// Filter and sort
const sortBy = ref('default')
const filterDiscount = ref(false)
const filterNew = ref(false)
const filterHot = ref(false)

// State for pagination
const currentPage = ref(1)
const totalPages = ref(1)
const visiblePages = ref([])
const productsTotal = ref(0)

// State for price filter
const priceMin = ref(null)
const priceMax = ref(null)

// Get category details and products
const fetchCategoryData = async () => {
  try {
    loading.value = true
    error.value = null
    
    console.log('Starting to get category details, ID:', categoryId)
    
    // Get category details
    try {
      const categoryData = await api.categories.getById(categoryId)
      console.log('Category details response:', categoryData)
      category.value = categoryData || null
      
      // 如果是根分类但它有子分类，重定向到第一个子分类
      if (category.value && category.value.level === 1 && 
          category.value.children && category.value.children.length > 0) {
        const firstSubCategory = category.value.children[0]
        // 使用重定向而不是直接加载子分类的商品，这样URL也会更新
        try {
        if (process.client) {
            console.log('重定向到子分类:', firstSubCategory.id)
          window.location.href = `/categories/${firstSubCategory.id}`
          return // 中断后续处理
          }
        } catch (redirectError) {
          console.error('重定向到子分类失败:', redirectError)
          // 重定向失败时继续执行，直接加载子分类的商品
          try {
            await loadCategoryProducts(1, firstSubCategory.id)
            return
          } catch (loadError) {
            console.error('加载子分类商品失败:', loadError)
            // 继续执行，尝试加载原始分类的商品
          }
        }
      }
    } catch (categoryErr) {
      console.error('Failed to get category details:', categoryErr)
      error.value = categoryErr.message || 'Failed to get category details'
      // 即使分类获取失败，仍尝试获取产品
      try {
        await loadCategoryProducts(1)
        return
      } catch (productsError) {
        console.error('Initial products load failed after category error:', productsError)
        // 设置完整错误信息
        error.value = `Category error: ${error.value}. Products error: ${productsError.message || 'Unknown error'}`
      }
    }
    
    // Load initial products
    await loadCategoryProducts(1)
  } catch (err) {
    console.error('Failed to get category data:', err)
    error.value = err.message || 'Failed to get category data'
  } finally {
    loading.value = false
  }
}

// Load products with pagination - 添加可选参数用于加载特定分类的商品
const loadCategoryProducts = async (page = 1, overrideCategoryId = null) => {
  try {
    loading.value = true
    
    const pageSize = 28 // 每页显示28个商品
    const targetCategoryId = overrideCategoryId || categoryId
    
    // Get products for this category
    console.log('Starting to get category products, ID:', targetCategoryId, 'Page:', page)
    let productsData = await api.categories.getProducts(targetCategoryId, page, pageSize)
    console.log('Category products response:', productsData)
    
    // 检查是否是根分类且没有商品
    if (category.value && category.value.level === 1 && 
        (productsData.results?.length === 0 || productsData.count === 0)) {
      console.log('根分类没有直接关联的商品，尝试加载子分类商品')
      
      // 如果分类有子分类，则加载第一个子分类的商品
      if (category.value.children && category.value.children.length > 0) {
        const firstSubCategory = category.value.children[0]
        console.log('加载子分类商品:', firstSubCategory.name, firstSubCategory.id)
        try {
        productsData = await api.categories.getProducts(firstSubCategory.id, page, pageSize)
        console.log('子分类商品响应:', productsData)
        } catch (subCategoryError) {
          console.error('加载子分类商品失败:', subCategoryError)
          // 如果加载子分类商品失败，使用原始的空响应
        }
      }
    }
    
    // Handle different API response formats
    if (productsData.data) {
      products.value = productsData.data
      totalPages.value = productsData.totalPages || 1
      productsTotal.value = productsData.total || products.value.length
    } else if (productsData.results) {
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
    
    currentPage.value = page
    visiblePages.value = getVisiblePages()
    
    console.log('Products loaded:', products.value.length)
    console.log('Total products:', productsTotal.value)
    console.log('Total pages:', totalPages.value)
  } catch (productsErr) {
    console.error('Failed to get category products:', productsErr)
    products.value = []
    totalPages.value = 1
    productsTotal.value = 0
    // If category details succeeded but products failed, still show category info
    if (!error.value) {
      error.value = productsErr.message || 'Failed to get category products'
    }
  } finally {
    loading.value = false
  }
}

// Change page
const changePage = (page) => {
  currentPage.value = page
  loadCategoryProducts(page)
}

// Get visible pages for pagination
const getVisiblePages = () => {
  const pages = []
  const maxVisiblePages = 7 // 最多显示7个页码按钮
  
  if (totalPages.value <= maxVisiblePages) {
    // 如果总页数不多，全部显示
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    // 始终显示第一页
    pages.push(1)
    
    // 计算中间页码的开始和结束
    let startPage = Math.max(2, currentPage.value - 2)
    let endPage = Math.min(totalPages.value - 1, currentPage.value + 2)
    
    // 调整显示范围避免偏向一边
    if (currentPage.value <= 4) {
      // 靠近开始位置
      endPage = Math.min(6, totalPages.value - 1)
    } else if (currentPage.value >= totalPages.value - 3) {
      // 靠近结束位置
      startPage = Math.max(totalPages.value - 5, 2)
    }
    
    // 添加第一个省略号
    if (startPage > 2) {
      pages.push('...')
    }
    
    // 添加中间页码
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i)
    }
    
    // 添加第二个省略号
    if (endPage < totalPages.value - 1) {
      pages.push('...')
    }
    
    // 始终显示最后一页
    pages.push(totalPages.value)
  }
  
  return pages
}

// Apply price filter
const applyPriceFilter = () => {
  // Trigger recalculation of computed property by forcing update
  // The filtering logic is already in the computed property
  sortedAndFilteredProducts.value = [...sortedAndFilteredProducts.value]
}

// Reset filters
const resetFilters = () => {
  priceMin.value = null
  priceMax.value = null
  filterDiscount.value = false
  sortBy.value = 'default'
}

// Filtered product list
const filteredProducts = computed(() => {
  let result = [...products.value]
  
  // Apply filter conditions
  if (filterNew.value) {
    result = result.filter(product => product.is_new)
  }
  
  if (filterHot.value) {
    result = result.filter(product => product.is_hot)
  }
  
  if (filterDiscount.value) {
    // Support two discount formats: discount_price or original_price
    result = result.filter(product => {
      return product.discount_price || 
        (product.original_price && product.original_price !== product.price)
    })
  }
  
  // Apply price filter
  if (priceMin.value) {
    result = result.filter(product => {
      // Get actual selling price, supporting two discount formats
      const price = product.discount_price || product.price
      return parseFloat(price) >= Number(priceMin.value)
    })
  }
  
  if (priceMax.value) {
    result = result.filter(product => {
      // Get actual selling price, supporting two discount formats
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
    default:
      // Default sorting, maintain original order
      break
  }
  
  return result
})

// 按条件排序产品
const sortedAndFilteredProducts = computed(() => {
  let result = [...products.value];
  
  // 应用促销筛选
  if (filterDiscount.value) {
    result = result.filter(product => product.is_on_sale || product.discount > 0);
  }
  
  // 应用价格筛选
  if (priceMin.value && !isNaN(priceMin.value)) {
    result = result.filter(product => {
      const price = parseFloat(product.discount_price || product.price);
      return price >= Number(priceMin.value);
    });
  }
  
  if (priceMax.value && !isNaN(priceMax.value)) {
    result = result.filter(product => {
      const price = parseFloat(product.discount_price || product.price);
      return price <= Number(priceMax.value);
    });
  }
  
  // 应用排序
  if (sortBy.value === 'price-asc') {
    result.sort((a, b) => (a.price - (a.discount || 0)) - (b.price - (b.discount || 0)));
  } else if (sortBy.value === 'price-desc') {
    result.sort((a, b) => (b.price - (b.discount || 0)) - (a.price - (a.discount || 0)));
  } else if (sortBy.value === 'newest') {
    result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  }
  
  return result;
})

// Get data when page loads
onMounted(() => {
  fetchCategoryData()
})

// Watch for route changes to refresh data
watch(() => route.params.id, (newId) => {
  if (newId) {
    fetchCategoryData()
  }
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
