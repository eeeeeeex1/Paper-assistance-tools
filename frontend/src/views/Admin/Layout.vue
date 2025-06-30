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
  width: 250px;
  background: linear-gradient(135deg, #304156, #4e6c8e);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding-top: 40px;
  box-shadow: 5px 0 20px rgba(0, 0, 0, 0.15);
}

.menu-item {
  padding: 20px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s ease;
  font-size: 18px;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.menu-item.active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  border-left: 5px solid #fff;
}

.logout-item {
  margin-top: auto;
  padding: 20px;
  cursor: pointer;
  text-align: center;
  background: #ef4444;
  color: white;
  transition: all 0.3s ease;
  font-size: 18px;
}

.logout-item:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
}

.main-content {
  flex: 1;
  padding: 40px;
  background: #f8fafc;
}
</style>