<template>
  <div class="modern-user-management">
    <!-- 顶部导航栏 -->
 <div class="page-header">
      <h2 class="page-title">
        <i class="iconfont icon-user-permission"></i>
        用户权限管理
      </h2>
    </div>

    <!-- 主内容区 -->
    <div class="app-content">
      <!-- 搜索和筛选区域 -->
      <div class="action-bar">
        <div class="search-container">
          <i class="fas fa-search search-icon"></i>
          <input 
            type="text" 
            class="search-input" 
            placeholder="搜索用户ID、用户名或邮箱..." 
            v-model="searchQuery"
          >
          <button class="search-btn">搜索</button>
        </div>
        <div class="filter-options">
          <div class="filter-item">
            <label>每页显示</label>
            <select v-model="pagination.perPage" @change="changePageSize">
              <option value="5">5条</option>
              <option value="10">10条</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 用户表格卡片 -->
      <div class="user-table-card">
        <!-- 表格头部 -->
        <div class="table-header">
          <div class="header-item" style="width: 8%">ID</div>
          <div class="header-item" style="width: 15%">用户名</div>
          <div class="header-item" style="width: 20%">邮箱</div>
          <div class="header-item" style="width: 15%">创建时间</div>
          <div class="header-item" style="width: 15%">更新时间</div>
          <div class="header-item" style="width: 17%">权限</div>
          <div class="header-item" style="width: 10%">操作</div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <span>加载用户数据中...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <i class="fas fa-exclamation-triangle"></i>
          <span>{{ error }}</span>
          <button @click="fetchUsers" class="retry-btn">重试</button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="userList.length === 0" class="empty-state">
          <i class="fas fa-user-slash"></i>
          <span>暂无用户数据</span>
          <button @click="fetchUsers" class="refresh-btn">刷新</button>
        </div>

        <!-- 用户数据行 -->
        <div v-else class="table-body">
          <div 
            v-for="user in filteredUsers" 
            :key="user.id" 
            class="user-row"
            :class="{ 'expanded': expandedRows.includes(user.id) }"
          >
            <div class="row-main" @click="toggleRow(user.id)">
              <div class="row-item" style="width: 8%">{{ user.id }}</div>
              <div class="row-item" style="width: 15%">
                <div class="user-avatar">
                  <i class="fas fa-user"></i>
                </div>
                <span>{{ user.username }}</span>
              </div>
              <div class="row-item" style="width: 20%">{{ user.email }}</div>
              <div class="row-item" style="width: 15%">{{ formatTime(user.created_at) }}</div>
              <div class="row-item" style="width: 15%">{{ formatTime(user.updated_at) }}</div>
              <div class="row-item permissions" style="width: 17%">
                <div class="permission-badges">
                  <span 
                    v-if="user.permissions.checkPlagiarism" 
                    class="badge badge-blue"
                  >
                    <i class="fas fa-copy"></i> 查重
                  </span>
                  <span 
                    v-if="user.permissions.checkTypos" 
                    class="badge badge-green"
                  >
                    <i class="fas fa-spell-check"></i> 纠错
                  </span>
                  <span 
                    v-if="user.permissions.extractTheme" 
                    class="badge badge-purple"
                  >
                    <i class="fas fa-lightbulb"></i> 主题
                  </span>
                </div>
              </div>
              <div class="row-item actions" style="width: 10%">
                <button class="more-btn">
                  <i class="fas fa-ellipsis-v"></i>
                </button>
              </div>
            </div>

            <!-- 展开的详情区域 -->
            <div v-if="expandedRows.includes(user.id)" class="row-details">
              <div class="details-content">
                <div class="details-section">
                  <h4>权限管理</h4>
                  <div class="permission-controls">
                    <label class="permission-toggle">
                      <input 
                        type="checkbox" 
                        v-model="user.permissions.checkPlagiarism"
                      >
                      <span class="toggle-slider"></span>
                      <span>论文查重权限</span>
                    </label>
                    <label class="permission-toggle">
                      <input 
                        type="checkbox" 
                        v-model="user.permissions.checkTypos"
                      >
                      <span class="toggle-slider"></span>
                      <span>错字检查权限</span>
                    </label>
                    <label class="permission-toggle">
                      <input 
                        type="checkbox" 
                        v-model="user.permissions.extractTheme"
                      >
                      <span class="toggle-slider"></span>
                      <span>主题提取权限</span>
                    </label>
                  </div>
                </div>
                <div class="details-actions">
                  <button 
                    class="save-btn"
                    @click.stop="savePermissions(user.id, user.permissions)"
                    :disabled="isSaving(user.id)"
                  >
                    <i class="fas" :class="isSaving(user.id) ? 'fa-spinner fa-spin' : 'fa-save'"></i>
                    保存权限
                  </button>
                  <button 
                    class="delete-btn"
                    @click.stop="confirmDelete(user)"
                    :disabled="isDeleting(user.id)"
                  >
                    <i class="fas" :class="isDeleting(user.id) ? 'fa-spinner fa-spin' : 'fa-trash-alt'"></i>
                    删除用户
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页控制 -->
        <div class="table-footer">
          <div class="pagination-controls">
            <button 
              class="pagination-btn prev"
              @click="prevPage"
              :disabled="pagination.currentPage === 1"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            <div class="page-indicator">
              第 {{ pagination.currentPage }} 页 / 共 {{ pagination.pages }} 页
            </div>
            <button 
              class="pagination-btn next"
              @click="nextPage"
              :disabled="pagination.currentPage === pagination.pages"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <transition name="modal">
      <div v-if="showDeleteModal" class="modal-overlay">
        <div class="modal-container">
          <div class="modal-header">
            <h3>确认删除用户</h3>
            <button class="close-btn" @click="showDeleteModal = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="modal-body">
            <div class="warning-icon">
              <i class="fas fa-exclamation-circle"></i>
            </div>
            <p>您确定要永久删除用户 <strong>{{ selectedUser?.username }}</strong> (ID: {{ selectedUser?.id }}) 吗？</p>
            <p class="warning-text">此操作无法撤销，所有相关数据将被永久删除。</p>
          </div>
          <div class="modal-footer">
            <button class="cancel-btn" @click="showDeleteModal = false">取消</button>
            <button class="confirm-btn" @click="deleteUserConfirmed">
              <i class="fas fa-trash-alt"></i> 确认删除
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 状态管理
const userList = ref([])
const loading = ref(false)
const error = ref('')
const searchQuery = ref('')
const savingUsers = ref([])
const deletingUsers = ref([])
const showDeleteModal = ref(false)
const selectedUser = ref(null)
const expandedRows = ref([])

