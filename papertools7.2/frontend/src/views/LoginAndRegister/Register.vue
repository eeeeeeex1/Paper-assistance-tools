<template>
   <div class="register-container">
    <div class="register-wrapper">
      <div class="floating-elements">
        <div class="floating-circle circle-1"></div>
        <div class="floating-circle circle-2"></div>
      </div>
      
      <div class="avatar-container">
        <div class="calligraphy-title">欢迎注册</div>
        <div class="avatar-ring ring-1"></div>
        <div class="avatar-ring ring-2"></div>
      </div>
     
      <div class="form-group">
        <label for="email" class="form-label">邮箱</label>
        <div class="input-group">
          <i class="iconfont icon-email"></i>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="请输入邮箱" 
            class="form-input"
            :class="{ 'is-error': emailError }"
          >
          <div v-if="emailError" class="error-message">{{ emailError }}</div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="username" class="form-label">用户名</label>
        <div class="input-group">
          <i class="iconfont icon-user"></i>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="请输入用户名" 
            class="form-input"
            :class="{ 'is-error': usernameError }"
          >
          <div v-if="usernameError" class="error-message">{{ usernameError }}</div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="password" class="form-label">密码</label>
        <div class="input-group">
          <i class="iconfont icon-lock"></i>
          <input 
            :type="showPassword ? 'text' : 'password'" 
            id="password" 
            v-model="password" 
            placeholder="请输入密码" 
            class="form-input"
            :class="{ 'is-error': passwordError }"
          >
          <i 
            class="iconfont toggle-password" 
            :class="showPassword ? 'icon-eye-slash' : 'icon-eye'"
            @click="togglePassword"
          ></i>
          <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
        </div>
      </div>
      
      <div class="form-group">
        <label for="confirmPassword" class="form-label">确认密码</label>
        <div class="input-group">
          <i class="iconfont icon-lock"></i>
          <input 
            :type="showConfirmPassword ? 'text' : 'password'" 
            id="confirmPassword" 
            v-model="confirmPassword" 
            placeholder="请再次输入密码" 
            class="form-input"
            :class="{ 'is-error': confirmPasswordError }"
          >
          <i 
            class="iconfont toggle-password" 
            :class="showConfirmPassword ? 'icon-eye-slash' : 'icon-eye'"
            @click="toggleConfirmPassword"
          ></i>
          <div v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
        </div>
      </div>
      
      <div class="btn-group">
        <button 
          class="register-btn btn-ripple"
          @click="handleRegister"
          :disabled="isLoading"
          :class="{ 'btn-loading': isLoading }"
        >
          <span v-if="!isLoading">立即注册</span>
          <span v-else class="loading-spinner"></span>
        </button>
      </div>
      
      <div class="footer-links">
        <span>已有账号？</span>
        <a @click="goToLogin">立即登录</a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'  // 引入 axios

// 定义API基础路径（使用环境变量）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const email = ref('');
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const emailError = ref('');
const usernameError = ref('');
const passwordError = ref('');
const confirmPasswordError = ref('');
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const router = useRouter();
const registerMessage = ref('');  
const isLoading = ref(false);   

// 表单验证逻辑
const validateForm = () => {
  let isValid = true;
  emailError.value = '';
  usernameError.value = '';
  passwordError.value = '';
  confirmPasswordError.value = '';

  if (!email.value.trim()) {
    emailError.value = '邮箱不能为空';
    isValid = false;
  }

  if (!username.value.trim()) {
    usernameError.value = '用户名不能为空';
    isValid = false;
  }

  if (password.value.length < 6) {
    passwordError.value = '密码长度至少为6位';
    isValid = false;
  }

  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = '两次输入密码不一致';
    isValid = false;
  }

  return isValid;
};

// 切换密码可见性
const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

// 切换确认密码可见性
const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value;
};

// 注册逻辑
const handleRegister = async () => {
  if (!validateForm()) return
  
  isLoading.value = true;
  registerMessage.value = '';
  
  try {
      // 调用后端注册接口
      const response = await axios.post(`${API_BASE_URL}/api/user/register`, {
      email: email.value,
      username: username.value,
      password: password.value
    });
    
    // 处理成功响应
    if (response.status >= 200 && response.status < 300) {
      registerMessage.value = '注册成功！即将跳转到登录页面...';
      console.log("注册成功")
      // 2秒后跳转到登录页面
      setTimeout(() => {
        router.push({ name: 'Login' });
      }, 500);
    }
  } catch (error: any) {
    // 处理错误响应
    registerMessage.value = '注册失败：' + (error.response?.data?.message || '服务器错误');
    console.log("注册失败")
    // 根据错误类型显示不同的错误信息
    if (error.response?.status === 400) {
      usernameError.value = '用户名已存在';
    } else if (error.response?.status === 500) {
      usernameError.value = '服务器内部错误，请稍后再试';
    }
  } finally {
    isLoading.value = false;
  }
};

/////////
// 跳转到登录页面
const goToLogin = () => {
  router.push('/login' ) 
}

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700&family=ZCOOL+QingKe+HuangYou&display=swap');

