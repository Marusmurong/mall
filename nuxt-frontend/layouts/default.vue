<template>
  <div class="min-h-screen flex flex-col">
    <!-- Top navigation bar -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <!-- Left Logo and navigation links -->
          <div class="flex">
            <div class="flex-shrink-0 flex items-center relative">
              <!-- Website LOGO -->
              <NuxtLink to="/" class="flex items-center">
                <img v-if="siteLogo" :src="siteLogo" alt="Mall Logo" class="h-8 w-auto" />
                <span v-else class="text-2xl font-bold text-primary-600">Mall</span>
              </NuxtLink>
              
              <!-- Admin mode switch (only shown in development) -->
              <div v-if="isDev" class="absolute -top-4 -right-4 z-10">
                <button 
                  @click="adminModeEnabled = !adminModeEnabled" 
                  class="px-2 py-0.5 text-xs rounded-full" 
                  :class="adminModeEnabled ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-700'"
                >
                  {{ adminModeEnabled ? $t('common.admin') : $t('common.normal') }}
                </button>
              </div>
              
              <!-- LOGO upload button -->
              <div v-if="adminModeEnabled" class="absolute top-full left-0 mt-1 bg-white shadow-md rounded-md p-2 z-50">
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
      
      <!-- Mobile navigation menu -->
      <div class="sm:hidden">
        <div class="pt-2 pb-3 space-y-1">
          <NuxtLink to="/" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
            {{ $t('common.home') }}
          </NuxtLink>
          <NuxtLink to="/categories" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
            {{ $t('common.categories') }}
          </NuxtLink>
          <NuxtLink to="/wishlist" class="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-800">
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
    <footer class="bg-gray-800 text-white">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- Company information -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.about_us') }}</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/about/company" class="text-gray-300 hover:text-white">{{ $t('footer.company_profile') }}</NuxtLink></li>
              <li><NuxtLink to="/info/about/contact" class="text-gray-300 hover:text-white">{{ $t('footer.contact_us') }}</NuxtLink></li>
              <li><NuxtLink to="/info/about/join" class="text-gray-300 hover:text-white">{{ $t('footer.join_us') }}</NuxtLink></li>
            </ul>
          </div>
          
          <!-- Shopping guide -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.shopping_guide') }}</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/shopping/process" class="text-gray-300 hover:text-white">{{ $t('footer.shopping_process') }}</NuxtLink></li>
              <li><NuxtLink to="/info/shopping/payment" class="text-gray-300 hover:text-white">{{ $t('footer.payment_methods') }}</NuxtLink></li>
              <li><NuxtLink to="/info/shopping/delivery" class="text-gray-300 hover:text-white">{{ $t('footer.delivery_methods') }}</NuxtLink></li>
            </ul>
          </div>
          
          <!-- After-sales service -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.after_sales') }}</h3>
            <ul class="space-y-2">
              <li><NuxtLink to="/info/service/return" class="text-gray-300 hover:text-white">{{ $t('footer.return_policy') }}</NuxtLink></li>
              <li><NuxtLink to="/info/service/warranty" class="text-gray-300 hover:text-white">{{ $t('footer.warranty_terms') }}</NuxtLink></li>
              <li><NuxtLink to="/info/service/faq" class="text-gray-300 hover:text-white">{{ $t('footer.faq') }}</NuxtLink></li>
            </ul>
          </div>
          
          <!-- Contact information -->
          <div>
            <h3 class="text-lg font-semibold mb-4">{{ $t('footer.contact_info') }}</h3>
            <ul class="space-y-2">
              <li class="flex items-center text-gray-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                400-123-4567
              </li>
              <li class="flex items-center text-gray-300">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                support@mall.com
              </li>
            </ul>
          </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-700 text-center text-gray-400">
          <p>&copy; {{ new Date().getFullYear() }} {{ $t('footer.copyright') }}</p>
        </div>
      </div>
    </footer>
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
const isDev = process.env.NODE_ENV === 'development'

// Use computed property to get login status
const isLoggedIn = computed(() => authStore.isAuthenticated)

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
</script>

<style scoped>
/* You can add some styles here */
</style>
