Page({
  data: {
    formData: {
      nickname: '',
      phone: ''
    },
    loading: false
  },

  onLoad: function() {
    this.getUserInfo();
  },

  // 获取用户信息
  getUserInfo: function() {
    this.setData({ loading: true });
    const app = getApp();
    app.request({
      url: '/user/info',
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({
            formData: {
              nickname: res.data.data.nickname || '',
              phone: res.data.data.phone || ''
            }
          });
        } else {
          wx.showToast({ title: '获取用户信息失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  // 提交表单
  submitForm: function(e) {
    const { nickname, phone } = e.detail.value;
    
    // 表单验证
    if (!nickname) {
      wx.showToast({ title: '请输入昵称', icon: 'none' });
      return;
    }
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }
    
    this.setData({ loading: true });
    const app = getApp();
    
    app.request({
      url: '/user/info',
      method: 'PUT',
      data: {
        nickname: nickname,
        phone: phone
      },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ 
            title: '修改成功',
            success: () => {
              wx.navigateBack();
            }
          });
        } else {
          wx.showToast({ title: '修改失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.showToast({ title: '网络错误', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  }
});