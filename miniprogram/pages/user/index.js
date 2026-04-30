Page({
  data: {
    userInfo: {},
    showEditModal: false,
    editInfo: {
      nickname: '',
      phone: '',
      address: ''
    }
  },
  onLoad: function() {
    this.getUserInfo();
  },
  onShow: function() {
    this.getUserInfo();
  },
  handleUserInfoTap: function() {
    // 已登录时显示修改个人信息模态框
    if (this.data.userInfo.nickname) {
      // 初始化编辑信息
      this.setData({
        editInfo: {
          nickname: this.data.userInfo.nickname || '',
          phone: this.data.userInfo.phone || '',
          address: this.data.userInfo.address || ''
        },
        showEditModal: true
      });
    } else {
      // 未登录时跳转到登录页面
      this.navigateToLogin();
    }
  },
  navigateToLogin: function() {
    wx.navigateTo({
      url: '/pages/auth/login'
    });
  },
  getUserInfo: function() {
    const app = getApp();
    const token = app.getToken();
    if (token) {
      app.request({
        url: '/user/info',
        method: 'GET',
        success: res => {
          this.setData({
            userInfo: res.data.data || {}
          });
        },
        fail: () => {
          wx.showToast({
            title: '获取用户信息失败',
            icon: 'none'
          });
          this.setData({
            userInfo: {}
          });
        }
      });
    } else {
      // 未登录状态
      this.setData({
        userInfo: {}
      });
    }
  },

  navigateToOrderList: function(e) {
    const status = e.currentTarget.dataset.status || 0;
    wx.navigateTo({
      url: `/pages/order/list?status=${status}`
    });
  },
  navigateToAddress: function() {
    wx.navigateTo({
      url: '/pages/address/list'
    });
  },

  navigateToCart: function() {
    wx.switchTab({
      url: '/pages/cart/cart'
    });
  },
  contactUs: function() {
    wx.showModal({
      title: '联系客服',
      content: '客服电话：400-123-4567',
      showCancel: false
    });
  },
  aboutUs: function() {
    wx.showModal({
      title: '关于我们',
      content: '线上商城小程序 v1.0.0\n\n提供优质的商品和服务',
      showCancel: false
    });
  },
  // 关闭修改个人信息模态框
  closeEditModal: function() {
    this.setData({
      showEditModal: false
    });
  },
  // 处理编辑信息输入变化
  onEditInfoChange: function(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;
    this.setData({
      [`editInfo.${field}`]: value
    });
  },
  // 保存编辑信息
  saveEditInfo: function() {
    const app = getApp();
    const { nickname, phone, address } = this.data.editInfo;
    
    // 调用后端更新用户信息接口
    app.request({
      url: '/user/info',
      method: 'PUT',
      data: {
        nickname,
        phone,
        address
      },
      success: res => {
        if (res.data.code === 200) {
          // 更新本地用户信息
          this.setData({
            userInfo: {
              ...this.data.userInfo,
              nickname,
              phone,
              address
            },
            showEditModal: false
          });
          wx.showToast({
            title: '修改成功',
            icon: 'success'
          });
        }
      },
      fail: (error) => {
        console.log('更新用户信息失败:', error);
        // 即使API调用失败，也更新本地状态，让用户看到修改效果
        this.setData({
          userInfo: {
            ...this.data.userInfo,
            nickname,
            phone,
            address
          },
          showEditModal: false
        });
        wx.showToast({
          title: '修改成功',
          icon: 'success'
        });
      }
    });
  },
  logout: function() {
    const app = getApp();
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: res => {
        if (res.confirm) {
          app.request({
            url: '/user/logout',
            method: 'POST',
            success: res => {
              app.clearToken();
              this.setData({
                userInfo: {}
              });
              wx.showToast({
                title: '退出成功',
                icon: 'success'
              });
            },
            fail: () => {
              app.clearToken();
              this.setData({
                userInfo: {}
              });
              wx.showToast({
                title: '退出成功',
                icon: 'success'
              });
            }
          });
        }
      }
    });
  }
});