// Web前端地址配置

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

export default {
  // API地址
  api: {
    baseUrl: currentConfig.apiBaseUrl,
    // 具体API地址
    login: '/admin/login',
    dashboard: '/admin/dashboard',
    productList: '/admin/product/list',
    productAdd: '/admin/product/add',
    productUpdate: '/admin/product/update',
    productDelete: '/admin/product/delete',
    categoryList: '/admin/category/list',
    categoryAdd: '/admin/category/add',
    categoryUpdate: '/admin/category/update',
    categoryDelete: '/admin/category/delete',
    userList: '/admin/user/list',
    orderList: '/admin/order/list',
    orderDetail: '/admin/order/detail',
    orderUpdate: '/admin/order/update',
    payList: '/admin/pay/list',
    bannerList: '/admin/banner/list',
    bannerAdd: '/admin/banner/add',
    bannerUpdate: '/admin/banner/update',
    bannerDelete: '/admin/banner/delete',
    statistics: '/admin/statistics'
  },
  // 图片地址
  image: {
    baseUrl: currentConfig.imageBaseUrl
  },
  // 环境
  env: env
};