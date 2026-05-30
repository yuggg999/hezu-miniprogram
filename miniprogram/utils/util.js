/**
 * 工具函数
 */

// 格式化时间
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  // 1小时内
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
  }
  // 24小时内
  if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  }
  // 7天内
  if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  }
  // 超过7天
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}月${day}日`
}

// 格式化价格
const formatPrice = (price) => {
  if (!price) return '面议'
  return `¥${price}/月`
}

// 来源平台映射
const sourceMap = {
  douban: { name: '豆瓣', color: '#2D963A', icon: '📖' },
  xianyu: { name: '闲鱼', color: '#FF6600', icon: '🐟' },
  '58': { name: '58同城', color: '#FF0000', icon: '🏠' },
  xiaohongshu: { name: '小红书', color: '#FF2442', icon: '📕' },
  weibo: { name: '微博', color: '#E6162D', icon: '📱' },
}

const getSourceInfo = (source) => {
  return sourceMap[source] || { name: source, color: '#999', icon: '📌' }
}

// 可信度等级
const getCredibilityLevel = (score) => {
  if (score >= 80) return { text: '高度可信', color: '#27ae60' }
  if (score >= 60) return { text: '较为可信', color: '#f39c12' }
  if (score >= 40) return { text: '需谨慎', color: '#e67e22' }
  return { text: '风险较高', color: '#e74c3c' }
}

module.exports = {
  formatTime,
  formatPrice,
  sourceMap,
  getSourceInfo,
  getCredibilityLevel,
}
