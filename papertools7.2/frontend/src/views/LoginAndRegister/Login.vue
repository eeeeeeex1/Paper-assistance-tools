<template>
   <div class="login-container">
    <div class="login-wrapper">
      <!-- 左侧项目介绍区域 -->
      <div class="project-intro">
        <div class="particles-background"></div>
        <div class="intro-content">
          <h2 class="intro-title">万卷书</h2>
          <p class="intro-desc">
            这是一个专业的论文辅助工具系统，致力于为用户提供高效、好用的论文处理方案。系统集成了多种功能模块，帮助用户轻松处理各类需求。
          </p>
          <ul class="features-list">
            <li 
              class="feature-item"
              :style="{ transitionDelay: '0.1s' }"
            >
              <i class="iconfont icon-security"></i>
              <span>安全可靠的用户认证体系</span>
            </li>
            <li 
              class="feature-item"
              :style="{ transitionDelay: '0.2s' }"
            >
              <i class="iconfont icon-efficiency"></i>
              <span>高效便捷的业务处理流程</span>
            </li>
            <li 
              class="feature-item"
              :style="{ transitionDelay: '0.3s' }"
            >
              <i class="iconfont icon-data"></i>
              <span>全面的数据统计与分析</span>
            </li>
          </ul>
        </div>
      </div>
      <!-- 右侧登录表单区域 -->
      <div class="login-form">
        <div class="floating-elements">
          <div class="floating-circle circle-1"></div>
          <div class="floating-circle circle-2"></div>
        </div>
        
        <h2 class="title">欢迎登录</h2>
        <div class="avatar-container">
          <div class="avatar">
            <i class="iconfont icon-user"></i>
          </div>
          <div class="avatar-ring"></div>
        </div>
        
        <div class="form-group">
          <label for="email" class="form-label">账号</label>
          <div class="input-group">
            <i class="iconfont icon-user"></i>
            <input
              type="text"
              id="email"
              v-model="email"
              placeholder="请输入账号"
              class="form-input"
              :class="{ 'is-error': emailError }"
            >
            <div v-if="emailError" class="error-message">{{ emailError }}</div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="password" class="form-label">密码</label>
          <div class="input-group">
            <i class="iconfont icon-lock"></i>
            <input
              type="password"
              id="password"
              v-model="password"
              placeholder="请输入密码"
              class="form-input"
              :class="{ 'is-error': passwordError }"
            >
            <i class="iconfont icon-eye" @click="togglePassword"></i>
            <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
          </div>
        </div>
        
        <div class="btn-group">
          <button
            class="login-btn btn-ripple"
            @click="handleLogin"
            :disabled="isFormInvalid"
            :class="{ 'btn-loading': isLoading }"
          >
            <span v-if="!isLoading">登 录</span>
            <span v-else class="loading-spinner"></span>
          </button>
        </div>
        
        <div class="footer-links">
          <a @click="openRegisterModal">注册账号</a>
          <span>|</span>
          <a @click="goAdminLogin">管理员登录</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import {setToken} from '../../utils/auth'
import { ElMessage } from 'element-plus';

// 定义API基础路径（使用环境变量）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const email = ref('');
const password = ref('');
const updated_at = ref('')
const emailError = ref('');
const passwordError = ref('');
const showPassword = ref(false);
const isLoading = ref(false);
const router = useRouter();

// 表单验证逻辑
const validateLoginForm = (): boolean => {
  let isValid = true;
  emailError.value = '';
  passwordError.value = '';

if (!email.value.trim()) {
    emailError.value = '邮箱不能为空';
    isValid = false;
  }

  if (password.value.length < 6) {
    passwordError.value = '密码长度至少为6位';
    isValid = false;
  }

  return isValid;
};

// 切换密码可见性
const togglePassword = () => {
  showPassword.value = !showPassword.value;
  const input = document.getElementById('password') as HTMLInputElement;
  input.type = showPassword.value ? 'text' : 'password';
};

// 登录逻辑
const handleLogin = async () => {
  isLoading.value = true;
  passwordError.value = '';

  try {
    // 表单验证
    if (!validateLoginForm()) {
      throw new Error('表单验证失败');
    }

    // 添加请求超时设置，避免长时间等待
    const response = await axios.post<{
      message: string;
      token: string;
      user: {
        id: number;
        username: string;
        email: string;
        permission: number;
      };
    }>(`${API_BASE_URL}/api/user/login`, {
      email: email.value,
      password: password.value,
    }, {
      timeout: 10000 // 设置10秒超时
    });
    
    // 处理登录成功
    console.log('登录响应：', response.data);

    // 处理登录成功
    if (response.status >= 200 && response.status < 300) {
      // 存储用户信息和token
      setToken(response.data.token); // 调用 auth.ts 的 setToken
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      // 显示成功消息并跳转
      //ElMessage.success('登录成功，正在跳转...');
      await router.push('/home'); // 确保跳转完成
    } else {
      emailError.value = response.data.message || '登录失败，请重试';
    }
  } catch (error: any) {
    console.error('登录请求出错：', error);
    
    // 处理不同类型的错误
    if (error.response?.status === 401) {
      emailError.value = '用户名/邮箱或密码错误';
    } else if (error.response?.status === 400) {
      emailError.value = error.response.data.message || '无效的请求';
    } else {
      emailError.value = '登录失败，请稍后再试';
    }
  } finally {
    isLoading.value = false;
  }
};

