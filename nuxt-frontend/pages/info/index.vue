<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-center mb-8">Website Information Center</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- About Us -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-gradient-to-r from-blue-500 to-indigo-600 py-4 px-6">
          <h2 class="text-xl font-bold text-white">About Us</h2>
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
      
      <!-- Shopping Guide -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-gradient-to-r from-purple-500 to-pink-500 py-4 px-6">
          <h2 class="text-xl font-bold text-white">Shopping Guide</h2>
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
      
      <!-- After-sales Service -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-gradient-to-r from-green-500 to-teal-500 py-4 px-6">
          <h2 class="text-xl font-bold text-white">After-sales Service</h2>
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
  { slug: 'company', title: 'Company Introduction' },
  { slug: 'contact', title: 'Contact Us' },
  { slug: 'join', title: 'Join Us' }
])

const shoppingItems = ref([
  { slug: 'process', title: 'Purchase Process' },
  { slug: 'payment', title: 'Payment Method' },
  { slug: 'delivery', title: 'Delivery Method' }
])

const serviceItems = ref([
  { slug: 'return', title: 'Return Policy' },
  { slug: 'warranty', title: 'Warranty Terms' },
  { slug: 'faq', title: 'FAQ' }
])

// 页面元数据
definePageMeta({
  layout: 'default'
})
</script>
