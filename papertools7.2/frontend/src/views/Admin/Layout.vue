<template>
  <div class="layout-container">
    <!-- 左侧导航 -->
    <div class="sidebar">
      <div class="logo-area">
        <h2>管理员后台</h2>
      </div>
      <div class="menu-container">
        <div 
          class="menu-item" 
          v-for="(item, index) in menuList" 
          :key="index" 
          @click="handleMenuClick(item)"
          :class="{ active: currentRoute === item.path }">
          <span class="menu-icon"></span>
          <span class="menu-label">{{ item.label }}</span>
          <span class="menu-arrow">›</span>
        </div>
      </div>
      <div class="logout-container">
        <div class="logout-item" @click="handleLogout">
          <svg class="logout-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M16 17v-3H9v-4h7V7l5 5-5 5M14 2a2 2 0 0 1 2 2v2h-2V4H5v16h9v-2h2v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9z"/>
          </svg>
          <span class="logout-text">退出登录</span>
        </div>
      </div>
    </div>
    <!-- 右侧内容 -->
    <div class="main-content">
      <div class="content-container">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'

const router = useRouter()
const menuList = [
  { label: '用户管理', path: '/admin/user-manage' },
  { label: '日志管理', path: '/admin/log-manage' },
  { label: '数据统计', path: '/admin/statistic'}
]

const currentRoute = computed(() => router.currentRoute.value.path)

const handleMenuClick = (item) => {
  router.push(item.path)
}

const handleLogout = () => {
  // 这里可补充退出登录逻辑（如清除 token、用户信息等）
  console.log('退出登录')
  router.push('/')
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.sidebar {
  width: 280px;
  background: linear-gradient(135deg, #1e293b, #334155);
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  box-shadow: 5px 0 20px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 10;
}

.logo-area {
  padding: 24px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 16px;
}

.logo-area h2 {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  letter-spacing: 1px;
}

.menu-container {
  flex: 1;
  padding: 0 16px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
  transform: translateX(4px);
}

.menu-item.active {
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.2), transparent);
  color: #fff;
  border-left: 3px solid #3b82f6;
}

.menu-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), transparent);
}

.menu-icon {
  margin-right: 12px;
  font-size: 1.1rem;
}

.menu-label {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
}

.menu-arrow {
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
  color: #3b82f6;
  font-size: 1.2rem;
}

.menu-item:hover .menu-arrow {
  opacity: 1;
  transform: translateX(0);
}

.logout-container {
  padding: 20px 16px;
  margin-top: auto;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
  color: #e2e8f0;
  transition: all 0.3s ease;
  border-radius: 6px;
  font-weight: 500;
  gap: 12px;
}

.logout-item:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.logout-icon {
  transition: all 0.3s ease;
  opacity: 0.8;
  width: 20px;
  height: 20px;
}

.logout-item:hover .logout-icon {
  transform: translateX(3px);
  opacity: 1;
}

.logout-text {
  position: relative;
  font-size: 1.05rem; /* 增大字体大小 */
  font-weight: 600; /* 加粗字体 */
}

.logout-text::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 0;
  height: 2px; /* 加粗下划线 */
  background: #ef4444;
  transition: all 0.3s ease;
}

.logout-item:hover .logout-text::after {
  width: 100%;
}

.main-content {
  flex: 1;
  background: #f1f5f9;
  overflow-y: auto;
  position: relative;
}

.content-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* 平滑滚动 */
.main-content {
  scroll-behavior: smooth;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 220px;
  }
  
  .content-container {
    padding: 24px;
  }
  
  .logout-text {
    font-size: 1rem; /* 响应式调整 */
  }
}
</style>