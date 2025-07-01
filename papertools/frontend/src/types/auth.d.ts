// src/types/auth.d.ts定义类型
declare namespace Auth {
  interface UserInfo {
    id: number
    username: string
    email: string
  }
  
  interface LoginResponse {
    token: string
    user: UserInfo
  }
}