// 注册逻辑
const openRegisterModal = () => {
  router.push('/register');
};

// 管理员登录页面跳转
const goAdminLogin = () => {
  router.push('/admin/login');
};

// 禁用按钮计算属性
const isFormInvalid = computed(() => {
  return !email.value.trim() || password.value.length < 6 || isLoading.value;
});

// 页面加载动画
onMounted(() => {
  const form = document.querySelector('.login-form');
  if (form) {
    form.classList.add('fade-in');
  }
});

</script>


<style scoped>
/* 基础样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.login-container {
  width: 100%;
  height: 100vh;
  background: #fcfffb;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-wrapper {
  display: flex;
  flex-direction: row;
  width: 100%;
  max-width: 1000px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* 左侧项目介绍区域 */
.project-intro {
  flex: 1;
  position: relative;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #fff;
  overflow: hidden;
}

.particles-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #56e688 0%, #45b1f0 100%);
  z-index: 0;
}

.particles-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: radial-gradient(circle at 20% 30%, rgba(255,255,255,0.1) 0%, transparent 20%),
                    radial-gradient(circle at 80% 70%, rgba(255,255,255,0.1) 0%, transparent 20%);
  animation: particles-move 20s infinite alternate;
}

@keyframes particles-move {
  0% { transform: translate(0, 0); }
  100% { transform: translate(20px, 20px); }
}

.intro-content {
  position: relative;
  z-index: 1;
}

.intro-title {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 20px;
  line-height: 1.3;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.intro-desc {
  font-size: 15px;
  margin-bottom: 40px;
  line-height: 1.7;
  opacity: 0.9;
}

.features-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 15px;
  opacity: 0;
  transform: translateX(-20px);
  animation: fadeIn 0.5s forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.feature-item i {
  font-size: 22px;
  color: rgba(255,255,255,0.9);
}

/* 右侧登录表单区域 */
.login-form {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.floating-elements {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  z-index: 0;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(102, 126, 234, 0.05);
  animation: float 15s infinite ease-in-out;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -50px;
  right: -50px;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: -30px;
  left: -30px;
  animation-delay: 5s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, 20px) scale(1.05); }
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #2c3e50;
  font-size: 26px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.avatar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
}

.avatar {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #37e9c5, #1239e7);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 40px;
  box-shadow: 0 8px 25px rgba(85, 180, 221, 0.4);
  transition: all 0.4s ease;
  position: relative;
  z-index: 1;
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(66, 206, 234, 0.5);
}

.avatar-ring {
  position: absolute;
  width: 120px;
  height: 120px;
  border: 2px dashed rgba(76, 205, 244, 0.4);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: spin 15s linear infinite;
}

@keyframes spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.form-group {
  margin-bottom: 28px;
  position: relative;
  z-index: 1;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #555;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-group i {
  position: absolute;
  left: 15px;
  color: #909399;
  font-size: 18px;
  transition: all 0.3s ease;
}

.input-group .icon-eye {
  right: 15px;
  left: auto;
  cursor: pointer;
  color: #c0c4cc;
}

.input-group .icon-eye:hover {
  color: #66d2ea;
}

.form-input {
  width: 100%;
  padding: 14px 15px 14px 45px;
  border: 1px solid #e6e8eb;
  border-radius: 8px;
  background-color: #f9fafc;
  color: #333;
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: #66c7ea;
  background-color: #fff;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.form-input.is-error {
  border-color: #ff6b6b;
}

.form-input.is-error + .iconfont {
  color: #ff6b6b;
}

.error-message {
  position: absolute;
  bottom: -20px;
  left: 0;
  color: #ff6b6b;
  font-size: 12px;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.btn-group {
  margin: 30px 0 20px;
  position: relative;
  z-index: 1;
}

.login-btn {
  width: 100%;
  padding: 14px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, hwb(139 45% 2%), #3cb6e6);
  color: #edf4f7;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(28, 110, 181, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.btn-ripple:after {
  content: "";
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, #fff 10%, transparent 10.01%);
  background-repeat: no-repeat;
  background-position: 50%;
  transform: scale(10, 10);
  opacity: 0;
  transition: transform .5s, opacity 1s;
}

.btn-ripple:active:after {
  transform: scale(0, 0);
  opacity: .3;
  transition: 0s;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  font-size: 13px;
  color: #909399;
  position: relative;
  z-index: 1;
}

.footer-links a {
  color: #87c3e3;
  cursor: pointer;
  transition: all 0.2s ease;
}

.footer-links a:hover {
  color: #4b7ca2;
  text-decoration: underline;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
  }

  .project-intro,
  .login-form {
    padding: 40px 30px;
  }

  .project-intro {
    order: 2;
    text-align: center;
  }

  .features-list {
    align-items: center;
  }
  
  .intro-title {
    font-size: 28px;
  }
  
  .title {
    font-size: 24px;
  }
}
</style>
