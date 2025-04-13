import { writeFile, mkdir } from 'node:fs/promises'
import { resolve, join } from 'node:path'
import { existsSync } from 'node:fs'

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    
    if (!body || !Array.isArray(body)) {
      return {
        code: 1,
        message: '无效的数据格式'
      }
    }
    
    // 确保数据目录存在
    const dataDir = resolve(process.cwd(), 'server/data')
    if (!existsSync(dataDir)) {
      await mkdir(dataDir, { recursive: true })
    }
    
    // 保存数据到文件
    const dataFile = join(dataDir, 'slides.json')
    await writeFile(dataFile, JSON.stringify(body, null, 2), 'utf-8')
    
    return {
      code: 0,
      message: '保存成功'
    }
  } catch (error) {
    console.error('保存幻灯片数据失败:', error)
    return {
      code: 1,
      message: `保存失败: ${error.message}`
    }
  }
})
