// API请求工具
import axios from 'axios';
import config from '../config';

// 创建axios实例
const apiClient = axios.create({
  baseURL: config.api.baseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    // 从本地存储获取token
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    // 处理错误
    if (error.response) {
      // 服务器返回错误
      switch (error.response.status) {
        case 401:
          // 未授权，跳转到登录页
          window.location.href = '/login';
          break;
        case 403:
          // 禁止访问
          console.error('禁止访问');
          break;
        case 404:
          // 资源不存在
          console.error('资源不存在');
          break;
        case 500:
          // 服务器错误
          console.error('服务器错误');
          break;
        default:
          console.error('请求失败');
      }
    } else if (error.request) {
      // 请求发送成功但没有收到响应
      console.error('网络错误，请检查网络连接');
    } else {
      // 请求配置出错
      console.error('请求配置出错');
    }
    return Promise.reject(error);
  }
);

// 导出API请求方法
export default {
  // GET请求
  get(url, params = {}) {
    return apiClient.get(url, { params });
  },
  
  // POST请求
  post(url, data = {}) {
    return apiClient.post(url, data);
  },
  
  // PUT请求
  put(url, data = {}) {
    return apiClient.put(url, data);
  },
  
  // DELETE请求
  delete(url, params = {}) {
    return apiClient.delete(url, { params });
  },
  
  // 上传文件
  upload(url, formData) {
    return apiClient.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};