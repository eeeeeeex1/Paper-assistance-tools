<template>
  <div class="statistic-container">
    <div class="statistic">
      <h2 class="statistic-title">日志管理</h2>

      <!-- 搜索与筛选区域 -->
      <div class="filter-area">
        <div class="filter-group">
          <label>用户ID</label>
          <input 
            type="number" 
            v-model="filter.userId" 
            placeholder="输入用户ID"
            class="filter-input"
          >
        </div>
        
        <div class="filter-group">
          <label>操作类型</label>
          <select v-model="filter.operationType" class="filter-select">
            <option value="">全部</option>
            <option value="similaritycheck">论文相似度查询</option>
            <option value="spellcheck">论文错字纠正</option>
            <option value="textsummary">论文主题总结</option>
          </select>
        </div>
        
        <button class="filter-button" @click="applyFilter">
          <i class="fas fa-search"></i> 筛选
        </button>
      </div>
      <!-- 表格区域 -->
      <div class="chart-section">
        <h3>操作记录</h3>
        
        <!-- 加载状态 -->
        <div v-if="isLoadingHistory" class="loading-state">
          <i class="fas fa-spinner fa-spin"></i>
          <span>加载中...</span>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <i class="fas fa-exclamation-circle"></i>
          <span>{{ error }}</span>
        </div>
        
        <!-- 空状态 -->
        <div v-else-if="filteredRecords.length === 0" class="empty-state">
          <i class="fas fa-file-alt"></i>
          <span>暂无日志记录</span>
        </div>
        
        <!-- 表格 -->
        <div v-else class="data-table">
          <table>
            <thead>
              <tr>
                <th>序号</th>
                <th>用户ID</th>
                <th>论文ID</th>
                <th>操作类型</th>
                <th>操作时间</th>
                <th>文件名</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record) in filteredRecords" :key="record.id">
                <td>{{ record.id }}</td>
                <td>{{ record.userId }}</td>
                <td>{{ record.paperId || '-' }}</td>
                <td>{{ getOperationName(record.operationType) }}</td>
                <td>{{ formatDate(record.operationTime) }}</td>
                <td>{{ record.documentName || '-' }}</td>
                <td class="action-buttons">
                  <button 
                    class="download-btn" 
                    @click="downloadFile(record.paperId)"
                    :disabled="!record.paperId || record.paperId === '-'"
                  >
                    <i class="fas fa-download"></i> 下载
                  </button>
                  <button class="delete-btn" @click="confirmDelete(record.id)">
                    <i class="fas fa-trash"></i> 删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 分页 -->
      <!-- 分页 -->
      <div class="pagination-container" v-if="filteredRecords.length > 0">
        <div class="pagination-wrapper">
          <button 
            @click="goToPage(1)" 
            :disabled="currentPage === 1"
            class="pagination-button"
          >
            <i class="fas fa-angle-double-left"></i>
          </button>
          <button 
            @click="goToPage(currentPage - 1)" 
            :disabled="currentPage === 1"
            class="pagination-button"
          >
            <i class="fas fa-angle-left"></i>
          </button>
          
          <div class="page-info">
            <span>当前第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
          </div>
          
          <button 
            @click="goToPage(currentPage + 1)" 
            :disabled="currentPage === totalPages"
            class="pagination-button"
          >
            <i class="fas fa-angle-right"></i>
          </button>
          <button 
            @click="goToPage(totalPages)" 
            :disabled="currentPage === totalPages"
            class="pagination-button"
          >
            <i class="fas fa-angle-double-right"></i>
          </button>
        </div>
        </div>
       </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { getAuthorId } from '@/utils/auth';
import axios from 'axios';
import { ElMessage } from 'element-plus';

// 定义API基础路径（使用环境变量）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// 操作类型映射
const operationTypes = {
  similaritycheck: '论文相似度查询',
  spellcheck: '论文错字纠正',
  textsummary: '论文主题总结'
};

