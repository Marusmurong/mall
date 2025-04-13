import { writeFile } from 'fs/promises'
import { randomUUID } from 'crypto'
import path from 'path'

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
    
    const file = formData.find(part => part.name === 'logo')
    
    if (!file) {
      return {
        code: 1,
        message: '没有找到logo文件'
      }
    }
    
    // 检查文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml']
    if (!allowedTypes.includes(file.type)) {
      return {
        code: 1,
        message: '不支持的文件类型，请上传JPG、PNG、GIF或SVG图片'
      }
    }
    
    // 生成唯一文件名
    const fileExt = file.filename.split('.').pop()
    const fileName = `logo-${randomUUID()}.${fileExt}`
    
    // 保存文件路径
    const publicDir = path.resolve(process.cwd(), 'public')
    const uploadsDir = path.join(publicDir, 'images', 'site')
    const filePath = path.join(uploadsDir, fileName)
    
    // 写入文件
    await writeFile(filePath, file.data)
    
    // 返回文件URL
    return {
      code: 0,
      data: {
        url: `/images/site/${fileName}`
      },
      message: '上传成功'
    }
  } catch (error) {
    console.error('上传LOGO失败:', error)
    return {
      code: 1,
      message: `上传失败: ${error.message}`
    }
  }
})
