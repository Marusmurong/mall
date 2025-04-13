<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-center mb-8">网站信息中心</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- 关于我们 -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 py-4 px-6">
          <h2 class="text-xl font-bold text-white">关于我们</h2>
        </div>
        <div class="p-6">
          <ul class="space-y-2">
            <li v-for="item in aboutItems" :key="item.slug" class="border-b border-gray-100 last:border-b-0">
              <NuxtLink 
                :to="`/info/about/${item.slug}`" 
                class="block py-2 hover:text-indigo-600 transition-colors"
              >
                {{ item.title }}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 购物指南 -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 py-4 px-6">
          <h2 class="text-xl font-bold text-white">购物指南</h2>
        </div>
        <div class="p-6">
          <ul class="space-y-2">
            <li v-for="item in shoppingItems" :key="item.slug" class="border-b border-gray-100 last:border-b-0">
              <NuxtLink 
                :to="`/info/shopping/${item.slug}`" 
                class="block py-2 hover:text-indigo-600 transition-colors"
              >
                {{ item.title }}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 售后服务 -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-gradient-to-r from-green-500 to-teal-500 py-4 px-6">
          <h2 class="text-xl font-bold text-white">售后服务</h2>
        </div>
        <div class="p-6">
          <ul class="space-y-2">
            <li v-for="item in serviceItems" :key="item.slug" class="border-b border-gray-100 last:border-b-0">
              <NuxtLink 
                :to="`/info/service/${item.slug}`" 
                class="block py-2 hover:text-indigo-600 transition-colors"
              >
                {{ item.title }}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </NuxtLink>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 页面数据
const aboutItems = ref([
  { slug: 'company', title: '公司简介' },
  { slug: 'contact', title: '联系我们' },
  { slug: 'join', title: '加入我们' }
])

const shoppingItems = ref([
  { slug: 'process', title: '购物流程' },
  { slug: 'payment', title: '支付方式' },
  { slug: 'delivery', title: '配送方式' }
])

const serviceItems = ref([
  { slug: 'return', title: '退换货政策' },
  { slug: 'warranty', title: '保修条款' },
  { slug: 'faq', title: '常见问题' }
])

// 页面元数据
definePageMeta({
  layout: 'default'
})
</script>
