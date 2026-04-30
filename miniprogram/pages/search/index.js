Page({
  data: {
    keyword: '',
    showResult: false,
    goodsList: [],
    searchHistory: []
  },
  
  onLoad: function(options) {
    // 从URL参数中获取关键词
    if (options.keyword) {
      this.setData({
        keyword: options.keyword
      });
      // 如果有关键词，直接搜索
      this.onSearch();
    } else {
      // 加载搜索历史
      this.loadSearchHistory();
    }
  },
  
  onInput: function(e) {
    this.setData({
      keyword: e.detail.value
    });
  },
  
  onSearch: function() {
    const keyword = this.data.keyword.trim();
    if (!keyword) {
      wx.showToast({
        title: '请输入搜索关键词',
        icon: 'none'
      });
      return;
    }
    
    // 保存搜索历史
    this.saveSearchHistory(keyword);
    
    // 显示搜索结果
    this.setData({
      showResult: true
    });
    
    // 调用搜索接口
    this.searchGoods(keyword);
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
  
  onCancel: function() {
    wx.navigateBack();
  },
  
  navigateToDetail: function(e) {
    const productId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/product/detail?id=${productId}`
    });
  },
  
  // 保存搜索历史
  saveSearchHistory: function(keyword) {
    let history = wx.getStorageSync('searchHistory') || [];
    // 去重
    history = history.filter(item => item !== keyword);
    // 添加到最前面
    history.unshift(keyword);
    // 只保留最近10条
    if (history.length > 10) {
      history = history.slice(0, 10);
    }
    wx.setStorageSync('searchHistory', history);
  },
  
  // 加载搜索历史
  loadSearchHistory: function() {
    const history = wx.getStorageSync('searchHistory') || [];
    this.setData({
      searchHistory: history
    });
  },
  
  // 点击历史记录
  searchHistoryItem: function(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({
      keyword: keyword
    });
    this.onSearch();
  },
  
  // 清空历史记录
  clearHistory: function() {
    wx.removeStorageSync('searchHistory');
    this.setData({
      searchHistory: []
    });
  }
});