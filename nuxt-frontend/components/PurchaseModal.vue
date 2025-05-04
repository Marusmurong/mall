<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="close"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
              <!-- 替换信用卡图标为网站LOGO -->
              <img v-if="siteLogo" :src="siteLogo" alt="Mall Logo" class="h-6 w-auto" />
              <span v-else class="text-lg font-bold text-primary-600">Mall</span>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                Complete Your Purchase
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  You're about to purchase the entire wishlist for {{ props.totalAmount ? `$${formatPrice(props.totalAmount)}` : '-' }}.
                </p>
              </div>
            </div>
          </div>

          <!-- Product information -->
          <div v-if="props.items && props.items.length > 0" class="mt-4 border rounded-lg p-4">
            <h4 class="text-sm font-medium text-gray-900 mb-2">Wishlist Items ({{ props.items.length }})</h4>
            <div class="max-h-40 overflow-y-auto">
              <div v-for="(item, index) in props.items" :key="index" class="flex items-center py-2 border-b last:border-0">
                <div class="w-10 h-10 overflow-hidden rounded-md flex-shrink-0 bg-gray-100">
                  <img v-if="item.image" :src="item.image" :alt="item.title" class="w-full h-full object-cover">
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                </div>
                <div class="ml-3 flex-1">
                  <h5 class="text-xs font-medium text-gray-900 truncate">{{ item.title }}</h5>
                  <div class="flex justify-between mt-1">
                    <span class="text-xs text-gray-500">Price:</span>
                    <span class="text-xs font-medium text-gray-900">${{ formatPrice(item.price) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Form fields -->
          <div class="mt-4">
            <form @submit.prevent="submitPurchase">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
                <div v-if="loadingPaymentMethods" class="flex items-center justify-center py-4">
                  <svg class="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span class="ml-2 text-sm text-gray-600">Loading payment methods...</span>
                </div>
                <div v-else-if="paymentMethods.length === 0" class="py-4 text-center text-sm text-gray-600">
                  No payment methods available
                </div>
                <div v-else class="grid grid-cols-2 gap-3">
                  <div 
                    v-for="method in paymentMethods" 
                    :key="method.id"
                    @click="selectPaymentMethod(method)"
                    class="border rounded-lg p-3 cursor-pointer transition-colors"
                    :class="{'border-blue-500 bg-blue-50': formData.paymentMethod === method, 'border-gray-200 hover:border-gray-300': formData.paymentMethod !== method}"
                  >
                    <div class="flex items-center">
                      <div v-if="method.icon" class="h-8 w-8 bg-gray-100 rounded flex items-center justify-center mr-2">
                        <img :src="method.icon" :alt="method.name" class="h-6 w-auto object-contain" />
                      </div>
                      <div v-else class="h-8 w-8 bg-gray-100 rounded flex items-center justify-center mr-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                        </svg>
                      </div>
                      <div>
                        <div class="font-medium text-sm">{{ method.name }}</div>
                        <div class="text-xs text-gray-500">{{ method.description }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Credit card fields -->
              <div v-if="formData.paymentMethod && formData.paymentMethod.code === 'credit_card'" class="space-y-4 border-t pt-4">
                <div>
                  <label for="cardNumber" class="block text-sm font-medium text-gray-700">Card Number</label>
                  <div class="mt-1">
                    <input 
                      type="text" 
                      id="cardNumber" 
                      v-model="formData.cardNumber"
                      required
                      pattern="[0-9]{13,19}"
                      class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      placeholder="1234 5678 9012 3456"
                    >
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label for="expiryDate" class="block text-sm font-medium text-gray-700">Expiry Date</label>
                    <div class="mt-1">
                      <input 
                        type="text" 
                        id="expiryDate" 
                        v-model="formData.expiryDate"
                        required
                        pattern="(0[1-9]|1[0-2])\/[0-9]{2}"
                        class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        placeholder="MM/YY"
                      >
                    </div>
                  </div>

                  <div>
                    <label for="cvv" class="block text-sm font-medium text-gray-700">CVV</label>
                    <div class="mt-1">
                      <input 
                        type="text" 
                        id="cvv" 
                        v-model="formData.cvv"
                        required
                        pattern="[0-9]{3,4}"
                        class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        placeholder="123"
                      >
                    </div>
                  </div>
                </div>

                <div>
                  <label for="cardholderName" class="block text-sm font-medium text-gray-700">Cardholder Name</label>
                  <div class="mt-1">
                    <input 
                      type="text" 
                      id="cardholderName" 
                      v-model="formData.cardholderName"
                      required
                      class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      placeholder="John Doe"
                    >
                  </div>
                </div>
              </div>

              <!-- PayPal payment -->
              <div v-if="formData.paymentMethod && formData.paymentMethod.code === 'paypal'" class="border-t pt-4">
                <div class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg">
                  <div class="text-center mb-4">
                    <p class="text-sm text-gray-600">
                      You will be redirected to PayPal to complete your payment securely
                    </p>
                  </div>
                </div>
              </div>

              <!-- USDT payment -->
              <div v-if="formData.paymentMethod && formData.paymentMethod.code === 'usdt'" class="border-t pt-4">
                <div class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg">
                  <div class="text-center">
                    <div class="w-48 h-48 mx-auto bg-white border p-2 rounded flex items-center justify-center">
                      <div class="h-32 w-32 bg-teal-500 text-white rounded-full flex items-center justify-center">
                        <span class="font-bold text-2xl">USDT</span>
                      </div>
                    </div>
                    <p class="mt-2 text-sm font-medium text-gray-800">USDT (TRC20)</p>
                    <p class="text-xs text-gray-600 mt-1 mb-2">Send exactly: {{ formatPrice(props.totalAmount || 0) }} USDT</p>
                    
                    <div class="bg-white rounded border p-2 mb-4">
                      <p class="text-xs text-gray-800 break-all select-all">TMu29JxBT9TNUnwLD9JijhR5qSppiDjwKP</p>
                    </div>
                  </div>
                  
                  <div class="w-full">
                    <label for="txHash" class="block text-sm font-medium text-gray-700">Transaction Hash</label>
                    <div class="mt-1">
                      <input 
                        type="text" 
                        id="txHash" 
                        v-model="formData.transactionHash" 
                        required
                        class="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        placeholder="Enter the transaction hash after payment"
                      >
                    </div>
                    <p class="mt-1 text-xs text-gray-500">Please enter the transaction hash after sending USDT</p>
                  </div>
                </div>
              </div>

              <!-- Coinbase Commerce payment -->
              <div v-if="formData.paymentMethod && formData.paymentMethod.code === 'coinbase_commerce'" class="border-t pt-4">
                <div class="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg">
                  <div class="text-center mb-4">

                    <p class="text-sm text-gray-600">
                      Pay with various cryptocurrencies via Coinbase Commerce
                    </p>
                  </div>
                  
                  <div class="w-full px-4">
                  
                  </div>
                </div>
              </div>

              <!-- Error message -->
              <div v-if="false && errorMessage" class="mt-4 p-2 bg-red-50 text-red-600 text-sm rounded">
                {{ errorMessage }}
              </div>

              <!-- Total and checkout button -->
              <div class="mt-6 border-t pt-4">
                <div class="flex justify-between mb-4">
                  <span class="text-sm font-medium text-gray-700">Total:</span>
                  <span class="text-lg font-bold text-gray-900">${{ formatPrice(props.totalAmount || 0) }}</span>
                </div>
                
                <div class="flex flex-col space-y-3">
                  <button 
                    type="submit"
                    class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm"
                    :disabled="isSubmitting"
                  >
                    <span v-if="isSubmitting" class="mr-2">
                      <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </span>
                    {{ isSubmitting ? 'Processing...' : 'Confirm Payment' }}
                  </button>
                  
                  <button 
                    type="button"
                    class="inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm"
                    @click="close"
                    :disabled="isSubmitting"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRuntimeConfig } from 'nuxt/app'
import { useApi } from '~/composables/useApi'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  items: {
    type: Array,
    default: () => []
  },
  totalAmount: {
    type: Number,
    default: 0
  },
  wishlistId: {
    type: String,
    default: ''
  }
})

