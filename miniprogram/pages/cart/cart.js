Page({
  data: {
    cartItems: [],
    totalAmount: 0,
    loading: false,
    maxQuantity: 99, // 商品最大数量限制
    updateTimeout: null, // 防抖定时器
    isLoggedIn: false // 登录状态
  },
  onLoad: function() {
    const app = getApp();
    const isLoggedIn = !!app.getToken();
    this.setData({ isLoggedIn });
    if (isLoggedIn) {
      this.getCartItems();
    } else {
      // 未登录状态，显示空购物车
      this.setData({
        cartItems: [],
        totalAmount: '0.00'
      });
    }
  },
  onShow: function() {
    const app = getApp();
    const isLoggedIn = !!app.getToken();
    this.setData({ isLoggedIn });
    if (isLoggedIn) {
      this.getCartItems();
    } else {
      // 未登录状态，显示空购物车
      this.setData({
        cartItems: [],
        totalAmount: '0.00'
      });
    }
  },
  getCartItems: function() {
    this.setData({ loading: true });
    const app = getApp();
    app.request({
      url: '/cart/items',
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          const items = res.data.data.items || [];
          this.setCartItems(items);
        } else {
          wx.showToast({
            title: '获取购物车失败',
            icon: 'none'
          });
          // 即使获取失败，也保持登录状态
          this.setData({ isLoggedIn: !!app.getToken() });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，获取购物车失败',
          icon: 'none'
        });
        // 即使获取失败，也保持登录状态
        this.setData({ isLoggedIn: !!app.getToken() });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },
  setCartItems: function(items) {
    this.setData({
      cartItems: items
    });
    this.calculateTotal();
  },
  calculateTotal: function() {
    const cartItems = this.data.cartItems;
    let total = 0;
    cartItems.forEach(item => {
      total += item.amount || 0;
    });
    this.setData({
      totalAmount: total.toFixed(2)
    });
  },
  decreaseCount: function(e) {
    const cartId = e.currentTarget.dataset.cartId;
    const cartItems = this.data.cartItems;
    const itemIndex = cartItems.findIndex(item => item.product_id === cartId);
    if (itemIndex !== -1 && cartItems[itemIndex].quantity > 1) {
      const newQuantity = cartItems[itemIndex].quantity - 1;
      // 先更新本地数据
      cartItems[itemIndex].quantity = newQuantity;
      this.setData({
        cartItems: cartItems
      });
      this.calculateTotal();
      // 防抖更新数据库
      this.debounceUpdateCartItem(cartId, newQuantity);
    }
  },
  increaseCount: function(e) {
    const cartId = e.currentTarget.dataset.cartId;
    const cartItems = this.data.cartItems;
    const itemIndex = cartItems.findIndex(item => item.product_id === cartId);
    if (itemIndex !== -1) {
      const currentQuantity = cartItems[itemIndex].quantity;
      if (currentQuantity >= this.data.maxQuantity) {
        wx.showToast({
          title: `商品数量不能超过${this.data.maxQuantity}`,
          icon: 'none'
        });
        return;
      }
      const newQuantity = currentQuantity + 1;
      // 先更新本地数据
      cartItems[itemIndex].quantity = newQuantity;
      this.setData({
        cartItems: cartItems
      });
      this.calculateTotal();
      // 防抖更新数据库
      this.debounceUpdateCartItem(cartId, newQuantity);
    }
  },
  debounceUpdateCartItem: function(cartId, quantity) {
    // 清除之前的定时器
    if (this.data.updateTimeout) {
      clearTimeout(this.data.updateTimeout);
    }
    // 设置新的定时器，300ms后更新数据库
    const timeout = setTimeout(() => {
      this.updateCartItem(cartId, quantity);
    }, 300);
    this.setData({
      updateTimeout: timeout
    });
  },
  handleQuantityInput: function(e) {
    const cartId = e.currentTarget.dataset.cartId;
    let value = e.detail.value;
    let quantity;
    
    if (value === '') {
      quantity = '';
    } else {
      quantity = parseInt(value);
      if (isNaN(quantity)) {
        quantity = '';
      } else if (quantity > this.data.maxQuantity) {
        quantity = this.data.maxQuantity;
      }
    }
    
    // 只更新本地数据，不调用API
    const cartItems = this.data.cartItems;
    const itemIndex = cartItems.findIndex(item => item.product_id === cartId);
    if (itemIndex !== -1) {
      cartItems[itemIndex].quantity = quantity;
      this.setData({
        cartItems: cartItems
      });
      this.calculateTotal();
    }
  },
  handleQuantityBlur: function(e) {
    const cartId = e.currentTarget.dataset.cartId;
    let value = e.detail.value;
    let quantity;
    
    if (value === '' || isNaN(parseInt(value))) {
      quantity = 1;
    } else {
      quantity = parseInt(value);
      if (quantity < 1) {
        quantity = 1;
      } else if (quantity > this.data.maxQuantity) {
        quantity = this.data.maxQuantity;
        wx.showToast({
          title: `商品数量不能超过${this.data.maxQuantity}`,
          icon: 'none'
        });
      }
    }
    
    // 失去焦点时更新数据库
    this.updateCartItem(cartId, quantity);
  },
  updateCartItem: function(cartId, quantity) {
    this.setData({ loading: true });
    const app = getApp();
    app.request({
      url: `/cart/items`,
      method: 'PUT',
      data: {
        product_id: cartId,
        quantity: quantity
      },
      success: res => {
        if (res.data.code === 200) {
          this.getCartItems();
        } else {
          wx.showToast({
            title: '更新失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，更新失败',
          icon: 'none'
        });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },
  deleteItem: function(e) {
    const cartId = e.currentTarget.dataset.cartId;
    wx.showModal({
      title: '删除商品',
      content: '确定要删除这个商品吗？',
      success: (res) => {
        if (res.confirm) {
          this.setData({ loading: true });
          const app = getApp();
          app.request({
            url: `/cart/items/${cartId}`,
            method: 'DELETE',
            success: res => {
              if (res.data.code === 200) {
                this.getCartItems();
              } else {
                wx.showToast({
                  title: '删除失败',
                  icon: 'none'
                });
              }
            },
            fail: () => {
              wx.showToast({
                title: '网络错误，删除失败',
                icon: 'none'
              });
            },
            complete: () => {
              this.setData({ loading: false });
            }
          });
        }
      }
    });
  },
  navigateToConfirm: function() {
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
    const productIds = this.data.cartItems.map(item => item.product_id).join(',');
    wx.navigateTo({
      url: `/pages/order/confirm?product_ids=${productIds}`
    });
  },
  navigateToHome: function() {
    wx.switchTab({
      url: '/pages/index/index'
    });
  },
  navigateToLogin: function() {
    wx.navigateTo({
      url: '/pages/auth/login'
    });
  }
});