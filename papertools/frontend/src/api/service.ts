import axios from 'axios';

const baseURL = process.env.VITE_API_BASE_URL || '/api';  // 兼容构建工具

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器（用于JWT认证）
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 添加响应拦截器（处理错误）
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const UserService = {
  // 获取用户信息
  getUserInfo: () => api.get('/api/user/info'),
  
  // 用户登录
  login: (credentials: { username: string; password: string }) => 
    api.post('/api/user/login', credentials),
  
  // 用户注册
  register: (userData: { username: string; password: string; email?: string }) => 
    api.post('/api/user/register', userData),
  
  // 删除用户
  deleteUser: (userId: string) => 
    api.delete(`/api/user/${userId}`)
};