// Runtime config
const config = useRuntimeConfig()
const apiBaseUrl = config.public.apiBaseUrl || 'http://127.0.0.1:8000'

// API
const api = useApi()

// Emits
const emit = defineEmits(['close', 'purchase'])

// State
const formData = ref({
  paymentMethod: '',
  cardNumber: '',
  expiryDate: '',
  cvv: '',
  cardholderName: '',
  transactionHash: '',
  selectedItem: null
})
const isSubmitting = ref(false)
const errorMessage = ref('')
const paymentMethods = ref([])
const loadingPaymentMethods = ref(false)
const siteLogo = ref('') // Add a new state variable for the site logo

// Fetch payment methods from API
const fetchPaymentMethods = async () => {
  try {
    loadingPaymentMethods.value = true
    const response = await api.payments.getMethods()
    console.log('Payment methods response:', response) // 添加日志，查看响应内容
    
    // 修复：确保正确解析API返回的数据结构
    if (response && response.data && response.data.results) {
      // 处理标准响应结构 {code: 0, message: "success", data: {results: []}}
      paymentMethods.value = response.data.results || []
    } else if (response && response.results) {
      // 处理直接返回结果的结构 {results: []}
      paymentMethods.value = response.results || []
    } else {
      // 尝试处理其他可能的结构
      paymentMethods.value = Array.isArray(response) ? response : []
    }
    
    console.log('Available payment methods:', paymentMethods.value) // 添加日志，查看可用的支付方式
    
    // 如果有支付方式，默认选择第一个
    if (paymentMethods.value.length > 0) {
      formData.value.paymentMethod = paymentMethods.value[0]
    }
  } catch (error) {
    console.error('Error fetching payment methods:', error)
    errorMessage.value = 'Failed to load payment methods. Please try again.'
  } finally {
    loadingPaymentMethods.value = false
  }
}

