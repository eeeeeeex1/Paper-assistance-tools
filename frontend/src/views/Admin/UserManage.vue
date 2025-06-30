<template>
  <div class="user-manage">
    <h2>用户管理界面</h2>
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>用户名</th>
          <th>邮箱</th>
          <th>创建时间</th>
          <th>更新时间</th>
          <th>操作权限管理</th>
          <th>删除用户</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="7" class="loading-message">加载中...</td>
        </tr>
        <tr v-else-if="error">
          <td colspan="7" class="error-message">{{ error }}</td>
        </tr>
        <tr v-else-if="userList && userList.length === 0">
          <td colspan="7" class="empty-message">暂无用户数据</td>
        </tr>
        <tr v-for="user in userList" :key="user.id" v-else>
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.email }}</td>
          <td>{{ formatTime(user.created_at) }}</td>
          <td>{{ formatTime(user.updated_at) }}</td>
          <td>
            <div v-if="user.permissions">
              <input type="checkbox" v-model="user.permissions.checkPlagiarism"> 论文查重
            </div>
            <div v-if="user.permissions">
              <input type="checkbox" v-model="user.permissions.checkTypos"> 论文错字检测
            </div>
            <div v-if="user.permissions">
              <input type="checkbox" v-model="user.permissions.extractTheme"> 论文主题提取
            </div>
          </td>
          <td><button @click="deleteUser(user.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
    <div class="pagination" v-if="pagination.pages > 0">
      <button @click="prevPage" :disabled="pagination.currentPage === 1">上一页</button>
      <span>
        第 {{ pagination.currentPage }} 页，共 {{ pagination.pages }} 页
      </span>
      <button @click="nextPage" :disabled="pagination.currentPage === pagination.pages">下一页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const userList = ref([])
const loading = ref(false)
const error = ref('')
const pagination = ref({
  total: 0,
  pages: 0,
  currentPage: 1,
  perPage: 10
})

const fetchUsers = async (page = 1) => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:5000/api/user/getall', {
      params: {
        page: page,
        per_page: pagination.value.perPage,
        username: '',
        include_sensitive: false
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token') || 'test-token'}`
      }
    })

    const responseData = response.data.data
    userList.value = responseData.items
    pagination.value = {
      total: responseData.total,
      pages: responseData.pages,
      currentPage: responseData.current_page,
      perPage: responseData.per_page
    }
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}

const deleteUser = async (userId) => {
  if (!confirm('确定要删除该用户吗？此操作不可恢复！')) return

  loading.value = true
  try {
    const response = await axios.delete(`http://localhost:5000/api/user/${userId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    if (response.status === 200) {
      await fetchUsers(pagination.value.currentPage)
      alert('用户删除成功')
    } else {
      throw new Error(`请求失败，状态码: ${response.status}`)
    }
  } catch (err) {
    error.value = getErrorMessage(err)
    alert(`删除用户失败: ${error.value}`)
  } finally {
    loading.value = false
  }
}

const getErrorMessage = (err) => {
  if (err.response) {
    const { status, data } = err.response
    return data.message || `错误码 ${status}：请求失败`
  }
  return '网络错误，请检查连接'
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString()
}

const prevPage = () => {
  if (pagination.value.currentPage > 1) {
    fetchUsers(pagination.value.currentPage - 1)
  }
}

const nextPage = () => {
  if (pagination.value.currentPage < pagination.value.pages) {
    fetchUsers(pagination.value.currentPage + 1)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-manage {
  background: #fff;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.user-manage h2 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th {
  background-color: #f5f7fa;
  font-weight: 600;
  padding: 15px;
  border: 1px solid #e0e0e0;
  font-size: 16px;
  color: #333;
}

td {
  text-align: center;
  padding: 15px;
  border: 1px solid #e0e0e0;
  color: #666;
  font-size: 16px;
}

button {
  padding: 10px 20px;
  cursor: pointer;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 16px;
}

button:hover {
  background-color: #ff7875;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 77, 79, 0.3);
}

.loading-message, .error-message, .empty-message {
  color: #909399;
  font-style: italic;
  padding: 25px 0;
  font-size: 16px;
}

.error-message {
  color: #f56c6c;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.pagination button {
  padding: 10px 15px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination button:hover {
  background-color: #66b1ff;
}

.pagination button:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

.pagination span {
  font-size: 16px;
  color: #606266;
}
</style>