import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Login from '../components/Login.vue';
import Home from '../views/Home.vue';
import AdminLogin from '../views/AdminLogin.vue';
import Layout from '../components/Layout.vue';
import UserManage from '../views/UserManage.vue';
import LogManage from '../views/LogManage.vue';    
import Statistic from '../views/Statistic.vue';
import Register from '../../components/Register.vue';


const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: Login
  },
  {
    path: '/',
    component: Layout,
    children: [
      { path: 'user-manage', component: UserManage, name: 'UserManage' },
      { path: 'log-manage', component: LogManage, name: 'LogManage' },
      { path: 'statistic', component: Statistic, name: 'Statistic' },
      { path: '', redirect: '/user-manage' }  
    ]
  },
   {
    path: '/register',
    name: 'Register',
    component: Register
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