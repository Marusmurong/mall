<template>
  <div>
    <!-- Decide whether to use default layout based on route -->
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

// Check if current page is a wishlist share page
const route = useRoute()
const isWishlistSharePage = computed(() => {
  return route.path.startsWith('/wishlist/share/')
})
</script>
