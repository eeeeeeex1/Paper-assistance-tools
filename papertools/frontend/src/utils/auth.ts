// src/utils/auth.ts
import axios from 'axios';

export function getToken(): string | null {
  return localStorage.getItem('token'); // 与登录逻辑统一
}

export function setToken(token: string): void {
  localStorage.setItem('token', token);
}

export function removeToken(): void {
  localStorage.removeItem('token');
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

// 登录API
export async function login(email: string, password: string) {
  const response = await axios.post('/api/user/login', { email, password });
  setToken(response.data.token);
  return response.data;
}

// 登出
export function logout(): void {
  removeToken();
  localStorage.removeItem('user');
  // 不需要重复清除localStorage
}

// 刷新Token
export async function refreshToken(): Promise<string> {
  const response = await axios.post<{ token: string }>(
    '/api/user/refresh', 
    { token: getToken() }
  );
  
  const newToken = response.data.token;
  setToken(newToken);
  return newToken;
}

//用户信息获取
export const getCurrentUser = () => {
  const userJson = localStorage.getItem('user');
  if (!userJson) return null;
  
  try {
    const user = JSON.parse(userJson);
    return user;
  } catch (error) {
    console.error('解析用户信息失败:', error);
    return null;
  }
};

export const getAuthorId = () => {
  const user = getCurrentUser();
  return user?.id || null;
};