// 数据状态
const records = ref<any[]>([]);
const filter = ref({
  userId: '',
  operationType: '',
});
const dateRange = ref<[string, string]>(['', '']);
const currentPage = ref(1);
const pageSize = 8;
const totalRecords = ref(0);
const isLoadingHistory = ref(false);
const totalPages = ref(1);
const error = ref('');

// 计算属性
const uniqueUsers = computed(() => {
  const userIds = new Set(records.value.map(record => record.userId));
  return userIds.size;
});

const uniquePapers = computed(() => {
  const paperIds = new Set(records.value.map(record => record.paperId).filter(Boolean));
  return paperIds.size;
});

const filteredRecords = computed(() => {
  let result = [...records.value];
  
  // 用户ID筛选
  if (filter.value.userId) {
    const targetUserId = parseInt(filter.value.userId, 10);
    result = result.filter(record => record.userId === targetUserId);
  }
  
  // 操作类型筛选
  if (filter.value.operationType) {
    result = result.filter(record => record.operationType === filter.value.operationType);
  }
  
  // 日期范围筛选
  if (dateRange.value[0] && dateRange.value[1]) {
    const startDate = new Date(dateRange.value[0]);
    const endDate = new Date(dateRange.value[1]);
    
    result = result.filter(record => {
      const recordDate = new Date(record.operationTime);
      return recordDate >= startDate && recordDate <= endDate;
    });
  }
  
  return result;
});

const visiblePages = computed(() => {
  const pages = [];
  const current = currentPage.value;
  const total = totalPages.value;
  const range = 0; 
  
  if (current > range + 1) {
    pages.push(1);
    if (current > range + 2) {
      pages.push('...');
    }
  }
  
  for (let i = Math.max(1, current - range); i <= Math.min(total, current + range); i++) {
    pages.push(i);
  }
  
  if (current < total - range) {
    if (current < total - range - 1) {
      pages.push('...');
    }
    pages.push(total);
  }
  
  return pages;
});
const fetchHistoryRecords = async ( page = 1, perPage = 8) => {
  try {
    isLoadingHistory.value = true;
    error.value = '';
    const response = await axios.get(
      `${API_BASE_URL}/api/operations/getall`,
      {
        params: {
          page,
          per_page: perPage,
        }
      }
    );
    
    // 适配后端返回格式
    if (response.data.status === 'success') {
      records.value = response.data.data.records.map((record: any) => ({
        id: record.id,
        userId: record.user_id,
        paperId: record.paper_id,
        operationTime: record.operation_time, // 时间格式已在后端处理为ISO字符串
        documentName: record.file_name,
        operationType: record.operation_type,
      }));
      
      totalRecords.value = response.data.data.total;
      totalPages.value = response.data.data.pages;
    } else {
      error.value = response.data.message || '获取操作记录失败';
    }
  } catch (err) {
    console.error('获取操作记录失败:', err);
    error.value = err.response?.data?.message || '网络错误，请稍后重试';
  } finally {
    isLoadingHistory.value = false;
  }
};

const applyFilter = () => {
  currentPage.value = 1;
  const userId = getAuthorId();
  fetchHistoryRecords(currentPage.value, pageSize);
};

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  const userId = getAuthorId();
  fetchHistoryRecords( page, pageSize);
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getOperationName = (type: string) => {
  return operationTypes[type as keyof typeof operationTypes] || type;
};

const confirmDelete = async (id: number) => {
  // 1. 立即显示加载状态，防止重复点击
  const isDeleting = ref(false);
  if (isDeleting.value) return;
  isDeleting.value = true;

  // 2. 保存当前列表快照，用于回滚
  const originalRecords = [...records.value];
  
  try {
    // 3. 乐观更新：立即从UI中移除记录，提升响应速度
    records.value = records.value.filter(item => item.id !== id);
    ElMessage.info('正在删除...');
    
    // 4. 发送删除请求到后端
    const response = await axios.delete(`${API_BASE_URL}/api/operations/${id}`);
    
    // 5. 验证后端响应
    if (response.data.code === 200) {
      ElMessage.success('操作记录删除成功');
      
      // 6. 可选：刷新分页状态（如果删除后当前页为空）
      if (records.value.length === 0 && currentPage.value > 1) {
        await fetchHistoryRecords(currentPage.value - 1, pageSize.value);
      }
    } else {
      // 7. 后端返回错误，回滚UI
      records.value = originalRecords;
      ElMessage.error(response.data.message || '删除操作记录失败');
    }
  } catch (err) {
    // 8. 网络错误，回滚UI
    records.value = originalRecords;
    console.error('删除操作记录失败:', err);
    ElMessage.error('网络错误，请稍后重试');
  } finally {
    // 9. 重置加载状态
    isDeleting.value = false;
  }
};

