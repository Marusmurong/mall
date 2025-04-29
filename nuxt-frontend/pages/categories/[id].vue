<template>
  <div class="py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Loading state -->
      <div v-if="loading" class="flex justify-center py-10">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
      
      <template v-else-if="category">
        <!-- Category information -->
        <div class="mb-8">
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
          
          <div class="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">{{ category.name }}</h1>
              <p v-if="category.description" class="mt-2 text-gray-600">{{ category.description }}</p>
            </div>
            
            <!-- Product count -->
            <div class="mt-4 md:mt-0">
              <span class="text-gray-500">{{ products.length }} products</span>
            </div>
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
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="newest">Newest</option>
                <option value="sales">Best Selling</option>
              </select>
            </div>
            
            <!-- Price range -->
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2">Price:</span>
              <div class="flex items-center">
                <input 
                  v-model="priceMin" 
                  type="number" 
                  placeholder="Min" 
                  class="w-20 text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                >
                <span class="mx-2">-</span>
                <input 
                  v-model="priceMax" 
                  type="number" 
                  placeholder="Max" 
                  class="w-20 text-sm border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                >
                <button 
                  @click="applyPriceFilter"
                  class="ml-2 px-2 py-1 bg-primary-600 text-white text-sm rounded hover:bg-primary-700"
                >
                  Apply
                </button>
              </div>
            </div>
            
            <!-- Filter options -->
            <div class="flex items-center space-x-4">
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterNew" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">New Arrivals</span>
              </label>
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterHot" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">Hot Sales</span>
              </label>
              <label class="inline-flex items-center">
                <input type="checkbox" v-model="filterDiscount" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500">
                <span class="ml-2 text-sm text-gray-700">On Sale</span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- Product list -->
        <div v-if="filteredProducts.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 md:gap-6">
          <ProductCard 
            v-for="product in filteredProducts" 
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
        <div v-if="filteredProducts.length" class="mt-8 flex justify-center">
          <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <a href="#" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
              <span class="sr-only">Previous</span>
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
              <span class="sr-only">Next</span>
              <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
              </svg>
            </a>
          </nav>
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
const priceMin = ref('')
const priceMax = ref('')
const filterNew = ref(false)
const filterHot = ref(false)
const filterDiscount = ref(false)

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
    } catch (categoryErr) {
      console.error('Failed to get category details:', categoryErr)
      error.value = categoryErr.message || 'Failed to get category details'
    }
    
    // Get products for this category
    try {
      console.log('Starting to get category products, ID:', categoryId)
      const productsData = await api.categories.getProducts(categoryId)
      console.log('Category products response:', productsData)
      products.value = productsData || []
    } catch (productsErr) {
      console.error('Failed to get category products:', productsErr)
      // If category details succeeded but products failed, still show category info
      if (!error.value) {
        error.value = productsErr.message || 'Failed to get category products'
      }
    }
  } catch (err) {
    console.error('Failed to get category data:', err)
    error.value = err.message || 'Failed to get category data'
  } finally {
    loading.value = false
  }
}

// Apply price filter
const applyPriceFilter = () => {
  // Price validation logic can be added here
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
</script>
