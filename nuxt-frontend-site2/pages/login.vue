<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {{ $t('login.title') }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          {{ $t('login.subtitle') }}
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">{{ $t('login.username') }}</label>
            <input id="username" v-model="username" name="username" type="text" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('login.username')" />
          </div>
          <div>
            <label for="password" class="sr-only">{{ $t('login.password') }}</label>
            <input id="password" v-model="password" name="password" type="password" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('login.password')" />
          </div>
        </div>


        
        <div v-if="error" class="text-red-500 text-sm text-center">
          {{ error }}
        </div>

        <div>
          <button type="submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            :disabled="isLoading">
            <span v-if="isLoading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-indigo-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ $t('login.submit') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRoute } from 'vue-router'

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const authStore = useAuthStore()
const router = useRouter()

// 使用 URL 参数预填充登录表单（仅用于测试）
const route = useRoute()
if (route.query && route.query.username) {
  username.value = route.query.username.toString()
}
if (route.query && route.query.password) {
  password.value = route.query.password.toString()
}

const handleLogin = async () => {
  // 清除之前的错误消息
  error.value = ''
  
  if (!username.value || !password.value) {
    error.value = 'Please enter username and password'
    return
  }

  try {
    isLoading.value = true
    error.value = ''
    
    console.log('Attempting login with:', { username: username.value, password: password.value })
    
    try {
      const result = await authStore.login(username.value, password.value)
      
      console.log('Login result:', result)
      
      if (result && result.success) {
        // 登录成功，跳转到首页
        console.log('Login successful, navigating to home page')
        navigateTo('/')
      } else {
        console.error('Login failed:', result?.error)
        error.value = result?.error?.message || 'Login failed. Please check your credentials.'
      }
    } catch (loginError) {
      console.error('Login exception:', loginError)
      error.value = `Login error: ${loginError.message || 'Unknown error'}`
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// 定义页面元数据，指定使用默认布局
definePageMeta({
  layout: 'default'
})
</script>

<i18n lang="json">
{
  "en": {
    "login": {
      "title": "Sign in to your account",
      "subtitle": "Or start your free trial",
      "username": "Username",
      "password": "Password",
      "submit": "Sign in"
    }
  },
  "zh": {
    "login": {
      "title": "登录您的账户",
      "subtitle": "或者开始免费试用",
      "username": "用户名",
      "password": "密码",
      "submit": "登录"
    }
  }
}
</i18n>
