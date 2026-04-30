Page({
  data: {
    order: {}
  },
  onLoad: function(options) {
    const orderId = options.id;
    if (!orderId) {
      wx.showToast({
        title: '订单ID不存在',
        icon: 'none'
      });
      setTimeout(() => {
        wx.navigateBack();
      }, 1000);
      return;
    }
    this.orderId = orderId;
    this.getOrderDetail(orderId);
  },
  
  onShow: function() {
    // 页面显示时刷新订单状态，确保返回到该页面时能看到最新状态
    if (this.orderId) {
      this.getOrderDetail(this.orderId);
    }
  },
  getOrderDetail: function(orderId) {
    if (!orderId) {
      wx.showToast({
        title: '订单ID不存在',
        icon: 'none'
      });
      return;
    }
    const app = getApp();
    app.request({
      url: `/order/${orderId}`,
      method: 'GET',
      success: res => {
        this.setOrder(res.data.data);
      },
      fail: (err) => {
        console.log('获取订单详情失败:', err);
        wx.showToast({
          title: '获取订单详情失败',
          icon: 'none'
        });
      }
    });
  },
  setOrder: function(order) {
    this.setData({
      order: order
    });
  },
  payOrder: function() {
    const orderId = this.data.order.order_id;
    const orderStatus = this.data.order.order_status;
    console.log('支付订单ID:', orderId);
    console.log('订单状态:', orderStatus);
    if (!orderId) {
      wx.showToast({
        title: '订单ID不存在',
        icon: 'none'
      });
      return;
    }
    if (orderStatus !== 1) {
      wx.showToast({
        title: '订单状态错误，无法支付',
        icon: 'none'
      });
      return;
    }
    
    // 模拟支付成功（跳过真实的微信支付）
    wx.showLoading({
      title: '支付中...',
      mask: true
    });
    
    // 发起支付请求
    const app = getApp();
    app.request({
      url: `/pay/pay/${orderId}`,
      method: 'POST',
      data: {
        order_id: parseInt(orderId)
      },
      success: res => {
        console.log('模拟支付成功:', res);
        wx.hideLoading();
        if (res.data.code === 200) {
          wx.showToast({
            title: '支付成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: res.data.msg || '支付失败',
            icon: 'none'
          });
        }
        // 刷新订单详情
        this.getOrderDetail(orderId);
      },
      fail: (err) => {
        console.log('模拟支付失败:', err);
        wx.hideLoading();
        wx.showToast({
          title: '支付失败',
          icon: 'none'
        });
        // 刷新订单详情
        this.getOrderDetail(orderId);
      }
    });
    
    /* 真实的微信支付代码（暂时注释）
    const app = getApp();
    app.request({
      url: '/pay/wechat',
      method: 'POST',
      data: {
        order_id: parseInt(orderId)
      },
      success: res => {
        console.log('支付API响应:', res);
        if (res.data.data && res.data.data.pay_params) {
          const payParams = res.data.data.pay_params;
          // 调用微信支付
          wx.requestPayment({
            timeStamp: payParams.timeStamp,
            nonceStr: payParams.nonceStr,
            package: payParams.package,
            signType: 'MD5',
            paySign: payParams.paySign,
            success: () => {
              wx.showToast({
                title: '支付成功',
                icon: 'success'
              });
              // 刷新订单详情
              this.getOrderDetail(orderId);
            },
            fail: (err) => {
              console.log('微信支付失败:', err);
              wx.showToast({
                title: '支付失败',
                icon: 'none'
              });
            }
          });
        } else {
          wx.showToast({
            title: '获取支付参数失败',
            icon: 'none'
          });
        }
      },
      fail: (err) => {
        console.log('获取支付参数失败:', err);
        wx.showToast({
          title: '获取支付参数失败',
          icon: 'none'
        });
      }
    });
    */
  },
  cancelOrder: function() {
    const orderId = this.data.order.order_id;
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
              // 刷新订单详情
              this.getOrderDetail(orderId);
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
  receiveOrder: function() {
    const orderId = this.data.order.order_id;
    const app = getApp();
    wx.showModal({
      title: '确认收货',
      content: '确定要确认收货吗？',
      success: res => {
        if (res.confirm) {
          app.request({
            url: `/order/${orderId}/receive`,
            method: 'PUT',
            success: res => {
              wx.showToast({
                title: '确认收货成功',
                icon: 'success'
              });
              // 刷新订单详情
              this.getOrderDetail(orderId);
            },
            fail: () => {
              wx.showToast({
                title: '确认收货失败',
                icon: 'none'
              });
            }
          });
        }
      }
    });
  },
  navigateToList: function() {
    wx.navigateTo({
      url: '/pages/order/list'
    });
  }
});