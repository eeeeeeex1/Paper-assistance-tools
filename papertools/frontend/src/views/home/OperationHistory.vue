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
        <div class="date-filter">
          <label>时间范围：</label>
          <date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </div>
      </div>

      <!-- 操作记录表格 -->
      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>操作时间</th>
              <th>文档名称</th>
              <th>具体操作</th>
              <th>操作后文件</th>
              <th>操作前文件</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(record, index) in filteredRecords" :key="record.id">
              <td>{{ index + 1 }}</td>
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
                  @click="downloadFile(record.afterFileUrl, record.documentName)"
                  :disabled="!record.afterFileUrl"
                >
                  <i class="iconfont icon-download"></i> 下载
                </button>
              </td>
              <td>
                <button 
                  class="download-btn"
                  @click="downloadFile(record.beforeFileUrl, record.documentName)"
                  :disabled="!record.beforeFileUrl"
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
import { ref, computed, onMounted } from 'vue';
import { DatePicker as VanDatePicker } from 'vant';
import 'vant/lib/date-picker/style';
import { getAuthorId } from '@/utils/auth';
import axios from 'axios';
import { ElMessage } from 'element-plus';

// 模拟API获取操作记录*********************************************************************
const operationTypes = {
  similarity: '论文相似度查询',
  spellcheck: '论文错字纠正',
  summary: '论文主题总结'
};

const records = ref<any[]>([]);
const searchQuery = ref('');
const dateRange = ref<[Date, Date] | null>(null);
const currentPage = ref(1);
const pageSize = 10;
const historyRecords = ref([]);
const totalRecords = ref(0);
const isLoadingHistory = ref(false);
const totalPages = ref(1)
const fetchHistoryRecords = async (userId, page = 1, perPage = 20) => {
  try {
    // 显示加载状态
    isLoadingHistory.value = true;
    
    // 发送GET请求到后端API
    const response = await axios.get(
      `http://localhost:5000/api/operations/user/${userId}`,
      {
        params: {
          page,
          per_page: perPage
        }
      }
    );
    
    // 处理成功响应
    if (response.data.code === 200) {
      // 更新操作记录数据
      historyRecords.value = response.data.data.operations;
      totalRecords.value = response.data.data.total;
      currentPage.value = response.data.data.current_page;
      totalPages.value = response.data.data.pages;
      
      ElMessage.info('操作记录获取成功');
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
// 初始化加载数据
onMounted(async () => {
  const userId = getAuthorId(); // 从auth工具获取用户ID
  if (!userId) {
    ElMessage.error('未获取到用户ID，无法加载操作记录');
    return;
  }
  
  const result = await fetchHistoryRecords(userId, currentPage.value, pageSize);
  if (result) {
    records.value = result.operations;
    totalPages.value = result.pages;
    totalRecords.value = result.total;
  }
});


//*----------------------------------------------------------
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
  
  // 分页
  const start = (currentPage.value - 1) * pageSize;
  return result.slice(start, start + pageSize);
});

// 总页数


// 下载文件
const downloadFile = (url: string, filename: string) => {
  if (!url) return;
  
  // 实际项目中这里应该是文件下载逻辑
  console.log(`下载文件: ${filename} (${url})`);
  alert(`开始下载: ${filename}`);
};

// 删除记录
const confirmDelete = (id: string) => {
  if (confirm('确定要删除这条记录吗？')) {
    records.value = records.value.filter(record => record.id !== id);
  }
};
</script>

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

.operation-tag.similarity {
  background-color: #e0f2fe;
  color: #0369a1;
}

.operation-tag.spellcheck {
  background-color: #dcfce7;
  color: #166534;
}

.operation-tag.summary {
  background-color: #fae8ff;
  color: #86198f;
}

.download-btn, .delete-btn {
  padding: 0.3rem 0.6rem;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.download-btn {
  background-color: #e0f2fe;
  color: #0369a1;
}

.download-btn:hover:not(:disabled) {
  background-color: #bae6fd;
}

.download-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.delete-btn {
  background-color: #fee2e2;
  color: #b91c1c;
}

.delete-btn:hover {
  background-color: #fecaca;
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