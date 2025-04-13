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
    'about': '关于我们',
    'shopping': '购物指南',
    'service': '售后服务'
  }
  return categoryMap[category] || '信息'
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
        { slug: 'company', title: '公司简介' },
        { slug: 'contact', title: '联系我们' },
        { slug: 'join', title: '加入我们' }
      ]
    } else if (category.value === 'shopping') {
      navigationItems.value = [
        { slug: 'process', title: '购物流程' },
        { slug: 'payment', title: '支付方式' },
        { slug: 'delivery', title: '配送方式' }
      ]
    } else if (category.value === 'service') {
      navigationItems.value = [
        { slug: 'return', title: '退换货政策' },
        { slug: 'warranty', title: '保修条款' },
        { slug: 'faq', title: '常见问题' }
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
          title: '公司简介',
          content: `# 公司简介\n\n我们是一家专注于提供高品质商品的电子商务平台，致力于为消费者提供最好的购物体验。\n\n## 我们的使命\n\n为消费者提供优质、安全、实惠的商品，让每一次购物都充满愉悦。\n\n## 我们的愿景\n\n成为最受消费者信赖的电子商务平台，引领行业发展，创造更美好的购物未来。`
        },
        'contact': {
          title: '联系我们',
          content: `# 联系我们\n\n## 客服热线\n\n- 电话：400-123-4567\n- 服务时间：周一至周日 9:00-22:00\n\n## 总部地址\n\n北京市朝阳区建国路88号现代城SOHO B座20层\n\n## 电子邮箱\n\nservice@example.com`
        },
        'join': {
          title: '加入我们',
          content: `# 加入我们\n\n我们正在寻找优秀的人才加入我们的团队，共同成长，共创未来。\n\n## 开放职位\n\n- 产品经理\n- 前端开发工程师\n- 后端开发工程师\n- UI/UX设计师\n- 运营专员\n\n## 应聘方式\n\n请将您的简历发送至：hr@example.com，邮件主题请注明：应聘职位+姓名`
        }
      },
      'shopping': {
        'process': {
          title: '购物流程',
          content: `# 购物流程\n\n## 1. 浏览商品\n\n在首页或分类页面浏览商品，或使用搜索功能查找您需要的商品。\n\n## 2. 将商品加入购物车\n\n找到心仪的商品后，点击"加入购物车"按钮将商品添加到购物车。\n\n## 3. 结算\n\n在购物车页面，确认商品信息后点击"结算"按钮进入结算页面。\n\n## 4. 填写订单信息\n\n填写收货地址、选择支付方式和配送方式。\n\n## 5. 提交订单\n\n确认订单信息无误后，点击"提交订单"按钮完成下单。\n\n## 6. 支付\n\n根据选择的支付方式完成支付。\n\n## 7. 等待收货\n\n订单支付成功后，我们会尽快为您发货，您可以在"我的订单"中查看订单状态。`
        },
        'payment': {
          title: '支付方式',
          content: `# 支付方式\n\n我们提供多种支付方式，您可以根据自己的需求选择合适的支付方式。\n\n## 在线支付\n\n- 支付宝\n- 微信支付\n- 银联在线支付\n- 信用卡支付\n\n## 其他支付方式\n\n- 货到付款（部分地区支持）\n- 银行转账\n\n## 发票信息\n\n如需开具发票，请在提交订单时选择开具发票，并填写相关发票信息。`
        },
        'delivery': {
          title: '配送方式',
          content: `# 配送方式\n\n## 标准配送\n\n- 配送范围：全国大部分地区\n- 配送时间：一般在下单后1-3个工作日内发货，3-5个工作日送达\n- 配送费用：订单满99元免运费，否则收取10元运费\n\n## 加急配送\n\n- 配送范围：部分一线城市\n- 配送时间：下单后24小时内送达\n- 配送费用：每单收取20元运费\n\n## 自提\n\n- 自提点：全国各大城市的自提点\n- 自提时间：下单后1-2个工作日可自提\n- 自提费用：免费`
        }
      },
      'service': {
        'return': {
          title: '退换货政策',
          content: `# 退换货政策\n\n## 退换货条件\n\n1. 商品收到后7天内，如商品有质量问题，可申请退换货\n2. 商品收到后7天内，如对商品不满意，可申请退货（部分特殊商品除外）\n3. 商品收到后8-15天内，如商品有质量问题，可申请换货或维修\n\n## 不支持退换货的情况\n\n1. 超过退换货期限\n2. 商品已使用、损坏或缺少配件\n3. 定制类商品\n4. 个人护理类商品已拆封\n5. 食品类商品已拆封\n\n## 退换货流程\n\n1. 登录账户，进入"我的订单"，找到对应订单点击"申请退换货"\n2. 填写退换货原因，上传相关凭证\n3. 等待审核通过\n4. 按照指引寄回商品\n5. 商品验收通过后，按原支付方式退款`
        },
        'warranty': {
          title: '保修条款',
          content: `# 保修条款\n\n## 保修期限\n\n- 电子产品：自收到商品之日起12个月\n- 家用电器：自收到商品之日起24个月\n- 服装、鞋帽、箱包：自收到商品之日起3个月\n\n## 保修范围\n\n在正常使用情况下出现的质量问题，我们将提供免费维修或更换服务。\n\n## 不在保修范围内的情况\n\n1. 超过保修期\n2. 人为损坏\n3. 未按说明书操作导致的损坏\n4. 自行拆卸或修理导致的损坏\n5. 不可抗力（如自然灾害）导致的损坏\n\n## 保修流程\n\n1. 联系客服，说明商品问题\n2. 按客服指引，提供相关凭证\n3. 寄送商品至指定维修点\n4. 维修完成后，我们会将商品寄回给您`
        },
        'faq': {
          title: '常见问题',
          content: `# 常见问题\n\n## 订单相关\n\n### Q: 如何查询订单状态？\nA: 登录账户后，在"我的订单"中可以查看所有订单的状态。\n\n### Q: 下单后可以修改订单信息吗？\nA: 订单提交后，如果订单状态为"待付款"，可以取消订单重新下单；如果订单已付款但未发货，请联系客服协助修改。\n\n## 支付相关\n\n### Q: 支付成功但订单显示未支付？\nA: 支付成功后，订单状态更新可能有延迟，请稍等片刻刷新页面，如长时间未更新，请联系客服。\n\n### Q: 如何申请退款？\nA: 在"我的订单"中找到对应订单，点击"申请退款"，按提示操作即可。\n\n## 配送相关\n\n### Q: 为什么我的订单显示"已发货"但查不到物流信息？\nA: 订单发货后，物流信息更新可能有延迟，一般1-2个工作日内可查询到物流信息。\n\n### Q: 收到商品与描述不符怎么办？\nA: 请联系客服并提供相关凭证，我们会尽快为您解决。`
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
        title: '页面不存在',
        content: '抱歉，您访问的页面不存在。'
      }
    }
  } catch (error) {
    console.error('获取页面内容失败:', error)
    pageContent.value = {
      title: '加载失败',
      content: '页面内容加载失败，请稍后再试。'
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
