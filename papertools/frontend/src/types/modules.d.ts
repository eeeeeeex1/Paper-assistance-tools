// src/types/modules.d.ts,使用非ts文件|生命模块
declare module '*!*.vue' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 声明自定义模块
declare module '../utils/auth' {
  export function getToken(): string | null
  export function setToken(token: string): void
  export function removeToken(): void
  export function isAuthenticated(): boolean
}