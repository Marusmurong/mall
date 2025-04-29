<template>
  <div class="card group">
    <!-- Product Image -->
    <div class="relative overflow-hidden aspect-square">
      <NuxtLink :to="`/products/${product.id}`">
        <img 
          :src="productImage" 
          :alt="product.name" 
          class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        >
      </NuxtLink>
      
      <!-- Quick Action Buttons -->
      <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100">
        <div class="flex space-x-2">
          <!-- Add to Cart -->
          <button 
            @click="addToCart"
            class="p-2 bg-white rounded-full shadow-md hover:bg-primary-50 transition-colors"
            :title="$t('common.add_to_cart')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </button>
          
          <!-- Add to Wishlist -->
          <button 
            @click="toggleWishlist"
            class="p-2 bg-white rounded-full shadow-md hover:bg-primary-50 transition-colors"
            :title="isInWishlist ? $t('common.remove_from_wishlist') : $t('common.add_to_wishlist')"
            :disabled="isCheckingWishlists"
            :class="{'opacity-50 cursor-wait': isCheckingWishlists}"
          >
            <svg v-if="isInWishlist" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-secondary-600" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>
          
          <!-- Quick View -->
          <NuxtLink 
            :to="`/products/${product.id}`"
            class="p-2 bg-white rounded-full shadow-md hover:bg-primary-50 transition-colors"
            :title="$t('common.view_details')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </NuxtLink>
        </div>
      </div>
      
      <!-- Tags -->
      <div class="absolute top-2 left-2 flex flex-col space-y-1">
        <span v-if="product.is_new" class="px-2 py-1 bg-green-500 text-white text-xs font-medium rounded">{{ $t('product.new') }}</span>
        <span v-if="product.is_hot" class="px-2 py-1 bg-red-500 text-white text-xs font-medium rounded">{{ $t('product.hot') }}</span>
        <span v-if="hasDiscount" class="px-2 py-1 bg-orange-500 text-white text-xs font-medium rounded">
          {{ discountPercentage }}% {{ $t('product.discount') }}
        </span>
      </div>
    </div>
    
    <!-- Product Info -->
    <div class="p-4">
      <!-- Category -->
      <div class="text-xs text-gray-500 mb-1">{{ product.category?.name || $t('product.uncategorized') }}</div>
      
      <!-- Product Name -->
      <h3 class="text-sm font-medium text-gray-900 mb-1 line-clamp-2">
        <NuxtLink :to="`/products/${product.id}`">{{ product.name }}</NuxtLink>
      </h3>
      
      <!-- Price -->
      <div class="flex items-center space-x-2">
        <span v-if="discountPrice" class="text-sm font-medium text-secondary-600">
          ${{ discountPrice }}
        </span>
        <span :class="[discountPrice ? 'text-xs text-gray-500 line-through' : 'text-sm font-medium text-gray-900']">
          ${{ product.price }}
        </span>
      </div>
      
      <!-- Rating -->
      <div v-if="product.rating" class="flex items-center mt-1">
        <div class="flex">
          <template v-for="i in 5" :key="i">
            <svg 
              :class="[i <= Math.round(product.rating) ? 'text-yellow-400' : 'text-gray-300']"
              xmlns="http://www.w3.org/2000/svg" 
              class="h-4 w-4" 
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </template>
        </div>
        <span class="text-xs text-gray-500 ml-1">{{ product.rating_count || 0 }}{{ $t('product.reviews_count') }}</span>
      </div>
    </div>
  </div>
  
  <!-- Wishlist Selection Modal -->
  <WishlistSelectModal 
    :show="showWishlistModal" 
    :product="props.product" 
    @close="showWishlistModal = false"
    @added="handleWishlistAdded"
  />
</template>

<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

// Import Wishlist Selection Modal Component
import WishlistSelectModal from './WishlistSelectModal.vue'

// Get State Management
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const authStore = useAuthStore()
const { t } = useI18n()

