<template>
  <div>
    <!-- Top categories navigation -->
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
              All Products
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
const products = ref([])
const loading = ref(true)
const error = ref(null)
const selectedCategory = ref(null)
const selectedSubcategories = ref([])
const mobileFilterOpen = ref(false)

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
    const response = await api.categories.getTree()
    categories.value = response || []
  } catch (err) {
    console.error('Failed to get categories:', err)
  }
}

// Get products
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
    console.error('Failed to get products:', err)
    error.value = err.message || 'Failed to get product data'
  } finally {
    loading.value = false
  }
}

// Select category
const selectCategory = async (category) => {
  selectedCategory.value = category
  selectedSubcategories.value = []
  await fetchProducts(category.id)
}

// Apply filters
const applyFilters = () => {
  // Trigger re-calculation of computed properties
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
  let result = [...products.value]
  
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

// Load data when page loads
onMounted(async () => {
  await fetchCategories()
  
  // Check URL for category ID
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

// Define page metadata
definePageMeta({
  layout: 'default',
  title: 'Product Categories',
  description: 'Browse our entire product catalog and find products you love'
})
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
