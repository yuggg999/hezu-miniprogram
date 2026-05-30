const { postsApi } = require('../../utils/api')
const { formatTime, getSourceInfo, getCredibilityLevel } = require('../../utils/util')

Page({
  data: {
    post: null,
    loading: true,
    sourceInfo: {},
    credibility: {},
    scoreItems: [],
  },

  onLoad(options) {
    if (options.id) {
      this.loadPost(options.id)
    }
  },

  async loadPost(id) {
    try {
      const post = await postsApi.getDetail(id)
      const sourceInfo = getSourceInfo(post.source)
      const credibility = getCredibilityLevel(post.credibility_score)

      // 构建评分明细
      const detail = post.credibility_detail || {}
      const scoreItems = [
        { label: '价格合理性', key: 'price', icon: '💰', score: detail.price || 0 },
        { label: '评论区信号', key: 'comment', icon: '💬', score: detail.comment || 0 },
        { label: '发帖人可信度', key: 'poster', icon: '👤', score: detail.poster || 0 },
        { label: '图片真实性', key: 'image', icon: '🖼️', score: detail.image || 0 },
        { label: '内容完整度', key: 'completeness', icon: '📋', score: detail.completeness || 0 },
      ]

      this.setData({
        post,
        sourceInfo,
        credibility,
        scoreItems,
        loading: false,
      })
    } catch (err) {
      console.error('加载帖子详情失败:', err)
      wx.showToast({ title: '加载失败', icon: 'none' })
      this.setData({ loading: false })
    }
  },

  // 复制链接
  onCopyLink() {
    const url = this.data.post?.source_url
    if (!url) return

    wx.setClipboardData({
      data: url,
      success() {
        wx.showToast({ title: '链接已复制', icon: 'success' })
      },
    })
  },

  // 打开原帖
  onOpenOriginal() {
    const url = this.data.post?.source_url
    if (!url) return

    // 复制链接并在提示中打开
    wx.setClipboardData({
      data: url,
      success() {
        wx.showModal({
          title: '链接已复制',
          content: '原帖链接已复制到剪贴板，请在浏览器中打开查看',
          showCancel: false,
          confirmText: '知道了',
        })
      },
    })
  },

  // 拨打电话
  onCallPhone() {
    const contact = this.data.post?.contact
    if (!contact) return

    // 提取手机号
    const phoneMatch = contact.match(/1[3-9]\d{9}/)
    if (phoneMatch) {
      wx.makePhoneCall({
        phoneNumber: phoneMatch[0],
      })
    } else {
      wx.setClipboardData({
        data: contact,
        success() {
          wx.showToast({ title: '联系方式已复制', icon: 'success' })
        },
      })
    }
  },

  // 预览图片
  onPreviewImage(e) {
    const current = e.currentTarget.dataset.src
    wx.previewImage({
      current,
      urls: this.data.post.images || [],
    })
  },

  // 分享
  onShareAppMessage() {
    const post = this.data.post
    return {
      title: post?.title || '合租信息',
      path: `/pages/detail/detail?id=${post?.id}`,
    }
  },
})
