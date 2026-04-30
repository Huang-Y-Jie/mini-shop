Page({
  data: {
    address: null,
    orderItems: [],
    goodsAmount: 0,
    shippingFee: 0,
    totalAmount: 0,
    regions: [],
    selectedRegion: null
  },
  onLoad: function(options) {
    const productIds = options.product_ids.split(',');
    const quantity = options.quantity;
    this.setData({
      product_ids: options.product_ids,
      quantity: quantity
    });
    if (quantity) {
      // 立即购买的情况
      this.getProductDetails(productIds, quantity);
    } else {
      // 从购物车结算的情况
      this.getOrderItems(productIds);
    }
    this.getAddress();
    this.getRegions();
  },
  getOrderItems: function(productIds) {
    const app = getApp();
    app.request({
      url: '/cart/items',
      method: 'GET',
      success: res => {
        const items = res.data.data.items || [];
        const orderItems = items.filter(item => productIds.includes(item.product_id.toString()));
        this.setOrderItems(orderItems);
      },
      fail: () => {
        wx.showToast({
          title: '获取购物车失败',
          icon: 'none'
        });
      }
    });
  },
  getProductDetails: function(productIds, quantity) {
    const app = getApp();
    const productId = productIds[0]; // 立即购买只支持单个商品
    app.request({
      url: `/product/detail/${productId}`,
      method: 'GET',
      success: res => {
        const product = res.data.data;
        if (product) {
          const orderItems = [{
            product_id: product.id,
            product_name: product.name,
            price: product.price,
            quantity: parseInt(quantity),
            amount: product.price * parseInt(quantity)
          }];
          this.setOrderItems(orderItems);
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取商品详情失败',
          icon: 'none'
        });
      }
    });
  },
  setOrderItems: function(items) {
    this.setData({
      orderItems: items
    });
    this.calculateAmounts();
  },
  calculateAmounts: function() {
    const orderItems = this.data.orderItems;
    let goodsAmount = 0;
    orderItems.forEach(item => {
      goodsAmount += item.amount || 0;
    });
    let shippingFee = 0;
    if (this.data.selectedRegion) {
      shippingFee = this.data.selectedRegion.shipping_fee || 0;
    }
    const totalAmount = goodsAmount + shippingFee;
    this.setData({
      goodsAmount: goodsAmount.toFixed(2),
      shippingFee: shippingFee.toFixed(2),
      totalAmount: totalAmount.toFixed(2)
    });
  },
  showRegionSelector: function() {
    const regions = this.data.regions;
    if (regions.length === 0) {
      wx.showToast({
        title: '暂无可用地区',
        icon: 'none'
      });
      return;
    }
    wx.showActionSheet({
      itemList: regions.map(region => region.region_name),
      success: (res) => {
        const selectedRegion = regions[res.tapIndex];
        this.setData({
          selectedRegion: selectedRegion
        });
        this.calculateAmounts();
      },
      fail: (res) => {
        console.log('选择地区失败:', res);
      }
    });
  },
  getAddress: function() {
    const app = getApp();
    app.request({
      url: '/user/info',
      method: 'GET',
      success: res => {
        if (res.data.user && res.data.user.address) {
          this.setData({
            address: {
              name: res.data.user.nickname || '',
              phone: res.data.user.phone || '',
              address: res.data.user.address || ''
            }
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取地址失败',
          icon: 'none'
        });
      }
    });
  },
  getRegions: function() {
    const app = getApp();
    app.request({
      url: '/region/list?&is_active=1',
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            regions: res.data.data
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '获取地区列表失败',
          icon: 'none'
        });
      }
    });
  },
  navigateToAddressList: function() {
    wx.navigateTo({
      url: '/pages/address/list',
      success: function(res) {
        // 地址选择成功后，通过回调更新地址
        res.eventChannel.on('selectAddress', function(data) {
          console.log('选择地址成功:', data);
          const selectedAddress = data.address;
          // 组合地址信息
          const address = {
            name: selectedAddress.name || selectedAddress.consignee || '',
            phone: selectedAddress.phone || '',
            address: `${selectedAddress.province || ''}${selectedAddress.city || ''}${selectedAddress.district || ''}${selectedAddress.detail || ''}`
          };
          this.setData({
            address: address
          });
        }.bind(this));
      }.bind(this),
      fail: function(err) {
        console.log('跳转地址管理页面失败:', err);
        wx.showToast({
          title: '跳转失败',
          icon: 'none'
        });
      }
    });
  },
  submitOrder: function() {
    if (!this.data.address) {
      wx.showToast({
        title: '请选择收货地址',
        icon: 'none'
      });
      return;
    }
    if (!this.data.selectedRegion) {
      wx.showToast({
        title: '请选择所在地区',
        icon: 'none'
      });
      return;
    }
    const app = getApp();
    const address = this.data.address;
    const data = {
      address: address.address,
      phone: address.phone,
      consignee: address.name,
      region_id: this.data.selectedRegion.id
    };
    
    // 如果是直接购买，传递商品信息
    if (this.data.quantity) {
      data.product_ids = this.data.product_ids;
      data.quantity = this.data.quantity;
    }
    
    app.request({
      url: '/order/create',
      method: 'POST',
      data: data,
      success: res => {
        if (res.data.code === 200 && res.data.data.order_id) {
          const orderId = res.data.data.order_id;
          // 跳转到支付页面，使用redirectTo确保无法返回
          wx.redirectTo({
            url: `/pages/order/detail?id=${orderId}`
          });
        } else {
          wx.showToast({
            title: res.data.msg || '提交订单失败',
            icon: 'none'
          });
        }
      },
      fail: err => {
        console.log('提交订单失败:', err);
        wx.showToast({
          title: '网络错误，提交订单失败',
          icon: 'none'
        });
      }
    });
  },
  generateReqId: function() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
});