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

<script setup>
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'

const router = useRouter()
const menuList = [
  { label: '用户管理界面', path: '/admin/user-manage' },
  { label: '日志管理界面', path: '/admin/log-manage' },
  { label: '统计界面', path: '/admin/statistic' }
]

const currentRoute = computed(() => router.currentRoute.value.path)

const handleMenuClick = (item) => {
  router.push(item.path)
}

const handleLogout = () => {
  // 这里可补充退出登录逻辑（如清除 token、用户信息等）
  console.log('退出登录')
  // 新增跳转逻辑
  router.push('/')
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
}
.menu-item.active {
  background: #66b1ff;
}
.logout-item {
  margin-top: auto;
  padding: 16px;
  cursor: pointer;
  text-align: center;
  background: #3a8ee6;
}
.main-content {
  flex: 1;
  padding: 20px;
  background: #f0f2f5;
}
</style>