<script setup>
// 创建重定向从 /auth/login 到 /login
definePageMeta({
  middleware: () => {
    return navigateTo('/login')
  }
})
</script>

<template>
  <div>Redirecting to login page...</div>
</template> 