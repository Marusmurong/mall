<template>
  <!-- Telegram绑定模态框 -->
  <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
      <div class="flex items-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-500 mr-3" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18.717-.962 4.963-1.361 6.585-.165.669-.537 1.291-1.167 1.639-.597.331-1.133.146-1.755-.224-.982-.584-1.5-.927-2.467-1.5-.969-.573-1.745-.271-2.127.128-.379.399-1.188 1.394-1.188 1.394s-.328.33-.722.034c-.393-.296-.949-1.621-.949-1.621s-1.302-2.228.089-3.066c.452-.273 2.343-1.761 4.435-3.143.965-.639 1.906-1.263 2.457-1.624.842-.555 1.972-.887 2.755-.608z"/>
        </svg>
        <div>
          <h3 class="text-lg font-medium text-gray-900">绑定 Telegram</h3>
          <p class="text-sm text-gray-600">接收心愿单相关通知</p>
        </div>
      </div>
      
      <div class="mb-4">
        <p class="text-sm text-gray-600">请按照以下步骤操作：</p>
        <ol class="mt-2 space-y-2 text-sm text-gray-600 list-decimal list-inside">
          <li>添加官方机器人 <a href="https://t.me/cartit_bot" target="_blank" class="text-blue-600 hover:text-blue-800">@cartit_bot</a></li>
          <li>复制下方令牌并发送给机器人</li>
          <li>点击"检查绑定状态"按钮确认绑定成功</li>
        </ol>
      </div>
      
      <div class="bg-gray-50 p-3 rounded-md mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">您的绑定令牌</span>
          <button 
            @click="copyTelegramToken"
            class="text-xs text-blue-600 hover:text-blue-800 font-medium"
            :disabled="!telegramToken"
          >
            复制
          </button>
        </div>
        <div class="flex items-center">
          <input 
            type="text" 
            readonly 
            :value="telegramToken || '点击生成令牌'" 
            class="w-full bg-white border border-gray-300 rounded-l-md px-3 py-2 text-sm text-gray-700"
          />
          <button 
            @click="generateTelegramToken"
            class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-r-md text-sm"
            :disabled="telegramTokenLoading"
          >
            <span v-if="telegramTokenLoading">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            <span v-else>生成</span>
          </button>
        </div>
      </div>
      
      <div class="flex justify-between">
        <button 
          @click="checkTelegramConnection"
          class="btn btn-primary"
          :disabled="telegramLinking"
        >
          <span v-if="telegramLinking" class="flex items-center">
            <svg class="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            检查中...
          </span>
          <span v-else>检查绑定状态</span>
        </button>
        <button 
          @click="closeModal"
          class="btn btn-outline"
        >
          关闭
        </button>
      </div>
    </div>
  </div>

  <!-- Telegram状态显示 -->
  <div v-if="telegramConnected" class="flex items-center justify-between mt-4">
    <div class="flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-blue-500 mr-3" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18.717-.962 4.963-1.361 6.585-.165.669-.537 1.291-1.167 1.639-.597.331-1.133.146-1.755-.224-.982-.584-1.5-.927-2.467-1.5-.969-.573-1.745-.271-2.127.128-.379.399-1.188 1.394-1.188 1.394s-.328.33-.722.034c-.393-.296-.949-1.621-.949-1.621s-1.302-2.228.089-3.066c.452-.273 2.343-1.761 4.435-3.143.965-.639 1.906-1.263 2.457-1.624.842-.555 1.972-.887 2.755-.608z"/>
      </svg>
      <div>
        <div class="font-medium">已绑定账号</div>
        <div class="text-sm text-gray-600">{{ telegramUsername }}</div>
      </div>
    </div>
    <button 
      @click="disconnectTelegram"
      class="text-red-600 hover:text-red-800 text-sm font-medium"
    >
      解除绑定
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRuntimeConfig } from 'nuxt/app'
import { useAuthStore } from '~/stores/auth'

