<template>
  <footer class="bg-gray-800 text-white">
    <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- 动态生成页脚内容 -->
        <template v-if="footerSections && footerSections.length > 0">
          <div v-for="(section, index) in footerSections" :key="index">
            <h3 class="text-lg font-semibold mb-4">{{ section.title }}</h3>
            <ul class="space-y-2">
              <li v-for="(item, itemIndex) in section.items" :key="itemIndex">
                <NuxtLink :to="item.link" class="text-gray-300 hover:text-white">{{ item.title }}</NuxtLink>
              </li>
            </ul>
          </div>
        </template>
        
        <!-- 联系信息 -->
        <div>
          <h3 class="text-lg font-semibold mb-4">{{ $t('footer.contact_info') }}</h3>
          <ul class="space-y-2">
            <li class="flex items-center text-gray-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              +6012-5861693
            </li>
            <li class="flex items-center text-gray-300">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              samchenglu963@gmail.com
            </li>
          </ul>
        </div>
        
        <!-- 如果没有从API获取到数据，显示默认内容 -->
        <template v-if="!footerSections || footerSections.length === 0">
          <!-- Company information -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.about_us') }}</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/about/company-profile" class="text-gray-300 hover:text-white">{{ $t('footer.company_profile') }}</NuxtLink></li>
              <li><NuxtLink to="/info/about/contact-us" class="text-gray-300 hover:text-white">{{ $t('footer.contact_us') }}</NuxtLink></li>
              <li><NuxtLink to="/info/about/join-us" class="text-gray-300 hover:text-white">{{ $t('footer.join_us') }}</NuxtLink></li>
            </ul>
          </div>
          
          <!-- Shopping guide -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.shopping_guide') }}</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/shopping/shopping-process" class="text-gray-300 hover:text-white">{{ $t('footer.shopping_process') }}</NuxtLink></li>
              <li><NuxtLink to="/info/shopping/payment-methods" class="text-gray-300 hover:text-white">{{ $t('footer.payment_methods') }}</NuxtLink></li>
              <li><NuxtLink to="/info/shopping/delivery-methods" class="text-gray-300 hover:text-white">{{ $t('footer.delivery_methods') }}</NuxtLink></li>
            </ul>
          </div>
          
          <!-- After-sales service -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.after_sales') }}</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/policy/return-policy" class="text-gray-300 hover:text-white">{{ $t('footer.return_policy') }}</NuxtLink></li>
              <li><NuxtLink to="/info/policy/warranty-terms" class="text-gray-300 hover:text-white">{{ $t('footer.warranty_terms') }}</NuxtLink></li>
              <li><NuxtLink to="/info/policy/faq" class="text-gray-300 hover:text-white">{{ $t('footer.faq') }}</NuxtLink></li>
            </ul>
          </div>
        </template>
      </div>
      
      <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
        <p>{{ copyright }}</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useApi } from '~/composables/useApi'

const { t } = useI18n()
const api = useApi()

// 页脚数据
const footerSections = ref([])
const copyright = computed(() => `&copy; ${new Date().getFullYear()} ${t('footer.copyright')}`)

// 获取页脚导航数据
const fetchFooterData = async () => {
  try {
    console.log('开始获取页脚导航数据')
    
    // 使用useApi获取数据
    try {
      console.log('正在使用useApi获取页脚数据')
      
      // 获取about类别
      console.log('正在请求about类别')
      const aboutData = await api.getPageContent('about')
      console.log('about类别数据:', aboutData)
      
      // 获取shopping类别
      console.log('正在请求shopping类别')
      const shoppingData = await api.getPageContent('shopping')
      console.log('shopping类别数据:', shoppingData)
      
      // 获取policy类别
      console.log('正在请求policy类别')
      const policyData = await api.getPageContent('policy')
      console.log('policy类别数据:', policyData)
      
      // 构建页脚数据
      if (aboutData && shoppingData && policyData) {
        // 过滤掉 slug 为 "string" 或包含异常长字符串的条目
        const filterValidItems = (apiResponse) => {
          // 检查是否有完整的响应结构
          if (!apiResponse) return []
          
          // 如果是标准API响应格式 {code: 0, message: "success", data: {results: [...]}}
          if (apiResponse.code === 0 && apiResponse.data && apiResponse.data.results) {
            return apiResponse.data.results.filter(item => 
              item.slug !== 'string' && 
              item.slug.length < 50 && 
              item.title && 
              item.title.length < 50
            );
          }
          
          console.warn('API响应格式不符合预期:', apiResponse)
          return []
        };
        
        footerSections.value = [
          {
            title: t('footer.about_us'),
            items: filterValidItems(aboutData).map(item => ({
              title: item.title,
              link: `/info/about/${item.slug}`
            }))
          },
          {
            title: t('footer.shopping_guide'),
            items: filterValidItems(shoppingData).map(item => ({
              title: item.title,
              link: `/info/shopping/${item.slug}`
            }))
          },
          {
            title: t('footer.after_sales'),
            items: filterValidItems(policyData).map(item => ({
              title: item.title,
              link: `/info/policy/${item.slug}`
            }))
          }
        ]
        
        console.log('页脚数据已加载:', footerSections.value)
      } else {
        console.error('获取页脚数据失败: API返回无效响应')
      }
    } catch (apiError) {
      console.error('使用useApi获取数据失败:', apiError)
    }
  } catch (error) {
    console.error('获取页脚数据失败:', error)
  }
}

// 页面加载时获取数据
onMounted(async () => {
  await fetchFooterData()
})
</script>
