// 修复的获取分类函数
export const useCategoriesFixed = () => {
  const api = useApi()
  
  // 获取所有分类
  const fetchCategories = async () => {
    try {
      console.log('Starting to get category tree')
      const response = await api.categories.getTree({ site: 'default' })
      console.log('Category tree response:', response)
      
      if (response && response.code === 0 && response.data) {
        // 直接使用API返回的所有分类，不进行过滤
        return response.data
      } else {
        console.log('没有获取到分类数据')
        return []
      }
    } catch (err) {
      console.error('Failed to get categories:', err)
      return []
    }
  }

  return {
    fetchCategories
  }
}
