Page({
  data: {
    banners: [],
    goodsList: [],
    loading: true,
    requestCount: 0,
    searchKeyword: ''
  },
  
  onLoad: function() {
    console.log('页面加载，开始获取数据');
    try {
      this.getBanners();
      this.getAllGoods();
    } catch (error) {
      console.log('onLoad错误:', error);
    }
  },
  
  // 检查所有请求是否完成
  checkAllRequestsComplete: function() {
    this.setData({
      requestCount: this.data.requestCount + 1
    });
    console.log('请求完成数:', this.data.requestCount);
    if (this.data.requestCount >= 2) {
      console.log('所有请求完成，隐藏加载状态');
      this.setData({ loading: false });
    }
  },
  
  getBanners: function() {
    const app = getApp();
    app.request({
      url: '/banner/list',
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            banners: res.data.data || []
          });
        } else {
          wx.showToast({
            title: '获取轮播图失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，获取轮播图失败',
          icon: 'none'
        });
      },
      complete: () => {
        this.checkAllRequestsComplete();
      }
    });
  },
  
  getAllGoods: function() {
    const app = getApp();
    app.request({
      url: '/product/list',
      method: 'GET',
      data: {
        page: 1,
        size: 100
      },
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            goodsList: res.data.data.list || []
          });
        } else {
          wx.showToast({
            title: '获取商品列表失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，获取商品列表失败',
          icon: 'none'
        });
      },
      complete: () => {
        this.checkAllRequestsComplete();
      }
    });
  },
  
  handleSearch: function() {
    const that = this;
    wx.navigateTo({
      url: '/pages/search/index?keyword=' + that.data.searchKeyword
    });
  },
  
  searchGoods: function(keyword) {
    const app = getApp();
    app.request({
      url: '/product/list',
      method: 'GET',
      data: {
        page: 1,
        size: 100,
        keyword: keyword
      },
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            goodsList: res.data.data.list || []
          });
        } else {
          wx.showToast({
            title: '搜索商品失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，搜索商品失败',
          icon: 'none'
        });
      }
    });
  },
  
  navigateToDetail: function(e) {
    const productId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/product/detail?id=${productId}`
    });
  }
});