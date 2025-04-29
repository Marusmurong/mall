<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Overlay -->
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="close"></div>
    <!-- Modal Content -->
    <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 p-8 border border-gray-200">
      <div class="flex items-center mb-6">
        <svg class="h-8 w-8 text-primary-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
        <h2 class="text-2xl font-bold text-gray-900">Add to Wishlist</h2>
      </div>
      <!-- 错误提示区域 -->
      <div v-if="errorMessage" class="mb-3 px-3 py-2 bg-red-50 text-red-600 rounded text-center text-sm font-medium">
        {{ errorMessage }}
      </div>
      <div class="mb-6">
        <div class="flex space-x-4 mb-4">
          <button :class="['px-4 py-2 rounded-lg font-medium', !isCreatingNew ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700']" @click="isCreatingNew = false">Select</button>
          <button :class="['px-4 py-2 rounded-lg font-medium', isCreatingNew ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700']" @click="isCreatingNew = true">Create New</button>
        </div>
        <transition name="fade" mode="out-in">
          <div v-if="!isCreatingNew" key="select">
            <div v-if="wishlists.length > 0" class="space-y-3 max-h-56 overflow-y-auto">
              <div v-for="wishlist in wishlists" :key="wishlist.id" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-primary-400 cursor-pointer transition group" @click="selectWishlist(wishlist.id)">
                <div>
                  <div class="font-semibold text-lg text-gray-800 flex items-center">
                    <span class="truncate max-w-xs">{{ wishlist.name }}</span>
                    <span v-if="wishlist.is_public" class="ml-2 px-2 py-0.5 text-xs rounded bg-green-100 text-green-700">Public</span>
                  </div>
                  <div class="text-sm text-gray-500 mt-1 truncate max-w-xs">{{ wishlist.description || 'No description' }}</div>
                </div>
                <div class="flex items-center">
                  <span class="text-xs text-gray-400 mr-2">{{ wishlist.items?.length || 0 }} items</span>
                </div>
              </div>
            </div>
            <div v-else class="text-center text-gray-400 py-8">
              <p class="mb-2">You don't have any wishlists yet.</p>
              <p>Click "Create New" to get started.</p>
            </div>
          </div>
          <div v-else key="create">
            <form @submit.prevent="createAndAddToWishlist" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Wishlist Name <span class="text-primary-600">*</span></label>
                <input v-model="newWishlistName" type="text" class="w-full p-2 border rounded-md focus:ring-primary-500 focus:border-primary-500" placeholder="Wishlist name" maxlength="255" required />
                <div class="text-xs text-gray-400 text-right">{{ newWishlistName.length }}/255</div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea v-model="newWishlistDescription" class="w-full p-2 border rounded-md focus:ring-primary-500 focus:border-primary-500" placeholder="Describe your wishlist..." rows="2" maxlength="512"></textarea>
                <div class="text-xs text-gray-400 text-right">{{ newWishlistDescription.length }}/512</div>
              </div>
              <div class="flex items-center">
                <input id="is-public" v-model="newWishlistIsPublic" type="checkbox" class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500" />
                <label for="is-public" class="ml-2 block text-sm text-gray-700">Public Wishlist</label>
              </div>
              <div class="flex flex-col space-y-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Product Notes</label>
                <textarea v-model="productNotes" class="w-full p-2 border rounded-md focus:ring-primary-500 focus:border-primary-500" placeholder="Add a note for this product..." rows="2" maxlength="512"></textarea>
                <div class="text-xs text-gray-400 text-right">{{ productNotes.length }}/512</div>
              </div>
              <button type="submit" class="w-full py-2 mt-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-60" :disabled="loading || !newWishlistName.trim()">{{ loading ? 'Processing...' : 'Create and Add' }}</button>
            </form>
          </div>
        </transition>
      </div>
      <div class="flex justify-end space-x-2 mt-2">
        <button @click="close" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">Cancel</button>
      </div>
      <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center z-10 rounded-2xl">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary-200 border-t-primary-600 mb-2"></div>
          <div class="text-primary-600 font-medium">Processing...</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useWishlistStore } from '../stores/wishlist'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'added'])
const wishlistStore = useWishlistStore()

const loading = ref(false)
const isCreatingNew = ref(false)
const newWishlistName = ref('Wishlist')
const newWishlistDescription = ref('')
const newWishlistIsPublic = ref(true)
const productNotes = ref('')

const wishlists = computed(() => wishlistStore.getUserWishlists || [])

const MAX_NOTES_LENGTH = 512
const MAX_TITLE_LENGTH = 255
const safeNotes = (notes) => notes && notes.length > MAX_NOTES_LENGTH ? notes.slice(0, MAX_NOTES_LENGTH) : notes
const safeTitle = (title) => title && title.length > MAX_TITLE_LENGTH ? title.slice(0, MAX_TITLE_LENGTH) : title
const truncateProductName = (name) => {
  if (!name) return 'Untitled Product'
  return safeTitle(name)
}

// 新增：错误提示状态
const errorMessage = ref('')

// --- 自动加载用户心愿单 ---
onMounted(async () => {
  if (props.show) {
    loading.value = true
    errorMessage.value = ''
    try {
      await wishlistStore.fetchUserWishlists()
    } catch (e) {
      errorMessage.value = '无法加载心愿单列表，请稍后重试'
    } finally {
      loading.value = false
    }
  }
})

watch(() => props.show, async (val) => {
  if (val) {
    loading.value = true
    errorMessage.value = ''
    try {
      await wishlistStore.fetchUserWishlists()
    } catch (e) {
      errorMessage.value = '无法加载心愿单列表，请稍后重试'
    } finally {
      loading.value = false
    }
  }
})

const selectWishlist = async (wishlistId) => {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await wishlistStore.addToWishlist({
      ...props.product,
      name: truncateProductName(props.product.name),
      title: truncateProductName(props.product.title || props.product.name),
      notes: safeNotes(productNotes.value || props.product.notes || '')
    }, wishlistId)
    if (result.success) {
      await wishlistStore.fetchUserWishlists()
      emit('added', { success: true, message: 'Added to wishlist' })
      close()
    } else {
      errorMessage.value = result.error || '添加失败'
    }
  } catch (error) {
    console.error('Failed to add to wishlist:', error)
    errorMessage.value = error.message || '添加失败'
  } finally {
    loading.value = false
  }
}

const createAndAddToWishlist = async () => {
  const name = newWishlistName.value.trim()
  if (!name) {
    errorMessage.value = '请输入心愿单名称'
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    const createResult = await wishlistStore.createWishlist({
      name: name,
      description: newWishlistDescription.value.trim(),
      is_public: newWishlistIsPublic.value
    })
    if (!createResult.success || !createResult.wishlist) {
      throw new Error(createResult.error || 'Failed to create wishlist')
    }
    const addResult = await wishlistStore.addToWishlist({
      ...props.product,
      name: truncateProductName(props.product.name),
      title: truncateProductName(props.product.title || props.product.name),
      notes: safeNotes(productNotes.value || props.product.notes || '')
    }, createResult.wishlist.id)
    if (addResult.success) {
      await wishlistStore.fetchUserWishlists()
      emit('added', { success: true, message: 'Added to new wishlist' })
      close()
    } else {
      errorMessage.value = addResult.error || '添加失败'
    }
  } catch (error) {
    console.error('Failed to create wishlist and add product:', error)
    errorMessage.value = error.message || '操作失败'
  } finally {
    loading.value = false
  }
}

const close = () => {
  isCreatingNew.value = false
  errorMessage.value = ''
  emit('close')
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
