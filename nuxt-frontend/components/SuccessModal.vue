<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="close"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <!-- Success animation -->
        <div class="bg-gradient-to-r from-green-50 to-teal-50 p-6 sm:p-8">
          <div class="flex flex-col items-center justify-center">
            <!-- Success checkmark animation -->
            <div class="rounded-full bg-green-100 p-3 mb-4">
              <svg class="h-12 w-12 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            
            <h3 class="text-lg sm:text-xl font-bold text-gray-900 text-center">
              Payment Successful!
            </h3>
            
            <p class="mt-2 text-sm text-gray-600 text-center">
              Your purchase has been completed successfully. Thank you for your contribution!
            </p>
          </div>
        </div>
        
        <!-- Transaction details -->
        <div class="bg-white px-4 py-5 sm:p-6">
          <div v-if="data" class="space-y-4">
            <div class="border-b pb-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Purchase Details</h4>
              
              <div class="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
                <div class="text-gray-500">Item:</div>
                <div class="text-gray-900 font-medium">{{ data.item?.title }}</div>
                
                <div class="text-gray-500">Price:</div>
                <div class="text-gray-900 font-medium">${{ formatPrice(data.item?.price || 0) }}</div>
                
                <div class="text-gray-500">Payment Method:</div>
                <div class="text-gray-900 font-medium">{{ formatPaymentMethod(data.paymentMethod) }}</div>
                
                <div class="text-gray-500">Transaction ID:</div>
                <div class="text-gray-900 font-medium">{{ data.transactionId }}</div>
                
                <div class="text-gray-500">Date:</div>
                <div class="text-gray-900 font-medium">{{ formatDate(data.timestamp) }}</div>
                
                <div class="text-gray-500">Purchaser:</div>
                <div class="text-gray-900 font-medium">{{ data.buyerName }}</div>
              </div>
            </div>
            
            <!-- Notification to wishlist owner -->
            <div class="bg-blue-50 rounded-lg p-4">
              <div class="flex">
                <div class="flex-shrink-0">
                  <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div class="ml-3 flex-1 md:flex md:justify-between">
                  <p class="text-sm text-blue-700">
                    The wishlist owner has been notified of your purchase.
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Next steps -->
            <div class="border-t pt-4">
              <h4 class="text-sm font-medium text-gray-700 mb-2">Next Steps</h4>
              <ul class="space-y-2 text-sm text-gray-600">
                <li class="flex items-start">
                  <svg class="h-5 w-5 text-green-500 mr-2 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span>You will receive a confirmation email with purchase details.</span>
                </li>
                <li class="flex items-start">
                  <svg class="h-5 w-5 text-green-500 mr-2 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span>The item will be marked as fulfilled on the wishlist.</span>
                </li>
                <li class="flex items-start">
                  <svg class="h-5 w-5 text-green-500 mr-2 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <span>You can check your purchase history in your account settings if you're logged in.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
            @click="close"
          >
            Done
          </button>
          
          <button 
            type="button"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            @click="goToWishlist"
          >
            View Wishlist
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  data: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close'])

// Methods
const close = () => {
  emit('close')
}

const goToWishlist = () => {
  // Close the modal
  close()
  
  // Optionally refresh the page or navigate back to the wishlist list
  // window.location.reload()
}

// Utility functions
const formatPrice = (price) => {
  if (!price) return '0.00'
  return Number(price).toFixed(2)
}

const formatPaymentMethod = (method) => {
  if (!method) return ''
  
  const methods = {
    credit_card: 'Credit Card',
    paypal: 'PayPal',
    usdt: 'USDT',
    coinbase_commerce: 'Coinbase Commerce'
  }
  
  return methods[method] || method
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script> 