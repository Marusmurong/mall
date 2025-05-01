<template>
  <!-- Independent page without website header and footer -->
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-2">
    <div class="max-w-md mx-auto px-2">
      <NuxtLayout name="empty">
      
      <!-- Loading state -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <div class="relative">
          <div class="animate-spin rounded-full h-16 w-16 border-4 border-gray-200"></div>
          <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-primary-500 absolute top-0 left-0"></div>
        </div>
        <p class="mt-4 text-gray-600 animate-pulse">Loading wishlist...</p>
      </div>
      
      <!-- Wishlist details -->
      <div v-else-if="wishlist" class="bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-500 hover:shadow-2xl">
        <!-- Top decoration bar -->
        <div class="h-2 bg-gradient-to-r from-primary-400 via-primary-500 to-secondary-500"></div>
        
        <!-- Wishlist header - using light dreamy gradient -->
        <div class="bg-gradient-to-r from-blue-100 via-purple-100 to-pink-100 p-4 text-center">
          <!-- Title -->
          <h1 class="text-2xl font-bold text-gray-800 mb-1">{{ wishlist.name.includes('的心愿单') ? wishlist.name.replace('的心愿单', "'s Wishlist") : wishlist.name }}</h1>
          
          <!-- Description text -->
          <p v-if="wishlist.description" class="text-gray-600 text-sm italic mb-2">{{ wishlist.description }}</p>
        </div>
        
        <!-- Wishlist content -->
        <div class="p-8" ref="itemsSection">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl font-bold text-gray-900 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-2 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Wishlist
            </h2>
            
            <div class="flex items-center text-sm text-gray-500">
              <span v-if="wishlist.items && wishlist.items.length > 0" class="bg-primary-50 text-primary-700 px-3 py-1 rounded-full font-medium">
                {{ wishlist.items.length }} items
              </span>
            </div>
          </div>
          
          <!-- Empty state -->
          <div v-if="!wishlist.items || !wishlist.items.length" class="text-center py-16 bg-gray-50 rounded-2xl border border-gray-100 shadow-inner">
            <div class="w-24 h-24 mx-auto bg-white rounded-full shadow-md flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900">Wishlist is empty</h3>
            <p class="mt-2 text-gray-600 max-w-md mx-auto">This wishlist has no items yet. Please check back later.</p>
          </div>
          
          <!-- Product carousel -->
          <div v-else class="relative">
            <!-- Removed product index display, will move to product card -->
            
            
            <!-- Carousel -->
            <div class="relative overflow-hidden rounded-2xl shadow-lg">
              <!-- Added obvious left and right arrow buttons -->
              <button 
                v-if="wishlist.items.length > 1"
                @click="prevItem"
                class="absolute left-2 top-1/2 transform -translate-y-1/2 z-30 bg-white/80 rounded-full p-2 shadow-md hover:bg-white transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <button 
                v-if="wishlist.items.length > 1"
                @click="nextItem"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 z-30 bg-white/80 rounded-full p-2 shadow-md hover:bg-white transition-all duration-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <!-- Swipe indicators -->
              <div v-if="wishlist.items.length > 1" class="absolute bottom-2 left-0 right-0 z-20 flex justify-center space-x-2">
                <div 
                  v-for="(_, index) in wishlist.items" 
                  :key="index"
                  class="h-2 w-2 rounded-full transition-all duration-300"
                  :class="index === currentItemIndex ? 'bg-white scale-125' : 'bg-white/50'"
                ></div>
              </div>
              
              <!-- Removed hidden left/right click areas, using obvious buttons instead -->
              
              <!-- Product card -->
              <div 
                v-for="(item, index) in wishlist.items" 
                :key="item.id"
                v-show="index === currentItemIndex"
                class="bg-white rounded-2xl overflow-hidden shadow-lg transition-all duration-300 relative"
                :class="{'opacity-90 bg-gray-50': item.purchased}"
              >
                <!-- Fulfilled mark -->
                <div 
                  v-if="item.purchased" 
                  class="absolute top-0 right-0 z-30 w-full h-12 flex items-center justify-center bg-gradient-to-r from-green-500 to-green-600 text-white font-bold shadow-lg"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Fulfilled by {{ item.purchased_by || 'Anonymous' }}
                </div>
                
                <!-- Product image - portrait layout -->
                <div 
                  class="relative w-full overflow-hidden" 
                  style="height: 120vw; max-height: 500px; min-height: 400px; aspect-ratio: 5/6;"
                >
                  <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent z-10"></div>
                  <img 
                    v-if="item.image" 
                    :src="item.image" 
                    :alt="item.title" 
                    class="w-full h-full object-cover object-center transition-transform duration-700 hover:scale-110"
                  >
                  <div v-else class="w-full h-full flex items-center justify-center bg-gray-100">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                  
                  <!-- Price tag - moved to top right -->
                  <div class="absolute top-2 right-2 bg-white rounded-full shadow-md px-3 py-1 z-10">
                    <div class="flex items-center">
                      <span class="text-base font-bold text-primary-600">{{ formatPrice(Number(item.price)) }}</span>
                      <span v-if="item.original_price && item.original_price !== item.price" class="text-xs text-gray-500 line-through ml-1">
                        {{ formatPrice(Number(item.original_price)) }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Product index display -->
                  <div 
                    v-if="wishlist.items.length > 1" 
                    class="absolute top-4 left-4 z-20 px-3 py-1 rounded-full shadow-md text-xs font-bold bg-gray-700/70 text-white"
                  >
                    {{ currentItemIndex + 1 }} / {{ wishlist.items.length }}
                  </div>
                  
                  <!-- Product title (overlaid on image) -->
                  <div class="absolute bottom-0 left-0 right-0 z-10 p-4 text-white">
                    <h3 class="text-lg font-bold line-clamp-2"><!-- Reduced font size, allowing two lines -->
                      {{ item.title }}
                    </h3>
                  </div>
                </div>
                
                <!-- Product info -->
                <div class="p-5">
                  <!-- Product description -->
                  <div v-if="item.description" class="mb-4">
                    <p class="text-gray-700 text-sm line-clamp-2">
                      {{ item.description }}
                    </p>
                  </div>
                  
                  <!-- Product attributes -->
                  <div class="flex items-center justify-between text-xs text-gray-500 mb-4">
                    <div class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2" />
                      </svg>
                      Added on {{ formatDate(item.added_at) }}
                    </div>
                    
                    <div class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                      {{ wishlist.owner_name }}'s wish
                    </div>
                  </div>
                  
                  <!-- Total amount and button area -->
                  <div v-if="!item.purchased" class="mt-4">
                    <!-- Total amount display - in a row -->
                    <div class="mb-3 flex items-center justify-between px-1">
                      <div class="text-xs text-gray-500">Total Amount:</div>
                      <div class="text-lg font-bold text-primary-600">{{ formatPrice(getTotalAmount()) }}</div>
                    </div>
                    
                    <button 
                      @click="purchaseDirectly"
                      class="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-bold py-3 px-4 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Purchase Now
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Error state -->
      <div v-else-if="error" class="bg-white rounded-2xl shadow-lg p-8 text-center">
        <div class="w-20 h-20 mx-auto bg-red-50 rounded-full flex items-center justify-center mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">Wishlist Not Found</h2>
        <p class="text-gray-600 mb-6">The wishlist you're looking for might have been removed or the link is incorrect.</p>
        <a href="/" class="inline-flex items-center text-primary-600 hover:text-primary-700">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Homepage
        </a>
      </div>
      
      <!-- Purchase modals -->
      <PurchaseModal 
        :show="showPurchaseModal" 
        :items="getUnpurchasedItems()"
        :total-amount="getUnpurchasedAmount()"
        :wishlist-id="wishlist?.id || ''"
        @close="closePurchaseModal" 
        @purchase="completePurchase"
      />
      
      <SuccessModal 
        :show="showSuccessModal" 
        :data="purchaseData"
        @close="closeSuccessModal"
      />
      
      <!-- Footer -->
      <div class="mt-6 text-center">
        <p class="text-xs text-gray-500">
          {{ new Date().getFullYear() }} CartiTop. All rights reserved.
        </p>
        <div class="mt-2">
          <a 
            href="/" 
            class="text-xs text-primary-600 hover:text-primary-700"
          >
            Visit CartiTop Website
          </a>
        </div>
      </div>
      </NuxtLayout>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRuntimeConfig } from 'nuxt/app'
