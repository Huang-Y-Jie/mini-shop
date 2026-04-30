Page({
  data: {
    activeTab: 0,
    orders: []
  },
  onLoad: function() {
    this.getOrders();
  },
  onShow: function() {
    this.getOrders();
  },
  switchTab: function(e) {
    const tab = parseInt(e.currentTarget.dataset.tab);
    this.setData({
      activeTab: tab
    });
    this.getOrders();
  },
  getOrders: function() {
    const app = getApp();
    const activeTab = this.data.activeTab;
    const data = {
      page: 1,
      size: 20
    };
    // 映射tab值到订单状态
    const tabStatusMap = {
      0: null,  // 全部
      1: 1,     // 待支付
      3: 3,     // 已完成
      4: 4      // 已取消
    };
    const orderStatus = tabStatusMap[activeTab];
    if (orderStatus !== null) {
      data.order_status = orderStatus;
    }
    app.request({
      url: '/order/list',
      method: 'GET',
      data: data,
      success: res => {
        console.log('获取订单成功:', res);
        const orders = res.data.data.list || [];
        this.setData({
          orders: orders
        });
      },
      fail: (err) => {
        console.log('获取订单失败:', err);
        wx.showToast({
          title: '获取订单失败',
          icon: 'none'
        });
        this.setData({
          orders: []
        });
      }
    });
  },
  payOrder: function(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.navigateTo({
      url: `/pages/order/detail?id=${orderId}`
    });
  },
  cancelOrder: function(e) {
    const orderId = e.currentTarget.dataset.orderId;
    const app = getApp();
    wx.showModal({
      title: '取消订单',
      content: '确定要取消该订单吗？',
      success: res => {
        if (res.confirm) {
          app.request({
            url: `/order/${orderId}/cancel`,
            method: 'PUT',
            success: res => {
              wx.showToast({
                title: '取消成功',
                icon: 'success'
              });
              this.getOrders();
            },
            fail: () => {
              wx.showToast({
                title: '取消失败',
                icon: 'none'
              });
            }
          });
        }
      }
    });
  },
  viewOrderDetail: function(e) {
    const orderId = e.currentTarget.dataset.orderId;
    wx.navigateTo({
      url: `/pages/order/detail?id=${orderId}`
    });
  },
  navigateToHome: function() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  }
});