// 使用Nuxt 3的方式导入模块
import { writeFile, mkdir } from 'node:fs/promises'
import { randomUUID } from 'node:crypto'
import { resolve, join } from 'node:path'
import { existsSync } from 'node:fs'

export default defineEventHandler(async (event) => {
  try {
    // 获取上传的文件
    const formData = await readMultipartFormData(event)
    
    if (!formData || !formData.length) {
      return {
        code: 1,
        message: '没有接收到文件'
      }
    }
    
    const file = formData.find(part => part.name === 'slide')
    
    if (!file) {
      return {
        code: 1,
        message: '没有找到幻灯片图片文件'
      }
    }
    
    // 检查文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      return {
        code: 1,
        message: '不支持的文件类型，请上传JPG、PNG、GIF或WEBP图片'
      }
    }
    
    // 生成唯一文件名
    const fileExt = file.filename.split('.').pop()
    const fileName = `slide-${randomUUID()}.${fileExt}`
    
    // 保存文件路径
    const publicDir = resolve(process.cwd(), 'public')
    const uploadsDir = join(publicDir, 'images', 'slides')
    
    // 确保目录存在
    if (!existsSync(uploadsDir)) {
      await mkdir(uploadsDir, { recursive: true })
    }
    
    const filePath = join(uploadsDir, fileName)
    
    // 写入文件
    await writeFile(filePath, file.data)
    
    // 返回文件URL
    return {
      code: 0,
      data: {
        url: `/images/slides/${fileName}`
      },
      message: '上传成功'
    }
  } catch (error) {
    console.error('上传幻灯片图片失败:', error)
    return {
      code: 1,
      message: `上传失败: ${error.message}`
    }
  }
})