// Select payment method
const selectPaymentMethod = (method) => {
  formData.value.paymentMethod = method
}

// Watch for modal opening to reset form and fetch payment methods
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    // Reset form when modal opens
    formData.value = {
      paymentMethod: '',
      cardNumber: '',
      expiryDate: '',
      cvv: '',
      cardholderName: '',
      transactionHash: '',
      selectedItem: null
    }
    errorMessage.value = ''
    isSubmitting.value = false
    
    // Fetch payment methods
    fetchPaymentMethods()
  }
})

// Fetch payment methods on component mount
onMounted(() => {
  if (props.show) {
    fetchPaymentMethods()
  }
  
  // 加载网站LOGO
  const savedLogo = localStorage.getItem('siteLogo')
  if (savedLogo) {
    siteLogo.value = savedLogo
  }
})

// Methods
const close = () => {
  if (isSubmitting.value) return
  emit('close')
}

const submitPurchase = async () => {
  try {
    isSubmitting.value = true;
    errorMessage.value = '';
    
    // 1. 校验支付方式
    if (!formData.value.paymentMethod) {
      errorMessage.value = '请选择支付方式';
      isSubmitting.value = false;
      return;
    }
    // 校验心愿单ID
    if (!props.wishlistId) {
      errorMessage.value = '心愿单ID无效';
      isSubmitting.value = false;
      return;
    }
    // 自动获取未购买商品的第一个ID（UUID字符串），直接传递给后端
    let wishlistItemId = null;
    const unpurchasedItems = props.items && props.items.length ? props.items.filter(item => !item.purchased) : [];
    if (unpurchasedItems.length > 0) {
      wishlistItemId = unpurchasedItems[0].id; // 直接用UUID字符串
      // 验证是否是有效的UUID格式 (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(wishlistItemId)) {
        console.error('无效的UUID格式:', wishlistItemId);
        errorMessage.value = '心愿单物品ID格式不正确';
        isSubmitting.value = false;
        return;
      }
    }
    if (!wishlistItemId) {
      errorMessage.value = '心愿单没有可支付的商品，无法发起支付。';
      isSubmitting.value = false;
      return;
    }
    // 2. 构造支付参数
    const paymentData = {
      wishlist_item_id: wishlistItemId, // 直接传UUID字符串
      payment_method_id: formData.value.paymentMethod.id,
      amount: props.totalAmount ? props.totalAmount.toString() : '0',
      payer_email: 'guest@example.com' // 添加默认的游客邮箱
    };
    console.log('支付参数:', paymentData);
    
    // 调试：显示每个参数的类型和值
    console.log('wishlist_item_id:', typeof paymentData.wishlist_item_id, paymentData.wishlist_item_id);
    console.log('payment_method_id:', typeof paymentData.payment_method_id, paymentData.payment_method_id);
    console.log('amount:', typeof paymentData.amount, paymentData.amount);
    
    // 3. 发起支付请求
    let paymentResponse;
    try {
      paymentResponse = await api.payments.createPayment(paymentData);
      console.log('支付响应:', paymentResponse);
    } catch (err) {
      console.error('支付请求失败:', err);
      isSubmitting.value = false;
      close(); // 直接关闭模态框
      return;
    }
    
    // 4. 处理支付响应
    // 检查是否有payment_link (后端直接返回的支付链接)
    console.log('支付完整响应:', paymentResponse);
    console.log('支付链接类型:', typeof paymentResponse?.payment_link);
    console.log('支付链接值:', paymentResponse?.payment_link);
    
    // 直接获取payment_link并跳转
    if (paymentResponse && paymentResponse.payment_link) {
      console.log('检测到支付链接，准备跳转:', paymentResponse.payment_link);
      try {
        // 直接使用window.open打开新窗口，避免可能的跳转限制
        window.open(paymentResponse.payment_link, '_blank');
        console.log('已尝试使用window.open打开支付页面');
        
        // 关闭模态框
        close();
        return;
      } catch (e) {
        console.error('跳转失败，尝试备用方法:', e);
        try {
          // 备用方法：设置location.href
          window.location.href = paymentResponse.payment_link;
          close(); // 关闭模态框
          return;
        } catch (e2) {
          console.error('所有跳转方法均失败:', e2);
          // 不显示错误消息弹窗，只在控制台记录
          console.error('无法跳转到支付页面，支付链接:', paymentResponse.payment_link);
          isSubmitting.value = false;
          close(); // 直接关闭模态框
          return;
        }
      }
    }
    
    // 检查是否有支付ID和checkout_url (传统方式)
    if (paymentResponse && paymentResponse.id) {
      const paymentRecord = paymentResponse;
      
      // 检查是否有checkout_url
      if (paymentRecord.payment_data && paymentRecord.payment_data.checkout_url) {
        console.log('检测到checkout_url，准备跳转:', paymentRecord.payment_data.checkout_url);
        // 跳转到支付页面
        window.location.href = paymentRecord.payment_data.checkout_url;
        close(); // 关闭模态框
        return;
      }
    }
    
    // 如果没有跳转链接，显示支付成功
    console.log('支付创建成功，但没有跳转链接');
    errorMessage.value = '';
    isSubmitting.value = false;
    emit('purchase', paymentResponse);
    close();
    
  } catch (error) {
    console.error('Payment error:', error);
    errorMessage.value = '支付过程中发生错误，请重试。';
    isSubmitting.value = false;
  }
}

// Utility functions
const formatPrice = (price) => {
  if (!price) return '0.00'
  return Number(price).toFixed(2)
}
</script>