// src/types/router.d.ts定义路由元数据类型
import { RouteMeta } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta extends Record<string, any> {
    requiresAuth?: boolean // 路由是否需要认证
  }
}