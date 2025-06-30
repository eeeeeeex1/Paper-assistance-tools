// src/utils/axios.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { refreshToken,getToken,removeToken } from './auth'

const router = useRouter()

// 创建axios实例
const service = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    config.headers = config.headers || {}; 
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response
  },
  async error => {
    const { response } = error
    
    // 401未授权错误
    if (response && response.status === 401) {
      ElMessage.error('登录状态已过期，请重新登录')
      
      // 清除Token并跳转到登录页
      removeToken()
      router.push('/login')
    } 
    // 403禁止访问
    else if (response && response.status === 403) {
      ElMessage.error('没有访问权限')
    }
    
    return Promise.reject(error)
  }
)

export default service