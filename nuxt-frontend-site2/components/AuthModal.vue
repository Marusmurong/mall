<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- 背景遮罩 -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="$emit('close')"></div>

      <!-- 模态框内容 -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <!-- 标签切换 -->
          <div class="flex border-b mb-4">
            <button 
              @click="activeTab = 'login'" 
              class="py-2 px-4 font-medium" 
              :class="activeTab === 'login' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500'"
            >
              登录
            </button>
            <button 
              @click="activeTab = 'register'" 
              class="py-2 px-4 font-medium" 
              :class="activeTab === 'register' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-500'"
            >
              注册
            </button>
          </div>

          <!-- 登录表单 -->
          <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700">用户名</label>
              <input 
                id="username" 
                v-model="loginForm.username" 
                type="text" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700">密码</label>
              <input 
                id="password" 
                v-model="loginForm.password" 
                type="password" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
            <div v-if="loginError" class="text-red-500 text-sm">
              {{ loginError }}
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <input id="remember-me" type="checkbox" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                <label for="remember-me" class="ml-2 block text-sm text-gray-900">
                  记住我
                </label>
              </div>
              <div class="text-sm">
                <a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">
                  忘记密码?
                </a>
              </div>
            </div>
            <div>
              <button 
                type="submit" 
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                :disabled="isLoading"
              >
                <span v-if="isLoading" class="mr-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                登录
              </button>
            </div>
          </form>

          <!-- 注册表单 -->
          <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="space-y-4">
            <div>
              <label for="reg-username" class="block text-sm font-medium text-gray-700">用户名</label>
              <input 
                id="reg-username" 
                v-model="registerForm.username" 
                type="text" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
            <div>
              <label for="reg-email" class="block text-sm font-medium text-gray-700">邮箱</label>
              <input 
                id="reg-email" 
                v-model="registerForm.email" 
                type="email" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
            <div>
              <label for="reg-invite-code" class="block text-sm font-medium text-gray-700">邀请码</label>
              <input 
                id="reg-invite-code" 
                v-model="registerForm.inviteCode" 
                type="text" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="请输入邀请码"
              />
              <p class="mt-1 text-xs text-gray-500">注册需要邀请码，请联系已注册用户获取</p>
            </div>
            <div>
              <label for="reg-password" class="block text-sm font-medium text-gray-700">密码</label>
              <input 
                id="reg-password" 
                v-model="registerForm.password" 
                type="password" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
            <div>
              <label for="reg-confirm-password" class="block text-sm font-medium text-gray-700">确认密码</label>
              <input 
                id="reg-confirm-password" 
                v-model="registerForm.confirmPassword" 
                type="password" 
                required 
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
            <div v-if="registerError" class="text-red-500 text-sm">
              {{ registerError }}
            </div>
            <div>
              <button 
                type="submit" 
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                :disabled="isLoading"
              >
                <span v-if="isLoading" class="mr-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </span>
                注册
              </button>
            </div>
          </form>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button" 
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            @click="$emit('close')"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { useAuthStore } from '~/stores/auth'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'login-success', 'register-success'])

const activeTab = ref('login')
const isLoading = ref(false)
const loginError = ref('')
const registerError = ref('')
const authStore = useAuthStore()

// 登录表单数据
const loginForm = ref({
  username: '',
  password: ''
})

// 注册表单数据
const registerForm = ref({
  username: '',
  email: '',
  inviteCode: '',
  password: '',
  confirmPassword: ''
})

// 处理登录
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    loginError.value = '请输入用户名和密码'
    return
  }

  try {
    isLoading.value = true
    loginError.value = ''
    
    console.log('尝试登录:', { username: loginForm.value.username })
    
    const result = await authStore.login(loginForm.value.username, loginForm.value.password)
    
    if (result && result.success) {
      // 登录成功
      console.log('登录成功')
      emit('login-success')
      emit('close')
    } else {
      console.error('登录失败:', result?.error)
      loginError.value = result?.error?.message || '登录失败，请检查您的凭据'
    }
  } catch (error) {
    console.error('登录过程中出错:', error)
    loginError.value = '登录过程中出错，请稍后再试'
  } finally {
    isLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  // 验证密码
  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerError.value = '两次输入的密码不一致'
    return
  }

  // 验证邀请码
  if (!registerForm.value.inviteCode) {
    registerError.value = '请输入邀请码'
    return
  }

  try {
    isLoading.value = true
    registerError.value = ''
    
    console.log('尝试注册:', { 
      username: registerForm.value.username, 
      email: registerForm.value.email,
      inviteCode: registerForm.value.inviteCode 
    })
    
    const result = await authStore.register(
      registerForm.value.username, 
      registerForm.value.email, 
      registerForm.value.password,
      registerForm.value.inviteCode
    )
    
    if (result && result.success) {
      // 注册成功
      console.log('注册成功')
      emit('register-success')
      // 可以自动切换到登录标签
      activeTab.value = 'login'
      // 或者直接关闭模态框
      // emit('close')
    } else {
      console.error('注册失败:', result?.error)
      registerError.value = result?.error?.message || '注册失败，请稍后再试'
    }
  } catch (error) {
    console.error('注册过程中出错:', error)
    registerError.value = '注册过程中出错，请稍后再试'
  } finally {
    isLoading.value = false
  }
}
</script>
