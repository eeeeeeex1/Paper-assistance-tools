import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Login from '../components/Login.vue';
import Home from '../views/Home.vue';
import AdminLogin from '../views/AdminLogin.vue';
import UserManagement from '../components/UserManagement.vue';
import LogManagement from '../components/LogManagement.vue';
import Statistic from '../components/Statistic.vue';


const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: Login
  },
  {
    path: '/home',
    component: Home
  },
  {
    path: '/admin-login',
    component: AdminLogin
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;