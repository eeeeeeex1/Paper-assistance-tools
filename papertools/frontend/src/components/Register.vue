<template>
  <div class="register-container">
    <div class="register-wrapper">
      <h2 class="title">用户注册</h2>
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
          <!-- 密码可见性切换按钮 -->
          <button 
            type="button" 
            class="toggle-password-btn" 
            @click="togglePassword"
          >
            <i class="iconfont" :class="showPassword ? 'icon-eye-slash' : 'icon-eye'"></i>
          </button>
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
          <!-- 确认密码可见性切换按钮 -->
          <button 
            type="button" 
            class="toggle-password-btn" 
            @click="toggleConfirmPassword"
          >
            <i class="iconfont" :class="showConfirmPassword ? 'icon-eye-slash' : 'icon-eye'"></i>
          </button>
          <div v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
        </div>
      </div>
      <button 
        class="register-btn" 
        @click="handleRegister" 
      >
        注册
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'  // 引入 axios

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
const registerMessage = ref('');  // 新增：注册结果消息
const isLoading = ref(false);     // 新增：加载状态

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
      const response = await axios.post('http://localhost:5000/api/user/register', {
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
</script>

<style scoped>
/* 基础样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', sans-serif;
}

.register-container {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.register-wrapper {
  width: 100%;
  max-width: 400px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
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
  z-index: 10;
}

/* 密码可见性切换按钮样式 */
.toggle-password-btn {
  position: absolute;
  right: 15px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 10;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color:#409eff;
  transition: all 0.2s ease;
}

.toggle-password-btn:hover {
  color: #409eff;
}

.form-input {
  width: 100%;
  padding: 16px 45px 16px 45px; /* 右侧增加45px padding为按钮留出空间 */
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

.form-input.is-error + .toggle-password-btn i,
.form-input.is-error + i {
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

.register-btn {
  padding: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #fff;
  background: linear-gradient(135deg, #67c23a, #85ce61);
  box-shadow: 0 5px 25px rgba(103, 194, 58, 0.3);
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 30px rgba(103, 194, 58, 0.4);
}
</style>