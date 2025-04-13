<template>
  <div class="wishlist-add-modal">
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ product ? '添加到心愿单' : '创建心愿单' }}</h3>
          <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        
        <div class="modal-body">
          <!-- 加载状态 -->
          <div v-if="loading" class="loading-container">
            <div class="spinner"></div>
            <p>加载中...</p>
          </div>
          
          <!-- 错误信息 -->
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          
          <!-- 选择现有心愿单 -->
          <div v-if="product && wishlists.length > 0" class="existing-wishlists">
            <h4>选择心愿单</h4>
            <div class="wishlist-list">
              <div 
                v-for="wishlist in wishlists" 
                :key="wishlist.id" 
                class="wishlist-item"
                :class="{ 'selected': selectedWishlistId === wishlist.id }"
                @click="selectWishlist(wishlist.id)"
              >
                <div class="wishlist-name">{{ wishlist.name }}</div>
                <div class="wishlist-info">
                  <span>{{ wishlist.items?.length || 0 }}个商品</span>
                  <span>{{ wishlist.is_public ? '公开' : '私密' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 或者创建新的心愿单 -->
          <div class="create-new-wishlist">
            <div class="divider" v-if="product && wishlists.length > 0">
              <span>或者</span>
            </div>
            
            <h4>{{ product && wishlists.length > 0 ? '创建新的心愿单' : '创建心愿单' }}</h4>
            
            <div class="form-group">
              <label for="wishlist-name">名称</label>
              <input 
                type="text" 
                id="wishlist-name" 
                v-model="newWishlist.name" 
                placeholder="心愿单名称"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="wishlist-description">描述 (可选)</label>
              <textarea 
                id="wishlist-description" 
                v-model="newWishlist.description" 
                placeholder="心愿单描述"
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-group">
              <div class="checkbox-container">
                <input 
                  type="checkbox" 
                  id="wishlist-public" 
                  v-model="newWishlist.is_public"
                />
                <label for="wishlist-public">公开心愿单 (可被其他用户查看)</label>
              </div>
            </div>
          </div>
          
          <!-- 商品信息 (如果有) -->
          <div v-if="product" class="product-info">
            <div class="product-image">
              <img :src="product.image" :alt="product.name" />
            </div>
            <div class="product-details">
              <h4>{{ product.name }}</h4>
              <p class="product-price">{{ formatPrice(product.price) }}</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button 
            class="save-btn" 
            @click="saveToWishlist" 
            :disabled="loading || (!selectedWishlistId && !newWishlist.name)"
          >
            {{ product ? '添加到心愿单' : '创建心愿单' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useWishlistStore } from '../stores/wishlist'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'WishlistAddModal',
  props: {
    product: {
      type: Object,
      default: null
    },
    showModal: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      loading: false,
      error: null,
      selectedWishlistId: null,
      newWishlist: {
        name: '',
        description: '',
        is_public: true
      }
    }
  },
  
  computed: {
    wishlists() {
      const wishlistStore = useWishlistStore()
      return wishlistStore.getUserWishlists
    }
  },
  
  watch: {
    showModal(newVal) {
      if (newVal) {
        this.fetchWishlists()
      }
    }
  },
  
  methods: {
    async fetchWishlists() {
      const authStore = useAuthStore()
      if (!authStore.isAuthenticated) {
        this.$emit('show-auth-modal')
        this.$emit('close')
        return
      }
      
      this.loading = true
      this.error = null
      
      try {
        const wishlistStore = useWishlistStore()
        await wishlistStore.fetchUserWishlists()
        
        // 如果有心愿单，默认选中第一个
        if (this.wishlists.length > 0) {
          this.selectedWishlistId = this.wishlists[0].id
        }
      } catch (error) {
        this.error = '获取心愿单失败，请稍后再试'
        console.error('获取心愿单失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    selectWishlist(wishlistId) {
      this.selectedWishlistId = wishlistId
    },
    
    async saveToWishlist() {
      const authStore = useAuthStore()
      if (!authStore.isAuthenticated) {
        this.$emit('show-auth-modal')
        this.$emit('close')
        return
      }
      
      this.loading = true
      this.error = null
      
      try {
        const wishlistStore = useWishlistStore()
        
        // 如果是创建新心愿单
        if (!this.selectedWishlistId) {
          const result = await wishlistStore.createWishlist(this.newWishlist)
          
          if (!result.success) {
            this.error = result.error || '创建心愿单失败'
            return
          }
          
          // 如果有商品，添加到新创建的心愿单
          if (this.product) {
            const addResult = await wishlistStore.addToWishlist(this.product, result.wishlist.id)
            
            if (!addResult.success) {
              this.error = addResult.error || '添加商品到心愿单失败'
              return
            }
          }
          
          this.$emit('success', {
            action: 'create',
            wishlistId: result.wishlist.id,
            wishlistName: result.wishlist.name
          })
        } 
        // 添加商品到现有心愿单
        else if (this.product) {
          const result = await wishlistStore.addToWishlist(this.product, this.selectedWishlistId)
          
          if (!result.success) {
            this.error = result.error || '添加商品到心愿单失败'
            return
          }
          
          const wishlist = this.wishlists.find(w => w.id === this.selectedWishlistId)
          
          this.$emit('success', {
            action: 'add',
            wishlistId: this.selectedWishlistId,
            wishlistName: wishlist ? wishlist.name : '心愿单'
          })
        }
        
        this.closeModal()
      } catch (error) {
        this.error = '操作失败，请稍后再试'
        console.error('心愿单操作失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    closeModal() {
      // 重置表单
      this.selectedWishlistId = null
      this.newWishlist = {
        name: '',
        description: '',
        is_public: true
      }
      this.error = null
      
      this.$emit('close')
    },
    
    formatPrice(price) {
      return `¥${parseFloat(price).toFixed(2)}`
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn, .save-btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  color: #333;
}

.save-btn {
  background-color: #1976d2;
  border: 1px solid #1976d2;
  color: white;
}

.save-btn:disabled {
  background-color: #cccccc;
  border-color: #cccccc;
  cursor: not-allowed;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #1976d2;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.wishlist-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.wishlist-item {
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.wishlist-item:hover {
  background-color: #f5f5f5;
}

.wishlist-item.selected {
  border-color: #1976d2;
  background-color: #e3f2fd;
}

.wishlist-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.wishlist-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #666;
}

.divider {
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: "";
  flex: 1;
  border-bottom: 1px solid #eee;
}

.divider span {
  padding: 0 10px;
  color: #999;
  font-size: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.checkbox-container {
  display: flex;
  align-items: center;
}

.checkbox-container input {
  margin-right: 8px;
}

.product-info {
  display: flex;
  align-items: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.product-image {
  width: 80px;
  height: 80px;
  margin-right: 16px;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.product-details h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.product-price {
  color: #d32f2f;
  font-weight: 500;
  margin: 0;
}
</style>
