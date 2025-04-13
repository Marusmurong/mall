<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">API测试页面</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 热门商品API测试 -->
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold mb-2">热门商品API</h2>
        <button @click="testHotProducts" class="btn btn-primary mb-4">测试热门商品API</button>
        
        <div v-if="hotLoading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-if="hotError" class="bg-red-50 p-4 rounded mb-4 text-red-600">
          <p class="font-semibold">错误:</p>
          <pre class="text-sm overflow-auto">{{ hotError }}</pre>
        </div>
        
        <div v-if="hotResult" class="bg-green-50 p-4 rounded">
          <p class="font-semibold text-green-700 mb-2">成功! 获取到 {{ hotResult.length }} 个热门商品</p>
          <div class="max-h-60 overflow-auto">
            <pre class="text-xs">{{ JSON.stringify(hotResult, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <!-- 分类树API测试 -->
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold mb-2">分类树API</h2>
        <button @click="testCategories" class="btn btn-primary mb-4">测试分类树API</button>
        
        <div v-if="categoriesLoading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-if="categoriesError" class="bg-red-50 p-4 rounded mb-4 text-red-600">
          <p class="font-semibold">错误:</p>
          <pre class="text-sm overflow-auto">{{ categoriesError }}</pre>
        </div>
        
        <div v-if="categoriesResult" class="bg-green-50 p-4 rounded">
          <p class="font-semibold text-green-700 mb-2">成功! 获取到 {{ categoriesResult.length }} 个分类</p>
          <div class="max-h-60 overflow-auto">
            <pre class="text-xs">{{ JSON.stringify(categoriesResult, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <!-- 推荐商品API测试 -->
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold mb-2">推荐商品API</h2>
        <button @click="testRecommended" class="btn btn-primary mb-4">测试推荐商品API</button>
        
        <div v-if="recommendedLoading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-if="recommendedError" class="bg-red-50 p-4 rounded mb-4 text-red-600">
          <p class="font-semibold">错误:</p>
          <pre class="text-sm overflow-auto">{{ recommendedError }}</pre>
        </div>
        
        <div v-if="recommendedResult" class="bg-green-50 p-4 rounded">
          <p class="font-semibold text-green-700 mb-2">成功! 获取到 {{ recommendedResult.length }} 个推荐商品</p>
          <div class="max-h-60 overflow-auto">
            <pre class="text-xs">{{ JSON.stringify(recommendedResult, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <!-- 新品API测试 -->
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold mb-2">新品API</h2>
        <button @click="testNew" class="btn btn-primary mb-4">测试新品API</button>
        
        <div v-if="newLoading" class="flex justify-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-if="newError" class="bg-red-50 p-4 rounded mb-4 text-red-600">
          <p class="font-semibold">错误:</p>
          <pre class="text-sm overflow-auto">{{ newError }}</pre>
        </div>
        
        <div v-if="newResult" class="bg-green-50 p-4 rounded">
          <p class="font-semibold text-green-700 mb-2">成功! 获取到 {{ newResult.length }} 个新品</p>
          <div class="max-h-60 overflow-auto">
            <pre class="text-xs">{{ JSON.stringify(newResult, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
    
    <div class="mt-8 bg-gray-100 p-4 rounded">
      <h2 class="text-xl font-semibold mb-2">API配置信息</h2>
      <pre class="text-sm bg-white p-4 rounded">{{ configInfo }}</pre>
    </div>
  </div>
</template>

<script setup>
// 获取API服务
const api = useApi()
const config = useRuntimeConfig()

// 配置信息
const configInfo = computed(() => {
  return {
    apiBase: config.public.apiBase,
    authBase: config.public.authBase,
    currentSite: config.public.currentSite
  }
})

// 热门商品API测试
const hotResult = ref(null)
const hotError = ref(null)
const hotLoading = ref(false)

const testHotProducts = async () => {
  try {
    hotLoading.value = true
    hotError.value = null
    hotResult.value = null
    
    console.log('测试热门商品API...')
    const response = await api.products.getHot()
    console.log('热门商品API响应:', response)
    
    hotResult.value = response
  } catch (error) {
    console.error('热门商品API错误:', error)
    hotError.value = error.message || String(error)
  } finally {
    hotLoading.value = false
  }
}

// 分类树API测试
const categoriesResult = ref(null)
const categoriesError = ref(null)
const categoriesLoading = ref(false)

const testCategories = async () => {
  try {
    categoriesLoading.value = true
    categoriesError.value = null
    categoriesResult.value = null
    
    console.log('测试分类树API...')
    const response = await api.categories.getTree()
    console.log('分类树API响应:', response)
    
    categoriesResult.value = response
  } catch (error) {
    console.error('分类树API错误:', error)
    categoriesError.value = error.message || String(error)
  } finally {
    categoriesLoading.value = false
  }
}

// 推荐商品API测试
const recommendedResult = ref(null)
const recommendedError = ref(null)
const recommendedLoading = ref(false)

const testRecommended = async () => {
  try {
    recommendedLoading.value = true
    recommendedError.value = null
    recommendedResult.value = null
    
    console.log('测试推荐商品API...')
    const response = await api.products.getRecommended()
    console.log('推荐商品API响应:', response)
    
    recommendedResult.value = response
  } catch (error) {
    console.error('推荐商品API错误:', error)
    recommendedError.value = error.message || String(error)
  } finally {
    recommendedLoading.value = false
  }
}

// 新品API测试
const newResult = ref(null)
const newError = ref(null)
const newLoading = ref(false)

const testNew = async () => {
  try {
    newLoading.value = true
    newError.value = null
    newResult.value = null
    
    console.log('测试新品API...')
    const response = await api.products.getNew()
    console.log('新品API响应:', response)
    
    newResult.value = response
  } catch (error) {
    console.error('新品API错误:', error)
    newError.value = error.message || String(error)
  } finally {
    newLoading.value = false
  }
}
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
</style>
