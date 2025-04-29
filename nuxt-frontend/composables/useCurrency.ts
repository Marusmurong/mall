import { ref } from 'vue'

export const useCurrency = () => {
  // 默认货币为美元
  const currency = ref('USD')
  
  // 货币符号映射
  const currencySymbols = {
    USD: '$',
    EUR: '€',
    JPY: '¥',
    GBP: '£',
    CNY: '¥'
  }
  
  // 获取当前货币符号
  const getCurrencySymbol = () => {
    return currencySymbols[currency.value] || '$'
  }
  
  // 格式化价格
  const formatPrice = (price: number) => {
    if (typeof price !== 'number') {
      return `${getCurrencySymbol()}0.00`
    }
    
    return `${getCurrencySymbol()}${price.toFixed(2)}`
  }
  
  // 设置货币
  const setCurrency = (newCurrency: string) => {
    if (currencySymbols[newCurrency]) {
      currency.value = newCurrency
    }
  }
  
  return {
    currency,
    getCurrencySymbol,
    formatPrice,
    setCurrency,
    availableCurrencies: Object.keys(currencySymbols)
  }
}

// 创建一个全局单例
export const currencySymbol = '$'
export const formatPrice = (price: number) => {
  if (typeof price !== 'number') {
    return `$0.00`
  }
  return `$${price.toFixed(2)}`
}