// 分页配置
const pagination = ref({
  total: 0,
  pages: 0,
  currentPage: 1,
  perPage: 5
})

// 计算属性
const filteredUsers = computed(() => {
  if (!searchQuery.value) return userList.value
  const query = searchQuery.value.toLowerCase()
  return userList.value.filter(user => 
    user.username.toLowerCase().includes(query) || 
    user.email.toLowerCase().includes(query) ||
    user.id.toString().includes(query)
  )
})

// 方法
const isSaving = (userId) => savingUsers.value.includes(userId)
const isDeleting = (userId) => deletingUsers.value.includes(userId)

const toggleRow = (userId) => {
  const index = expandedRows.value.indexOf(userId)
  if (index === -1) {
    expandedRows.value.push(userId)
  } else {
    expandedRows.value.splice(index, 1)
  }
}

const fetchUsers = async (page = 1) => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get('http://localhost:5000/api/user/getall', {
      params: {
        page: page,
        per_page: pagination.value.perPage,
        username: searchQuery.value,
        include_sensitive: false
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token') || 'test-token'}`
      }
    })

    const responseData = response.data.data
    userList.value = responseData.items.map(user => ({
      ...user,
      permissions: {
        checkPlagiarism: [1, 4, 5, 7].includes(user.permission),
        checkTypos: [2, 4, 6, 7].includes(user.permission),
        extractTheme: [3, 5, 6, 7].includes(user.permission)
      }
    }))
    
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

