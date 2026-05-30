/**
 * API 请求封装
 */
const app = getApp()

const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.baseUrl}${url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: (err) => {
        reject(err)
      },
    })
  })
}

// 帖子相关 API
const postsApi = {
  // 获取帖子列表
  getList(params = {}) {
    const { city = app.globalData.city, page = 1, page_size = 20, ...filters } = params
    const query = new URLSearchParams({ city, page, page_size, ...filters }).toString()
    return request(`/api/posts?${query}`)
  },

  // 搜索帖子
  search(params = {}) {
    const { q, city = app.globalData.city, page = 1, page_size = 20 } = params
    const query = new URLSearchParams({ q, city, page, page_size }).toString()
    return request(`/api/posts/search?${query}`)
  },

  // 获取帖子详情
  getDetail(id) {
    return request(`/api/posts/${id}`)
  },

  // 获取支持的平台列表
  getSources() {
    return request('/api/posts/sources')
  },
}

module.exports = {
  request,
  postsApi,
}
