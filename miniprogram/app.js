App({
  globalData: {
    baseUrl: 'http://localhost:8000',  // API 地址，上线时改为实际域名
    city: '北京',
  },

  onLaunch() {
    // 获取系统信息
    const sysInfo = wx.getSystemInfoSync()
    this.globalData.statusBarHeight = sysInfo.statusBarHeight
    this.globalData.screenWidth = sysInfo.screenWidth
    this.globalData.screenHeight = sysInfo.screenHeight
  },
})
