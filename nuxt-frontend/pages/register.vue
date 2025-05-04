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
        <div class="rounded-md shadow-sm space-y-3">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('auth.username') }}
            </label>
            <input id="username" v-model="username" name="username" type="text" required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.username')" />
          </div>
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('auth.email') }}
            </label>
            <input id="email" v-model="email" name="email" type="email" required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.email')" />
          </div>
          <div>
            <label for="invite-code" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('auth.invite_code') }}
            </label>
            <input id="invite-code" v-model="inviteCode" name="invite-code" type="text" required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.inviteCode')" />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('auth.password') }}
            </label>
            <input id="password" v-model="password" name="password" type="password" required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.password')" />
          </div>
          <div>
            <label for="confirm-password" class="block text-sm font-medium text-gray-700 mb-1">
              {{ $t('auth.confirm_password') }}
            </label>
            <input id="confirm-password" v-model="confirmPassword" name="confirm-password" type="password" required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-400 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="$t('register.confirmPassword')" />
          </div>
        </div>

        <div v-if="error" class="text-red-500 text-sm text-center p-2 bg-red-50 rounded-md">
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
    console.error('注册失败: 两次输入的密码不一致')
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
      // 显示更详细的错误信息
      if (result?.error?.message) {
        error.value = result.error.message
      } else if (typeof result?.error === 'string' && result.error.includes('Bad Request')) {
        // 处理API返回的错误信息，解析JSON字符串
        try {
          const errorJson = result.error.match(/\{.*\}/)?.[0];
          if (errorJson) {
            const parsedError = JSON.parse(errorJson);
            if (parsedError.message && typeof parsedError.message === 'object') {
              // 构建错误消息
              const errorMessages = [];
              for (const field in parsedError.message) {
                errorMessages.push(`${field}: ${parsedError.message[field]}`);
              }
              error.value = errorMessages.join('\n');
            } else {
              error.value = parsedError.message || '注册失败';
            }
          } else {
            error.value = result.error;
          }
        } catch (e) {
          console.error('解析错误信息失败:', e);
          error.value = result.error;
        }
      } else if (result?.error?.details) {
        // 处理字段特定的错误
        const details = result.error.details
        if (typeof details === 'object') {
          // 如果有字段特定错误，构建错误消息
          const fieldErrors = []
          for (const field in details) {
            if (Array.isArray(details[field])) {
              fieldErrors.push(`${field}: ${details[field].join(', ')}`)
            } else {
              fieldErrors.push(`${field}: ${details[field]}`)
            }
          }
          if (fieldErrors.length > 0) {
            error.value = fieldErrors.join('\n')
          } else {
            error.value = '注册失败，请检查您的信息'
          }
        } else {
          error.value = '注册失败，请检查您的信息'
        }
      } else {
        error.value = '注册失败，请检查您的信息'
      }
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
