<template>
  <div>
    <!-- 根据路由决定是否使用默认布局 -->
    <template v-if="isWishlistSharePage">
      <NuxtPage />
    </template>
    <template v-else>
      <NuxtLayout name="default">
        <NuxtPage />
      </NuxtLayout>
    </template>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

// 判断当前是否是心愿单分享页面
const route = useRoute()
const isWishlistSharePage = computed(() => {
  return route.path.startsWith('/wishlist/share/')
})
</script>