const confirmDelete = (user) => {
  selectedUser.value = user
  showDeleteModal.value = true
}

const deleteUserConfirmed = async () => {
  if (!selectedUser.value) return
  
  const userId = selectedUser.value.id
  deletingUsers.value.push(userId)
  
  try {
    const response = await axios.delete(`http://localhost:5000/api/user/${userId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    
    if (response.status === 200) {
      await fetchUsers(pagination.value.currentPage)
      showDeleteModal.value = false
    }
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    deletingUsers.value = deletingUsers.value.filter(id => id !== userId)
  }
}

const savePermissions = async (userId, permissions) => {
  savingUsers.value.push(userId)
  
  try {
    const response = await axios.put(
      `http://localhost:5000/api/user/${userId}/permissions`, 
      permissions,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token') || 'test-token'}`
        }
      }
    )
    
    if (response.status === 200) {
      await fetchUsers(pagination.value.currentPage)
    }
  } catch (err) {
    error.value = getErrorMessage(err)
  } finally {
    savingUsers.value = savingUsers.value.filter(id => id !== userId)
  }
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

const changePageSize = () => {
  fetchUsers(1)
}

const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

const getErrorMessage = (err) => {
  if (err.response) {
    const { status, data } = err.response
    return data.message || `请求失败 (${status})`
  }
  return err.message || '网络错误，请检查连接'
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
/* 基础变量 */
:root {
  --primary-color: #4361ee;
  --secondary-color: #3f37c9;
  --accent-color: #4895ef;
  --danger-color: #f72585;
  --success-color: #4cc9f0;
  --warning-color: #f8961e;
  --light-color: #f8f9fa;
  --dark-color: #212529;
  --gray-color: #6c757d;
  --border-color: #e9ecef;
  --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  --transition-speed: 0.3s;
}

/* 基础重置 */
.modern-user-management {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  min-height: 100vh;
  background-color: #f5f7fb;
  color: var(--dark-color);
}

/* 新增顶部标题样式 */
.page-header {
  padding: 20px 0;  /* 移除左右padding */
  margin-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: center; /* 水平居中 */
  width: 100%;
}

.page-title {
  font-size: 1.8rem;
  color: #1e293b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  text-align: center; /* 文字居中 */
}

.page-title i {
  font-size: 1.8rem;
  color: #4f46e5;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--gray-color);
  font-size: 0.9rem;
  cursor: pointer;
  transition: color var(--transition-speed);
  padding: 8px 12px;
  border-radius: 6px;
}

.refresh-btn:hover {
  color: var(--primary-color);
  background: rgba(67, 97, 238, 0.05);
}

.user-profile {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(108, 117, 125, 0.1);
  border-radius: 50%;
  color: var(--gray-color);
  font-size: 1.2rem;
}

/* 主内容区 */
.app-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-container {
  display: flex;
  align-items: center;
  width: 400px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  color: var(--gray-color);
  font-size: 0.9rem;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all var(--transition-speed);
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
}

.search-btn {
  position: absolute;
  right: 8px;
  padding: 4px 10px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background var(--transition-speed);
}

.search-btn:hover {
  background: var(--secondary-color);
}

.filter-options {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: var(--gray-color);
}

.filter-item select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

/* 用户表格卡片 */
.user-table-card {
  background: white;
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.table-header {
  display: flex;
  background: #f8f9fa;
  padding: 0 1.5rem;
  height: 50px;
  border-bottom: 1px solid var(--border-color);
  font-weight: 600;
  color: var(--gray-color);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-item {
  display: flex;
  align-items: center;
  padding: 0 10px;
}

/* 表格内容 */
.table-body {
  padding: 0 1.5rem;
}

.user-row {
  border-bottom: 1px solid var(--border-color);
  transition: all var(--transition-speed);
}

.user-row:last-child {
  border-bottom: none;
}

.user-row:hover {
  background: rgba(67, 97, 238, 0.02);
}

.row-main {
  display: flex;
  align-items: center;
  height: 70px;
  cursor: pointer;
  padding: 0 10px;
}

.row-item {
  padding: 0 10px;
  font-size: 0.9rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(108, 117, 125, 0.1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  color: var(--gray-color);
}

.permission-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge-blue {
  background: rgba(67, 97, 238, 0.1);
  color: var(--primary-color);
}

.badge-green {
  background: rgba(76, 201, 240, 0.1);
  color: var(--success-color);
}

.badge-purple {
  background: rgba(111, 66, 193, 0.1);
  color: #6f42c1;
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.more-btn {
  background: none;
  border: none;
  color: var(--gray-color);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all var(--transition-speed);
}

.more-btn:hover {
  background: rgba(108, 117, 125, 0.1);
  color: var(--dark-color);
}

/* 展开详情 */
.row-details {
  background: #f9fafc;
  padding: 1.5rem;
  border-top: 1px dashed var(--border-color);
}

.details-content {
  display: flex;
  gap: 2rem;
}

.details-section {
  flex: 1;
}

.details-section h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: var(--gray-color);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.permission-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.permission-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
  padding-left: 50px;
  height: 24px;
}

.permission-toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 42px;
  height: 24px;
  background-color: #e9ecef;
  transition: .4s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--primary-color);
}

input:checked + .toggle-slider:before {
  transform: translateX(18px);
}

.details-actions {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
}

.save-btn, .delete-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  border: none;
}

.save-btn {
  background: var(--primary-color);
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: var(--secondary-color);
}

.delete-btn {
  background: rgba(247, 37, 133, 0.1);
  color: var(--danger-color);
}

.delete-btn:hover:not(:disabled) {
  background: rgba(247, 37, 133, 0.2);
}

.save-btn:disabled, .delete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 表格底部 */
.table-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--gray-color);
  cursor: pointer;
  transition: all var(--transition-speed);
}

