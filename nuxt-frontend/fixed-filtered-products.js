// Filtered product list
const filteredProducts = computed(() => {
  // 确保products.value是一个数组
  let result = Array.isArray(products.value) ? [...products.value] : []
  
  // Apply subcategory filter
  if (selectedSubcategories.value.length > 0) {
    result = result.filter(product => 
      product.categories && product.categories.some(cat => 
        selectedSubcategories.value.includes(cat.id)
      )
    )
  }
  
  // Apply product attribute filter
  if (filterNew.value) {
    result = result.filter(product => product.is_new)
  }
  
  if (filterHot.value) {
    result = result.filter(product => product.is_hot)
  }
  
  if (filterDiscount.value) {
    result = result.filter(product => {
      return product.discount_price || 
        (product.original_price && product.original_price !== product.price)
    })
  }
  
  // Apply price filter
  if (priceMin.value) {
    result = result.filter(product => {
      const price = product.discount_price || product.price
      return parseFloat(price) >= Number(priceMin.value)
    })
  }
  
  if (priceMax.value) {
    result = result.filter(product => {
      const price = product.discount_price || product.price
      return parseFloat(price) <= Number(priceMax.value)
    })
  }
  
  // Apply sorting
  switch (sortBy.value) {
    case 'price_asc':
      result.sort((a, b) => {
        const priceA = parseFloat(a.discount_price || a.price)
        const priceB = parseFloat(b.discount_price || b.price)
        return priceA - priceB
      })
      break
    case 'price_desc':
      result.sort((a, b) => {
        const priceA = parseFloat(a.discount_price || a.price)
        const priceB = parseFloat(b.discount_price || b.price)
        return priceB - priceA
      })
      break
    case 'newest':
      result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      break
    case 'sales':
      result.sort((a, b) => (b.sales || 0) - (a.sales || 0))
      break
  }
  
  return result
})
