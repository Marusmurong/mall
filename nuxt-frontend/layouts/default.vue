<template>
  <div class="min-h-screen flex flex-col">
    <!-- Top navigation bar -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Left Logo and navigation links -->
          <div class="flex items-center">
            <!-- Mobile menu button -->
            <button 
              @click="mobileMenuOpen = !mobileMenuOpen" 
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:hidden"
              aria-expanded="false"
            >
              <span class="sr-only">打开主菜单</span>
              <!-- 菜单关闭图标 -->
              <svg 
                v-if="!mobileMenuOpen" 
                class="block h-6 w-6" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <!-- 菜单打开图标 -->
              <svg 
                v-else 
                class="block h-6 w-6" 
                xmlns="http://www.w3.org/2000/svg" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor" 
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="flex-shrink-0 flex items-center relative">
              <!-- Website LOGO -->
              <NuxtLink to="/" class="flex items-center">
                <img v-if="siteLogo" :src="siteLogo" alt="Cartitop Logo" class="h-8 w-auto" />
                <span v-else class="text-2xl font-bold text-primary-600">Cartitop</span>
              </NuxtLink>
              
              <!-- Admin mode switch component -->
              <AdminModeSwitch @update:adminMode="adminModeEnabled = $event" />
              
              <!-- LOGO upload button -->
              <div v-if="isAdmin && adminModeEnabled" class="absolute top-full left-0 mt-1 bg-white shadow-md rounded-md p-2 z-50">
                <button 
                  @click="showLogoUpload = true"
                  class="text-xs px-2 py-1 bg-blue-500 text-white rounded flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {{ $t('common.change_logo') }}
                </button>
              </div>
              
              <!-- LOGO upload modal -->
              <div v-if="showLogoUpload" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
                  <h3 class="text-lg font-bold mb-4">{{ $t('common.upload_site_logo') }}</h3>
                  
                  <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('common.select_image') }}</label>
                    <input 
                      type="file" 
                      accept="image/*" 
                      @change="handleLogoFileChange"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                  </div>
                  
                  <!-- Preview -->
                  <div v-if="logoPreview" class="mb-4 p-4 border border-gray-200 rounded-md">
                    <p class="text-sm text-gray-500 mb-2">{{ $t('common.preview') }}:</p>
                    <img :src="logoPreview" alt="Logo Preview" class="h-12 w-auto mx-auto">
                  </div>
                  
                  <div class="flex justify-end space-x-2">
                    <button 
                      @click="showLogoUpload = false" 
                      class="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700"
                    >
                      {{ $t('common.cancel') }}
                    </button>
                    <button 
                      @click="saveLogo"
                      class="px-4 py-2 bg-primary-600 text-white rounded-md text-sm"
                      :disabled="!logoFile || isUploading"
                    >
                      {{ isUploading ? $t('common.uploading') : $t('common.save') }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <nav class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <NuxtLink to="/" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                {{ $t('common.home') }}
              </NuxtLink>
              <NuxtLink to="/categories" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                {{ $t('common.categories') }}
              </NuxtLink>
              <NuxtLink to="/wishlist" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300">
                {{ $t('common.wishlist') }}
              </NuxtLink>
            </nav>
          </div>
          
          <!-- Right user menu and shopping cart -->
          <div class="flex items-center">
            <!-- Search icon for mobile -->
            <button @click="showMobileSearch = !showMobileSearch" class="md:hidden p-2 text-gray-500 hover:text-gray-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            
            <!-- Search box -->
            <div class="hidden md:block">
              <div class="relative">
                <input type="text" :placeholder="$t('common.search_products')" class="input w-64" />
              </div>
            </div>
            
            <!-- Heart icon -->
            <NuxtLink to="/wishlist" class="ml-4 p-2 text-gray-500 hover:text-gray-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </NuxtLink>
            
            <!-- Shopping cart icon -->
            <NuxtLink to="/cart" class="ml-4 p-2 text-gray-500 hover:text-gray-700">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </NuxtLink>
            
            <!-- User menu -->
            <div class="ml-4 relative flex-shrink-0" ref="userMenuContainer">
              <!-- Show login button when not logged in -->
              <button v-if="!isLoggedIn" @click="showAuthModal = true" class="flex items-center text-sm rounded-full focus:outline-none">
                <span class="sr-only">{{ $t('common.user_login') }}</span>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </button>
              
              <!-- Show user info and logout button when logged in -->
              <div v-else class="flex items-center">
                <span class="text-sm text-gray-700 mr-2">{{ $t('common.greeting') }}, {{ authStore.user?.username || $t('common.user') }}</span>
                <button @click="logout" class="text-sm text-red-500 hover:text-red-700">{{ $t('common.logout') }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Mobile search bar -->
      <div v-if="showMobileSearch" class="sm:hidden px-4 pb-3">
        <div class="relative">
          <input type="text" :placeholder="$t('common.search_products')" class="input w-full py-2" />
          <button @click="showMobileSearch = false" class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Mobile navigation menu -->
      <div 
        v-show="mobileMenuOpen" 
        class="sm:hidden bg-white"
        x-transition:enter="transition ease-out duration-100"
        x-transition:enter-start="transform opacity-0 scale-95"
        x-transition:enter-end="transform opacity-100 scale-100"
        x-transition:leave="transition ease-in duration-75"
        x-transition:leave-start="transform opacity-100 scale-100"
        x-transition:leave-end="transform opacity-0 scale-95"
      >
        <div class="pt-2 pb-3 space-y-1 border-t border-gray-200">
          <NuxtLink 
            to="/" 
            class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800"
            @click="mobileMenuOpen = false"
          >
            {{ $t('common.home') }}
          </NuxtLink>
          <NuxtLink 
            to="/categories" 
            class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800"
            @click="mobileMenuOpen = false"
          >
            {{ $t('common.categories') }}
          </NuxtLink>
          <NuxtLink 
            to="/wishlist" 
            class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800"
            @click="mobileMenuOpen = false"
          >
            {{ $t('common.wishlist') }}
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Main content area -->
    <main class="flex-grow">
      <slot />
    </main>

    <!-- Footer -->
    <AppFooter />
    
    <!-- Login/Registration modal -->
    <AuthModal 
      :show="showAuthModal" 
      @close="showAuthModal = false" 
      @login-success="handleLoginSuccess" 
      @register-success="handleRegisterSuccess" 
    />
  </div>
</template>

<script setup>
// Default layout component
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '~/stores/auth'
import AuthModal from '~/components/AuthModal.vue'
import AppFooter from '~/components/AppFooter.vue'
import AdminModeSwitch from '~/components/AdminModeSwitch.vue'

// Use auth store
const authStore = useAuthStore()

// Control login modal display
const showAuthModal = ref(false)

// Website LOGO related state
const siteLogo = ref('')
const showLogoUpload = ref(false)
const logoFile = ref(null)
const logoPreview = ref('')
const isUploading = ref(false)

// Admin mode (temporary feature in development environment)
const adminModeEnabled = ref(false)

// Use computed property to get login status
const isLoggedIn = computed(() => authStore.isAuthenticated)

// Check if current user is admin
const isAdmin = computed(() => {
  return authStore.user?.is_staff || authStore.user?.is_superuser || false
})

// Login success handler
const handleLoginSuccess = () => {
  // Close modal after successful login
  showAuthModal.value = false
  // Can add other logic here, such as showing welcome message
}

// Register success handler 
const handleRegisterSuccess = () => {
  // Close modal after successful registration
  showAuthModal.value = false
}

// Logout handler
const logout = () => {
  authStore.logout()
}

// LOGO file change handler
const handleLogoFileChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  logoFile.value = file
  
  // Generate preview
  const reader = new FileReader()
  reader.onload = (e) => {
    logoPreview.value = e.target.result
  }
  reader.readAsDataURL(file)
}

// Save logo
const saveLogo = async () => {
  if (!logoFile.value) return
  
  isUploading.value = true
  
  try {
    // Here would be the code to upload the logo to the server
    // For now, we'll just simulate it
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Set the logo (in a real app, this would be the URL returned from the server)
    siteLogo.value = logoPreview.value
    
    // Close the upload modal
    showLogoUpload.value = false
    
    // Reset state
    logoFile.value = null
    logoPreview.value = ''
  } catch (error) {
    console.error('Failed to upload logo:', error)
  } finally {
    isUploading.value = false
  }
}

// Load initial logo
onMounted(() => {
  // Here you would load the logo from the server or localStorage
  const savedLogo = localStorage.getItem('siteLogo')
  if (savedLogo) {
    siteLogo.value = savedLogo
  }
})

// Save logo to localStorage when it changes
watch(siteLogo, (newLogo) => {
  if (newLogo) {
    localStorage.setItem('siteLogo', newLogo)
  } else {
    localStorage.removeItem('siteLogo')
  }
})

// 移动端菜单状态
const mobileMenuOpen = ref(false)
const showMobileSearch = ref(false)
</script>

<style scoped>
/* 添加移动菜单的过渡动画 */
.transition {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style>