.register-container {
  width: 100%;
  height: 100vh;
   background: rgb(245, 248, 244);
  display: flex;
  justify-content: center;
  align-items: flex-start; 
  padding-top: 5vh; 
  align-items: center;
  padding: 15px;
  position: relative;
  overflow: hidden;
  z-index: 0;
}

.register-wrapper {
  width: 100%;
  max-width: 380px;
  min-height: 600px;
  background-color: rgba(250, 251, 253, 1);
  backdrop-filter: blur(5px);
  border-radius: 12px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  padding: 30px 40px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  margin-top: 20px;
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
  background: rgba(64, 158, 255, 0.08);
  animation: float 15s infinite ease-in-out;
}

.circle-1 {
  width: 180px;
  height: 180px;
  top: -40px;
  right: -40px;
  animation-delay: 0s;
}

.circle-2 {
  width: 220px;
  height: 220px;
  bottom: -30px;
  left: -30px;
  animation-delay: 5s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(15px, 15px) scale(1.03); }
}

.calligraphy-title {
  font-size: 30px;
  font-weight: 600;
  margin-bottom: 35px;
  line-height: 1.3
}

@keyframes textFloat {
  0% { transform: rotate(-5deg) translateY(0); }
  50% { transform: rotate(-5deg) translateY(-8px); }
  100% { transform: rotate(-5deg) translateY(0); }
}

.avatar-container {
  display: flex;
  justify-content: center;
 margin-bottom: 10px; 
  position: relative;
  height: auto; 
  z-index: 1;
}
.avatar-ring {
position: absolute;
  border-radius: 50%;
  z-index: 2;
}
.ring-1 {
  width: 250px;
  height:250px;
  top: -50px;   
  right: -150px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: conic-gradient(
    from 0deg,
    rgba(41, 135, 172, 0.3),
    rgba(34, 183, 129, 0.6),
    transparent
  );
  -webkit-mask: radial-gradient(
    farthest-side,
    transparent calc(100% - 2px),
    #fff
  );
  mask: radial-gradient(
    farthest-side,
    transparent calc(100% - 2px),
    #fff
  );
  animation: spin 8s linear infinite;
}
.ring-2 {
  width:400px;
  height:400px;
  border-radius: 50%;
  bottom: -750px;
  left: -10px;
  border: 2px solid transparent;
  background: conic-gradient(
    from 180deg,
    rgba(19, 234, 116, 0.2),
    rgba(12, 77, 145, 0.4),
    transparent
  );
  -webkit-mask: radial-gradient(
    farthest-side,
    transparent calc(100% - 2px),
    #fff
  );
  mask: radial-gradient(
    farthest-side,
    transparent calc(100% - 2px),
    #fff
  );
  animation: spinReverse 10s linear infinite;
}
@keyframes spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes spinReverse {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(-360deg); }
}

.title {
  text-align: center;
  margin-bottom: 25px;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
  position: relative;
  z-index: 1;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-size: 13px;
  font-weight:500;
  transition: all 0.3s ease;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.input-group i {
  position: absolute;
  left: 12px;
  color: rgba(144, 147, 153, 0.8);
  font-size: 16px;
  transition: all 0.3s ease;
  z-index: 2;
}

.toggle-password {
  position: absolute;
  right: 12px;
  color: #c0c4cc;
  font-size: 16px;
  cursor: pointer;
  z-index: 2;
  transition: all 0.2s ease;
}

.toggle-password:hover {
  color: #409eff;
}

.form-input {
  width: 280px;
  margin: 0 auto;
  padding: 12px 40px;
  border: 1px solid rgba(120, 175, 231, 0.3);
  border-radius: 8px;
  background-color: rgba(182, 208, 247, 0.2);
  backdrop-filter: blur(5px);
  color: #333;
  font-size: 13px;
  transition: all 0.3s ease;
  outline: none;
  position: relative;
  z-index: 1;
}

.form-input:focus {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(64, 158, 255, 0.6);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.15);
}

.form-input.is-error {
  border-color: rgba(255, 107, 107, 0.6);
  background-color: rgba(255, 255, 255, 0.25);
}

.form-input.is-error ~ .iconfont {
  color: #ff6b6b;
}

.error-message {
  position: absolute;
  bottom: -18px;
  left: 0;
  color: #ff6b6b;
  font-size: 11px;
  line-height: 1.5;
  transition: all 0.3s ease;
}

.btn-group {
  margin: 25px 0 15px;
  position: relative;
  z-index: 1;
}

.register-btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #2dd571, #66b1ff);
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.25);
  position: relative;
  overflow: hidden;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(64, 158, 255, 0.35);
}

.register-btn:active {
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
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #909399;
  position: relative;
  z-index: 1;
}

.footer-links a {
  color: #409eff;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.footer-links a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式布局 */
@media (max-width: 480px) {
  .register-wrapper {
    padding: 25px 20px;
  }
  
  .title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .form-input {
    padding: 10px 35px;
  }
  
  .input-group i {
    left: 10px;
    font-size: 15px;
  }
  
  .toggle-password {
    right: 10px;
    font-size: 15px;
  }
}
</style>
