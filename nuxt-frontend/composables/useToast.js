// 创建全局Toast通知组件
export default function useToast() {
  // 显示通知
  function showToast(message, type = 'success', duration = 3000) {
    // 先移除可能已经存在的toast
    let existingToast = document.getElementById('global-toast');
    if (existingToast) {
      document.body.removeChild(existingToast);
    }
    
    // 创建toast元素
    const toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.left = '50%';
    toast.style.transform = 'translateX(-50%)';
    toast.style.padding = '10px 20px';
    toast.style.borderRadius = '4px';
    toast.style.zIndex = '9999';
    toast.style.fontWeight = '500';
    toast.style.fontSize = '14px';
    toast.style.transition = 'opacity 0.3s ease';
    toast.style.opacity = '0';
    
    // 根据类型设置样式
    if (type === 'error') {
      toast.style.backgroundColor = '#f44336';
      toast.style.color = 'white';
    } else if (type === 'warning') {
      toast.style.backgroundColor = '#ff9800';
      toast.style.color = 'white';
    } else {
      toast.style.backgroundColor = '#4caf50';
      toast.style.color = 'white';
    }
    
    // 设置消息内容
    toast.textContent = message;
    
    // 添加到DOM
    document.body.appendChild(toast);
    
    // 显示toast
    setTimeout(() => {
      toast.style.opacity = '1';
    }, 10);
    
    // 定时隐藏
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast);
        }
      }, 300);
    }, duration);
  }
  
  return {
    showToast
  };
} 