import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import Login from '../components/Login.vue';
import Home from '../views/Home.vue';
import SimilarityCheck from '.../src/views/home/SimilarityCheck.vue';
import SpellCheck from '.../src/views/home/SpellCheck.vue';
import TextSummary from '.../src/views/home/TextSummary.vue';
import OperationHistory from '.../src/views/home/OperationHistory.vue';
import AdminLogin from '../src/views/AdminLogin.vue';
import AdminDashboard from '../src/views/AdminDashboard.vue';
///import UserManagement from '../components/UserManagement.vue';
//import LogManagement from '../components/LogManagement.vue';
//import Statistic from '../components/Statistic.vue';


const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: Login   //登录界面
  },
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
  {
    path: '/admin-login',
    component: AdminLogin   //管理员登录界面
  },
  {
    path:'/admin-dashboard',
    component: AdminDashboard,  //管理员界面
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;