<template>
  <div v-if="show" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto py-10">
    <div class="bg-white rounded-lg shadow-lg w-full max-w-4xl max-h-full overflow-hidden flex flex-col">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-lg font-bold">管理首页幻灯片</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="p-4 overflow-y-auto flex-grow">
        <div class="mb-4 flex justify-end">
          <button 
            @click="addNewSlide" 
            class="btn btn-primary flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            添加幻灯片
          </button>
        </div>
        
        <div v-if="slides.length === 0" class="text-center py-10 text-gray-500">
          暂无幻灯片，请点击"添加幻灯片"按钮创建
        </div>
        
        <div v-else class="space-y-6">
          <div 
            v-for="(slide, index) in slides" 
            :key="slide.id"
            class="border border-gray-200 rounded-lg overflow-hidden"
          >
            <div class="bg-gray-50 p-3 flex justify-between items-center">
              <h4 class="font-medium">幻灯片 #{{ index + 1 }}</h4>
              <div class="flex space-x-2">
                <button 
                  v-if="index > 0"
                  @click="moveSlide(index, -1)" 
                  class="text-gray-500 hover:text-gray-700 p-1"
                  title="上移"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                </button>
                <button 
                  v-if="index < slides.length - 1"
                  @click="moveSlide(index, 1)" 
                  class="text-gray-500 hover:text-gray-700 p-1"
                  title="下移"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </button>
                <button 
                  @click="removeSlide(index)" 
                  class="text-red-500 hover:text-red-700 p-1"
                  title="删除"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">标题</label>
                  <input 
                    v-model="slide.title" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="幻灯片标题"
                  >
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">副标题</label>
                  <textarea 
                    v-model="slide.subtitle" 
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="幻灯片副标题或描述"
                  ></textarea>
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">按钮文字</label>
                  <input 
                    v-model="slide.buttonText" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="按钮文字"
                  >
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">按钮链接</label>
                  <input 
                    v-model="slide.buttonLink" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="/categories"
                  >
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">背景颜色</label>
                  <input 
                    v-model="slide.backgroundColor" 
                    type="text" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    placeholder="bg-gradient-to-r from-primary-700 to-primary-900"
                  >
                  <p class="mt-1 text-xs text-gray-500">可以使用Tailwind CSS的颜色类或渐变类</p>
                </div>
              </div>
              
              <div>
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">背景图片</label>
                  <div class="border border-gray-300 rounded-md p-4">
                    <div v-if="slide.backgroundImage" class="mb-4">
                      <img 
                        :src="slide.backgroundImage" 
                        alt="背景图片预览" 
                        class="w-full h-40 object-cover rounded"
                      >
                      <button 
                        @click="slide.backgroundImage = ''" 
                        class="mt-2 text-sm text-red-500 hover:text-red-700"
                      >
                        移除图片
                      </button>
                    </div>
                    
                    <div v-if="!slide.backgroundImage || uploadingImage === slide.id">
                      <input 
                        type="file" 
                        accept="image/*" 
                        @change="(e) => handleImageUpload(e, slide)"
                        class="w-full"
                      >
                      <p class="mt-1 text-xs text-gray-500">推荐尺寸: 1920x500 像素</p>
                    </div>
                    
                    <div v-if="uploadingImage === slide.id" class="mt-2">
                      <div class="h-2 bg-gray-200 rounded">
                        <div 
                          class="h-full bg-primary-600 rounded" 
                          :style="`width: ${uploadProgress}%`"
                        ></div>
                      </div>
                      <p class="text-xs text-gray-500 mt-1">上传中... {{ uploadProgress }}%</p>
                    </div>
                  </div>
                </div>
                
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">预览</label>
                  <div 
                    class="w-full h-40 rounded-md flex items-center justify-center overflow-hidden"
                    :class="slide.backgroundColor"
                    :style="slide.backgroundImage ? `background-image: url(${slide.backgroundImage}); background-size: cover; background-position: center;` : ''"
                  >
                    <div class="text-white text-center p-4 relative z-10">
                      <h4 class="text-xl font-bold">{{ slide.title || '幻灯片标题' }}</h4>
                      <p class="text-sm mt-1">{{ slide.subtitle || '幻灯片副标题' }}</p>
                      <button class="mt-2 px-3 py-1 bg-primary-600 text-white text-sm rounded">
                        {{ slide.buttonText || '按钮文字' }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="p-4 border-t border-gray-200 flex justify-end space-x-2">
        <button 
          @click="$emit('close')" 
          class="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700"
        >
          取消
        </button>
        <button 
          @click="saveSlides" 
          class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm"
          :disabled="isSaving"
        >
          {{ isSaving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { v4 as uuidv4 } from 'uuid'

const props = defineProps({
  show: Boolean,
  initialSlides: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'save'])

// 幻灯片数据
const slides = ref([])
const isSaving = ref(false)
const uploadingImage = ref(null)
const uploadProgress = ref(0)

// 初始化幻灯片数据
onMounted(() => {
  slides.value = JSON.parse(JSON.stringify(props.initialSlides))
})

// 添加新幻灯片
const addNewSlide = () => {
  slides.value.push({
    id: uuidv4(),
    title: '新幻灯片标题',
    subtitle: '新幻灯片副标题',
    buttonText: '了解更多',
    buttonLink: '/categories',
    backgroundColor: 'bg-gradient-to-r from-blue-700 to-indigo-900',
    backgroundImage: ''
  })
}

// 移动幻灯片位置
const moveSlide = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= slides.value.length) return
  
  const temp = slides.value[index]
  slides.value[index] = slides.value[newIndex]
  slides.value[newIndex] = temp
}

// 删除幻灯片
const removeSlide = (index) => {
  if (confirm('确定要删除这个幻灯片吗？')) {
    slides.value.splice(index, 1)
  }
}

// 处理图片上传
const handleImageUpload = async (event, slide) => {
  const file = event.target.files[0]
  if (!file) return
  
  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }
  
  try {
    uploadingImage.value = slide.id
    uploadProgress.value = 0
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)
    
    // 使用FileReader将图片转换为Base64
    const reader = new FileReader()
    
    reader.onload = () => {
      clearInterval(progressInterval)
      uploadProgress.value = 100
      
      // 更新幻灯片背景图片为Base64数据
      const slideIndex = slides.value.findIndex(s => s.id === slide.id)
      if (slideIndex !== -1) {
        slides.value[slideIndex].backgroundImage = reader.result
      }
      
      setTimeout(() => {
        uploadingImage.value = null
        uploadProgress.value = 0
      }, 500)
    }
    
    reader.onerror = () => {
      clearInterval(progressInterval)
      console.error('读取文件失败')
      alert('读取文件失败，请重试')
      
      setTimeout(() => {
        uploadingImage.value = null
        uploadProgress.value = 0
      }, 500)
    }
    
    // 开始读取文件
    reader.readAsDataURL(file)
  } catch (error) {
    console.error('处理图片失败:', error)
    alert('处理图片失败，请重试')
    
    uploadingImage.value = null
    uploadProgress.value = 0
  }
}

// 保存幻灯片
const saveSlides = async () => {
  try {
    isSaving.value = true
    
    // 使用localStorage保存幻灯片数据
    localStorage.setItem('carouselSlides', JSON.stringify(slides.value))
    
    // 通知父组件更新数据
    emit('save', slides.value)
    emit('close')
    alert('幻灯片保存成功')
  } catch (error) {
    console.error('保存幻灯片失败:', error)
    alert('保存失败，请重试')
  } finally {
    isSaving.value = false
  }
}
</script>
