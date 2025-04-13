<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-6">API调试页面</h1>
    
    <div class="grid grid-cols-1 gap-6">
      <!-- API请求测试 -->
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold mb-4">API请求测试</h2>
        
        <div class="flex space-x-4 mb-6">
          <button @click="testHotProducts" class="btn btn-primary">测试热门商品API</button>
          <button @click="testCategories" class="btn btn-primary">测试分类API</button>
          <button @click="testRecommended" class="btn btn-primary">测试推荐商品API</button>
          <button @click="testNew" class="btn btn-primary">测试新品API</button>
        </div>
        
        <div v-if="loading" class="flex justify-center py-4 mb-4">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
        </div>
        
        <div v-if="error" class="bg-red-50 p-4 rounded mb-4">
          <p class="font-semibold text-red-600">错误:</p>
          <pre class="text-sm overflow-auto text-red-600">{{ error }}</pre>
        </div>
        
        <div v-if="requestUrl" class="mb-4">
          <p class="font-semibold">请求URL:</p>
          <pre class="bg-gray-100 p-2 rounded text-sm">{{ requestUrl }}</pre>
        </div>
        
        <div v-if="rawResponse" class="mb-4">
          <p class="font-semibold">原始响应:</p>
          <pre class="bg-gray-100 p-2 rounded text-sm max-h-60 overflow-auto">{{ rawResponse }}</pre>
        </div>
        
        <div v-if="processedData" class="mb-4">
          <p class="font-semibold">处理后的数据 ({{ processedData.length }} 项):</p>
          <pre class="bg-gray-100 p-2 rounded text-sm max-h-60 overflow-auto">{{ JSON.stringify(processedData, null, 2) }}</pre>
        </div>
      </div>
      
      <!-- API配置信息 -->
      <div class="bg-gray-100 p-4 rounded">
        <h2 class="text-xl font-semibold mb-2">API配置信息</h2>
        <pre class="text-sm bg-white p-4 rounded">{{ configInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
// 获取API服务
const api = useApi()
const config = useRuntimeConfig()

// 状态变量
const loading = ref(false)
const error = ref(null)
const requestUrl = ref('')
const rawResponse = ref('')
const processedData = ref(null)

// 配置信息
const configInfo = computed(() => {
  return {
    apiBase: config.public.apiBase,
    authBase: config.public.authBase,
    currentSite: config.public.currentSite
  }
})

// 通用测试函数
const testApi = async (apiFunction, name) => {
  try {
    loading.value = true
    error.value = null
    requestUrl.value = ''
    rawResponse.value = ''
    processedData.value = null
    
    console.log(`测试${name}API...`)
    
    // 拦截fetch请求以获取URL
    const originalFetch = window.fetch
    window.fetch = async (url, options) => {
      requestUrl.value = url
      console.log(`发送请求到: ${url}`)
      const response = await originalFetch(url, options)
      
      // 克隆响应以便我们可以同时读取两次
      const clonedResponse = response.clone()
      const text = await clonedResponse.text()
      rawResponse.value = text
      console.log(`原始响应: ${text}`)
      
      return response
    }
    
    // 调用API函数
    const response = await apiFunction()
    console.log(`${name}API响应:`, response)
    
    // 恢复原始fetch
    window.fetch = originalFetch
    
    // 处理响应
    processedData.value = response
  } catch (err) {
    console.error(`${name}API错误:`, err)
    error.value = err.message || String(err)
  } finally {
    loading.value = false
  }
}

// 测试热门商品API
const testHotProducts = () => testApi(() => api.products.getHot(), '热门商品')

// 测试分类API
const testCategories = () => testApi(() => api.categories.getTree(), '分类树')

// 测试推荐商品API
const testRecommended = () => testApi(() => api.products.getRecommended(), '推荐商品')

// 测试新品API
const testNew = () => testApi(() => api.products.getNew(), '新品')
</script>

<style scoped>
.btn {
  @apply px-4 py-2 rounded font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
</style>
