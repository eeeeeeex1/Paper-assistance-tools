<template>
  <div class="history-container">
    <div class="history-header">
      <h2><i class="iconfont icon-history"></i> 历史操作记录</h2>
    </div>

    <div class="history-content">
      <!-- 搜索和筛选区域 -->
      <div class="filter-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery"
            placeholder="搜索文档名称或操作类型..."
          />
          <i class="iconfont icon-search"></i>
        </div>
      </div>

      <!-- 操作记录表格 -->
      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>用户 ID</th> <!-- 新增列 -->
              <th>论文 ID</th> <!-- 新增：论文ID列 -->
              <th>操作时间</th>
              <th>文档名称</th>
              <th>具体操作</th>
              <th>下载</th> <!-- 下载列 -->
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="record in filteredRecords" :key="record.id">
              <!-- 直接显示id作为序号 -->
              <td>{{ record.id }}</td>
              <td>{{ record.userId }}</td> <!-- 显示用户 ID -->
              <td>{{ record.paperId ||   '  ---' }}</td> <!-- 新增：显示论文ID -->
              <td>{{ formatDate(record.operationTime) }}</td>
              <td>{{ record.documentName }}</td>
              
              <td>
                <span :class="`operation-tag ${record.operationType}`">
                  {{ getOperationName(record.operationType) }}
                </span>
              </td>

              <td>
                <button 
                  class="download-btn"
                  @click="downloadFile(record.paperId)"
                >
                  <i class="iconfont icon-download"></i> 下载
                </button>
              </td>
              
              <td>
                <button 
                  class="delete-btn"
                  @click="confirmDelete(record.id)"
                >
                  <i class="iconfont icon-delete"></i> 删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 空状态 -->
        <div class="empty-state" v-if="filteredRecords.length === 0">
          <i class="iconfont icon-empty"></i>
          <p>暂无操作记录</p>
        </div>

        <!-- 分页控件 -->
        <div class="pagination" v-if="filteredRecords.length > 0">
          <button 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            上一页
          </button>
          <span>第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
          <button 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>




<script setup lang="ts">
import { ref, computed, onMounted,watch } from 'vue';
import { DatePicker as VanDatePicker } from 'vant';
import 'vant/lib/date-picker/style';
import { getAuthorId } from '@/utils/auth';
import axios from 'axios';
import { ElMessage } from 'element-plus';

// 定义API基础路径（使用环境变量）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

// 模拟API获取操作记录
const operationTypes = {
  similaritycheck: '论文相似度查询',
  spellcheck: '论文错字纠正',
  textsummary: '论文主题总结'
};

// 设置默认值为空数组
const records = ref<any[]>([]);
const searchQuery = ref('');
const dateRange = ref<[Date, Date] | null>(null);
const currentPage = ref(1);
const pageSize = 8;
const historyRecords = ref([]);
const totalRecords = ref(0);
const isLoadingHistory = ref(false);
const totalPages = ref(1)

const fetchHistoryRecords = async (userId: any, page = 1, perPage = 8) => {
  try {
    // 显示加载状态
    isLoadingHistory.value = true;
    
    // 发送GET请求到后端API
    const response = await axios.get(
      `${API_BASE_URL}/api/operations/user/${userId}`,
      {
        params: {
          page,
          per_page: perPage
        }
      }
    );
    
    // 处理成功响应
    if (response.data.code === 200) {
      // 转换后端返回的数据格式以适配前端表格
        records.value  = response.data.data.operations.map((record: { id: any; user_id: any; paper_id: any; operation_time: any; file_name: any; operation_type: any; }) => ({
        id: record.id,
        userId: record.user_id, // 新增用户 ID
        paperId: record.paper_id, // 新增论文 ID
        operationTime: record.operation_time,
        documentName: record.file_name,
        operationType: record.operation_type,
      }));
      console.log('转换后的记录:',records.value); // 打印转换后的数据
     // 更新操作记录数据
      totalRecords.value = response.data.data.total;
      totalPages.value = response.data.data.pages;
      
      //ElMessage.info('操作记录获取成功');
      return response.data.data;
    } else {
      ElMessage.error(response.data.message || '获取操作记录失败');
      return null;
    }
  } catch (error) {
    console.error('获取操作记录失败:', error);
    ElMessage.error('网络错误，请稍后重试');
    return null;
  } finally {
    // 隐藏加载状态
    isLoadingHistory.value = false;
  }
};

