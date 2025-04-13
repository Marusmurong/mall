<template>
  <div class="container mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">支付方式</h1>
    
    <div class="bg-white p-6 rounded-lg shadow mb-8">
      <p class="text-gray-700 mb-4">
        Mall电商平台支持多种支付方式，为您提供安全、便捷的支付体验。您可以根据自己的偏好选择以下任一支付方式：
      </p>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
          <h2 class="text-xl font-semibold">信用卡/借记卡支付</h2>
        </div>
        <p class="text-gray-700 mb-3">
          我们支持Visa、MasterCard、American Express、UnionPay等主流信用卡和借记卡支付。
        </p>
        <ul class="list-disc list-inside text-gray-700 space-y-1">
          <li>安全的SSL加密技术保护您的支付信息</li>
          <li>支持信用卡分期付款</li>
          <li>实时交易确认</li>
        </ul>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 class="text-xl font-semibold">支付宝</h2>
        </div>
        <p class="text-gray-700 mb-3">
          使用支付宝快速完成支付，方便又安全。
        </p>
        <ul class="list-disc list-inside text-gray-700 space-y-1">
          <li>无需输入银行卡信息</li>
          <li>支持花呗分期</li>
          <li>交易有保障</li>
        </ul>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <h2 class="text-xl font-semibold">微信支付</h2>
        </div>
        <p class="text-gray-700 mb-3">
          使用微信支付，扫码即可完成支付。
        </p>
        <ul class="list-disc list-inside text-gray-700 space-y-1">
          <li>支持微信余额支付</li>
          <li>支持微信绑定的银行卡支付</li>
          <li>交易记录可在微信查看</li>
        </ul>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow">
        <div class="flex items-center mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-primary-600 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h2 class="text-xl font-semibold">货到付款</h2>
        </div>
        <p class="text-gray-700 mb-3">
          收到商品后再付款，更加安心。
        </p>
        <ul class="list-disc list-inside text-gray-700 space-y-1">
          <li>支持现金支付</li>
          <li>支持POS机刷卡</li>
          <li>收货验货后再付款</li>
        </ul>
      </div>
    </div>
    
    <div class="bg-white p-6 rounded-lg shadow mt-8">
      <h2 class="text-xl font-semibold mb-4">支付常见问题</h2>
      
      <div class="space-y-4">
        <div>
          <h3 class="font-medium mb-2">支付过程中遇到问题怎么办？</h3>
          <p class="text-gray-700">
            如果您在支付过程中遇到任何问题，请联系我们的客服热线400-123-4567，或发送邮件至support@mall.com，我们会尽快为您解决。
          </p>
        </div>
        
        <div>
          <h3 class="font-medium mb-2">支付成功后没有收到订单确认怎么办？</h3>
          <p class="text-gray-700">
            支付成功后，系统会自动发送订单确认邮件。如果您没有收到，请检查垃圾邮件文件夹，或登录您的账户查看订单状态。
          </p>
        </div>
        
        <div>
          <h3 class="font-medium mb-2">如何申请发票？</h3>
          <p class="text-gray-700">
            您可以在下单时选择是否需要发票，并填写发票信息。如果您在下单后需要申请发票，可以在"我的订单"中找到相应订单，点击"申请发票"按钮进行操作。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 支付方式页面
</script>
