<template>
  <div class="layout-container">
    <!-- 左侧导航 -->
    <div class="sidebar">
      <div class="menu-item" 
           v-for="(item, index) in menuList" 
           :key="index" 
           @click="handleMenuClick(item)"
           :class="{ active: currentRoute === item.path }">
        {{ item.label }}
      </div>
      <div class="logout-item" @click="handleLogout">退出登录</div>
    </div>
    <!-- 右侧内容 -->
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

// 定义菜单项类型
interface MenuItem {
  label: string
  path: string
}

const router = useRouter()
const route = useRoute()

const menuList: MenuItem[] = [
  { label: '用户管理界面', path: '/user-manage' },
  { label: '日志管理界面', path: '/log-manage' },
  { label: '统计界面', path: '/statistic' }
]

// 获取当前路由路径
const currentRoute = computed(() => route.path)

// 菜单点击处理
const handleMenuClick = (item: MenuItem) => {
  router.push(item.path as RouteLocationRaw)
}

// 退出登录处理
const handleLogout = () => {
  // 清除本地存储
  localStorage.removeItem('token')
  localStorage.removeItem('userInfo')
  
  // 跳转到登录页
  router.push('/login')
  
  // 可选：强制刷新页面
  // window.location.reload()
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
}
.sidebar {
  width: 200px;
  background: #409eff;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding-top: 20px;
}
.menu-item {
  padding: 16px;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.3s;
}
.menu-item:hover {
  background: #66b1ff;
}
.menu-item.active {
  background: #66b1ff;
  font-weight: bold;
}
.logout-item {
  margin-top: auto;
  padding: 16px;
  cursor: pointer;
  text-align: center;
  background: #3a8ee6;
  transition: background-color 0.3s;
}
.logout-item:hover {
  background: #1d78d8;
}
.main-content {
  flex: 1;
  padding: 20px;
  background: #f0f2f5;
  overflow-y: auto;
}
</style>