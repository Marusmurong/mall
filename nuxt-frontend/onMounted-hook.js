// 添加这段代码到categories/index.vue文件中的fetchCategories函数之后

// Load data when page loads
onMounted(async () => {
  await fetchCategories()
  
  // Check URL for category ID
  if (route.query.category) {
    const categoryId = route.query.category
    const category = categories.value.find(c => c.id === categoryId)
    if (category) {
      await selectCategory(category)
    } else {
      await fetchProducts()
    }
  } else {
    await fetchProducts()
  }
})
