import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
//登录注册界面
import Login from '@/views/LoginAndRegister/Login.vue';
import Register from '@/views/LoginAndRegister/Register.vue';
//主界面
import Home from '@/views/home/Home.vue';
import SimilarityCheck from '@/views/home/SimilarityCheck.vue';
import SpellCheck from '@/views/home/SpellCheck.vue';
import TextSummary from '@/views/home/TextSummary.vue';
import OperationHistory from '../views/home/OperationHistory.vue';
//管理员界面
import AdminLogin from '@/views/Admin/AdminLogin.vue';
import Layout from '@/views/Admin/Layout.vue';
import LogManage from '@/views/Admin/LogManage.vue';
import Statistic from '@/views/Admin/Statistic.vue';
import UserManage from '@/views/Admin/UserManage.vue';
import { getToken } from '@/utils/auth'
import { isAuthenticated } from '@/utils/auth'; // 导入优化后的认证检查

const routes: Array<RouteRecordRaw> = [
  // 登录页（根路径）
  {
    path: '/',
    name: 'Login', // 添加命名路由
    component: Login
  },
   // 显式添加/login路径，指向同一个登录组件
  {
    path: '/login',
    name: 'LoginRedirect', // 使用不同的名称避免冲突
    component: Login
  },
  // 用户主页（需要认证）
  {
    path: '/home',
    name:'Home',
    component: Home,
    meta: { requiresAuth: true }, // 标记需要认证的路由
    children: [
      { path: 'similarity', name: 'Similarity', component: SimilarityCheck },
      { path: 'spellcheck', name: 'SpellCheck', component: SpellCheck },
      { path: 'summary', name: 'Summary', component: TextSummary },
      { path: 'history', name: 'History', component: OperationHistory }
    ]
  },
  
  // 管理员界面（需要权限）
  {
    path: '/admin',
    component: Layout,
    children: [
      { path: 'user-manage', component: UserManage, name: 'UserManage' },
      { path: 'log-manage', component: LogManage, name: 'LogManage' },
      { path: 'statistic', component: Statistic, name: 'Statistic' },
      { path: '', redirect: '/admin/user-manage' }  //管理员默认页
    ]
  },
  
  // 其他页面
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 全局前置守卫 - 验证路由访问权限
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('token');
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } else if (to.path === '/login' && isLoggedIn) {
    next('/home'); // 已登录时访问登录页，重定向到主页
  } else {
    next(); // 正常放行
  }
});

export default router;