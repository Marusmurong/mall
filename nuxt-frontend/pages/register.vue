<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {{ $t('register.title') }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          {{ $t('register.subtitle') }}
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">{{ $t('register.username') }}</label>
            <input id="username" v-model="username" name="username" type="text" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.username')" />
          </div>
          <div>
            <label for="email" class="sr-only">{{ $t('register.email') }}</label>
            <input id="email" v-model="email" name="email" type="email" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.email')" />
          </div>
          <div>
            <label for="invite-code" class="sr-only">{{ $t('register.inviteCode') }}</label>
            <input id="invite-code" v-model="inviteCode" name="invite-code" type="text" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.inviteCode')" />
          </div>
          <div>
            <label for="password" class="sr-only">{{ $t('register.password') }}</label>
            <input id="password" v-model="password" name="password" type="password" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.password')" />
          </div>
          <div>
            <label for="confirm-password" class="sr-only">{{ $t('register.confirmPassword') }}</label>
            <input id="confirm-password" v-model="confirmPassword" name="confirm-password" type="password" required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.confirmPassword')" />
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
            {{ $t('register.submit') }}
          </button>
        </div>
        
        <div class="text-center">
          <p class="text-sm text-gray-600">
            {{ $t('register.alreadyHaveAccount') }}
            <NuxtLink to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
              {{ $t('register.signIn') }}
            </NuxtLink>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const inviteCode = ref('')
const error = ref('')
const isLoading = ref(false)
const authStore = useAuthStore()
const router = useRouter()

const handleRegister = async () => {
  // 清除之前的错误消息
  error.value = ''
  
  // 验证表单
  if (!username.value || !email.value || !password.value || !confirmPassword.value || !inviteCode.value) {
    error.value = '请填写所有必填字段'
    return
  }
  
  // 验证密码匹配
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  try {
    isLoading.value = true
    error.value = ''
    
    console.log('尝试注册:', { username: username.value, email: email.value, inviteCode: inviteCode.value })
    
    const result = await authStore.register(
      username.value, 
      email.value, 
      password.value,
      inviteCode.value
    )
    
    if (result && result.success) {
      // 注册成功，跳转到登录页
      console.log('注册成功，跳转到登录页')
      navigateTo('/login?registered=true&username=' + encodeURIComponent(username.value))
    } else {
      console.error('注册失败:', result?.error)
      error.value = result?.error?.message || '注册失败，请检查您的信息'
    }
  } catch (err) {
    console.error('注册过程中出错:', err)
    error.value = '注册过程中出错，请稍后再试'
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
    "register": {
      "title": "Create your account",
      "subtitle": "Join our community today",
      "username": "Username",
      "email": "Email address",
      "inviteCode": "Invitation code",
      "password": "Password",
      "confirmPassword": "Confirm password",
      "submit": "Sign up",
      "alreadyHaveAccount": "Already have an account?",
      "signIn": "Sign in"
    }
  },
  "zh": {
    "register": {
      "title": "创建您的账户",
      "subtitle": "立即加入我们的社区",
      "username": "用户名",
      "email": "电子邮箱",
      "inviteCode": "邀请码",
      "password": "密码",
      "confirmPassword": "确认密码",
      "submit": "注册",
      "alreadyHaveAccount": "已有账户？",
      "signIn": "登录"
    }
  }
}
</i18n>
