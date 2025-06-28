import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Login from '../components/Login.vue';
//主界面
import Home from '../views/Home.vue';
import SimilarityCheck from '../views/home/SimilarityCheck.vue';
import SpellCheck from '../views/home/SpellCheck.vue';
import TextSummary from '../views/home/TextSummary.vue';
import OperationHistory from '../views/home/OperationHistory.vue';
//管理员界面
import AdminLogin from '../views/AdminLogin.vue';
import Layout from '../components/Layout.vue';
import LogManage from '../views/LogManage.vue';
import Statistic from '../views/Statistic.vue';
import UserManage from '../views/UserManage.vue';
import Register from '../components/Register.vue';

const routes: Array<RouteRecordRaw> = [
  // 登录页（根路径）
  {
    path: '/',
    name: 'Login', // 添加命名路由
    component: Login
  },
  
  // 用户主页（需要认证）
  {
    path: '/home',
    component: Home,
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

export default router;