import { useCurrency } from '~/composables/useCurrency'

// Get route and router
const route = useRoute()
const router = useRouter()
const { formatPrice } = useCurrency()

// Get state management
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()
const cartStore = useCartStore()

// State
const loading = ref(true)
const wishlist = ref(null)
const stats = ref(null)
const error = ref(null)
const showShareModal = ref(false)
const showPurchaseModal = ref(false)
const showSuccessModal = ref(false)
const selectedItem = ref(null)
const purchaseData = ref(null)
const currentItemIndex = ref(0) // Current carousel item index

// Touch swipe related state
const touchStartX = ref(0)
const touchEndX = ref(0)

// Fetch wishlist details
const fetchSharedWishlist = async () => {
  try {
    loading.value = true
    error.value = null
    
    await wishlistStore.fetchWishlistByShareCode(route.params.code)
    wishlist.value = wishlistStore.sharedWishlist
    
    // Record view
    if (wishlist.value) {
      recordView()
      fetchStats()
    }
  } catch (err) {
    console.error('Failed to fetch wishlist:', err)
    error.value = err.message || 'Failed to load wishlist'
  } finally {
    loading.value = false
  }
}

// Record view count
const recordView = async () => {
  try {
    const api = useApi()
    await api.wishlist.recordShareView(route.params.code)
  } catch (error) {
    console.error('Failed to record view:', error)
  }
}

