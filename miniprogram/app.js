// 导入地址配置
const config = require('./config/index');

App({
  globalData: {
    userInfo: null,
    token: null,
    baseUrl: config.api.baseUrl
  },
  onLaunch: function() {
    // 初始化时检查本地存储的token
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.token = token;
    }
    // 登录
    this.login();
  },
  login: function() {
    wx.login({
      success: res => {
        if (res.code) {
          // 调用后端登录接口
          wx.request({
            url: `${this.globalData.baseUrl}/user/auth`,
            method: 'POST',
            data: {
              code: res.code
            },
            success: res => {
              if (res.data.code === 200 && res.data.data.token) {
                this.globalData.token = res.data.data.token;
                this.globalData.userInfo = { user_id: res.data.data.user_id };
                wx.setStorageSync('token', res.data.data.token);
              }
            }
          });
        }
      }
    });
  },
  getToken: function() {
    return this.globalData.token;
  },
  setToken: function(token) {
    this.globalData.token = token;
    wx.setStorageSync('token', token);
  },
  clearToken: function() {
    this.globalData.token = null;
    this.globalData.userInfo = null;
    wx.removeStorageSync('token');
  },
  request: function(options) {
    const token = this.getToken();
    options.header = options.header || {};
    if (token) {
      options.header['Authorization'] = `Bearer ${token}`;
    }
    // 添加X-Request-Id请求头
    options.header['X-Request-Id'] = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    options.url = `${this.globalData.baseUrl}${options.url}`;
    console.log('发送请求:', options.url);
    return wx.request({
      ...options,
      success: function(res) {
        console.log('请求成功:', options.url, res.data);
        // 检查响应的状态码
        if (res.statusCode >= 200 && res.statusCode < 300) {
          if (options.success) {
            options.success(res);
          }
        } else {
          console.log('请求失败:', options.url, res);
          if (options.fail) {
            options.fail(res);
          }
        }
      },
      fail: function(err) {
        console.log('请求失败:', options.url, err);
        if (options.fail) {
          options.fail(err);
        }
      },
      complete: function() {
        if (options.complete) {
          options.complete();
        }
      }
    });
  }
});