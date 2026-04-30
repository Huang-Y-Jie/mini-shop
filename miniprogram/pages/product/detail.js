Page({
  data: {
    product: {},
    quantity: 1,
    carouselImages: []
  },
  onLoad: function(options) {
    const productId = options.id;
    this.getProductDetail(productId);
  },
  getProductDetail: function(productId) {
    const app = getApp();
    app.request({
      url: `/product/detail/${productId}`,
      method: 'GET',
      success: res => {
        this.setData({
          product: res.data.data
        });
        this.setCarouselImages(res.data.data);
      },
      fail: () => {
        wx.showToast({
          title: '获取商品详情失败',
          icon: 'none'
        });
      }
    });
  },
  decreaseQuantity: function() {
    if (this.data.quantity > 1) {
      this.setData({
        quantity: this.data.quantity - 1
      });
    }
  },
  increaseQuantity: function() {
    this.setData({
      quantity: this.data.quantity + 1
    });
  },
  handleQuantityInput: function(e) {
    let value = e.detail.value;
    if (value === '') {
      this.setData({
        quantity: ''
      });
    } else {
      let numValue = parseInt(value);
      if (isNaN(numValue)) {
        numValue = '';
      }
      this.setData({
        quantity: numValue
      });
    }
  },
  handleQuantityBlur: function(e) {
    let value = parseInt(e.detail.value);
    if (isNaN(value) || value < 1) {
      value = 1;
    }
    this.setData({
      quantity: value
    });
  },
  addToCart: function() {
    const app = getApp();
    // 检查是否已登录
    if (!app.getToken()) {
      // 未登录，显示提示信息
      wx.showToast({
        title: '请进行登录',
        icon: 'none',
        duration: 2000
      });
      // 延迟跳转到登录页面
      setTimeout(() => {
        wx.navigateTo({
          url: '/pages/auth/login'
        });
      }, 1500);
      return;
    }
    const productId = this.data.product.id;
    const quantity = this.data.quantity;
    app.request({
      url: '/cart/add',
      method: 'POST',
      data: {
        product_id: productId,
        quantity: quantity
      },
      success: res => {
        wx.showToast({
          title: '加入购物车成功',
          icon: 'success'
        });
      },
      fail: () => {
        wx.showToast({
          title: '加入购物车失败',
          icon: 'none'
        });
      }
    });
  },
  buyNow: function() {
    const app = getApp();
    // 检查是否已登录
    if (!app.getToken()) {
      // 未登录，显示提示信息
      wx.showToast({
        title: '请进行登录',
        icon: 'none',
        duration: 2000
      });
      // 延迟跳转到登录页面
      setTimeout(() => {
        wx.navigateTo({
          url: '/pages/auth/login'
        });
      }, 1500);
      return;
    }
    const productId = this.data.product.id;
    const quantity = this.data.quantity;
    wx.navigateTo({
      url: `/pages/order/confirm?product_ids=${productId}&quantity=${quantity}`
    });
  },
  setCarouselImages: function(product) {
    const images = [];
    
    // 确保封面图片作为第一张
    if (product.cover_img) {
      images.push(product.cover_img);
    }
    
    // 添加其他图片
    if (product.imgs) {
      // 确保imgs是数组
      const imgsArray = Array.isArray(product.imgs) ? product.imgs : [];
      // 过滤掉与封面图片相同的图片，避免重复
      imgsArray.forEach(img => {
        if (img && img !== product.cover_img) {
          images.push(img);
        }
      });
    }
    
    // 如果没有图片，添加一个默认图片
    if (images.length === 0) {
      images.push('https://img.baidu.com/it/u=123456789,123456789&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=500');
    }
    
    this.setData({
      carouselImages: images
    });
  }
});