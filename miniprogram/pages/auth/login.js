Page({
  data: {},
  onLoad: function(options) {
    // 检查是否已登录
    const app = getApp();
    if (app.getToken()) {
      // 已登录，跳转回之前的页面
      this.navigateBack();
    }
  },
  login: function() {
    const app = getApp();
    // 调用微信登录
    wx.login({
      success: res => {
        if (res.code) {
          // 生成默认昵称：用户 + 日期 + 时间（精确到秒）
          const now = new Date();
          const year = now.getFullYear();
          const month = String(now.getMonth() + 1).padStart(2, '0');
          const day = String(now.getDate()).padStart(2, '0');
          const hour = String(now.getHours()).padStart(2, '0');
          const minute = String(now.getMinutes()).padStart(2, '0');
          const second = String(now.getSeconds()).padStart(2, '0');
          const defaultNickname = `用户${year}${month}${day}${hour}${minute}${second}`;
          
          // 调用后端登录接口
          app.request({
            url: '/user/auth',
            method: 'POST',
            data: {
              code: res.code,
              nickname: defaultNickname // 传递默认昵称
            },
            success: res => {
              if (res.data.code === 200 && res.data.data.token) {
                app.setToken(res.data.data.token);
                wx.showToast({
                  title: '登录成功',
                  icon: 'success'
                });
                // 登录成功后跳转回之前的页面
                this.navigateBack();
              }
            },
            fail: () => {
              wx.showToast({
                title: '登录失败',
                icon: 'none'
              });
            }
          });
        }
      }
    });
  },
  navigateBack: function() {
    const pages = getCurrentPages();
    if (pages.length > 1) {
      // 如果有上一个页面，返回上一个页面
      wx.navigateBack({
        delta: 1
      });
    } else {
      // 如果没有上一个页面，跳转到首页
      wx.switchTab({
        url: '/pages/index/index'
      });
    }
  },
  showAgreement: function() {
    wx.showModal({
      title: '用户协议',
      content: '欢迎使用线上商城小程序。\n\n1. 您在使用本服务前，应当仔细阅读并理解本协议的全部内容。\n2. 您的登录和使用行为将视为对本协议的接受。\n3. 我们将保护您的个人信息安全。\n4. 您应当遵守法律法规，不得利用本服务从事违法活动。',
      showCancel: false
    });
  },
  showPrivacy: function() {
    wx.showModal({
      title: '隐私政策',
      content: '我们重视您的隐私保护。\n\n1. 我们收集的信息仅用于提供和改进服务。\n2. 我们不会向第三方分享您的个人信息。\n3. 我们采取安全措施保护您的信息。\n4. 您可以随时查看和管理您的个人信息。',
      showCancel: false
    });
  }
});