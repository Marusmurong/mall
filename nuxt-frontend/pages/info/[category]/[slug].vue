<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex flex-col md:flex-row gap-8">
      <!-- 左侧导航栏 -->
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
            添加新项目
          </button>
        </div>
      </div>

      <!-- 右侧内容区域 -->
      <div class="w-full md:w-3/4 bg-white rounded-lg shadow-md p-6">
        <!-- 临时管理员模式开关 -->
        <div class="mb-4 p-2 bg-gray-100 rounded-md flex items-center justify-between">
          <span class="text-sm text-gray-700">管理员模式</span>
          <button 
            @click="adminModeEnabled = !adminModeEnabled" 
            class="px-3 py-1 text-xs rounded-full" 
            :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
          >
            {{ adminModeEnabled ? '已启用' : '未启用' }}
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
              {{ editMode ? '退出编辑' : '编辑内容' }}
            </button>
            <button 
              v-if="editMode" 
              @click="saveContent" 
              class="px-3 py-1 rounded text-sm font-medium bg-green-600 text-white hover:bg-green-700"
              :disabled="isSaving"
            >
              {{ isSaving ? '保存中...' : '保存' }}
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
          <!-- 编辑模式 -->
          <div v-if="editMode" class="space-y-4">
            <div>
              <label for="page-title" class="block text-sm font-medium text-gray-700 mb-1">页面标题</label>
              <input 
                id="page-title" 
                v-model="editableContent.title" 
                type="text" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div>
              <label for="page-content" class="block text-sm font-medium text-gray-700 mb-1">页面内容</label>
              <textarea 
                id="page-content" 
                v-model="editableContent.content" 
                rows="15" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              ></textarea>
            </div>
          </div>
          
          <!-- 查看模式 -->
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

