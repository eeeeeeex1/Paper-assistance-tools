<template>
  <div class="log-manage">
    <h2>日志管理界面</h2>
    
    <!-- 搜索与筛选区域 -->
    <div class="filter-area">
      <div>
        <label>用户ID: </label>
        <input type="number" v-model="filter.userId" placeholder="输入用户ID">
      </div>
      <div>
        <label>论文ID: </label>
        <input type="number" v-model="filter.paperId" placeholder="输入论文ID">
      </div>
      <div>
        <label>操作类型: </label>
        <select v-model="filter.operationType">
          <option value="">全部</option>
          <option value="checkPlagiarism">论文查重</option>
          <option value="checkTypos">论文错字检测</option>
          <option value="extractTheme">论文主题提取</option>
        </select>
      </div>
      <button @click="fetchLogs">筛选</button>
    </div>
    
    <!-- 始终显示表头，内容根据状态动态变化 -->
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>序号</th>
          <th>用户</th>
          <th>论文ID</th>
          <th>操作类型</th>
          <th>时间</th>
          <th>文件名</th>
          <th>操作</th>
        </tr>
      </thead>
      
      <tbody>
        <!-- 加载中状态 -->
        <tr v-if="loading">
          <td colspan="7" class="loading-message">加载日志中...</td>
        </tr>
        
        <!-- 错误状态 -->
        <tr v-else-if="error">
          <td colspan="7" class="error-message">{{ error }}</td>
        </tr>
        
        <!-- 空数据状态 -->
        <tr v-else-if="logList.length === 0">
          <td colspan="7" class="empty-message">暂无日志记录</td>
        </tr>
        
        <!-- 正常数据状态 -->
        <tr v-for="(log, index) in logList" :key="log.id" v-else>
          <td>{{ index + 1 }}</td>
          <td>{{ log.userId }}</td>
          <td>{{ log.paperId || '-' }}</td>
          <td>{{ getOperationName(log.operation) }}</td>
          <td>{{ formatTime(log.createTime) }}</td>
          <td>{{ log.fileName || '-' }}</td>
          <td>
            <button @click="viewLogDetail(log.id)">查看详情</button>
            <button @click="deleteLog(log.id)" style="margin-left: 5px;">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 分页组件 -->
    <div class="pagination" v-if="logList.length > 0">
      <button @click="goToPage(1)" :disabled="currentPage === 1">首页</button>
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">上一页</button>
      <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">下一页</button>
      <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">末页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

// 状态管理
const logList = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalRecords = ref(0)

// 筛选条件
const filter = ref({
  userId: '',
  paperId: '',
  operationType: '',
  page: 1,
  perPage: 20
})

// API路径
const OPERATIONS_API = '/api/operations'

// 操作类型映射（用于显示友好名称）
const OPERATION_TYPES = {
  checkPlagiarism: '论文查重',
  checkTypos: '论文错字检测',
  extractTheme: '论文主题提取',
  upload: '论文上传',
  download: '论文下载'
}

