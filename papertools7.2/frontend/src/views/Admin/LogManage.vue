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
        <label>操作类型: </label>
        <select v-model="filter.operationType">
          <option value="">全部</option>
          <option value="similaritycheck">similaritycheck</option>
          <option value="spellcheck">spellcheck</option>
          <option value="textsummary">textsummary</option>
        </select>
      </div>
      <button @click="applyFilter">筛选</button>
    </div>

    <!-- 表格 -->
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>序号</th>
          <th>用户ID</th>
          <th>论文ID</th>
          <th>操作类型</th>
          <th>操作时间</th>
          <th>文件名</th>
          <th>下载</th>
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
        <tr v-else-if="filteredLogList.length === 0">
          <td colspan="7" class="empty-message">暂无日志记录</td>
        </tr>

        <!-- 正常数据状态 -->
        <tr v-for="(log, index) in sortedLogList" :key="log.id">
          <td>{{ log.id }}</td>
          <td>{{ log.user_id }}</td>
          <td>{{ log.paper_id || '-' }}</td>
          <td>{{ getOperationName(log.operation_type) }}</td>
          <td>{{ formatTime(log.operation_time) }}</td>
          <td>{{ log.file_name || '-' }}</td>
          <td>
            <button @click="downloadFile(log)" style="margin-left: 5px;">下载</button>
          </td>
          <td>
            <button @click="deleteLog(log.id)" style="margin-left: 5px;">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 统计信息区域 -->
    <div v-if="statsData && Object.keys(statsData).length > 0" class="stats-area">
      <h3>操作统计信息</h3>
      <div class="stats-card">
        <div class="stats-item">
          <div class="stats-label">总操作次数</div>
          <div class="stats-value">{{ statsData.totalOperations || 0 }}</div>
        </div>
        <div class="stats-item">
          <div class="stats-label">用户数</div>
          <div class="stats-value">{{ statsData.totalUsers || 0 }}</div>
        </div>
        <div class="stats-item">
          <div class="stats-label">论文数</div>
          <div class="stats-value">{{ statsData.totalPapers || 0 }}</div>
        </div>
      </div>

      <div class="stats-chart">
        <h4>操作类型分布</h4>
        <ul>
          <li v-for="(count, type) in statsData.operationTypes || {}" :key="type">
            {{ getOperationName(type) }}: {{ count }} 次
          </li>
        </ul>
      </div>
    </div>

    <!-- 分页组件 -->
    <div class="pagination" v-if="filteredLogList.length > 0">
      <button @click="goToPage(1)" :disabled="currentPage === 1">首页</button>
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">上一页</button>
      <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">下一页</button>
      <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">末页</button>
      <span style="margin-left: 20px;">每页显示: {{ filter.perPage }} 条</span>
      <select v-model="filter.perPage" @change="applyFilter">
        <option value="10">10</option>
        <option value="20">20</option>
        <option value="50">50</option>
        <option value="100">100</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'

// 状态管理
const logList = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalRecords = ref(0)
const statsData = ref({}) // 新增：统计数据

// 筛选条件
const filter = ref({
  userId: '',
  operationType: '',
  page: 1,
  perPage: 20
})

// 操作类型映射
const OPERATIONS_TYPES = {
  similaritycheck: '论文相似度查询',
  spellcheck: '论文错字纠正',
  textsummary: '论文主题总结'
}

// API路径
const OPERATIONS_API = '/api/operations'

// 加载日志列表
const fetchLogs = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await axios.get(`http://localhost:5000${OPERATIONS_API}/getall`);

    // 处理响应数据
    const data = response.data;
    if (data.status === 'success') {
      logList.value = data.data.records || [];
      totalRecords.value = data.data.total || 0;
      totalPages.value = Math.ceil(totalRecords.value / filter.value.perPage);
      currentPage.value = 1;
    } else {
      throw new Error(data.message || '获取日志失败');
    }
  } catch (err) {
    console.error('获取日志失败', err);
    error.value = err.message || '网络错误，请重试';
  } finally {
    loading.value = false;
    applyFilter();
  }
}

// 获取操作统计信息
const getOperationStats = async () => {
  loading.value = true;
  statsData.value = {}; // 清空之前的统计数据

  try {
    const params = {};
    if (filter.value.userId) params.user_id = filter.value.userId;
    if (filter.value.operationType) params.operation = filter.value.operationType;

    const response = await axios.get(`${OPERATIONS_API}/stats`, {
      params,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    });

    // 处理统计数据
    const data = response.data;
    if (data.status === 'success') {
      statsData.value = data.data || {};
      console.log('操作统计', statsData.value);
    } else {
      throw new Error(data.message || '获取统计信息失败');
    }
  } catch (err) {
    console.error('获取统计失败', err);
    error.value = err.message || '网络错误，请重试';
  } finally {
    loading.value = false;
  }
}

