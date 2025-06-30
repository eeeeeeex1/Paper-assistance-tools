<template>
  <div class="home-container">
    <!-- 侧边导航栏 (保持原样) -->
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <i class="iconfont icon-document"></i>
          <span>文本智能处理</span>
        </div>
      </div>

      <nav class="sidebar-menu">
        <div 
          v-for="item in menuItems" 
          :key="item.path"
          class="menu-item"
          :class="{ active: activeMenu === item.path }"
          @click="navigateTo(item.path)"
        >
          <div class="menu-icon">
            <i :class="`iconfont ${item.icon}`"></i>
          </div>
          <span class="menu-text">{{ item.title }}</span>
        </div>
      </nav>

      <div class="sidebar-footer" @click="handleLogout">
        <i class="iconfont icon-logout"></i>
        <span>退出登录</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 用户界面提示放在页面顶部 -->
      <div class="user-interface-header">
        <h2>用户界面</h2>
      </div>

      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>

      <!-- 默认欢迎页 - 上下两行布局 -->
      <div v-if="activeMenu === '/home'" class="welcome-container">
        <div class="welcome-card">
          <h1>欢迎使用智能文本处理系统</h1>
          <p>请从左侧菜单选择您需要的功能</p>
          
          <!-- 第一行两个功能 -->
          <div class="features-row top-row">
            <div 
              v-for="item in topFeatures" 
              :key="item.path"
              class="feature-card"
              @click="navigateTo(item.path)"
            >
              <div class="feature-icon" :style="{ backgroundColor: item.color }">
                <i :class="`iconfont ${item.icon}`"></i>
              </div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </div>
          
          <!-- 第二行两个功能 -->
          <div class="features-row bottom-row">
            <div 
              v-for="item in bottomFeatures" 
              :key="item.path"
              class="feature-card"
              @click="navigateTo(item.path)"
            >
              <div class="feature-icon" :style="{ backgroundColor: item.color }">
                <i :class="`iconfont ${item.icon}`"></i>
              </div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed,onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { logout } from '@/utils/auth';

const router = useRouter();
const route = useRoute();
const activeMenu = ref('/home');

// 菜单项配置
const menuItems = [
  { 
    path: '/home/similarity', 
    title: '论文相似度', 
    icon: 'icon-similarity',
    description: '检测文本相似度，避免抄袭风险',
    color: '#64b5f6'
  },
  { 
    path: '/home/spellcheck', 
    title: '错字纠正', 
    icon: 'icon-spellcheck',
    description: '自动检测并修正文本中的错别字',
    color: '#66bb6a'
  },
  { 
    path: '/home/summary', 
    title: '主题总结', 
    icon: 'icon-summary',
    description: '从长文本中提取关键信息和摘要',
    color: '#ba68c8'
  },
  { 
    path: '/home/history', 
    title: '操作记录', 
    icon: 'icon-history',
    description: '查看您的历史操作和结果',
    color: '#ffb74d'
  }
];

// 将功能分为上下两行
const topFeatures = computed(() => menuItems.slice(0, 2));
const bottomFeatures = computed(() => menuItems.slice(2, 4));

// 监听路由变化
watch(() => route.path, (newPath) => {
  activeMenu.value = newPath;
}, { immediate: true });

// 导航到指定页面
const navigateTo = (path: string) => {
  router.push(path);
};

// 组件挂载后执行
onMounted(() => {
  console.log('Home 组件已挂载');
  
  // 示例：检查用户权限
  checkUserPermissions();
  
  // 示例：显示欢迎消息（仅首次加载时）
  //ElMessage.success('欢迎回来！');
});

