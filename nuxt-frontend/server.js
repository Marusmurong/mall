const http = require('http');
const fs = require('fs');
const path = require('path');

// 配置端口
const PORT = 3002;

// 简单的静态文件服务器
const server = http.createServer((req, res) => {
  // 默认提供 index.html
  let filePath = path.join(__dirname, 'public', req.url === '/' ? 'index.html' : req.url);
  
  // 检查文件是否存在
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      res.statusCode = 404;
      res.end('404 Not Found');
      return;
    }

    // 读取文件
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.statusCode = 500;
        res.end('Server Error');
        return;
      }

      // 设置内容类型
      const ext = path.extname(filePath);
      let contentType = 'text/html';
      
      switch (ext) {
        case '.js':
          contentType = 'text/javascript';
          break;
        case '.css':
          contentType = 'text/css';
          break;
        case '.json':
          contentType = 'application/json';
          break;
        case '.png':
          contentType = 'image/png';
          break;
        case '.jpg':
          contentType = 'image/jpg';
          break;
      }

      res.setHeader('Content-Type', contentType);
      res.end(data);
    });
  });
});

// 启动服务器
server.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}/`);
  console.log(`注意: 这是一个简单的静态文件服务器，不支持 Nuxt 的 SSR 功能`);
});