//zyb----------------------------------------
// 下载文件函数，根据论文ID调用后端接口
const downloadFile = async (paper_id) => {
  // 获取论文ID，若为'-'表示没有论文ID，给出提示并返回
  console.log('下载按钮点击，论文ID:', paper_id); // 调试日志
  const paperId = paper_id;
  
  if (!paperId || paperId === '-') {
    //ElMessage.warning('该操作记录无有效论文ID，无法下载');
    return;
  }
  
  try {
    // 获取token
    const token = localStorage.getItem('token') || '';
    
    // 调用后端下载接口
    const response = await axios.get(`${API_BASE_URL}/api/paper/downloadPaper?paper_id=${paperId}`, {
      responseType: 'blob',
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      }
    });
    
    // 处理响应
    const blob = new Blob([response.data]);
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    
    // 解析文件名
    let fileName = 'downloaded_file';
    const contentDisposition = response.headers['content-disposition'] || '';
    
    // 1. 从Content-Disposition解析文件名
    const match = contentDisposition.match(/filename(?:\*=UTF-8''|=")([^;"]+)(?="|;|$)/);
    if (match && match[1]) {
      fileName = decodeURIComponent(match[1].trim());
    }
    
    // 2. 从Content-Type推断扩展名
    const contentType = response.headers['content-type'] || '';
    if (!fileName.match(/\.\w+$/)) {
      if (contentType.includes('docx')) fileName += '.docx';
      else if (contentType.includes('pdf')) fileName += '.pdf';
      else if (contentType.includes('excel') || contentType.includes('spreadsheet')) fileName += '.xlsx';
      else fileName += '.txt'; // 默认为文本文件
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
    link.click();
    window.URL.revokeObjectURL(link.href);
    
    //ElMessage.success('文件下载请求已发送');
  } catch (err) {
    console.error('文件下载失败:', err);
    //ElMessage.error(err.response?.data?.message || '下载失败，请重试');
  }
};
//zyb----------------------------------------



// 初始化加载数据
onMounted(() => {
  const userId = getAuthorId();
  fetchHistoryRecords( currentPage.value, pageSize);
});

// 监听页码变化
watch(currentPage, (newPage) => {
  const userId = getAuthorId();
  fetchHistoryRecords( newPage, pageSize);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');

.statistic-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  min-height: 100vh;
  padding: 30px;
  font-family: 'Poppins', sans-serif;
}

.statistic {
  max-width: 1400px;
  margin: 0 auto;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  padding: 40px;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.statistic-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
  position: relative;
  padding-bottom: 15px;
}

.statistic-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #647eff, #42d392);
  border-radius: 2px;
}

.filter-area {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
}

.filter-input, .filter-select, .date-input {
  padding: 10px 15px;
  border: 1px solid #e0e3e7;
  border-radius: 8px;
  min-width: 180px;
  transition: all 0.3s;
  font-family: 'Poppins', sans-serif;
  background: #f8fafc;
}

.filter-input:focus, .filter-select:focus, .date-input:focus {
  outline: none;
  border-color: #647eff;
  box-shadow: 0 0 0 2px rgba(100, 126, 255, 0.1);
}

.date-range-picker {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-button {
  padding: 10px 20px;
  background: linear-gradient(135deg, #647eff, #42d392);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.filter-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.statistic-cards {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  flex: 1;
  border-left: 4px solid;
  position: relative;
  overflow: hidden;
  min-height: 100px;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
  z-index: 1;
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
  z-index: 2;
}

.card-content {
  z-index: 2;
}

.card-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 5px;
}

.card-value {
  font-size: 22px;
  font-weight: 600;
  color: #2c3e50;
}

.card-user {
  border-left-color: #647eff;
}

.card-user .card-icon {
  background: linear-gradient(135deg, #647eff, #8a9cff);
}

.card-paper {
  border-left-color: #42d392;
}

.card-paper .card-icon {
  background: linear-gradient(135deg, #42d392, #6bdfaa);
}

.card-storage {
  border-left-color: #ff9a3c;
}

.card-storage .card-icon {
  background: linear-gradient(135deg, #ff9a3c, #ffb26b);
}

.chart-section {
  margin-bottom: 30px;
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.chart-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #7f8c8d;
  gap: 15px;
  font-size: 16px;
}

.loading-state i {
  font-size: 30px;
  color: #647eff;
  animation: rotating 2s linear infinite;
}

.error-state i {
  font-size: 30px;
  color: #ef476f;
}

.empty-state i {
  font-size: 30px;
  color: #ff9a3c;
}

.data-table {
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th {
  background-color: #f8fafc;
  font-weight: 600;
  padding: 15px;
  text-align: left;
  color: #2c3e50;
  border-bottom: 2px solid #e0e3e7;
}

td {
  padding: 12px 15px;
  border-bottom: 1px solid #e0e3e7;
  color: #4a5568;
}

tr:hover {
  background-color: #f8fafc;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.download-btn, .delete-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s;
  font-weight: 500;
}

.download-btn {
  background: linear-gradient(135deg, #42d392, #6bdfaa);
  color: white;
}

.download-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #3bc382, #5bd49c);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(66, 211, 146, 0.2);
}

.download-btn:disabled {
  background: #e0e3e7;
  color: #a0aec0;
  cursor: not-allowed;
}

.delete-btn {
  background: linear-gradient(135deg, #ef476f, #ff6b8b);
  color: white;
}

.delete-btn:hover {
  background: linear-gradient(135deg, #e63e66, #f55f7f);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(239, 71, 111, 0.2);
}

.pagination-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination-button {
  min-width: 40px;
  height: 40px;
  border: 1px solid #e0e3e7;
  background: white;
  color: #4a5568;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  font-family: 'Poppins', sans-serif;
  font-weight: 500;
}

.pagination-button:hover:not(:disabled) {
  color: #647eff;
  border-color: #c6e2ff;
  background-color: #f8fafc;
  transform: translateY(-2px);
}

.pagination-button.active {
  background: linear-gradient(135deg, #647eff, #8a9cff);
  color: white;
  border-color: #647eff;
  box-shadow: 0 4px 8px rgba(100, 126, 255, 0.2);
}

.pagination-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .statistic {
    padding: 20px;
  }
  
  .statistic-cards {
    flex-wrap: wrap;
  }
  
  .card {
    min-width: calc(50% - 10px);
  }
  
  .filter-area {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .statistic-cards {
    flex-direction: column;
  }
  
  .card {
    min-width: 100%;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .pagination-container {
    gap: 5px;
  }
  
  .pagination-button {
    min-width: 36px;
    height: 36px;
    font-size: 14px;
  }
}

.page-info {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4a5568;
  font-weight: 500;
  margin-left: 15px;
  font-size: 14px;
}
.pagination-wrapper {
  /* 核心：强制水平排列，覆盖可能的垂直布局 */
  display: flex;
  flex-direction: row;  
  align-items: center; /* 垂直居中对齐 */
  justify-content: center; /* 水平居中（可选，按需求调整） */
  gap: 8px; /* 按钮、文字间距 */
}

/* 确保按钮样式不干扰布局 */
.pagination-button {
  min-width: 40px;
  height: 40px;
  /* 其他原有样式... */
}

.page-info {
  /* 文字样式保持原有，确保和按钮对齐 */
  display: inline-flex; 
  align-items: center;
}

</style>