// Get statistics
const fetchStats = async () => {
  try {
    const api = useApi()
    const response = await api.wishlist.getShareStats(route.params.code)
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// Get completed items count
const getCompletedItemsCount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items.filter(item => item.purchased).length
}

// Get payment completed count
const getPaymentCompletedCount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items.filter(item => item.payment_completed).length
}

// Get payment completed amount
const getPaymentCompletedAmount = () => {
  if (!wishlist.value?.items) return 0
  
  return wishlist.value.items
    .filter(item => item.purchased && item.payment_completed)
    .reduce((sum, item) => sum + Number(item.price || 0), 0)
}

// Get unpaid count
const getUnpaidCount = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return 0
  return wishlist.value.items.filter(item => !item.payment_completed).length
}

// Get unpaid amount
const getUnpaidAmount = () => {
  if (!wishlist.value?.items) return 0
  
  return wishlist.value.items
    .filter(item => item.purchased && !item.payment_completed)
    .reduce((sum, item) => sum + Number(item.price || 0), 0)
}

// Get total amount
const getTotalAmount = () => {
  if (!wishlist.value?.items) return 0
  
  return wishlist.value.items
    .reduce((sum, item) => sum + Number(item.price || 0), 0)
}

// Get unpurchased items
const getUnpurchasedItems = () => {
  if (!wishlist.value?.items) return []
  
  return wishlist.value.items.filter(item => !item.purchased)
}

// Get unpurchased amount
const getUnpurchasedAmount = () => {
  if (!wishlist.value?.items) return 0
  
  return wishlist.value.items
    .filter(item => !item.purchased)
    .reduce((sum, item) => sum + Number(item.price || 0), 0)
}

// Carousel control functions - previous item
const prevItem = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return
  if (currentItemIndex.value <= 0) {
    currentItemIndex.value = wishlist.value.items.length - 1
  } else {
    currentItemIndex.value--
  }
}

// Carousel control functions - next item
const nextItem = () => {
  if (!wishlist.value?.items || !wishlist.value.items.length) return
  if (currentItemIndex.value >= wishlist.value.items.length - 1) {
    currentItemIndex.value = 0
  } else {
    currentItemIndex.value++
  }
}

