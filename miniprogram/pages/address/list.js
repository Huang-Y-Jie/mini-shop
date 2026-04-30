Page({
  data: {
    addresses: [],
    loading: false
  },

  onLoad: function() {
    this.getAddresses();
  },

  onShow: function() {
    this.getAddresses();
  },

  // 获取地址列表
  getAddresses: function() {
    this.setData({ loading: true });
    const app = getApp();
    app.request({
      url: '/address/',
      method: 'GET',
      success: (res) => {
        if (res.data.code === 200) {
          this.setData({ addresses: res.data.data || [] });
        } else {
          wx.showToast({ title: '获取地址失败', icon: 'none' });
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

  // 新增地址
  addAddress: function() {
    wx.navigateTo({ url: '/pages/address/edit' });
  },

  // 编辑地址
  editAddress: function(e) {
    const address = e.currentTarget.dataset.item;
    wx.navigateTo({
      url: `/pages/address/edit?id=${address.id}&address=${encodeURIComponent(JSON.stringify(address))}`
    });
  },

  // 删除地址
  deleteAddress: function(e) {
    const addressId = e.currentTarget.dataset.id;
    wx.showModal({
      title: '删除地址',
      content: '确定要删除这个地址吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({ loading: true });
          const app = getApp();
          app.request({
            url: `/address/${addressId}`,
            method: 'DELETE',
            success: (res) => {
              if (res.data.code === 200) {
                wx.showToast({ title: '删除成功' });
                this.getAddresses();
              } else {
                wx.showToast({ title: '删除失败', icon: 'none' });
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
      }
    });
  },

  // 选择地址（用于订单确认页）
  selectAddress: function(e) {
    const addressId = e.currentTarget.dataset.id;
    const address = this.data.addresses.find(addr => addr.id === addressId);
    if (address) {
      // 尝试使用eventChannel传递地址
      const eventChannel = this.getOpenerEventChannel();
      if (eventChannel) {
        eventChannel.emit('selectAddress', { address: address });
        wx.navigateBack();
      } else {
        // 兼容旧的方式
        const pages = getCurrentPages();
        const prevPage = pages[pages.length - 2];
        if (prevPage && prevPage.setSelectedAddress) {
          prevPage.setSelectedAddress(address);
          wx.navigateBack();
        }
      }
    }
  }
});