// 简单的Markdown解析函数
function parseMarkdown(markdown) {
  if (!markdown) return '';
  
  // 处理标题
  let html = markdown
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    
  // 处理粗体和斜体
  html = html
    .replace(/\*\*(.*)\*\*/gm, '<strong>$1</strong>')
    .replace(/\_\_(.*)\_\_/gm, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gm, '<em>$1</em>')
    .replace(/\_(.*?)\_/gm, '<em>$1</em>')
    
  // 处理链接
  html = html.replace(/\[(.*)\]\((.*)\)/gm, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
    
  // 处理列表
  html = html
    .replace(/^\s*\n\- (.*)/gm, '<ul>\n<li>$1</li>')
    .replace(/^\- (.*)/gm, '<li>$1</li>')
    .replace(/\n\n<\/ul>/gm, '</ul>')
    
  // 处理有序列表
  html = html
    .replace(/^\s*\n\d\. (.*)/gm, '<ol>\n<li>$1</li>')
    .replace(/^\d\. (.*)/gm, '<li>$1</li>')
    .replace(/\n\n<\/ol>/gm, '</ol>')
    
  // 处理段落
  html = html
    .replace(/^\s*\n\s*\n/gm, '</p><p>')
    .replace(/^([^<].*)/gm, '<p>$1</p>')
    
  // 修复可能的HTML问题
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

// 获取路由参数
const category = computed(() => route.params.category)
const currentSlug = computed(() => route.params.slug)

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
// 临时添加一个管理员模式开关，方便测试
const adminModeEnabled = ref(false)

const isAdmin = computed(() => {
  // 使用临时开关或检查用户权限
  return adminModeEnabled.value || (authStore.user && authStore.user.is_staff)
})

const pageTitle = computed(() => {
  return editMode.value ? editableContent.value.title : (pageContent.value?.title || '')
})

const renderedContent = computed(() => {
  if (!pageContent.value?.content) return ''
  // 简单地将换行符转换为<br>标签
  return pageContent.value.content.replace(/\n/g, '<br>')
})

// 获取分类标题
const getCategoryTitle = (category) => {
  const categoryMap = {
    'about': 'About Us',
    'shopping': 'Shopping Guide',
    'service': 'After-sales Service'
  }
  return categoryMap[category] || 'Information'
}

// 获取导航数据
const fetchNavigationItems = async () => {
  try {
    isLoading.value = true
    // 这里应该调用API获取导航数据
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 根据不同分类返回不同的导航项
    if (category.value === 'about') {
      navigationItems.value = [
        { slug: 'company', title: 'Company Introduction' },
        { slug: 'contact', title: 'Contact Us' },
        { slug: 'join', title: 'Join Us' }
      ]
    } else if (category.value === 'shopping') {
      navigationItems.value = [
        { slug: 'process', title: 'Purchase Process' },
        { slug: 'payment', title: 'Payment Methods' },
        { slug: 'delivery', title: 'Shipping Methods' }
      ]
    } else if (category.value === 'service') {
      navigationItems.value = [
        { slug: 'return', title: 'Return Policy' },
        { slug: 'warranty', title: 'Warranty Terms' },
        { slug: 'faq', title: 'FAQ' }
      ]
    }
    
    // 如果当前slug不在导航项中，跳转到第一个导航项
    if (navigationItems.value.length > 0 && !navigationItems.value.some(item => item.slug === currentSlug.value)) {
      router.replace(`/info/${category.value}/${navigationItems.value[0].slug}`)
    }
  } catch (error) {
    console.error('获取导航数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 获取页面内容
const fetchPageContent = async () => {
  try {
    isLoading.value = true
    // 这里应该调用API获取页面内容
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟返回数据
    const dummyContent = {
      'about': {
        'company': {
          title: 'Company Introduction',
          content: `# Company Introduction\n\nWe are an e-commerce platform dedicated to providing high-quality products, committed to delivering the best shopping experience for consumers.\n\n## Our Mission\n\nProvide quality, safe, and affordable products to consumers, making every shopping experience enjoyable.\n\n## Our Vision\n\nBecome the most trusted e-commerce platform, leading the industry, and creating a better shopping future.`
        },
        'contact': {
          title: 'Contact Us',
          content: `# Contact Us\n\n## Customer Service\n\n- Phone: 400-123-4567\n- Service Hours: Monday to Sunday 9:00-22:00\n\n## Headquarters Address\n\nBeijing, China\n\n## Email\n\nservice@example.com`
        },
        'join': {
          title: 'Join Us',
          content: `# Join Us\n\nWe are looking for outstanding talents to join our team,共同成长，共创未来。\n\n## Open Positions\n\n- Product Manager\n- Frontend Developer\n- Backend Developer\n- UI/UX Designer\n- Operation Staff\n\n## Application Method\n\nPlease send your resume to：hr@example.com，mail subject please注明：应聘职位+姓名`
        }
      },
      'shopping': {
        'process': {
          title: 'Purchase Process',
          content: `# Purchase Process\n\n## 1. Browse Products\n\nIn the homepage or category page, browse products, or use the search function to find the products you need.\n\n## 2. Add to Cart\n\nAfter finding the product you like, click the "Add to Cart" button to add the product to the shopping cart.\n\n## 3. Checkout\n\nGo to the shopping cart page, confirm the product information, and click the "Checkout" button to enter the checkout page.\n\n## 4. Fill in Order Information\n\nFill in the shipping address, payment method, and shipping method.\n\n## 5. Submit Order\n\nConfirm that the order information is correct and click the "Submit Order" button to complete the order.\n\n## 6. Payment\n\nPay according to the selected payment method.\n\n## 7. Wait for Delivery\n\nAfter the payment is successful, we will ship the goods as soon as possible. You can view the order status in "My Orders".`
        },
        'payment': {
          title: 'Payment Methods',
          content: `# Payment Methods\n\nWe provide multiple payment methods, you can choose the payment method that suits you.\n\n## Online Payment\n\n- Alipay\n- WeChat Pay\n- UnionPay Online Payment\n- Credit Card Payment\n\n## Other Payment Methods\n\n- Cash on Delivery (available in some areas)\n- Bank Transfer\n\n## Invoice Information\n\nIf you need an invoice, please select to issue an invoice when submitting the order, and fill in the relevant invoice information.`
        },
        'delivery': {
          title: 'Delivery Methods',
          content: `# Delivery Methods\n\n## Standard Delivery\n\n- Delivery Range: Most of China\n- Delivery Time:一般在下单后1-3个工作日内发货，3-5个工作日送达\n- Delivery Fee: Free shipping for orders over 99 yuan, otherwise 10 yuan\n\n## Rush Delivery\n\n- Delivery Range:部分一线城市\n- Delivery Time:下单后24小时内送达\n- Delivery Fee:每单收取20元运费\n\n## Self Pick-up\n\n- Pick-up Points: National major cities\n- Pick-up Time: After 1-2 working days\n- Pick-up Fee: Free`
        }
      },
      'service': {
        'return': {
          title: 'Return Policy',
          content: `# Return Policy\n\n## Return Conditions\n\n1. Goods must be returned within 7 days of receipt\n2. Goods must be returned within 7 days of receipt (some special goods may not be returned)\n3. Goods must be returned within 8-15 days of receipt\n\n## Goods must be returned within 8-15 days of receipt\n\n1. Goods must be returned within 8-15 days of receipt\n2. Goods must be returned within 8-15 days of receipt\n3. Goods must be returned within 8-15 days of receipt\n4. Goods must be returned within 8-15 days of receipt\n5. Goods must be returned within 8-15 days of receipt\n\n## Return Process\n\n1. Login to account, go to "My Orders", find the corresponding order and click "Apply for Return"\n2. Fill in the return reason, upload relevant proof\n3. Wait for approval\n4. Follow the instructions to return the goods\n5. After goods inspection, refund will be processed`
        },
        'warranty': {
          title: 'Warranty Terms',
          content: `# Warranty Terms\n\n## Warranty Period\n\n- Electronics: 12 months from receipt\n- Home Appliances: 24 months from receipt\n- Clothing, Hats, Bags: 3 months from receipt\n\n## Warranty Scope\n\nIn normal use, we will provide free maintenance or replacement services.\n\n## Warranty Exclusions\n\n1. Warranty Expiration\n2. Human Damage\n3. Damage Due to Improper Use\n4. Self-Dismantling or Repair\n5. Natural Disasters\n\n## Warranty Process\n\n1. Contact Customer Service, describe the goods issue\n2. Provide relevant proof according to customer service instructions\n3. Send goods to specified maintenance point\n4. After maintenance completion, we will return the goods`
        },
        'faq': {
          title: 'FAQ',
          content: `# FAQ\n\n## Order Related\n\n### Q: How to query order status?\nA: After logging in, you can view all order statuses in "My Orders".\n\n### Q: Can I modify order information after placing the order?\nA: After the order status is "Pending Payment", you can cancel the order and re-order; if the order has been paid but not shipped, please contact customer service for assistance.\n\n## Payment Related\n\n### Q: Payment successful but order shows unpaid?\nA: After payment, the order status update may take a delay, please wait a moment and refresh the page, if it is still not updated after a long time, please contact customer service.\n\n### Q: How to apply for refund?\nA: In "My Orders", find the corresponding order and click "Apply for Refund", follow the instructions.\n\n## Delivery Related\n\n### Q: Why can't I query the logistics information after the order is marked as "Shipped"?\nA: The logistics information update may take a delay, generally 1-2 working days can be queried.\n\n### Q: The goods received does not match the description?\nA: Please contact customer service and provide relevant proof, we will solve it as soon as possible.`
        }
      }
    }
    
    // 获取当前页面内容
    if (dummyContent[category.value] && dummyContent[category.value][currentSlug.value]) {
      pageContent.value = dummyContent[category.value][currentSlug.value]
      // 初始化可编辑内容
      editableContent.value = {
        title: pageContent.value.title,
        content: pageContent.value.content
      }
    } else {
      pageContent.value = {
        title: 'Page Not Found',
        content: 'Sorry, the page you are looking for does not exist.'
      }
    }
  } catch (error) {
    console.error('获取页面内容失败:', error)
    pageContent.value = {
      title: 'Page Not Found',
      content: 'Sorry, the page you are looking for does not exist.'
    }
  } finally {
    isLoading.value = false
  }
}

// 切换编辑模式
const toggleEditMode = () => {
  if (editMode.value) {
    // 退出编辑模式，恢复原始内容
    editableContent.value = {
      title: pageContent.value.title,
      content: pageContent.value.content
    }
  }
  editMode.value = !editMode.value
}

// 保存内容
const saveContent = async () => {
  try {
    isSaving.value = true
    // 这里应该调用API保存内容
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 更新本地内容
    pageContent.value = {
      title: editableContent.value.title,
      content: editableContent.value.content
    }
    
    // 退出编辑模式
    editMode.value = false
    
    // 显示成功提示
    alert('内容保存成功')
  } catch (error) {
    console.error('保存内容失败:', error)
    alert('保存失败，请稍后再试')
  } finally {
    isSaving.value = false
  }
}

// 编辑导航项
const editNavItem = (item) => {
  const newTitle = prompt('请输入新的标题', item.title)
  if (newTitle && newTitle !== item.title) {
    // 这里应该调用API更新导航项
    // 模拟更新
    const index = navigationItems.value.findIndex(i => i.slug === item.slug)
    if (index !== -1) {
      navigationItems.value[index].title = newTitle
      alert('导航项更新成功')
    }
  }
}

// 添加新导航项
const addNewNavItem = () => {
  const title = prompt('请输入标题')
  if (!title) return
  
  const slug = title.toLowerCase().replace(/\s+/g, '-')
  
  // 检查slug是否已存在
  if (navigationItems.value.some(item => item.slug === slug)) {
    alert('该标题对应的链接已存在，请使用其他标题')
    return
  }
  
  // 这里应该调用API添加导航项
  // 模拟添加
  navigationItems.value.push({ slug, title })
  alert('导航项添加成功')
  
  // 跳转到新添加的项
  router.push(`/info/${category.value}/${slug}`)
}

// 监听路由变化
watch(
  () => route.params,
  () => {
    if (category.value && currentSlug.value) {
      fetchPageContent()
    }
  }
)

// 页面加载时获取数据
onMounted(async () => {
  await fetchNavigationItems()
  if (category.value && currentSlug.value) {
    await fetchPageContent()
  }
})

// 页面元数据
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
