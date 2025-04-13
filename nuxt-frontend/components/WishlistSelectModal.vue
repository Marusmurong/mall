<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- 遮罩层 -->
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="close"></div>
    
    <!-- 弹窗内容 -->
    <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4 p-6">
      <h2 class="text-xl font-bold mb-4">添加到心愿单</h2>
      
      <!-- 选择现有心愿单 -->
      <div v-if="!isCreatingNew && wishlists.length > 0" class="mb-4">
        <h3 class="font-medium mb-2">选择心愿单</h3>
        <div class="space-y-2 max-h-60 overflow-y-auto">
          <div 
            v-for="wishlist in wishlists" 
            :key="wishlist.id"
            class="p-4 border rounded-lg cursor-pointer hover:bg-primary-50 transition-colors mb-2 flex justify-between items-center group relative"
            @click="selectWishlist(wishlist.id)"
          >
            <div class="flex-1">
              <div class="font-medium text-gray-800">{{ wishlist.name }}</div>
              <div class="text-sm text-gray-500 mt-1">{{ wishlist.items?.length || 0 }} 个商品</div>
            </div>
            <div class="opacity-0 group-hover:opacity-100 transition-opacity bg-primary-600 text-white rounded-full p-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <!-- 如果商品已在该心愿单中，显示标记 -->
            <div v-if="wishlist.items?.some(item => item.product?.id === props.product.id)" 
                 class="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
              已添加
            </div>
          </div>
        </div>
      </div>
      
      <!-- 创建新心愿单表单 -->
      <div v-if="isCreatingNew" class="mb-4">
        <h3 class="font-medium mb-2">创建新心愿单</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">名称</label>
            <input 
              v-model="newWishlistName" 
              type="text" 
              class="w-full p-2 border rounded-md focus:ring-primary-500 focus:border-primary-500"
              placeholder="我的心愿单"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">描述 (可选)</label>
            <textarea 
              v-model="newWishlistDescription" 
              class="w-full p-2 border rounded-md focus:ring-primary-500 focus:border-primary-500"
              placeholder="心愿单描述..."
              rows="2"
            ></textarea>
          </div>
          <div class="flex items-center">
            <input 
              id="is-public" 
              v-model="newWishlistIsPublic" 
              type="checkbox" 
              class="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label for="is-public" class="ml-2 block text-sm text-gray-700">公开心愿单</label>
          </div>
        </div>
      </div>
      
      <!-- 没有心愿单时的提示 -->
      <div v-if="!isCreatingNew && !loading && wishlists.length === 0" class="mb-4 text-center py-8">
        <div class="flex flex-col items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
          </svg>
          <p class="text-gray-700 font-medium">您还没有心愿单</p>
          <p class="text-gray-500 mt-1">点击下方按钮创建您的第一个心愿单</p>
          <button 
            @click="isCreatingNew = true" 
            class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors"
          >
            创建新心愿单
          </button>
        </div>
      </div>
      
      <!-- 加载中的提示 -->
      <div v-if="!isCreatingNew && loading && wishlists.length === 0" class="mb-4 text-center py-8">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary-200 border-t-primary-600 mb-3"></div>
          <p class="text-gray-500">正在加载心愿单...</p>
        </div>
      </div>
      
      <!-- 按钮区域 -->
      <div class="flex justify-between mt-6">
        <button 
          v-if="!isCreatingNew && wishlists.length > 0" 
          @click="isCreatingNew = true" 
          class="px-4 py-2 bg-primary-50 text-primary-700 rounded-md hover:bg-primary-100 transition-colors flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          创建新心愿单
        </button>
        <button 
          v-else-if="isCreatingNew && wishlists.length > 0" 
          @click="isCreatingNew = false" 
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回选择
        </button>
        <div class="flex-1"></div>
        
        <div class="flex">
          <button 
            @click="close" 
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors mr-2 flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            取消
          </button>
          <button 
            v-if="isCreatingNew" 
            @click="createAndAddToWishlist" 
            class="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors flex items-center"
            :disabled="loading || !newWishlistName.trim()"
            :class="{'opacity-70 cursor-not-allowed': loading || !newWishlistName.trim()}"
          >
            <svg v-if="!loading" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <svg v-else class="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '处理中...' : '创建并添加' }}
          </button>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center z-10">
        <div class="flex flex-col items-center">
          <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary-200 border-t-primary-600 mb-2"></div>
          <div class="text-primary-600 font-medium">处理中...</div>
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
const newWishlistName = ref('我的心愿单')
const newWishlistDescription = ref('')
const newWishlistIsPublic = ref(true)