// Product Image
const productImage = computed(() => {
  // 如果有图片 URL，直接使用
  if (props.product.image) return props.product.image
  // 如果有图片数组，使用第一张图片
  if (props.product.images?.length > 0) {
    // 如果图片项是字符串，直接使用
    if (typeof props.product.images[0] === 'string') return props.product.images[0]
    // 如果图片项是对象，尝试获取 image 字段
    if (props.product.images[0].image) return props.product.images[0].image
  }
  // 如果没有图片，使用占位图
  return '/images/product-placeholder.jpg'
})

// Discount Price
const discountPrice = computed(() => {
  // If there is a discount_price field, use it directly
  if (props.product.discount_price) return props.product.discount_price
  // If original_price is different from price, it means there is a discount
  if (props.product.original_price && props.product.original_price !== props.product.price) {
    return props.product.price
  }
  return null
})

// Is in Wishlist
const isInWishlist = computed(() => {
  return wishlistStore.isInAnyWishlist(props.product.id)
})

// Has Discount
const hasDiscount = computed(() => {
  return !!discountPrice.value
})

// Discount Percentage
const discountPercentage = computed(() => {
  if (!hasDiscount.value) return 0
  
  // If there is original_price, use it to calculate the discount
  if (props.product.original_price) {
    return Math.round((1 - parseFloat(props.product.price) / parseFloat(props.product.original_price)) * 100)
  }
  
  // If there is discount_price, use it to calculate the discount
  if (props.product.discount_price) {
    return Math.round((1 - parseFloat(props.product.discount_price) / parseFloat(props.product.price)) * 100)
  }
  
  return 0
})

// Add to Cart
const addToCart = () => {
  cartStore.addToCart(props.product)
  
  // Show notification
  // A toast notification component can be used here
  alert(t('product.added_to_cart'))
}

// Show/Hide Wishlist Selection Modal
const showWishlistModal = ref(false)
// Checking Wishlist Status
const isCheckingWishlists = ref(false)

// Handle Wishlist Added Result
const handleWishlistAdded = (result) => {
  if (result.success) {
    alert(result.message || t('wishlist.item_added'))
  } else {
    alert(result.message || t('common.error'))
  }
}

// Add/Remove Wishlist
const toggleWishlist = async () => {
  // Check if user is logged in
  if (!authStore.isAuthenticated) {
    const confirmed = confirm(t('wishlist.login_required'))
    if (confirmed) {
      navigateTo(`/login?redirect=${encodeURIComponent(window.location.pathname)}`)
    }
    return
  }
  
  if (isInWishlist.value) {
    // Remove from wishlist
    // Need to get the product ID in the wishlist
    const wishlistItem = wishlistStore.getWishlistItems.find(item => item.product?.id === props.product.id)
    if (wishlistItem) {
      const result = await wishlistStore.removeFromWishlist(wishlistItem.id)
      if (result.success) {
        alert(t('wishlist.item_removed'))
      } else {
        alert(result.error || t('common.error'))
      }
    }
  } else {
    // Check if there is a wishlist, if not, create a default wishlist first
    isCheckingWishlists.value = true
    
    try {
      // First get the user's wishlist list
      await wishlistStore.fetchUserWishlists()
      
      // If the user does not have a wishlist, create and add the product directly
      if (wishlistStore.getUserWishlists.length === 0) {
        const confirmed = confirm(t('wishlist.create_default_confirm'))
        
        if (confirmed) {
          const createResult = await wishlistStore.createWishlist({
            name: t('wishlist.my_wishlist'),
            description: '',
            is_public: true
          })
          
          if (createResult.success && createResult.wishlist) {
            // Add the product directly after successful creation
            const addResult = await wishlistStore.addToWishlist(props.product, createResult.wishlist.id)
            
            if (addResult.success) {
              alert(t('wishlist.added_to_new_wishlist'))
            } else {
              alert(addResult.error || t('common.error'))
            }
          } else {
            alert(createResult.error || t('common.error'))
          }
        }
      } else {
        // If the user has a wishlist, show the selection modal
        showWishlistModal.value = true
      }
    } catch (error) {
      console.error('Failed to check wishlist:', error)
      alert(t('common.error'))
    } finally {
      isCheckingWishlists.value = false
    }
  }
}
</script>
