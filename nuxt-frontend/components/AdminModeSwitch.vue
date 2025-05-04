<template>
  <div v-if="isLoggedIn && isAdmin" class="admin-mode-switch p-2 bg-gray-100 bg-opacity-80 rounded-md flex items-center justify-between">
    <span class="text-sm text-gray-700 mr-2">Admin Mode</span>
    <button 
      @click="toggleAdminMode" 
      class="px-3 py-1 text-xs rounded-full" 
      :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
    >
      {{ adminModeEnabled ? 'Enabled' : 'Disabled' }}
    </button>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()

// 检查用户是否登录
const isLoggedIn = computed(() => authStore.isAuthenticated)

// 检查用户是否是管理员
const isAdmin = computed(() => {
  return authStore.user?.is_staff || authStore.user?.is_superuser || false
})

// 管理员模式状态
const adminModeEnabled = ref(false)

// 获取可能已有的管理员模式状态（从localStorage）
const initAdminMode = () => {
  if (typeof window !== 'undefined') {
    const savedMode = localStorage.getItem('adminModeEnabled')
    adminModeEnabled.value = savedMode === 'true'
  }
}

// 切换管理员模式
const toggleAdminMode = () => {
  adminModeEnabled.value = !adminModeEnabled.value
  
  // 保存到localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('adminModeEnabled', adminModeEnabled.value.toString())
  }
  
  // 发出事件通知其他组件
  emit('update:adminMode', adminModeEnabled.value)
}

// 组件挂载时初始化
onMounted(() => {
  initAdminMode()
})

// 定义输出事件
const emit = defineEmits(['update:adminMode'])

// 定义props
defineProps({
  position: {
    type: String,
    default: 'default'
  }
})
</script>

<style scoped>
.admin-mode-switch {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style> 