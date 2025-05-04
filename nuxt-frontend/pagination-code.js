// 在State部分添加这些变量
// 分页相关
const currentPage = ref(1)
const totalPages = ref(1)
const totalItems = ref(0)
const pageSize = ref(40) // 每页显示40个商品

// 在methods部分添加这个函数
// 切换页面
const changePage = async (page) => {
  if (page < 1 || page > totalPages.value) return
  
  currentPage.value = page
  await fetchProducts(selectedCategory.value?.id)
}

// 修改fetchProducts函数
const fetchProducts = async (categoryId = null) => {
  try {
    loading.value = true
    error.value = null
    
    let response
    if (categoryId) {
      // 使用正确的API方法获取分类下的产品
      response = await api.categories.getProducts(categoryId)
      console.log('Category products response:', response)
    } else {
      // 使用正确的API方法获取所有产品，添加分页参数
      response = await api.products.getAll({ 
        limit: pageSize.value,
        page: currentPage.value
      })
      console.log('All products response:', response)
    }
    
    // 处理分页格式的响应
    if (response) {
      if (response.results && Array.isArray(response.results)) {
        products.value = response.results
        // 设置分页信息
        totalItems.value = response.count || 0
        totalPages.value = response.pages || Math.ceil(totalItems.value / pageSize.value)
        console.log('成功获取产品数据，数量:', response.results.length)
        console.log('分页信息:', { 
          currentPage: currentPage.value,
          totalPages: totalPages.value,
          totalItems: totalItems.value
        })
      } else if (Array.isArray(response)) {
        products.value = response
        totalItems.value = response.length
        totalPages.value = 1
        console.log('成功获取产品数据，数量:', response.length)
      } else {
        products.value = []
        totalItems.value = 0
        totalPages.value = 1
        console.log('没有获取到产品数据')
      }
    } else {
      products.value = []
      totalItems.value = 0
      totalPages.value = 1
      console.log('没有获取到产品数据')
    }
  } catch (err) {
    console.error('Failed to get products:', err)
    error.value = err.message || 'Failed to get product data'
    products.value = []
    totalItems.value = 0
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}
