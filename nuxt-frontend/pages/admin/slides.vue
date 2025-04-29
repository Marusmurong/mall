<template>
  <div class="admin-page">
    <h1 class="text-2xl font-bold mb-6">幻灯片管理</h1>
    
    <!-- 幻灯片列表 -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium">当前幻灯片</h2>
        <button 
          @click="addNewSlide" 
          class="btn btn-primary"
        >
          添加幻灯片
        </button>
      </div>
      
      <div v-if="loading" class="py-10 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500 mx-auto"></div>
        <p class="mt-2 text-gray-500">加载中...</p>
      </div>
      
      <div v-else-if="slides.length === 0" class="py-10 text-center">
        <p class="text-gray-500">暂无幻灯片，请添加</p>
      </div>
      
      <div v-else class="space-y-4">
        <!-- 可拖拽的幻灯片列表 -->
        <div 
          v-for="(slide, index) in slides" 
          :key="slide.id"
          class="border rounded-lg p-4 bg-gray-50"
        >
          <div class="flex items-start">
            <!-- 幻灯片预览 -->
            <div class="w-40 h-24 bg-gray-200 rounded overflow-hidden mr-4 relative">
              <img 
                v-if="slide.backgroundImage" 
                :src="slide.backgroundImage" 
                :alt="slide.title" 
                class="w-full h-full object-cover"
              >
              <div 
                v-else 
                class="absolute inset-0 flex items-center justify-center"
                :class="slide.backgroundColor || 'bg-gray-400'"
              >
                <span class="text-white text-xs">无图片</span>
              </div>
              <div class="absolute top-1 right-1">
                <span 
                  class="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium"
                  :class="slide.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
                >
                  {{ slide.active ? '启用' : '禁用' }}
                </span>
              </div>
            </div>
            
            <!-- 幻灯片信息 -->
            <div class="flex-1">
              <h3 class="font-medium">{{ slide.title }}</h3>
              <p class="text-sm text-gray-500 mt-1">{{ slide.subtitle }}</p>
              <div class="flex items-center mt-2 text-sm">
                <span class="text-gray-500 mr-2">按钮: {{ slide.buttonText }}</span>
                <span class="text-gray-500">链接: {{ slide.buttonLink }}</span>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="ml-4 flex space-x-2">
              <button 
                @click="editSlide(index)"
                class="p-1 text-blue-600 hover:text-blue-800"
                title="编辑"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button 
                @click="toggleSlideStatus(index)"
                :class="slide.active ? 'text-green-600 hover:text-green-800' : 'text-gray-600 hover:text-gray-800'"
                class="p-1"
                :title="slide.active ? '禁用' : '启用'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
              <button 
                @click="confirmDeleteSlide(index)"
                class="p-1 text-red-600 hover:text-red-800"
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 幻灯片编辑模态框 -->
    <div v-if="showSlideModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-3xl p-6">
        <h2 class="text-xl font-bold mb-4">{{ editingIndex === -1 ? '添加幻灯片' : '编辑幻灯片' }}</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 左侧表单 -->
          <div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
              <input 
                v-model="editingSlide.title" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="输入幻灯片标题"
              >
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">副标题</label>
              <input 
                v-model="editingSlide.subtitle" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="输入幻灯片副标题"
              >
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">按钮文字</label>
              <input 
                v-model="editingSlide.buttonText" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="输入按钮文字"
              >
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">按钮链接</label>
              <input 
                v-model="editingSlide.buttonLink" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="输入按钮链接，如 /products"
              >
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">背景颜色</label>
              <input 
                v-model="editingSlide.backgroundColor" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md"
                placeholder="输入背景颜色，如 bg-blue-700 或 #0047AB"
              >
            </div>
            
            <div class="mb-4 flex items-center">
              <input 
                v-model="editingSlide.active" 
                type="checkbox" 
                class="h-4 w-4 text-primary-600 border-gray-300 rounded"
                id="active-status"
              >
              <label for="active-status" class="ml-2 block text-sm text-gray-700">启用幻灯片</label>
            </div>
          </div>
          
          <!-- 右侧图片上传和预览 -->
          <div>
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">背景图片</label>
              <div class="flex items-center">
                <input 
                  type="text" 
                  v-model="editingSlide.backgroundImage"
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="输入图片URL或上传图片"
                >
                <button 
                  class="ml-2 px-3 py-2 bg-gray-200 text-gray-700 rounded-md"
                  @click="openImageUploader"
                >
                  上传
                </button>
              </div>
            </div>
            
            <!-- 图片预览 -->
            <div class="mt-4">
              <p class="text-sm font-medium text-gray-700 mb-2">预览</p>
              <div class="bg-gray-100 rounded-lg p-4 h-48 flex items-center justify-center overflow-hidden">
                <div 
                  v-if="editingSlide.backgroundImage" 
                  class="w-full h-full relative"
                >
                  <img 
                    :src="editingSlide.backgroundImage" 
                    alt="背景图片预览" 
                    class="w-full h-full object-cover"
                  >
                  <div class="absolute inset-0 flex items-center justify-center">
                    <div class="bg-black bg-opacity-50 p-4 rounded text-white max-w-xs text-center">
                      <h3 class="font-bold">{{ editingSlide.title || '幻灯片标题' }}</h3>
                      <p class="text-sm mt-1">{{ editingSlide.subtitle || '幻灯片副标题' }}</p>
                      <button class="mt-2 px-3 py-1 bg-primary-600 rounded text-sm">
                        {{ editingSlide.buttonText || '按钮文字' }}
                      </button>
                    </div>
                  </div>
                </div>
                <div 
                  v-else 
                  class="w-full h-full flex items-center justify-center"
                  :class="editingSlide.backgroundColor || 'bg-gray-400'"
                >
                  <div class="bg-black bg-opacity-50 p-4 rounded text-white max-w-xs text-center">
                    <h3 class="font-bold">{{ editingSlide.title || '幻灯片标题' }}</h3>
                    <p class="text-sm mt-1">{{ editingSlide.subtitle || '幻灯片副标题' }}</p>
                    <button class="mt-2 px-3 py-1 bg-primary-600 rounded text-sm">
                      {{ editingSlide.buttonText || '按钮文字' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 底部按钮 -->
        <div class="mt-6 flex justify-end space-x-3">
          <button 
            @click="showSlideModal = false" 
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700"
          >
            取消
          </button>
          <button 
            @click="saveSlide" 
            class="px-4 py-2 bg-primary-600 text-white rounded-md"
            :disabled="saving"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <h2 class="text-xl font-bold mb-4">确认删除</h2>
        <p class="mb-6">确定要删除这个幻灯片吗？此操作无法撤销。</p>
        
        <div class="flex justify-end space-x-3">
          <button 
            @click="showDeleteModal = false" 
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700"
          >
            取消
          </button>
          <button 
            @click="deleteSlide" 
            class="px-4 py-2 bg-red-600 text-white rounded-md"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

// 状态
const slides = ref([])
const loading = ref(true)
const saving = ref(false)
const showSlideModal = ref(false)
const showDeleteModal = ref(false)
const editingIndex = ref(-1)
const deleteIndex = ref(-1)

// 编辑中的幻灯片
const editingSlide = reactive({
  id: '',
  title: '',
  subtitle: '',
  buttonText: '',
  buttonLink: '',
  backgroundColor: '',
  backgroundImage: '',
  active: true,
  order: 0
})

// 获取幻灯片数据
const fetchSlides = async () => {
  loading.value = true
  try {
    const { data } = await useFetch('http://127.0.0.1:8000/api/v1/admin/settings/?site=default')
    if (data.value && data.value.code === 0 && data.value.data) {
      slides.value = data.value.data.homepage.carousel || []
    } else {
      slides.value = []
    }
  } catch (error) {
    console.error('Failed to fetch slides:', error)
    slides.value = []
  } finally {
    loading.value = false
  }
}

// 添加新幻灯片
const addNewSlide = () => {
  editingIndex.value = -1
  Object.assign(editingSlide, {
    id: Date.now().toString(),
    title: '新幻灯片',
    subtitle: '幻灯片描述',
    buttonText: '查看详情',
    buttonLink: '/products',
    backgroundColor: 'bg-gradient-to-r from-blue-700 to-indigo-900',
    backgroundImage: '',
    active: true,
    order: slides.value.length + 1
  })
  showSlideModal.value = true
}

// 编辑幻灯片
const editSlide = (index) => {
  editingIndex.value = index
  const slide = slides.value[index]
  Object.assign(editingSlide, { ...slide })
  showSlideModal.value = true
}

// 保存幻灯片
const saveSlide = async () => {
  saving.value = true
  try {
    if (editingIndex.value === -1) {
      // 添加新幻灯片
      slides.value.push({ ...editingSlide })
    } else {
      // 更新现有幻灯片
      slides.value[editingIndex.value] = { ...editingSlide }
    }
    
    // 调用API保存所有幻灯片
    await updateSlides()
    
    showSlideModal.value = false
  } catch (error) {
    console.error('Failed to save slide:', error)
    alert('保存幻灯片失败，请重试')
  } finally {
    saving.value = false
  }
}

// 切换幻灯片状态
const toggleSlideStatus = async (index) => {
  const slide = slides.value[index]
  slide.active = !slide.active
  
  try {
    // 调用API更新幻灯片
    await updateSlides()
  } catch (error) {
    console.error('Failed to update slide status:', error)
    // 恢复原状态
    slide.active = !slide.active
    alert('更新幻灯片状态失败，请重试')
  }
}

// 确认删除幻灯片
const confirmDeleteSlide = (index) => {
  deleteIndex.value = index
  showDeleteModal.value = true
}

// 删除幻灯片
const deleteSlide = async () => {
  try {
    slides.value.splice(deleteIndex.value, 1)
    
    // 更新剩余幻灯片的顺序
    slides.value.forEach((slide, index) => {
      slide.order = index + 1
    })
    
    // 调用API更新幻灯片
    await updateSlides()
    
    showDeleteModal.value = false
  } catch (error) {
    console.error('Failed to delete slide:', error)
    alert('删除幻灯片失败，请重试')
  }
}

// 更新所有幻灯片到服务器
const updateSlides = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/v1/admin/settings/?site=default', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        homepage: {
          carousel: slides.value
        }
      })
    })
    
    const result = await response.json()
    
    if (result.code !== 0) {
      throw new Error(result.message || '更新失败')
    }
    
    return result
  } catch (error) {
    console.error('Failed to update slides:', error)
    throw error
  }
}

// 打开图片上传器
const openImageUploader = () => {
  // 实际应用中，这里应该打开图片上传对话框
  // 现在我们只是模拟一个输入框
  const imageUrl = prompt('请输入图片URL')
  if (imageUrl) {
    editingSlide.backgroundImage = imageUrl
  }
}

// 初始化
onMounted(() => {
  fetchSlides()
})
</script>

<style scoped>
.admin-page {
  padding: 2rem;
}
</style>