// 初始化加载数据
onMounted(async () => {
  const userId = getAuthorId(); // 从auth工具获取用户ID

 if (userId) await fetchHistoryRecords(userId, currentPage.value, pageSize);
});

// 格式化日期
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

// 获取操作类型名称
const getOperationName = (type: string) => {
  return operationTypes[type as keyof typeof operationTypes] || type;
};

// 过滤后的记录
const filteredRecords = computed(() => {
  let result = [...records.value];
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(record => 
      record.documentName.toLowerCase().includes(query) || 
      getOperationName(record.operationType).includes(query)
    );
  }
  
  // 日期过滤
  if (dateRange.value) {
    const [start, end] = dateRange.value;
    result = result.filter(record => {
      const recordDate = new Date(record.operationTime);
      return recordDate >= start && recordDate <= end;
    });
  }    
  return result;
});
// 监听 currentPage 变化
watch(currentPage, async (newPage) => {
  const userId = getAuthorId();
  if (userId) {
    await fetchHistoryRecords(userId, newPage, pageSize);
  }
});

// 删除记录
const confirmDelete = async (id: number) => {
  if (confirm('确定要删除这条记录吗？')) {
    try {
      // 发送删除请求到后端
      const response = await axios.delete(`${API_BASE_URL}/api/operations/${id}`);
      if (response.data.code === 200) {
        //ElMessage.success('操作记录删除成功');
        // 从前端数据中移除已删除的记录
        records.value = records.value.filter(record => record.id !== id);
        // 重新加载操作记录
        const userId = getAuthorId();
        if (userId) {
          await fetchHistoryRecords(userId, currentPage.value, pageSize);
        }
      } else {
        ElMessage.error(response.data.message || '删除操作记录失败');
      }
    } catch (error) {
      console.error('删除操作记录失败:', error);
      ElMessage.error('网络错误，请稍后重试');
    }
  }
};


//zyb----------------------------------------
// 下载文件函数，根据论文ID调用后端接口
const downloadFile = async (paper_id) => {
  // 获取论文ID，若为'-'表示没有论文ID，给出提示并返回
  console.log('下载按钮点击，论文ID:', paper_id); // 调试日志
  const paperId = paper_id;
  
  if (!paperId || paperId === '-') {
    ElMessage.warning('该操作记录无有效论文ID，无法下载');
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
    ElMessage.error(err.response?.data?.message || '下载失败，请重试');
  }
};
//zyb----------------------------------------



</script>
<style scoped>
/* 样式部分保持不变 */
</style>

<style scoped>
.history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.history-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.history-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #1e293b;
}

.history-header i {
  margin-right: 10px;
  color: #4f46e5;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box input {
  width: 100%;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
}

.search-box i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.date-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-filter label {
  font-size: 0.9rem;
  color: #64748b;
}

.history-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th, td {
  padding: 0.8rem 1rem;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

th {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 500;
}

.operation-tag {
  display: inline-block;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.operation-tag.similaritycheck {
  background-color: #e0f2fe;
  color: #0369a1;
}

.operation-tag.spellcheck {
  background-color: #dcfce7;
  color: #166534;
}

.operation-tag.textsummary {
  background-color: #fae8ff;
  color: #86198f;
}

.delete-btn {
  padding: 0.3rem 0.6rem;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background-color: #fee2e2;
  color: #b91c1c;
}

.delete-btn:hover {
  background-color: #fecaca;
}

.download-btn {
  padding: 0.3rem 0.6rem;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  background-color: #b9d2e5;
  color: #2b46c9;
}

.download-btn:hover {
  background-color: #bed9ec;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #94a3b8;
}

.empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1.5rem;
  gap: 1rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  font-size: 0.9rem;
  color: #64748b;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-section {
    flex-direction: column;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .date-filter {
    width: 100%;
  }
  
  th, td {
    padding: 0.6rem;
    font-size: 0.8rem;
  }
}
</style>