const props = defineProps({
  showModal: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:showModal', 'statusChanged'])

// 获取认证存储
const authStore = useAuthStore()

// Telegram绑定状态
const telegramConnected = ref(false)
const telegramUsername = ref('')
const telegramToken = ref('')
const telegramTokenLoading = ref(false)
const telegramLinking = ref(false)

// 关闭模态框
const closeModal = () => {
  emit('update:showModal', false)
}

// 生成Telegram绑定令牌
const generateTelegramToken = async () => {
  telegramTokenLoading.value = true
  try {
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase || 'http://127.0.0.1:8000'
    
    console.log('正在生成令牌，API地址:', `${baseUrl}/v1/user/telegram/token/?site=default`)
    
    const response = await fetch(`${baseUrl}/v1/user/telegram/token/?site=default`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({}) // 添加空的请求体
    })
    
    const result = await response.json()
    console.log('令牌生成结果:', result)
    
    // 处理两种可能的API响应格式
    if (result && result.code === 0 && result.data && result.data.token) {
      // 标准API格式: {code: 0, data: {token: 'xxx'}}
      telegramToken.value = result.data.token
      console.log('成功设置令牌(标准格式):', telegramToken.value)
    } else if (result && result.token) {
      // 简化API格式: {token: 'xxx'}
      telegramToken.value = result.token
      console.log('成功设置令牌(简化格式):', telegramToken.value)
    } else {
      console.error('生成令牌失败:', result)
      alert(result.message || '生成令牌失败，请重试')
    }
  } catch (error) {
    console.error('生成令牌失败:', error)
    alert('生成令牌失败，请重试')
  } finally {
    telegramTokenLoading.value = false
  }
}

// 复制Telegram绑定令牌
const copyTelegramToken = () => {
  navigator.clipboard.writeText(telegramToken.value)
    .then(() => {
      alert('令牌已复制到剪贴板')
    })
    .catch(err => {
      console.error('复制失败:', err)
      alert('复制失败，请手动复制')
    })
}

// 检查Telegram绑定状态
const checkTelegramConnection = async () => {
  telegramLinking.value = true
  try {
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase
    const response = await fetch(`${baseUrl}/v1/user/telegram/status/?site=default`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    const result = await response.json()
    if (result && result.code === 0 && result.data) {
      if (result.data.connected) {
        telegramConnected.value = true
        telegramUsername.value = result.data.username || '未知用户'
        emit('update:showModal', false)
        emit('statusChanged', true)
        alert('Telegram绑定成功！')
      } else {
        telegramConnected.value = false
        emit('statusChanged', false)
        alert('尚未绑定Telegram，请完成绑定流程')
      }
    } else {
      console.error('检查绑定状态失败:', result)
      alert(result.message || '检查绑定状态失败，请重试')
    }
  } catch (error) {
    console.error('检查绑定状态失败:', error)
    alert('检查绑定状态失败，请重试')
  } finally {
    telegramLinking.value = false
  }
}

// 解除Telegram绑定
const disconnectTelegram = async () => {
  if (!confirm('确定要解除Telegram绑定吗？解除后将不再接收通知。')) {
    return
  }
  
  try {
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase
    const response = await fetch(`${baseUrl}/v1/user/telegram/disconnect/?site=default`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    const result = await response.json()
    if (result && result.code === 0) {
      telegramConnected.value = false
      telegramUsername.value = ''
      telegramToken.value = ''
      emit('statusChanged', false)
      alert('已成功解除Telegram绑定')
    } else {
      console.error('解除绑定失败:', result)
      alert(result.message || '解除绑定失败，请重试')
    }
  } catch (error) {
    console.error('解除绑定失败:', error)
    alert('解除绑定失败，请重试')
  }
}

// 检查Telegram绑定状态
const checkInitialTelegramStatus = async () => {
  if (!authStore.isAuthenticated) return
  
  try {
    const runtimeConfig = useRuntimeConfig()
    const baseUrl = runtimeConfig.public.apiBase
    const response = await fetch(`${baseUrl}/v1/user/telegram/status/?site=default`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    })
    
    const result = await response.json()
    if (result && result.code === 0 && result.data) {
      telegramConnected.value = result.data.connected || false
      telegramUsername.value = result.data.username || ''
      emit('statusChanged', telegramConnected.value)
    }
  } catch (error) {
    console.error('检查初始Telegram状态失败:', error)
  }
}

// 组件挂载时检查Telegram状态
onMounted(() => {
  if (authStore.isAuthenticated) {
    checkInitialTelegramStatus()
  }
})

// 暴露组件方法和状态
defineExpose({
  telegramConnected,
  telegramUsername,
  checkInitialTelegramStatus
})
</script>
