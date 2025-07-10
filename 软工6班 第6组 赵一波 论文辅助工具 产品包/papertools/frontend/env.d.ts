/// <reference types="vite/client" />
declare module '@/utils/auth' 
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  // 其他环境变量...
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}