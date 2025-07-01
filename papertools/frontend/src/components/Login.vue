<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- 左侧项目介绍区域 -->
      <div class="project-intro">
        <h2 class="intro-title">项目名称</h2>
        <p class="intro-desc">
          这是一个专业的管理系统，致力于为企业提供高效、安全的管理解决方案。系统集成了多种功能模块，帮助用户轻松处理各类业务需求。
        </p>
        <ul class="features-list">
          <li class="feature-item">
            <i class="iconfont icon-security"></i>
            <span>安全可靠的用户认证体系</span>
          </li>
          <li class="feature-item">
            <i class="iconfont icon-efficiency"></i>
            <span>高效便捷的业务处理流程</span>
          </li>
          <li class="feature-item">
            <i class="iconfont icon-data"></i>
            <span>全面的数据统计与分析</span>
          </li>
        </ul>
      </div>

      <!-- 右侧登录表单区域 -->
      <div class="login-form">
        <h2 class="title">用户登录</h2>
        <div class="avatar-container">
          <div class="avatar"></div>
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
            class="login-btn"
            @click="handleLogin"
            :disabled="isFormInvalid"
            :class="{ 'btn-loading': isLoading }"
          >
            <span v-if="!isLoading">登录</span>
            <span v-else class="loading-spinner"></span>
          </button>
          <button
            class="register-btn"
            @click="openRegisterModal"
          >注册</button>
        </div>
        <button
          class="admin-login-btn"
          @click="goAdminLogin"
        >
          管理员登录页面
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import {setToken} from '../utils/auth'
import { ElMessage } from 'element-plus';

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
      };
    }>('http://localhost:5000/api/user/login', {
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
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
}

.login-container {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-wrapper {
  display: flex;
  flex-direction: row;
  width: 100%;
  max-width: 1200px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 左侧项目介绍区域 */
.project-intro {
  flex: 1;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.intro-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 20px;
  line-height: 1.3;
}

.intro-desc {
  font-size: 16px;
  margin-bottom: 40px;
  line-height: 1.7;
  opacity: 0.9;
}

.features-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.feature-item i {
  font-size: 24px;
  margin-top: 2px;
}

/* 右侧登录表单区域 */
.login-form {
  flex: 1;
  padding: 60px 50px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 28px;
  font-weight: 700;
}

.avatar-container {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
  position: relative;
}

.avatar {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 48px;
  box-shadow: 0 6px 30px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 35px rgba(64, 158, 255, 0.4);
}

.form-group {
  margin-bottom: 30px;
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
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
  transition: all 0.2s ease;
}

.input-group .icon-eye {
  right: 15px;
  left: auto;
  cursor: pointer;
}

.form-input {
  width: 100%;
  padding: 16px 15px 16px 45px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  background-color: #fff;
  color: #606266;
  font-size: 14px;
  transition: all 0.3s ease;
  outline: none;
}

.form-input:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.form-input.is-error {
  border-color: #f56c6c;
}

.form-input.is-error + .iconfont {
  color: #f56c6c;
}

.error-message {
  position: absolute;
  bottom: -22px;
  left: 0;
  color: #f56c6c;
  font-size: 12px;
  line-height: 1.5;
  margin-top: 4px;
  transition: all 0.3s ease;
}

.btn-group {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 30px;
}

.login-btn,
.register-btn {
  padding: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.login-btn {
  background: linear-gradient(135deg, #409eff, #66b1ff);
  box-shadow: 0 5px 25px rgba(64, 158, 255, 0.3);
}

.register-btn {
  background: linear-gradient(135deg, #67c23a, #85ce61);
  box-shadow: 0 5px 25px rgba(103, 194, 58, 0.3);
}

.admin-login-btn {
  width: 100%;
  padding: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  background-color: #f5f7fa;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.admin-login-btn:hover {
  background-color: #ebeef5;
  border-color: #c0c4cc;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: scale(0.98);
}

.login-btn:hover,
.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 30px rgba(64, 158, 255, 0.4);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
}

/* 注册弹窗样式 */
.modal {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
  max-width: 400px;
  border-radius: 8px;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}
</style>