// 加载日志列表（整合图片2、4、6的获取功能）
const fetchLogs = async (page = 1) => {
  loading.value = true
  error.value = ''
  filter.value.page = page
  currentPage.value = page
  
  try {
    let url = `${OPERATIONS_API}`
    const params = {
      page: filter.value.page,
      per_page: filter.value.perPage
    }
    
    // 根据筛选条件添加参数
    if (filter.value.userId) {
      // 对应图片6：获取用户的操作记录
      url = `${OPERATIONS_API}/user/${filter.value.userId}`
    } else if (filter.value.paperId) {
      // 对应图片4：获取论文的操作记录
      url = `${OPERATIONS_API}/paper/${filter.value.paperId}`
    }
    
    // 添加操作类型筛选
    if (filter.value.operationType) {
      params.operation = filter.value.operationType
    }
    
    const response = await axios.get(url, {
      params,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    
    // 处理响应数据（假设后端返回标准分页格式）
    const data = response.data
    logList.value = Array.isArray(data.records) ? data.records : (Array.isArray(data) ? data : [])
    totalRecords.value = data.total || logList.value.length
    totalPages.value = Math.ceil(totalRecords.value / filter.value.perPage)
  } catch (err) {
    console.error('获取日志失败', err)
    error.value = handleError(err)
  } finally {
    loading.value = false
  }
}

// 查看日志详情（对应图片2：通过ID获取操作记录）
const viewLogDetail = async (operationId) => {
  loading.value = true
  try {
    const response = await axios.get(`${OPERATIONS_API}/${operationId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    
    // 示例：弹出详情模态框（实际开发中需实现模态框组件）
    console.log('日志详情', response.data)
    alert(`查看日志ID ${operationId} 的详情：\n${JSON.stringify(response.data, null, 2)}`)
  } catch (err) {
    error.value = handleError(err)
  } finally {
    loading.value = false
  }
}

// 新增操作记录（对应图片3：记录新的操作）
const createOperationLog = async () => {
  // 示例：弹出新增表单（实际开发中需实现表单组件）
  const newLog = {
    paperId: 1001,
    operation: 'checkPlagiarism',
    userId: 1,
    fileName: 'example.pdf'
  }
  
  if (!newLog.paperId || !newLog.operation || !newLog.userId) {
    error.value = '新增日志时缺少必要参数'
    return
  }
  
  loading.value = true
  try {
    const response = await axios.post(`${OPERATIONS_API}`, newLog, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`,
        'Content-Type': 'application/json'
      }
    })
    
    console.log('新增日志成功', response.data)
    fetchLogs() // 重新加载日志
    alert('操作记录添加成功')
  } catch (err) {
    error.value = handleError(err)
  } finally {
    loading.value = false
  }
}

// 删除日志记录（整合图片5的删除功能）
const deleteLog = async (logId) => {
  if (!confirm('确定要删除这条日志吗？')) return
  
  loading.value = true
  try {
    await axios.delete(`${OPERATIONS_API}/${logId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    
    fetchLogs() // 重新加载日志
  } catch (err) {
    error.value = handleError(err)
  } finally {
    loading.value = false
  }
}

// 获取操作统计信息（对应图片5：获取操作统计信息）
const getOperationStats = async () => {
  loading.value = true
  try {
    const params = {}
    if (filter.value.userId) params.user_id = filter.value.userId
    if (filter.value.startDate) params.start_date = filter.value.startDate
    if (filter.value.endDate) params.end_date = filter.value.endDate
    
    const response = await axios.get(`${OPERATIONS_API}/stats`, {
      params,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    })
    
    // 示例：显示统计信息（实际开发中需可视化展示）
    console.log('操作统计', response.data)
    alert(`操作统计信息：\n${JSON.stringify(response.data, null, 2)}`)
  } catch (err) {
    error.value = handleError(err)
  } finally {
    loading.value = false
  }
}

// 错误处理函数
const handleError = (err) => {
  if (err.response) {
    const { status, data } = err.response
    switch (status) {
      case 401: return '未授权，请重新登录'
      case 403: return '权限不足，无法访问日志'
      case 404: return data.message || '日志记录不存在'
      case 400: return data.message || '请求参数错误'
      default: return data.message || `错误码 ${status}：操作失败`
    }
  }
  return '网络错误，请检查连接后重试'
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  return new Date(timeStr).toLocaleString()
}

// 获取操作类型的友好名称
const getOperationName = (operationType) => {
  return OPERATIONS_TYPES[operationType] || operationType
}

// 分页跳转
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  fetchLogs(page)
}

// 监听筛选条件变化，自动刷新列表
watch([() => filter.value.userId, () => filter.value.paperId, () => filter.value.operationType], 
  () => {
    if (currentPage.value > 1) {
      fetchLogs(1)
    } else {
      fetchLogs()
    }
  })

// 组件挂载时加载日志
onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.log-manage {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}
.filter-area {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}
label {
  margin-right: 5px;
  font-weight: 500;
}
input, select {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
button {
  padding: 6px 12px;
  cursor: pointer;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  transition: background-color 0.2s;
}
button:hover {
  background-color: #66b1ff;
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
.loading-message, .error-message, .empty-message {
  color: #909399;
  font-style: italic;
  padding: 20px 0;
}
.error-message {
  color: #f56c6c;
}
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 15px;
  gap: 10px;
  font-size: 14px;
}
.pagination button {
  padding: 4px 8px;
  min-width: 40px;
}
.pagination button:disabled {
  background-color: #dcdfe6;
  cursor: not-allowed;
}
</style>