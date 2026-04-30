Page({
  data: {
    categories: [],
    activeCategoryId: 1,
    categoryGoods: []
  },
  onLoad: function(options) {
    const categoryId = options.id || 1;
    this.setData({
      activeCategoryId: parseInt(categoryId)
    });
    this.getCategories();
    this.getCategoryGoods(parseInt(categoryId));
  },
  getCategories: function() {
    const app = getApp();
    app.request({
      url: '/product/category/list',
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            categories: res.data.data
          });
        } else {
          wx.showToast({
            title: '获取分类列表失败',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，获取分类列表失败',
          icon: 'none'
        });
      }
    });
  },
  getCategoryGoods: function(categoryId) {
    const app = getApp();
    app.request({
      url: '/product/list',
      method: 'GET',
      data: {
        category_id: categoryId,
        page: 1,
        size: 20
      },
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            categoryGoods: res.data.data.list
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
      }
    });
  },
  selectCategory: function(e) {
    const categoryId = e.currentTarget.dataset.id;
    this.setData({
      activeCategoryId: categoryId
    });
    this.getCategoryGoods(categoryId);
  },
  navigateToDetail: function(e) {
    const productId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/product/detail?id=${productId}`
    });
  }
});