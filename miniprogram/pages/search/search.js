const { postsApi } = require('../../utils/api')
const { formatTime, getSourceInfo, getCredibilityLevel } = require('../../utils/util')

const app = getApp()

Page({
  data: {
    keyword: '',
    posts: [],
    loading: false,
    searched: false,
    page: 1,
    hasMore: true,
    history: [],
    hotKeywords: ['合租', '主卧', '次卧', '近地铁', '女生合租', '男生合租', '押一付一'],
  },

  onLoad() {
    this.loadHistory()
  },

  loadHistory() {
    const history = wx.getStorageSync('search_history') || []
    this.setData({ history })
  },

  saveHistory(keyword) {
    if (!keyword) return
    let history = wx.getStorageSync('search_history') || []
    history = history.filter(item => item !== keyword)
    history.unshift(keyword)
    history = history.slice(0, 10)
    wx.setStorageSync('search_history', history)
    this.setData({ history })
  },

  onClearHistory() {
    wx.showModal({
      title: '提示',
      content: '确定要清除搜索历史吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('search_history')
          this.setData({ history: [] })
        }
      },
    })
  },

  onInput(e) {
    this.setData({ keyword: e.detail.value })
  },

  async onSearch() {
    const keyword = this.data.keyword.trim()
    if (!keyword) return

    this.saveHistory(keyword)
    this.setData({ loading: true, searched: true, page: 1, hasMore: true })

    try {
      const res = await postsApi.search({
        q: keyword,
        city: app.globalData.city,
        page: 1,
        page_size: 20,
      })
      const items = (res.items || []).map(item => this._formatPost(item))
      this.setData({
        posts: items,
        hasMore: items.length >= 20,
      })
    } catch (err) {
      console.error('搜索失败:', err)
      wx.showToast({ title: '搜索失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  async loadMore() {
    if (this.data.loading || !this.data.hasMore) return
    this.setData({ loading: true })

    try {
      const nextPage = this.data.page + 1
      const res = await postsApi.search({
        q: this.data.keyword,
        city: app.globalData.city,
        page: nextPage,
        page_size: 20,
      })
      const items = (res.items || []).map(item => this._formatPost(item))
      this.setData({
        posts: [...this.data.posts, ...items],
        page: nextPage,
        hasMore: items.length >= 20,
      })
    } catch (err) {
      console.error('加载更多失败:', err)
    } finally {
      this.setData({ loading: false })
    }
  },

  onKeywordTap(e) {
    const keyword = e.currentTarget.dataset.keyword
    this.setData({ keyword })
    this.onSearch()
  },

  onPostTap(e) {
    const { id } = e.detail
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  onReachBottom() {
    this.loadMore()
  },

  _formatPost(item) {
    const sourceInfo = getSourceInfo(item.source)
    const credibility = getCredibilityLevel(item.credibility_score)
    return {
      ...item,
      sourceName: sourceInfo.name,
      sourceColor: sourceInfo.color,
      sourceIcon: sourceInfo.icon,
      credibilityText: credibility.text,
      credibilityColor: credibility.color,
      timeText: formatTime(item.published_at || item.scraped_at),
    }
  },
})
