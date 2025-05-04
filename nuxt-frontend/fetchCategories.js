// 添加这段代码到categories/index.vue文件中，放在fetchProducts函数之前

// Get all categories
const fetchCategories = async () => {
  try {
    console.log('Starting to get category tree')
    const response = await api.categories.getTree({ site: 'default' })
    console.log('Category tree response:', response)
    
    if (response && response.code === 0 && response.data) {
      // 直接使用API返回的所有分类，不进行过滤
      categories.value = response.data
      console.log('分类数量:', categories.value.length)
      console.log('分类数据:', categories.value)
    } else {
      categories.value = []
      console.log('没有获取到分类数据')
    }
  } catch (err) {
    console.error('Failed to get categories:', err)
    categories.value = []
  }
}