// 检查用户权限
const checkUserPermissions = () => {
  try {
    // 获取并解析用户信息
    const userStr = localStorage.getItem('user');
    let user = null;
    
    // 如果 userStr 存在且不是 JWT 格式，则尝试解析为 JSON
    if (userStr && !userStr.startsWith('eyJ')) {
      user = JSON.parse(userStr);
    } else if (userStr) {
      // 如果是 JWT 格式，尝试解码
      user = decodeJwt(userStr);
    }
    
    // 获取令牌（不解码，直接使用）
    const token = localStorage.getItem('token');
    
    // 验证用户和令牌
    if (!user || !token) {
      throw new Error('用户信息或令牌缺失');
    }
    
    // 检查令牌有效性
    if (!isTokenValid(token)) {
      throw new Error('令牌无效或已过期');
    }
    
    console.log('用户已登录:', user);
  } catch (error) {
    console.error('权限检查失败:', error);
    ElMessage.warning('请先登录');
    router.push('/login');
  }
};

// 解码 JWT 令牌
const decodeJwt = (token: string) => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    
    // 解码 payload 部分
    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('解码 JWT 失败:', error);
    logout();
    router.push('/login');
  }
};

// 验证令牌有效性
const isTokenValid = (token: string) => {
  if (!token) return false;
  
  try {
    const decoded = decodeJwt(token);
    if (!decoded || !decoded.exp) return false;
    
    // 检查过期时间（单位：秒）
    return Date.now() < decoded.exp * 1000;
  } catch (error) {
    console.error('验证令牌失败:', error);
    return false;
  }
};
// 退出登录
const handleLogout = () => {
  logout();
  console.log(localStorage.getItem('user'));
  console.log(localStorage.getItem('token'));
  setTimeout(() => {
    router.push('/login').then(() => {
       window.location.reload();
   });
  }, 100);
}

</script>

<style scoped>
/* 基础样式 */
.home-container {
  display: flex;
  height: 100vh;
  background-color: #f8fafc;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 侧边栏样式 (保持原样) */
.sidebar {
  width: 220px;
  background: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  z-index: 10;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
}

.logo i {
  font-size: 24px;
  color: #4f46e5;
}

.sidebar-menu {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.menu-item:hover {
  background-color: #f1f5f9;
}

.menu-item.active {
  background-color: #eef2ff;
}

.menu-item.active .menu-text {
  color: #4f46e5;
  font-weight: 500;
}

.menu-item.active .menu-icon i {
  color: #4f46e5;
}

.menu-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.menu-icon i {
  font-size: 20px;
  color: #64748b;
}

.menu-text {
  flex: 1;
  color: #334155;
  font-size: 0.95rem;
}

.sidebar-footer {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-top: 1px solid #f1f5f9;
  color: #64748b;
  cursor: pointer;
  transition: all 0.3s;
}

.sidebar-footer:hover {
  color: #ef4444;
}

.sidebar-footer i {
  margin-right: 12px;
  font-size: 20px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  overflow-y: auto;
  background-color: #f8fafc;
  padding: 0 2rem;
}

/* 用户界面标题 */
.user-interface-header {
  padding: 1.5rem 0;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
}

.user-interface-header h2 {
  color: #1e293b;
  font-size: 1.5rem;
  margin: 0;
}

/* 欢迎页面 */
.welcome-container {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  text-align: center;
  margin-top: 1rem;
}

.welcome-card h1 {
  font-size: 1.8rem;
  color: #1e293b;
  margin-bottom: 1rem;
}

.welcome-card p {
  color: #64748b;
  margin-bottom: 2rem;
}

/* 功能卡片布局 */
.features-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  justify-content: center;
}

.top-row {
  margin-top: 1rem;
}

.bottom-row {
  margin-bottom: 0;
}

.feature-card {
  flex: 1;
  min-width: 280px;
  max-width: 380px;
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  color: white;
}

.feature-icon i {
  font-size: 28px;
}

.feature-card h3 {
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .features-row {
    flex-wrap: wrap;
  }
  
  .feature-card {
    min-width: calc(50% - 1rem);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }
  
  .logo span,
  .menu-text,
  .sidebar-footer span {
    display: none;
  }
  
  .menu-icon {
    margin-right: 0;
  }
  
  .feature-card {
    min-width: 100%;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0 1rem;
  }
  
  .user-interface-header {
    padding: 1rem 0;
  }
  
  .welcome-card {
    padding: 1.5rem 1rem;
  }
  
  .feature-icon {
    width: 50px;
    height: 50px;
    margin-bottom: 1rem;
  }
}
</style>