// 删除日志记录
const deleteLog = async (logId) => {
  if (!confirm('确定要删除这条日志吗？')) return;

  loading.value = true;
  try {
    // 发送删除请求
    await axios.delete(`http://localhost:5000${OPERATIONS_API}/${logId}`);

    // 重新加载日志列表
    fetchLogs();
    alert('日志删除成功');
  } catch (err) {
    console.error('删除日志失败', err);
    error.value = err.message || '删除失败，请重试';
  } finally {
    loading.value = false;
  }
}

// 错误处理函数
const handleError = (err) => {
  if (err.response) {
    const { status, data } = err.response;
    switch (status) {
      case 401: return '未授权，请重新登录';
      case 403: return '权限不足，无法访问';
      //case 404: return '资源不存在';
      default: return data.message || `错误 ${status}`;
    }
  }
  return '网络错误，请检查连接';
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-';
  return new Date(timeStr).toLocaleString();
}

// 获取操作类型的友好名称
const getOperationName = (operationType) => {
  return OPERATIONS_TYPES[operationType] || operationType;
}

// 分页跳转
const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  applyFilter();
}

// 应用筛选条件
const applyFilter = () => {
  let filtered = logList.value;

  if (filter.value.userId) {
    const userId = parseInt(filter.value.userId);
    filtered = filtered.filter(log => log.user_id === userId);
  }

  if (filter.value.operationType) {
    filtered = filtered.filter(log => log.operation_type === filter.value.operationType);
  }

  totalRecords.value = filtered.length;
  totalPages.value = Math.ceil(totalRecords.value / filter.value.perPage);

  const startIndex = (currentPage.value - 1) * filter.value.perPage;
  const endIndex = startIndex + parseInt(filter.value.perPage);
  filteredLogList.value = filtered.slice(startIndex, endIndex);
}

// 对日志列表进行降序排序
const sortedLogList = computed(() => {
  return [...filteredLogList.value].sort((a, b) => b.id - a.id);
});

const filteredLogList = ref([]);


//zyb----------------------------------------
// 下载文件函数，根据论文ID调用后端接口
const downloadFile = async (log) => {
  // 获取论文ID，若为'-'表示没有论文ID，给出提示并返回
  console.log('下载按钮点击，日志数据:', log.paper_id); // 调试日志
  const paperId = log.paper_id;
  if (paperId === '-') {
    alert('该操作记录无有效论文ID，无法下载');
    return;
  }
  try {
    // 显示加载状态（可选，若需要提示用户正在下载）
    loading.value = true;

    // 调用后端下载接口，这里假设后端下载接口为 /api/downloadPaper，需要传递论文ID参数
    const response = await axios.get(`http://localhost:5000/api/paper/downloadPaper?paper_id=${paperId}`, {
      // 配置响应类型为 blob，用于处理文件下载
      responseType: 'blob',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
      }
    });
    // 处理响应，创建 blob 对象
    const blob = new Blob([response.data]);
    // 创建 a 标签用于下载
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    // 从响应头中获取文件名（如果后端设置了的话），这里假设后端返回的 Content-Disposition 包含文件名
    console.log('响应头完整信息:', response.headers);
    console.log('Content-Type:', response.headers.get('content-type'));
    console.log('Content-Disposition:', response.headers.get('content-disposition'));
    const contentDisposition = response.headers['content-disposition'];
    let fileName = 'downloaded_file';
    // 1. 精准解析文件名
    if (contentDisposition) {
      // 匹配 filename*=UTF-8''xxx 或 filename="xxx" 格式，只提取 xxx 部分
      const match = contentDisposition.match(/filename(?:\*=UTF-8''|=")([^;"]+)(?="|;|$)/);
      if (match && match[1]) {
        fileName = decodeURIComponent(match[1].trim());
      }
    }

    // 2. 清理多余后缀（如 ; filename=）
    fileName = fileName.replace(/; filename=.*$/, '');

    // 3. 删除前缀（如果需要）
    const separatorIndex = fileName.indexOf('_');
    if (separatorIndex !== -1) {
      fileName = fileName.slice(separatorIndex + 1);
    }

    // 4. 确保文件名包含扩展名
    if (!fileName.match(/\.\w+$/)) {
      // 如果扩展名丢失，可从 Content-Type 推断（示例：docx）
      if (contentType.includes('docx')) {
        fileName += '.docx';
      }
    }

    
    link.download = fileName;
    // 模拟点击 a 标签触发下载
    link.click();
    // 释放 blob 对象 URL
    window.URL.revokeObjectURL(link.href);
    alert('文件下载请求已发送，若有文件将开始下载');
  } catch (err) {
    console.error('文件下载失败', err);
    // 调用统一错误处理函数
    error.value = handleError(err);
    alert(error.value);
  } finally {
    // 关闭加载状态
    loading.value = false;
  }
};
//zyb----------------------------------------

// 组件挂载时加载日志
onMounted(() => {
  fetchLogs();
});
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
.stats-area {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f9f9f9;
}
.stats-card {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stats-item {
  flex: 1;
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.stats-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}
.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}
.stats-chart {
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.stats-chart ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.stats-chart li {
  margin-bottom: 8px;
}

</style>