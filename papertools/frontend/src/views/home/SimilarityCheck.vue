<template>
  <div class="similarity-check-page">
    <div class="page-header">
      <h2>论文相似度查询</h2>
      <p>上传您的论文并与现有文献进行对比</p>
    </div>

    <div class="function-container">
      <!-- 上传文件模块 -->
      <div class="upload-section">
        <h3>上传文件</h3>
        <div 
          class="upload-area"
          @dragover.prevent="dragOver = true"
          @dragleave="dragOver = false"
          @drop.prevent="handleFileDrop"
          :class="{ 'drag-over': dragOver }"
        >
          <i class="iconfont icon-upload"></i>
          <p>拖拽文件到此处或</p>
          <input 
            type="file" 
            id="fileInput"
            @change="handleFileSelect"
            accept=".doc,.docx,.pdf,.txt"
            hidden
          >
          <label for="fileInput" class="browse-btn">浏览文件</label>
          <p class="file-info" v-if="uploadedFile">
            <i class="iconfont icon-file"></i>
            {{ uploadedFile.name }} ({{ formatFileSize(uploadedFile.size) }})
            <button @click.stop="removeFile" class="remove-btn">
              <i class="iconfont icon-close"></i>
            </button>
          </p>
        </div>

        <!-- 文件预览区域 -->
        <div v-if="fileContent" class="file-preview">
          <h4>文件预览</h4>
          <div class="preview-content">
            <pre v-if="isTextFile">{{ fileContent }}</pre>
            <iframe 
              v-else-if="isPdfFile"
              :src="pdfPreviewUrl"
              width="100%"
              height="500px"
            ></iframe>
            <p v-else>不支持预览此文件类型</p>
          </div>
        </div>
      </div>

      <!-- 对比文件模块 -->
      <div class="compare-section">
        <h3>对比文件</h3>
        <div class="compare-options">
          <div class="option-item">
            <input 
              type="checkbox" 
              id="compareWeb"
              v-model="compareOptions.webSearch"
            >
            <label for="compareWeb">网络文献对比</label>
          </div>
          <div class="option-item">
            <input 
              type="checkbox" 
              id="compareDatabase"
              v-model="compareOptions.databaseSearch"
            >
            <label for="compareDatabase">本地数据库对比</label>
          </div>
          <div class="option-item">
            <input 
              type="checkbox" 
              id="comparePrevious"
              v-model="compareOptions.previousWorks"
            >
            <label for="comparePrevious">历史作品对比</label>
          </div>
        </div>
        <div class="api-settings" v-if="compareOptions.webSearch">
          <h4>API设置</h4>
          <div class="form-group">
            <label>爬取深度</label>
            <select v-model="apiSettings.depth">
              <option value="1">浅层 (快速)</option>
              <option value="2">中等</option>
              <option value="3">深层 (全面)</option>
            </select>
          </div>
          <div class="form-group">
            <label>结果数量</label>
            <input 
              type="number" 
              v-model.number="apiSettings.resultCount"
              min="1"
              max="20"
            >
          </div>
        </div>
      </div>
    </div>

    <!-- 开始对比按钮 -->
    <div class="action-section">
      <button 
        class="compare-btn"
        :class="{ disabled: !canCompare }"
        @click="startComparison"
        :disabled="!canCompare"
      >
        <i class="iconfont icon-compare"></i>
        开始对比
      </button>
    </div>

    <!-- 对比结果 -->
    <div class="result-section" :class="{ active: showResults }">
      <div class="result-header">
        <h3>对比结果</h3>
        <div class="result-meta">
          <span>检测时间: {{ new Date().toLocaleString() }}</span>
          <button 
            class="export-btn"
            :disabled="!resultsReady || isExporting"
            @click="handleExportReport"
          >
            <i class="iconfont" :class="exportBtnIcon"></i>
            {{ exportBtnText }}
          </button>
        </div>
      </div>
      
      <div class="result-content">
        <div v-if="!resultsReady" class="empty-result">
          <i class="iconfont icon-file-search"></i>
          <p>请先上传文件并点击"开始对比"</p>
        </div>
        
        <div v-else class="result-details">
          <!-- 导出状态提示 -->
          <div v-if="exportStatus" class="export-status" :class="exportStatus.type">
            <i class="iconfont" :class="exportStatus.icon"></i>
            <p>{{ exportStatus.message }}</p>
            <a 
              v-if="exportStatus.downloadUrl" 
              :href="exportStatus.downloadUrl"
              class="download-link"
              download="论文相似度报告.pdf"
            >
              <i class="iconfont icon-download"></i>
              下载报告
            </a>
          </div>

          <!-- 对比结果内容 -->
          <div class="similarity-score">
            <div class="score-card">
              <h4>总体相似度</h4>
              <div class="score-value">{{ overallSimilarity }}%</div>
              <div class="score-progress">
                <div 
                  class="progress-bar"
                  :style="{ width: overallSimilarity + '%' }"
                ></div>
              </div>
            </div>
          </div>
          
          <div class="sources-list">
            <h4>相似来源</h4>
            <div class="source-item" v-for="(source, index) in sources" :key="index">
              <div class="source-header">
                <span class="source-title">{{ source.title }}</span>
                <span class="source-similarity">{{ source.similarity }}%</span>
              </div>
              <div class="source-url">{{ source.url }}</div>
              <div class="source-excerpt">
                {{ source.excerpt }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue';

// 上传文件状态
const dragOver = ref(false);
const uploadedFile = ref<File | null>(null);
const fileContent = ref('');
const isTextFile = ref(false);
const isPdfFile = ref(false);
const pdfPreviewUrl = ref('');

// 对比选项
const compareOptions = ref({
  webSearch: true,
  databaseSearch: false,
  previousWorks: false
});

// API设置
const apiSettings = ref({
  depth: '2',
  resultCount: 10
});

// 对比结果状态
const showResults = ref(false);
const resultsReady = ref(false);
const overallSimilarity = ref(0);
const sources = ref<any[]>([]);

// 导出报告状态
const isExporting = ref(false);
const exportStatus = ref<{
  type: 'info' | 'success' | 'error';
  message: string;
  icon: string;
  downloadUrl?: string;
} | null>(null);

// 计算属性
const canCompare = computed(() => {
  return uploadedFile.value !== null && (
    compareOptions.value.webSearch || 
    compareOptions.value.databaseSearch || 
    compareOptions.value.previousWorks
  );
});

const exportBtnText = computed(() => {
  return isExporting.value ? '生成中...' : '导出报告';
});

const exportBtnIcon = computed(() => {
  return isExporting.value ? 'icon-loading spin' : 'icon-export';
});

// 文件处理方法
const handleFileDrop = async (e: DragEvent) => {
  dragOver.value = false;
  if (e.dataTransfer?.files) {
    uploadedFile.value = e.dataTransfer.files[0];
    await previewFile(uploadedFile.value);
  }
};

const handleFileSelect = async (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files?.length) {
    uploadedFile.value = input.files[0];
    await previewFile(uploadedFile.value);
  }
};