// 获取用户的心愿单列表
const wishlists = computed(() => {
  const lists = wishlistStore.getUserWishlists
  console.log('当前心愿单列表:', lists, '数量:', lists.length)
  return lists
})

// 初始化时获取用户的心愿单
onMounted(async () => {
  loading.value = true
  await wishlistStore.fetchUserWishlists()
  loading.value = false
})

// 当弹窗显示时获取心愿单
watch(() => props.show, async (newVal) => {
  if (newVal) {
    loading.value = true
    try {
      // 获取用户的心愿单列表
      const result = await wishlistStore.fetchUserWishlists()
      console.log('获取心愿单列表:', result)
      
      // 检查是否有心愿单
      if (wishlistStore.getUserWishlists.length === 0) {
        // 如果没有心愿单，自动切换到创建新心愿单模式
        isCreatingNew.value = true
        newWishlistName.value = '我的心愿单'
        console.log('用户没有心愿单，切换到创建模式')
      } else {
        // 如果有心愿单，默认选择列表模式
        isCreatingNew.value = false
        console.log('用户已有心愿单，显示列表模式')
      }
    } catch (error) {
      console.error('获取心愿单列表失败:', error)
      // 出错时默认切换到创建模式
      isCreatingNew.value = true
    } finally {
      loading.value = false
    }
  } else {
    // 当关闭弹窗时重置状态
    isCreatingNew.value = false
    newWishlistName.value = '我的心愿单'
    newWishlistDescription.value = ''
    newWishlistIsPublic.value = true
  }
})

// 选择现有心愿单
const selectWishlist = async (wishlistId) => {
  loading.value = true
  try {
    // 检查商品是否已在该心愿单中
    const wishlist = wishlistStore.getUserWishlists.find(w => w.id === wishlistId)
    const isProductInWishlist = wishlist?.items?.some(item => item.product?.id === props.product.id)
    
    if (isProductInWishlist) {
      emit('added', { success: true, message: '商品已在该心愿单中' })
    } else {
      // 添加商品到选择的心愿单
      const result = await wishlistStore.addToWishlist(props.product, wishlistId)
      
      if (result.success) {
        // 重新获取心愿单列表，确保状态更新
        await wishlistStore.fetchUserWishlists()
        emit('added', { success: true, message: '已添加到心愿单' })
      } else {
        emit('added', { success: false, message: result.error || '添加失败' })
      }
    }
  } catch (error) {
    console.error('添加到心愿单失败:', error)
    emit('added', { success: false, message: error.message || '添加失败' })
  } finally {
    loading.value = false
    close()
  }
}

// 创建新心愿单并添加商品
const createAndAddToWishlist = async () => {
  if (!newWishlistName.value.trim()) {
    alert('请输入心愿单名称')
    return
  }
  
  loading.value = true
  try {
    // 创建新心愿单
    const createResult = await wishlistStore.createWishlist({
      name: newWishlistName.value.trim(),
      description: newWishlistDescription.value.trim(),
      is_public: newWishlistIsPublic.value
    })
    
    if (!createResult.success || !createResult.wishlist) {
      throw new Error(createResult.error || '创建心愿单失败')
    }
    
    console.log('心愿单创建成功:', createResult.wishlist)
    
    // 添加商品到新创建的心愿单
    const addResult = await wishlistStore.addToWishlist(props.product, createResult.wishlist.id)
    
    if (addResult.success) {
      // 重新获取心愿单列表，确保状态更新
      await wishlistStore.fetchUserWishlists()
      emit('added', { success: true, message: '已添加到新心愿单' })
    } else {
      emit('added', { success: false, message: addResult.error || '添加失败' })
    }
  } catch (error) {
    console.error('创建心愿单并添加商品失败:', error)
    emit('added', { success: false, message: error.message || '操作失败' })
  } finally {
    loading.value = false
    close()
  }
}

// 关闭弹窗
const close = () => {
  isCreatingNew.value = false
  emit('close')
}
</script>