.pagination-btn:hover:not(:disabled) {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-indicator {
  font-size: 0.9rem;
  color: var(--gray-color);
}

/* 加载和空状态 */
.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(67, 97, 238, 0.1);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: var(--danger-color);
}

.error-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.empty-state {
  color: var(--gray-color);
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.retry-btn, .refresh-btn {
  margin-top: 1rem;
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background var(--transition-speed);
}

.retry-btn:hover, .refresh-btn:hover {
  background: var(--secondary-color);
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transform: translateY(0);
  opacity: 1;
  transition: all 0.3s ease;
}

.modal-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--dark-color);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: var(--gray-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: all var(--transition-speed);
}

.close-btn:hover {
  background: rgba(108, 117, 125, 0.1);
  color: var(--dark-color);
}

.modal-body {
  padding: 2rem;
  text-align: center;
}

.warning-icon {
  font-size: 3rem;
  color: var(--danger-color);
  margin-bottom: 1.5rem;
}

.warning-text {
  color: var(--danger-color);
  font-size: 0.9rem;
  margin-top: 1rem;
}

.modal-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  border-top: 1px solid var(--border-color);
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-speed);
  border: none;
}

.cancel-btn {
  background: white;
  color: var(--gray-color);
  border: 1px solid var(--border-color);
}

.cancel-btn:hover {
  background: #f8f9fa;
}

.confirm-btn {
  background: var(--danger-color);
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.confirm-btn:hover {
  background: #e3176a;
}

/* 过渡动画 */
.modal-enter-from, .modal-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 响应式设计 */
@media (max-width: 992px) {
  .app-content {
    padding: 1.5rem;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-container {
    width: 100%;
  }
  
  .details-content {
    flex-direction: column;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 1rem;
  }
  
  .header-item {
    display: none;
  }
  
  .header-item:first-child, 
  .header-item:nth-child(2),
  .header-item:last-child {
    display: flex;
  }
  
  .row-item {
    display: none;
  }
  
  .row-item:first-child, 
  .row-item:nth-child(2),
  .row-item:last-child {
    display: flex;
  }
  
  .user-avatar {
    margin-right: 0;
  }
  
  .user-name span {
    display: none;
  }
}
</style>