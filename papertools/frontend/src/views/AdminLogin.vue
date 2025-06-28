<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- 左侧项目介绍区域 -->
      <div class="project-intro">
        <h2 class="intro-title">管理员管理系统</h2>
        <p class="intro-desc">
          这是专业的管理员管理系统，为企业提供高效、安全的管理解决方案。系统集成多种功能模块，助力管理员轻松处理各类管理需求。
        </p>
        <ul class="features-list">
          <li class="feature-item">
            <i class="iconfont icon-security"></i>
            <span>多重安全认证机制</span>
          </li>
          <li class="feature-item">
            <i class="iconfont icon-efficiency"></i>
            <span>高效的管理操作流程</span>
          </li>
          <li class="feature-item">
            <i class="iconfont icon-data"></i>
            <span>全面的数据分析报表</span>
          </li>
        </ul>
      </div>

      <!-- 右侧登录表单区域 -->
      <div class="login-form">
        <h2 class="title">管理员登录</h2>
        <div class="avatar-container">
          <div class="avatar"></div>
        </div>
        <div class="form-group">
          <label for="account" class="form-label">管理员账号</label>
          <div class="input-group">
            <i class="iconfont icon-user"></i>
            <input
              type="text"
              id="account"
              v-model="account"
              placeholder="请输入管理员账号"
              class="form-input"
              :class="{ 'is-error': accountError }"
            >
            <div v-if="accountError" class="error-message">{{ accountError }}</div>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const account = ref('admin');
const password = ref('admin123');
const accountError = ref('');
const passwordError = ref('');
const showPassword = ref(false);
const isLoading = ref(false);
const router = useRouter();

// 表单验证逻辑
const validateForm = (): boolean => {
  let isValid = true;
  accountError.value = '';
  passwordError.value = '';

  if (!account.value.trim()) {
    accountError.value = '账号不能为空';
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
  if (!validateForm()) return;

  isLoading.value = true;

  try {
    // 模拟管理员账号密码验证
    const adminAccount = 'admin';
    const adminPassword = 'admin123';
    
    if (account.value === adminAccount && password.value === adminPassword) {
      // 模拟登录请求延迟
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // 登录成功后跳转到用户管理页面
      router.push('/admin/user-manage');
    } else {
      accountError.value = '账号或密码错误';
    }
  } catch (error) {
    console.error('登录请求出错：', error);
    accountError.value = '登录失败，请稍后再试';
  } finally {
    isLoading.value = false;
  }
};

// 禁用按钮计算属性
const isFormInvalid = computed(() => {
  return !account.value.trim() || password.value.length < 6 || isLoading.value;
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
/* 基础样式重置 (与原文件一致，省略重复部分) */
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

/* 左侧项目介绍区域 (与原文件一致，修改了标题和描述) */
.project-intro {
  flex: 1;
  background: linear-gradient(135deg, #304156 0%, #4e6c8e 100%);
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

/* 右侧登录表单区域 (与原文件一致，移除了注册按钮相关样式) */
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
  background: linear-gradient(135deg, #304156, #4e6c8e);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
  font-size: 48px;
  box-shadow: 0 6px 30px rgba(48, 65, 86, 0.3);
  transition: all 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 35px rgba(48, 65, 86, 0.4);
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

.login-btn {
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
  background: linear-gradient(135deg, #304156, #4e6c8e);
  box-shadow: 0 5px 25px rgba(48, 65, 86, 0.3);
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 7px 30px rgba(48, 65, 86, 0.4);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: scale(0.98);
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

/* 响应式布局 (与原文件一致) */
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
</style>