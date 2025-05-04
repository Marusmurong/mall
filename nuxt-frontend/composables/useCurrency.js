/**
 * Composable for currency formatting
 */
export const useCurrency = () => {
  /**
   * Format a number as currency
   * @param {number} amount - The amount to format
   * @param {string} currencyCode - The currency code (default: 'USD')
   * @param {string} locale - The locale (default: 'en-US')
   * @returns {string} Formatted currency string
   */
  const formatCurrency = (amount, currencyCode = 'USD', locale = 'en-US') => {
    if (amount === null || amount === undefined) return '';
    
    try {
      return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currencyCode,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount);
    } catch (error) {
      console.error('Error formatting currency:', error);
      return `${currencyCode} ${amount.toFixed(2)}`;
    }
  };

  /**
   * Format price without currency symbol
   * @param {number} amount - The amount to format
   * @returns {string} Formatted price string
   */
  const formatPrice = (amount) => {
    if (amount === null || amount === undefined) return '';
    
    try {
      return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount);
    } catch (error) {
      console.error('Error formatting price:', error);
      return amount.toFixed(2);
    }
  };

  return {
    formatCurrency,
    formatPrice
  };
}; 