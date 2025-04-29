<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8 text-center">Payment Methods</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
      <!-- Credit Card Payment -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
          <img src="/images/payment/credit-card.png" alt="Credit Card" class="w-12 h-12 mr-4">
          <h2 class="text-xl font-semibold">Credit Card Payment</h2>
        </div>
        <p class="text-gray-700 mb-4">
          We accept Visa, Mastercard, American Express, and Discover cards.
          Your card information is securely encrypted with the latest SSL technology.
        </p>
        <div class="flex flex-wrap gap-2">
          <img src="/images/payment/visa.png" alt="Visa" class="h-8">
          <img src="/images/payment/mastercard.png" alt="Mastercard" class="h-8">
          <img src="/images/payment/amex.png" alt="American Express" class="h-8">
          <img src="/images/payment/discover.png" alt="Discover" class="h-8">
        </div>
      </div>
      
      <!-- PayPal -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
          <img src="/images/payment/paypal.png" alt="PayPal" class="w-12 h-12 mr-4">
          <h2 class="text-xl font-semibold">PayPal</h2>
        </div>
        <p class="text-gray-700 mb-4">
          Pay with your PayPal account for fast and secure checkout.
          No need to enter your financial information every time you shop.
        </p>
        <div class="flex flex-wrap gap-2">
          <img src="/images/payment/paypal-full.png" alt="PayPal" class="h-8">
        </div>
      </div>
      
      <!-- USDT Payment -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
          <img src="/images/payment/usdt.png" alt="USDT" class="w-12 h-12 mr-4">
          <h2 class="text-xl font-semibold">USDT (TRC20)</h2>
        </div>
        <p class="text-gray-700 mb-4">
          Pay with USDT stablecoin using the TRC20 network.
          Fast transaction confirmation and low network fees.
        </p>
        <p class="text-sm text-gray-500">
          Note: Please ensure you're sending USDT on the TRC20 network only. 
          Other networks are not supported and may result in loss of funds.
        </p>
      </div>
      
      <!-- Coinbase Commerce -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <div class="flex items-center mb-4">
          <img src="/images/payment/coinbase.png" alt="Coinbase Commerce" class="w-12 h-12 mr-4">
          <h2 class="text-xl font-semibold">Coinbase Commerce</h2>
        </div>
        <p class="text-gray-700 mb-4">
          Pay with multiple cryptocurrencies through Coinbase Commerce.
          Supported coins include BTC, ETH, USDC, DAI, and more.
        </p>
        <div class="flex flex-wrap gap-2">
          <img src="/images/payment/btc.png" alt="Bitcoin" class="h-8">
          <img src="/images/payment/eth.png" alt="Ethereum" class="h-8">
          <img src="/images/payment/usdc.png" alt="USDC" class="h-8">
        </div>
      </div>
    </div>
    
    <!-- Payment FAQs -->
    <div class="bg-white p-6 rounded-lg shadow-md mb-12">
      <h2 class="text-2xl font-semibold mb-6">Payment FAQs</h2>
      
      <div class="space-y-6">
        <div>
          <h3 class="text-lg font-medium mb-2">What should I do if my payment doesn't go through?</h3>
          <p class="text-gray-700">
            If your payment is declined, please check the following:
            <ul class="list-disc ml-6 mt-2">
              <li>Verify that your payment information is entered correctly</li>
              <li>Ensure you have sufficient funds in your account</li>
              <li>Try a different payment method</li>
              <li>Contact your bank or payment provider to check for restrictions</li>
            </ul>
            If you still experience issues, please contact our customer support.
          </p>
        </div>
        
        <div>
          <h3 class="text-lg font-medium mb-2">How do I know my order is confirmed?</h3>
          <p class="text-gray-700">
            After successful payment, you will receive an order confirmation email. You can also check your order status 
            in the "My Orders" section of your account.
          </p>
        </div>
        
        <div>
          <h3 class="text-lg font-medium mb-2">How can I apply for an invoice?</h3>
          <p class="text-gray-700">
            You can request an invoice during checkout by selecting the "Request Invoice" option. 
            Alternatively, you can request an invoice for a completed order by contacting our customer service 
            with your order number.
          </p>
        </div>
        
        <div>
          <h3 class="text-lg font-medium mb-2">How long does it take to verify my cryptocurrency payment?</h3>
          <p class="text-gray-700">
            Cryptocurrency payments typically require network confirmations. USDT (TRC20) payments are usually confirmed 
            within 5-10 minutes. Payments via Coinbase Commerce may take longer depending on the cryptocurrency used.
            Your order will be processed once the payment is fully confirmed on the blockchain.
          </p>
        </div>
      </div>
    </div>
    
    <!-- Security Information -->
    <div class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-2xl font-semibold mb-6">Secure Payment Guarantee</h2>
      <p class="text-gray-700 mb-4">
        We take security seriously. All payment information is encrypted using industry-standard SSL technology.
        We never store your complete credit card information on our servers.
      </p>
      <div class="flex flex-wrap gap-4 items-center justify-center">
        <img src="/images/payment/ssl-secure.png" alt="SSL Secure" class="h-12">
        <img src="/images/payment/pci-compliant.png" alt="PCI Compliant" class="h-12">
        <img src="/images/payment/secure-payment.png" alt="Secure Payment" class="h-12">
      </div>
    </div>
  </div>
</template>

<script setup>
// Payment methods page
</script>