const previewFile = (file: File) => {
  fileContent.value = '';
  isTextFile.value = false;
  isPdfFile.value = false;
  
  if (file.type.includes('text/') || file.name.endsWith('.txt')) {
    isTextFile.value = true;
    const reader = new FileReader();
    reader.onload = (e) => {
      fileContent.value = e.target?.result as string;
    };
    reader.readAsText(file);
  } else if (file.type === 'application/pdf') {
    isPdfFile.value = true;
    pdfPreviewUrl.value = URL.createObjectURL(file);
  }
};

const removeFile = () => {
  uploadedFile.value = null;
  fileContent.value = '';
  if (pdfPreviewUrl.value) {
    URL.revokeObjectURL(pdfPreviewUrl.value);
    pdfPreviewUrl.value = '';
  }
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 对比功能
const startComparison = () => {
  if (!canCompare.value) return;
  
  showResults.value = true;
  resultsReady.value = false;
  
  // 模拟API调用
  setTimeout(() => {
    // 模拟结果数据
    overallSimilarity.value = Math.floor(Math.random() * 30) + 5; // 5-35%
    sources.value = [
      {
        title: "基于深度学习的文本相似度计算方法研究",
        url: "https://example.com/paper1",
        similarity: Math.floor(Math.random() * 20) + 5, // 5-25%
        excerpt: "本文提出了一种基于注意力机制的文本相似度计算方法..."
      },
      {
        title: "学术论文抄袭检测系统设计与实现",
        url: "https://example.com/paper2",
        similarity: Math.floor(Math.random() * 15) + 5, // 5-20%
        excerpt: "针对学术论文抄袭问题，本文设计了一种基于..."
      }
    ].sort((a, b) => b.similarity - a.similarity);
    
    resultsReady.value = true;
  }, 2000);
};

// 导出报告功能
const handleExportReport = async () => {
  if (!resultsReady.value || isExporting.value) return;
  
  isExporting.value = true;
  exportStatus.value = {
    type: 'info',
    message: '正在生成报告，请稍候...',
    icon: 'icon-hourglass'
  };

  try {
    // 实际API调用 - 替换为您的真实API
    const formData = new FormData();
    if (uploadedFile.value) {
      formData.append('file', uploadedFile.value);
    }
    formData.append('results', JSON.stringify({
      similarity: overallSimilarity.value,
      sources: sources.value
    }));

    const response = await fetch('https://your-api-endpoint/generate-report', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) throw new Error(data.message || '生成报告失败');
    
    exportStatus.value = {
      type: 'success',
      message: '报告生成成功！',
      icon: 'icon-check-circle',
      downloadUrl: data.downloadUrl
    };
  } catch (error: any) {
    exportStatus.value = {
      type: 'error',
      message: error.message || '报告生成失败',
      icon: 'icon-close-circle'
    };
  } finally {
    isExporting.value = false;
  }
};

// 清理资源
onUnmounted(() => {
  if (pdfPreviewUrl.value) {
    URL.revokeObjectURL(pdfPreviewUrl.value);
  }
});
</script>

<style scoped>
.similarity-check-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h2 {
  font-size: 1.8rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.page-header p {
  color: #64748b;
}

.function-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.upload-section, .compare-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

h3, h4 {
  font-size: 1.2rem;
  color: #1e293b;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area.drag-over {
  border-color: #4f46e5;
  background-color: #f5f3ff;
}

.upload-area i {
  font-size: 2.5rem;
  color: #4f46e5;
  margin-bottom: 1rem;
}

.browse-btn {
  display: inline-block;
  background: #4f46e5;
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  margin-top: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.browse-btn:hover {
  background: #4338ca;
}

.file-info {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.file-info i {
  font-size: 1.2rem;
  color: #64748b;
}

.remove-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  margin-left: 8px;
}

.file-preview {
  margin-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
  padding-top: 1.5rem;
}

.preview-content {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  max-height: 500px;
  overflow-y: auto;
}

.preview-content pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
}

.compare-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option-item {
  display: flex;
  align-items: center;
}

.option-item input {
  margin-right: 0.75rem;
}

.api-settings {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f1f5f9;
}

.api-settings h4 {
  font-size: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #475569;
}

.form-group select, .form-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.action-section {
  text-align: center;
  margin-bottom: 2rem;
}

.compare-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0.8rem 2.5rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.compare-btn:hover:not(:disabled) {
  background: #4338ca;
  transform: translateY(-2px);
}

.compare-btn.disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.result-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  transition: all 0.5s ease;
}

.result-section.active {
  opacity: 1;
  max-height: 2000px;
  padding: 1.5rem;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #f1f5f9;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #64748b;
  font-size: 0.9rem;
}

.export-btn {
  position: relative;
  padding: 0.75rem 1.5rem;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.export-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.export-status {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.export-status.info {
  background: #e0f2fe;
  color: #0369a1;
}

.export-status.success {
  background: #dcfce7;
  color: #166534;
}

.export-status.error {
  background: #fee2e2;
  color: #991b1b;
}

.download-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border-radius: 4px;
  text-decoration: none;
  color: #4f46e5;
  transition: all 0.3s;
}

.download-link:hover {
  background: #eef2ff;
}

.empty-result {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

.empty-result i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.similarity-score {
  margin-bottom: 2rem;
}

.score-card {
  background: #f8fafc;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
}

.score-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1e293b;
  margin: 1rem 0;
}

.score-progress {
  height: 10px;
  background: #e2e8f0;
  border-radius: 5px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: #4f46e5;
  transition: width 1s ease;
}

.sources-list {
  margin-top: 2rem;
}

.source-item {
  padding: 1.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.source-item:last-child {
  border-bottom: none;
}

.source-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.source-title {
  font-weight: 500;
  color: #1e293b;
}

.source-similarity {
  color: #ef4444;
  font-weight: bold;
}

.source-url {
  color: #3b82f6;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  word-break: break-all;
}

.source-excerpt {
  color: #475569;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .function-container {
    grid-template-columns: 1fr;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .result-meta {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .similarity-check-page {
    padding: 1rem;
  }
  
  .upload-area {
    padding: 1.5rem;
  }
  
  .compare-btn, .export-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>