App({
  globalData: {
    baseUrl: 'https://hezu-api-264152-4-1438558899.sh.run.tcloudbase.com',  // 微信云托管地址
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
