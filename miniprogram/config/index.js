// 小程序地址配置

// 环境配置
const env = 'development'; // development 或 production

// 不同环境的地址配置
const config = {
  development: {
    // API基础地址
    apiBaseUrl: 'http://127.0.0.1:8002/api',
    // 图片存储地址
    imageBaseUrl: 'http://localhost:8002/uploads'
  },
  production: {
    // API基础地址
    apiBaseUrl: 'https://api.example.com/api',
    // 图片存储地址
    imageBaseUrl: 'https://api.example.com/uploads'
  }
};

// 导出当前环境的配置
const currentConfig = config[env];

module.exports = {
  // API地址
  api: {
    baseUrl: currentConfig.apiBaseUrl,
    // 具体API地址
    auth: '/user/auth',
    productList: '/product/list',
    productDetail: '/product/detail',
    cartAdd: '/cart/add',
    cartList: '/cart/list',
    cartUpdate: '/cart/update',
    cartDelete: '/cart/delete',
    orderCreate: '/order/create',
    orderList: '/order/list',
    orderDetail: '/order/detail',
    addressList: '/address/list',
    addressAdd: '/address/add',
    addressUpdate: '/address/update',
    addressDelete: '/address/delete',
    addressSetDefault: '/address/set-default',
    bannerList: '/banner/list'
  },
  // 图片地址
  image: {
    baseUrl: currentConfig.imageBaseUrl
  },
  // 环境
  env: env
};