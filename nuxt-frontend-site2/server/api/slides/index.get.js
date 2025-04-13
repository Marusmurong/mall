import { readFile } from 'node:fs/promises'
import { resolve, join } from 'node:path'
import { existsSync } from 'node:fs'

export default defineEventHandler(async (event) => {
  try {
    const dataFile = resolve(process.cwd(), 'server/data/slides.json')
    
    try {
      const data = await readFile(dataFile, 'utf-8')
      return {
        code: 0,
        data: JSON.parse(data),
        message: '获取成功'
      }
    } catch (error) {
      // 如果文件不存在或无法解析，返回默认数据
      const defaultSlides = [
        {
          id: '1',
          title: '优质商品，精选推荐',
          subtitle: '为您提供高品质的精选商品，满足您的一站式购物需求。',
          buttonText: '开始购物',
          buttonLink: '/categories',
          backgroundColor: 'bg-gradient-to-r from-primary-700 to-primary-900',
          backgroundImage: ''
        }
      ]
      
      return {
        code: 0,
        data: defaultSlides,
        message: '获取成功'
      }
    }
  } catch (error) {
    console.error('获取幻灯片数据失败:', error)
    return {
      code: 1,
      message: `获取失败: ${error.message}`
    }
  }
})
