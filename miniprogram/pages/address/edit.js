Page({
  data: {
    isEdit: false,
    addressId: null,
    formData: {
      name: '',
      phone: '',
      province: '',
      city: '',
      district: '',
      detail: '',
      is_default: false
    },
    loading: false
  },

  onLoad: function(options) {
    if (options.id && options.address) {
      this.setData({
        isEdit: true,
        addressId: options.id,
        formData: JSON.parse(decodeURIComponent(options.address))
      });
    }
  },

  // 处理默认地址选择
  onDefaultChange: function(e) {
    this.setData({
      'formData.is_default': e.detail.value.length > 0
    });
  },

  // 提交表单
  submitForm: function(e) {
    const { name, phone, province, city, district, detail } = e.detail.value;
    
    // 表单验证
    if (!name) {
      wx.showToast({ title: '请输入收货人姓名', icon: 'none' });
      return;
    }
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' });
      return;
    }
    if (!province) {
      wx.showToast({ title: '请输入省份', icon: 'none' });
      return;
    }
    if (!city) {
      wx.showToast({ title: '请输入城市', icon: 'none' });
      return;
    }
    if (!district) {
      wx.showToast({ title: '请输入区县', icon: 'none' });
      return;
    }
    if (!detail) {
      wx.showToast({ title: '请输入详细地址', icon: 'none' });
      return;
    }
    
    this.setData({ loading: true });
    const app = getApp();
    const url = this.data.isEdit ? `/address/${this.data.addressId}` : '/address/';
    const method = this.data.isEdit ? 'PUT' : 'POST';
    
    app.request({
      url: url,
      method: method,
      data: {
        name: name,
        phone: phone,
        province: province,
        city: city,
        district: district,
        detail: detail,
        is_default: this.data.formData.is_default
      },
      success: (res) => {
        if (res.data.code === 200) {
          wx.showToast({ 
            title: this.data.isEdit ? '修改成功' : '添加成功',
            success: () => {
              wx.navigateBack();
            }
          });
        } else {
          wx.showToast({ title: '操作失败', icon: 'none' });
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
});