// Touch swipe handling functions
const handleTouchStart = (event) => {
  event.stopPropagation() // Prevent event bubbling
  touchStartX.value = event.touches[0].clientX
  console.log('Touch start:', touchStartX.value) // Add log
}

const handleTouchEnd = (event) => {
  event.stopPropagation() // Prevent event bubbling
  touchEndX.value = event.changedTouches[0].clientX
  console.log('Touch end:', touchEndX.value) // Add log
  handleSwipe()
}

const handleSwipe = () => {
  // Set minimum swipe distance to trigger change
  const minSwipeDistance = 30 // Reduce minimum swipe distance requirement
  const swipeDistance = touchEndX.value - touchStartX.value
  
  console.log('Swipe distance:', swipeDistance) // Add log for debugging
  
  if (swipeDistance > minSwipeDistance) {
    // Swipe right, show previous item
    prevItem()
  } else if (swipeDistance < -minSwipeDistance) {
    // Swipe left, show next item
    nextItem()
  }
}

// Add to cart
const addToCart = async (item) => {
  try {
    await cartStore.addToCart({
      product_id: item.product_id,
      quantity: 1,
      wishlist_item_id: item.id, // Add wishlist item ID to mark as purchase for someone else
      wishlist_id: wishlist.value.id,
      // Other necessary product information
    })
    alert('Added to cart')
  } catch (error) {
    console.error('Failed to add to cart:', error)
    alert('Failed to add, please try again')
  }
}

// Purchase directly
const purchaseDirectly = () => {
  // No longer select individual items, but pay for the entire wishlist
  selectedItem.value = null
  showPurchaseModal.value = true
}

// Close purchase modal
const closePurchaseModal = () => {
  showPurchaseModal.value = false
  selectedItem.value = null
}

// Complete purchase (after payment)
const completePurchase = async (data) => {
  try {
    // Close purchase modal
    showPurchaseModal.value = false
    
    // Store purchase data for success modal
    purchaseData.value = data
    
    // Build payment data - pay for the entire wishlist
    const paymentData = {
      wishlist_id: wishlist.value.id,
      buyer_name: data.buyerName,
      payment_method: data.paymentMethod,
      transaction_id: data.transactionId,
      is_full_wishlist: true // Mark as payment for the entire wishlist
    }
    
    // Add specific data for different payment methods
    if (data.paymentMethod === 'usdt') {
      paymentData.transaction_hash = data.transactionHash
    } else if (data.paymentMethod === 'credit_card') {
      paymentData.card_type = data.cardType || ''
      paymentData.last_four = data.lastFour || ''
    } else if (data.paymentMethod === 'paypal') {
      paymentData.paypal_order_id = data.transactionId
    } else if (data.paymentMethod === 'coinbase_commerce') {
      paymentData.charge_id = data.transactionId
    }
    
    // Mark the entire wishlist as purchased
    await wishlistStore.purchaseFullWishlist(paymentData)
    
    // Update local data - mark all unpurchased items as purchased
    wishlist.value.items.forEach((item, index) => {
      if (!item.purchased) {
        wishlist.value.items[index] = {
          ...item,
          purchased: true,
          purchased_by: data.buyerName,
          payment_completed: true
        }
      }
    })
    
    // Show success modal
    showSuccessModal.value = true
  } catch (error) {
    console.error('Purchase failed:', error)
    alert('Purchase failed, please try again')
  }
}

// Close success modal
const closeSuccessModal = () => {
  showSuccessModal.value = false
  purchaseData.value = null
}

// Get current page URL
const getCurrentUrl = () => {
  return window.location.href
}

// Copy current page URL
const copyCurrentUrl = () => {
  navigator.clipboard.writeText(getCurrentUrl())
    .then(() => {
      alert('Link copied to clipboard')
    })
    .catch(err => {
      console.error('Copy failed:', err)
      alert('Copy failed, please copy manually')
    })
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Fetch data on mount
onMounted(() => {
  fetchSharedWishlist()
})
</script>

<style scoped>
.stat-card {
  background-color: #f9fafb;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.stat-title {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.stat-desc {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}
</style>
