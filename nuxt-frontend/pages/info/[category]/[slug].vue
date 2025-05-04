<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row gap-8">
      <!-- Left Sidebar -->
      <div class="w-full md:w-1/4 bg-white rounded-lg shadow-md p-4">
        <h2 class="text-xl font-bold mb-4">{{ getCategoryTitle(category) }}</h2>
        <div v-if="isLoading" class="py-4">
          <div class="animate-pulse h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div class="animate-pulse h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div class="animate-pulse h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
        </div>
        <ul v-else class="space-y-2">
          <li v-for="item in navigationItems" :key="item.slug" class="border-b border-gray-100 last:border-b-0">
            <NuxtLink 
              :to="`/info/${category}/${item.slug}`" 
              class="block py-2 px-2 hover:bg-gray-50 transition-colors rounded"
              :class="{ 'bg-indigo-50 text-indigo-700 font-medium': currentSlug === item.slug }"
            >
              {{ item.title }}
              <span v-if="isAdmin && editMode" @click.prevent.stop="editNavItem(item)" class="ml-2 text-gray-400 hover:text-indigo-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
              </span>
            </NuxtLink>
          </li>
        </ul>
        <div v-if="isAdmin && editMode" class="mt-4 pt-4 border-t border-gray-100">
          <button @click="addNewNavItem" class="text-sm flex items-center text-indigo-600 hover:text-indigo-800">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add New Item
          </button>
        </div>
      </div>

      <!-- Right Content Area -->
      <div class="w-full md:w-3/4 bg-white rounded-lg shadow-md p-6">
        <!-- Admin Mode Switch -->
        <div class="mb-4 p-2 bg-gray-100 rounded-md flex items-center justify-between">
          <span class="text-sm text-gray-700">Admin Mode</span>
          <button 
            @click="adminModeEnabled = !adminModeEnabled" 
            class="px-3 py-1 text-xs rounded-full" 
            :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
          >
            {{ adminModeEnabled ? 'Enabled' : 'Disabled' }}
          </button>
        </div>

        <div class="flex justify-between items-center mb-6">
          <h1 class="text-2xl font-bold text-gray-800">{{ pageTitle }}</h1>
          <div v-if="isAdmin" class="flex space-x-2">
            <button 
              @click="toggleEditMode" 
              class="px-3 py-1 rounded text-sm font-medium"
              :class="editMode ? 'bg-gray-200 text-gray-700' : 'bg-indigo-600 text-white hover:bg-indigo-700'"
            >
              {{ editMode ? 'Exit Edit' : 'Edit Content' }}
            </button>
            <button 
              v-if="editMode" 
              @click="saveContent" 
              class="px-3 py-1 rounded text-sm font-medium bg-green-600 text-white hover:bg-green-700"
              :disabled="isSaving"
            >
              {{ isSaving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>

        <div v-if="isLoading" class="py-4">
          <div class="animate-pulse h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div class="animate-pulse h-4 bg-gray-200 rounded w-5/6 mb-2"></div>
          <div class="animate-pulse h-4 bg-gray-200 rounded w-4/6 mb-2"></div>
          <div class="animate-pulse h-4 bg-gray-200 rounded w-full mb-2"></div>
        </div>
        <div v-else>
          <!-- Edit Mode -->
          <div v-if="editMode" class="space-y-4">
            <div>
              <label for="page-title" class="block text-sm font-medium text-gray-700 mb-1">Page Title</label>
              <input 
                id="page-title" 
                v-model="editableContent.title" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label for="page-content" class="block text-sm font-medium text-gray-700 mb-1">Page Content</label>
              <textarea 
                id="page-content" 
                v-model="editableContent.content" 
                rows="15" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              ></textarea>
            </div>
          </div>
          
          <!-- View Mode -->
          <div v-else class="prose max-w-none">
            <h1 class="text-2xl font-bold mb-4">{{ pageContent.value?.title }}</h1>
            <div class="whitespace-pre-wrap" v-html="renderedContent"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import DOMPurify from 'dompurify'
import { useApi } from '~/composables/useApi'

// 解析Markdown的简单函数
function parseMarkdown(markdown) {
  if (!markdown) return '';
  
  // Process headings
  let html = markdown
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    
  // Process bold and italic
  html = html
    .replace(/\*\*(.*)\*\*/gm, '<strong>$1</strong>')
    .replace(/\_\_(.*)\_\_/gm, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gm, '<em>$1</em>')
    .replace(/\_(.*?)\_/gm, '<em>$1</em>')
    
  // Process links
  html = html.replace(/\[(.*)\]\((.*)\)/gm, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    
  // Process lists
  html = html
    .replace(/^\s*\n\- (.*)/gm, '<ul>\n<li>$1</li>')
    .replace(/^\- (.*)/gm, '<li>$1</li>')
    .replace(/\n\n<\/ul>/gm, '</ul>')
    
  // Process ordered lists
  html = html
    .replace(/^\s*\n\d\. (.*)/gm, '<ol>\n<li>$1</li>')
    .replace(/^\d\. (.*)/gm, '<li>$1</li>')
    .replace(/\n\n<\/ol>/gm, '</ol>')
    
  // Process paragraphs
  html = html
    .replace(/^\s*\n\s*\n/gm, '</p><p>')
    .replace(/^([^<].*)/gm, '<p>$1</p>')
    
  // Fix potential HTML issues
  html = html
    .replace(/<\/ul>\s*<\/p>/g, '</ul>')
    .replace(/<\/ol>\s*<\/p>/g, '</ol>')
    .replace(/<p>\s*<ul>/g, '<ul>')
    .replace(/<p>\s*<ol>/g, '<ol>')
    .replace(/<\/p>\s*<\/p>/g, '</p>')
    .replace(/^<\/p>/g, '')
    
  return html;
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { content } = useApi()

// =====================================================================
// 页面判断与数据调用流程
// =====================================================================

// 1. 从路由参数获取category和slug
const category = computed(() => route.params.category)  // 例如：'about'
const currentSlug = computed(() => route.params.slug)   // 例如：'join-us'

// 状态变量
const isLoading = ref(true)
const isSaving = ref(false)
const editMode = ref(false)
const navigationItems = ref([])
const pageContent = ref(null)
const editableContent = ref({
  title: '',
  content: ''
})

// 计算属性
// 临时添加管理员模式开关用于测试
const adminModeEnabled = ref(false)

const isAdmin = computed(() => {
  // 使用临时开关或检查用户权限
  return adminModeEnabled.value || (authStore.user && authStore.user.is_staff)
})

const pageTitle = computed(() => {
  return editMode.value ? editableContent.value.title : (pageContent.value?.title || '')
})

// 3. 内容渲染处理 - 将换行符转换为<br>标签
const renderedContent = computed(() => {
  if (!pageContent.value?.content) return ''
  // 将换行符转换为<br>标签
  return pageContent.value.content.replace(/\n/g, '<br>')
})

// 获取类别标题
const getCategoryTitle = (category) => {
  const categoryMap = {
    'about': 'About Us',
    'shopping': 'Shopping Guide',
    'service': 'After-Sales Service',
    'policy': 'Policies'
  }
  return categoryMap[category] || 'Information'
}

// 2.1 获取左侧导航数据
const fetchNavigationItems = async () => {
  try {
    isLoading.value = true
    console.log(`Getting content items for category ${category.value}`)
    
    // 调用API获取导航数据
    // API调用: GET /api/v1/content/page-contents/?category=about
    const response = await content.getPageContent(category.value)
    console.log('API response:', response)
    
    if (response && response.results) {
      // 从API响应中提取导航项
      navigationItems.value = response.results.map(item => ({
        slug: item.slug,
        title: item.title,
        id: item.id
      }))
      
      console.log('Navigation items:', navigationItems.value)
    } else {
      console.error('API response format incorrect:', response)
      navigationItems.value = []
    }
  } catch (error) {
    console.error('Failed to fetch navigation data:', error)
    navigationItems.value = []
  } finally {
    isLoading.value = false
  }
}

// 2.2 获取页面内容
const fetchPageContent = async () => {
  try {
    isLoading.value = true
    console.log(`Fetching page content: category=${category.value}, slug=${currentSlug.value}`)
    
    console.log('尝试通过slug获取内容...')
    // 方法1：直接通过slug获取内容
    // API调用: GET /api/v1/content/page-contents/by_category_slug/?category=about&slug=join-us
    const response = await content.getPageContentBySlug(category.value, currentSlug.value)
    console.log('Page content API response:', response)
    
    if (response && response.title) {
      console.log('通过slug成功获取内容')
      pageContent.value = {
        title: response.title,
        content: response.content || ''
      }
    } else {
      console.log('通过slug获取内容失败，尝试通过ID获取...')
      // 方法2：如果方法1失败，通过ID获取内容
      const selectedItem = navigationItems.value.find(item => item.slug === currentSlug.value)
      console.log('找到的导航项:', selectedItem)
      
      if (selectedItem && selectedItem.id) {
        console.log(`尝试通过ID ${selectedItem.id} 获取内容...`)
        // API调用: GET /api/v1/content/page-contents/3/
        const detailResponse = await content.getPageContentDetail(selectedItem.id)
        console.log('Content detail API response:', detailResponse)
        
        if (detailResponse && detailResponse.title) {
          console.log('通过ID成功获取内容')
          pageContent.value = {
            title: detailResponse.title,
            content: detailResponse.content || ''
          }
        } else {
          console.error('通过ID获取内容失败', detailResponse)
          throw new Error('Could not get content details')
        }
      } else {
        console.error('在导航项中找不到对应的内容', currentSlug.value, navigationItems.value)
        throw new Error('Could not find corresponding content')
      }
    }
  } catch (error) {
    console.error('Failed to fetch page content:', error)
    pageContent.value = {
      title: 'Loading Failed',
      content: 'Page content failed to load. Please try again later.'
    }
  } finally {
    isLoading.value = false
    editableContent.value = {
      title: pageContent.value.title,
      content: pageContent.value.content
    }
  }
}

// 切换编辑模式
const toggleEditMode = () => {
  if (editMode.value) {
    // Exit edit mode, restore original content
    editableContent.value = {
      title: pageContent.value.title,
      content: pageContent.value.content
    }
  }
  editMode.value = !editMode.value
}

// Save content
const saveContent = async () => {
  try {
    isSaving.value = true
    // Here we should call API to save content
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // Update local content
    pageContent.value = {
      title: editableContent.value.title,
      content: editableContent.value.content
    }
    
    // Exit edit mode
    editMode.value = false
    
    // Show success message
    alert('Content saved successfully')
  } catch (error) {
    console.error('Failed to save content:', error)
    alert('Save failed, please try again later')
  } finally {
    isSaving.value = false
  }
}

// Edit navigation item
const editNavItem = (item) => {
  const newTitle = prompt('Enter new title', item.title)
  if (newTitle && newTitle !== item.title) {
    // Here we should call API to update navigation item
    // Simulate update
    const index = navigationItems.value.findIndex(i => i.slug === item.slug)
    if (index !== -1) {
      navigationItems.value[index].title = newTitle
      alert('Navigation item updated successfully')
    }
  }
}

// Add new navigation item
const addNewNavItem = () => {
  const title = prompt('Enter title')
  if (!title) return
  
  const slug = title.toLowerCase().replace(/\s+/g, '-')
  
  // Check if slug already exists
  if (navigationItems.value.some(item => item.slug === slug)) {
    alert('A link with this title already exists, please use a different title')
    return
  }
  
  // Here we should call API to add navigation item
  // Simulate add
  navigationItems.value.push({ slug, title })
  alert('Navigation item added successfully')
  
  // Navigate to newly added item
  router.push(`/info/${category.value}/${slug}`)
}

// Watch route changes
watch(
  () => route.params,
  () => {
    if (category.value && currentSlug.value) {
      fetchPageContent()
    }
  }
)

// Fetch data on page load
onMounted(async () => {
  await fetchNavigationItems()
  if (category.value && currentSlug.value) {
    await fetchPageContent()
  }
})

// Page metadata
definePageMeta({
  layout: 'default'
})
</script>

<style>
.prose {
  max-width: 100%;
}
.prose h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #1f2937;
}
.prose h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #1f2937;
}
.prose h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  color: #1f2937;
}
.prose p {
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
  line-height: 1.625;
}
.prose ul {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding-left: 1.5rem;
  list-style-type: disc;
}
.prose li {
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}
</style>
