const { postsApi } = require('../../utils/api')
const { formatTime, getSourceInfo, getCredibilityLevel } = require('../../utils/util')

const app = getApp()

Page({
  data: {
    posts: [],
    loading: false,
    refreshing: false,
    page: 1,
    hasMore: true,
    filters: {
      source: '',
      minPrice: '',
      maxPrice: '',
      minCredibility: '',
    },
    sources: [],
    showFilter: false,
  },

  onLoad() {
    this.loadPosts()
    this.loadSources()
  },

  onShow() {
    // 每次显示页面时刷新
  },

  onPullDownRefresh() {
    this.setData({ refreshing: true, page: 1, hasMore: true })
    this.loadPosts().then(() => {
      wx.stopPullDownRefresh()
      this.setData({ refreshing: false })
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.loadMore()
    }
  },

  async loadPosts() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const params = {
        city: app.globalData.city,
        page: 1,
        page_size: 20,
        ...this._getFilterParams(),
      }
      const res = await postsApi.getList(params)
      const items = (res.items || []).map(item => this._formatPost(item))
      this.setData({
        posts: items,
        page: 1,
        hasMore: items.length >= 20,
      })
    } catch (err) {
      console.error('加载帖子失败:', err)
      wx.showToast({ title: '加载失败', icon: 'none' })
    } finally {
      this.setData({ loading: false })
    }
  },

  async loadMore() {
    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const nextPage = this.data.page + 1
      const params = {
        city: app.globalData.city,
        page: nextPage,
        page_size: 20,
        ...this._getFilterParams(),
      }
      const res = await postsApi.getList(params)
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

  async loadSources() {
    try {
      const res = await postsApi.getSources()
      const sources = Object.entries(res.sources || {}).map(([key, name]) => ({
        key,
        name,
      }))
      this.setData({ sources })
    } catch (err) {
      console.error('加载平台列表失败:', err)
    }
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

  _getFilterParams() {
    const { filters } = this.data
    const params = {}
    if (filters.source) params.source = filters.source
    if (filters.minPrice) params.min_price = filters.minPrice
    if (filters.maxPrice) params.max_price = filters.maxPrice
    if (filters.minCredibility) params.min_credibility = filters.minCredibility
    return params
  },

  // 事件处理
  onPostTap(e) {
    const { id } = e.detail
    wx.navigateTo({ url: `/pages/detail/detail?id=${id}` })
  },

  onFilterToggle() {
    this.setData({ showFilter: !this.data.showFilter })
  },

  onSourceFilter(e) {
    const source = e.currentTarget.dataset.source
    this.setData({
      'filters.source': this.data.filters.source === source ? '' : source,
    })
    this.loadPosts()
  },

  onPriceFilter(e) {
    const { min, max } = e.currentTarget.dataset
    this.setData({
      'filters.minPrice': min || '',
      'filters.maxPrice': max || '',
    })
    this.loadPosts()
  },

  onCredibilityFilter(e) {
    const score = e.currentTarget.dataset.score
    this.setData({
      'filters.minCredibility': this.data.filters.minCredibility === score ? '' : score,
    })
    this.loadPosts()
  },

  onClearFilters() {
    this.setData({
      filters: {
        source: '',
        minPrice: '',
        maxPrice: '',
        minCredibility: '',
      },
    })
    this.loadPosts()
  },

  onSearchTap() {
    wx.switchTab({ url: '/pages/search/search' })
  },
})
