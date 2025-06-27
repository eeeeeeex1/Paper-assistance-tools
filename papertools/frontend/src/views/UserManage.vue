<template>
  <div class="user-manage">
    <h2>用户管理界面</h2>
    
    <!-- 表格始终显示表头，内容根据状态动态变化 -->
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>用户名</th>
          <th>最后登录时间</th>
          <th>操作权限管理</th>
          <th>删除用户</th>
        </tr>
      </thead>
      
      <!-- 表格内容根据状态动态渲染 -->
      <tbody>
        <!-- 加载中状态 -->
        <tr v-if="loading">
          <td colspan="5" class="loading-message">加载中...</td>
        </tr>
        
        <!-- 错误状态 -->
        <tr v-else-if="error">
          <td colspan="5" class="error-message">{{ error }}</td>
        </tr>
        
        <!-- 空数据状态 -->
        <tr v-else-if="userList.length === 0">
          <td colspan="5" class="empty-message">暂无用户数据</td>
        </tr>
        
        <!-- 正常数据状态 -->
        <tr v-for="user in userList" :key="user.id" v-else>
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ formatTime(user.lastLoginTime) }}</td>
          <td>
            <div>
              <input type="checkbox" v-model="user.permissions.checkPlagiarism"> 论文查重
            </div>
            <div>
              <input type="checkbox" v-model="user.permissions.checkTypos"> 论文错字检测
            </div>
            <div>
              <input type="checkbox" v-model="user.permissions.extractTheme"> 论文主题提取
            </div>
          </td>
          <td><button @click="deleteUser(user.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const userList = ref([])
const loading = ref(false)
const error = ref('')

// API路径（需根据后端实际情况调整）
const USER_API_BASE = '/api/user'

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 假设获取用户列表的API为 /api/user/list
    const response = await axios.get(`${USER_API_BASE}/list`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}` // 测试时可固定token
      }
    })
    userList.value = Array.isArray(response.data) ? response.data : []
  } catch (err) {
    console.error('API错误', err)
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}

// 删除用户
const deleteUser = async (userId) => {
  if (!confirm('确定要删除该用户吗？此操作不可恢复！')) return
  
  loading.value = true
  try {
    await axios.delete(`${USER_API_BASE}/${userId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    fetchUsers()
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}

// 错误信息处理
const getErrorMessage = (err) => {
  if (err.response) {
    const { status, data } = err.response
    return data.message || `错误码 ${status}：请求失败`
  } 
  return '网络错误，请检查连接'
}

// 时间格式化
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString()
}

// 组件挂载时请求数据
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-manage {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
th {
  background-color: #f5f7fa;
  font-weight: 600;
  padding: 12px;
  border: 1px solid #e0e0e0;
}
td {
  text-align: center;
  padding: 12px;
  border: 1px solid #e0e0e0;
  color: #666;
}
button {
  padding: 6px 12px;
  cursor: pointer;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
}
.loading-message, .error-message, .empty-message {
  color: #909399;
  font-style: italic;
  padding: 20px 0;
}
.error-message {
  color: #f56c6c;
}
</style>