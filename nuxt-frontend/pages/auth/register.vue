<script setup>
// 创建重定向从 /auth/register 到 /register
definePageMeta({
  middleware: () => {
    return navigateTo('/register')
  }
})
</script>

<template>
  <div>Redirecting to register page...</div>
</template> 