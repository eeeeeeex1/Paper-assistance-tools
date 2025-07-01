<template>
  <div class="summary-container">
    <!-- 左右布局（左侧上传，右侧预览） -->
    <div class="summary-layout">
      <!-- 左侧文件上传区域 -->
      <div class="upload-section">
        <div class="upload-area">
          <h3>上传文件</h3>
          <div class="upload-box" @dragover.prevent="dragover" @drop.prevent="drop">
            <input 
              type="file" 
              id="fileInput" 
              ref="fileInput" 
              @change="handleFileUpload" 
              accept=".txt,.doc,.docx,.pdf" 
              style="display: none;"
            />
            <i class="iconfont icon-upload"></i>
            <p>拖放文件到此处或</p>
            <button class="upload-btn" @click="triggerFileInput">选择文件</button>
            <p class="file-format">支持格式: .txt, .doc, .docx, .pdf</p>
          </div>
        </div>

        <div class="file-info" v-if="fileContent">
          <h4>已上传文件</h4>
          <p><strong>文件名:</strong> {{ fileName }}</p>
          <p><strong>大小:</strong> {{ fileSize }} KB</p>
          <p><strong>字数:</strong> {{ wordCount }} 字</p>
        </div>

        <button 
          class="summary-btn" 
          :disabled="!fileContent || isSummarizing"
          @click="generateSummary"
        >
          <span v-if="!isSummarizing"><i class="iconfont icon-summarize"></i> 主题总结</span>
          <span v-else><i class="iconfont icon-loading"></i> 总结中...</span>
        </button>
      </div>

      <!-- 右侧总结预览区域 -->
      <div class="preview-section">
        <div class="preview-header">
          <h3>主题总结预览</h3>
          <button 
            class="export-btn"
            :disabled="!summaryContent"
            @click="exportSummary"
          >
            <i class="iconfont icon-export"></i> 导出总结
          </button>
        </div>
        <div class="preview-content" v-if="summaryContent">
          <div v-html="highlightedSummary"></div>
        </div>
        <div class="empty-preview" v-else>
          <i class="iconfont icon-summary"></i>
          <p>请上传文件并点击"主题总结"按钮</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import * as mammoth from 'mammoth';
import { getAuthorId } from '@/utils/auth';
import axios from 'axios';
// 文件处理相关
const fileInput = ref<HTMLInputElement | null>(null);
const fileContent = ref<string>('');
const fileName = ref<string>('');
const fileSize = ref<number>(0);
const isSummarizing = ref<boolean>(false);
const summaryContent = ref<string>('');
const errorMessage = ref<string>('');
// 统计信息
const wordCount = computed(() => {
  return fileContent.value ? fileContent.value.split(/\s+/).length : 0;
});
// 从后端返回结果中提取的关键词（用于高亮）
const extractedKeywords = ref<string[]>([]);


// 高亮显示关键词
const highlightedSummary = computed(() => {
  if (!summaryContent.value || extractedKeywords.value.length === 0) return '';
  
  let content = summaryContent.value;
  extractedKeywords.value.forEach(keyword => {
    const regex = new RegExp(escapeRegExp(keyword), 'g');
    content = content.replace(regex, `<span class="highlight-keyword">${keyword}</span>`);
  });
  
  return content;
});

// 转义正则特殊字符
const escapeRegExp = (string: string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click();
};

// 处理拖放事件
const dragover = (event: DragEvent) => {
  const target = event.currentTarget as HTMLElement;
  target?.classList.add('dragover');
};

const drop = (event: DragEvent) => {
  const target = event.currentTarget as HTMLElement;
  target?.classList.remove('dragover');
  const files = event.dataTransfer?.files;
  if (files && files.length > 0) {
    processFile(files[0]);
  }
};

// 处理文件上传
const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    processFile(input.files[0]);
  }
};

// 处理文件内容
const processFile = async (file: File) => {
  // 重置状态
  fileContent.value = '';
  summaryContent.value = '';
  fileName.value = file.name;
  fileSize.value = Math.round(file.size / 1024); // KB
  
  try {
    if (file.name.endsWith('.txt')) {
      // 处理TXT文件
      fileContent.value = await file.text();
    } else if (file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
      // 处理DOCX/DOC文件
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      fileContent.value = result.value;
    } else if (file.name.endsWith('.pdf')) {
      // 处理PDF文件 - 实际项目中需要使用PDF解析库
      alert('PDF解析功能需要额外集成PDF.js等库');
    } else {
      alert('不支持的文件格式');
    }
  } catch (error) {
    console.error('文件解析出错:', error);
    alert('文件解析失败，请重试');
  }
};

// 导出总结结果
const exportSummary = () => {
  if (!summaryContent.value) return;
  
  // 创建一个临时div来提取纯文本
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = summaryContent.value;
  const plainText = tempDiv.textContent || summaryContent.value;
  
  // 创建Blob对象
  const blob = new Blob([plainText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  
  // 创建下载链接
  const a = document.createElement('a');
  a.href = url;
  a.download = `主题总结_${fileName.value.replace(/\.[^/.]+$/, '')}.txt`;
  
  // 触发下载
  document.body.appendChild(a);
  a.click();
  
  // 清理
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 调用后端API生成主题总结
const generateSummary = async () => {
  const file = fileInput.value?.files[0];
  if (!file) {
    errorMessage.value = '请先上传文件';
    return;
  }
  
  isSummarizing.value = true;
  errorMessage.value = '';
  
  try {
    // 创建FormData并添加文件内容（实际项目中应直接上传文件）
    // 注意：当前实现是将文件内容转为文本上传，更优的方式是直接上传文件对象
    const formData = new FormData();
    formData.append('file', file);
    
    // 调用后端API
    const response = await axios.post(`http://localhost:5000/api/paper/theme`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    if (response.data.code === 200) {
      // 处理成功响应
      const data = response.data.data;
      summaryContent.value = generateSummaryHTML(data);
      extractedKeywords.value = data.keywords || [];
    } else {
      // 处理错误响应
      errorMessage.value = response.data.message || '主题总结生成失败';
    }
  } catch (error: any) {
    console.error('API调用出错:', error);
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试';
  } finally {
    isSummarizing.value = false;
  }
};


// 根据后端返回数据生成HTML摘要
const generateSummaryHTML = (data: any): string => {
  if (!data) return '';
  
  const { title, keywords, summary, top_words } = data;
  const topWordsList = top_words.slice(0, 5).map(([word, count]) => `<li>${word} (${count}次)</li>`).join('');
  
  return `
    <div class="summary-result">
      <h4>文档主题总结</h4>
      <p>生成时间: ${new Date().toLocaleString()}</p>
      
      <div class="summary-meta">
        <p><strong>文档标题:</strong> ${title || '未提取到标题'}</p>
        <p><strong>关键词:</strong> ${keywords.join('，')}</p>
      </div>
      
      <div class="summary-section">
        <h5>主题概述</h5>
        <p>${summary || '暂无主题概述'}</p>
      </div>
      
      <div class="summary-section">
        <h5>高频词汇</h5>
        <ul>
          ${topWordsList}
        </ul>
      </div>
      
      <div class="summary-footer">
        <p>本总结由智能系统生成，仅供参考。</p>
      </div>
    </div>
  `;
};

// 模拟总结算法
const mockSummaryAlgorithm = (text: string): string => {
  // 简单实现 - 实际项目中应使用NLP算法
  const sentences = text.split(/[.!?。！？]\s+/);
  const importantSentences = sentences
    .filter(s => s.length > 20 && s.length < 150)
    .slice(0, 5);
  
  // 提取关键词（模拟）
  const words = text.split(/\s+/);
  const wordFrequency: Record<string, number> = {};
  words.forEach(word => {
    if (word.length > 2) { // 只考虑长度大于2的词
      wordFrequency[word] = (wordFrequency[word] || 0) + 1;
    }
  });
  
  const topKeywords = Object.entries(wordFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([word]) => word);
  
  return `
    <div class="summary-result">
      <h4>文档主题总结</h4>
      <p>生成时间: ${new Date().toLocaleString()}</p>
      
      <div class="summary-section">
        <h5>核心主题</h5>
        <p>根据文档内容分析，主要讨论了以下几个核心主题：</p>
        <ul>
          ${topKeywords.map(kw => `<li>${kw}</li>`).join('')}
        </ul>
      </div>
      
      <div class="summary-section">
        <h5>主要内容</h5>
        <p>文档中的关键内容包括：</p>
        <ol>
          ${importantSentences.map(s => `<li>${s}</li>`).join('')}
        </ol>
      </div>
      
      <div class="summary-footer">
        <p>本总结由智能系统生成，仅供参考。</p>
      </div>
    </div>
  `;
};
</script>

<style scoped>
.summary-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.summary-layout {
  display: flex;
  gap: 2rem;
}

/* 左侧上传区域样式 */
.upload-section {
  width: 350px;
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-area {
  margin-bottom: 1.5rem;
}

.upload-box {
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-box.dragover {
  background-color: #f8fafc;
  border-color: #94a3b8;
}

.upload-box i {
  font-size: 2.5rem;
  color: #94a3b8;
  margin-bottom: 1rem;
}

.upload-btn {
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
  transition: background-color 0.3s;
}

.upload-btn:hover {
  background-color: #4338ca;
}

.file-format {
  font-size: 0.8rem;
  color: #94a3b8;
}

.file-info {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 6px;
}

.file-info h4 {
  margin-top: 0;
  color: #334155;
}

.file-info p {
  margin: 0.5rem 0;
}

.summary-btn {
  width: 100%;
  padding: 0.8rem;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.3s;
}

.summary-btn:hover:not(:disabled) {
  background-color: #059669;
}

.summary-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
}

/* 右侧预览区域样式 */
.preview-section {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.preview-header h3 {
  margin: 0;
}

.export-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.export-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
}

.export-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.preview-content {
  flex: 1;
  max-height: 600px;
  overflow-y: auto;
  padding: 1rem;
  line-height: 1.6;
}

.empty-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
}

.empty-preview i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* 总结内容样式 */
.summary-result {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.summary-result h4 {
  color: #1e40af;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.summary-section {
  margin: 1.5rem 0;
}

.summary-section h5 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.summary-section ul,
.summary-section ol {
  padding-left: 1.5rem;
}

.summary-section li {
  margin-bottom: 0.5rem;
}

.summary-footer {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px dashed #e5e7eb;
}

.highlight-keyword {
  background-color: #dbeafe;
  color: #1d4ed8;
  padding: 0 2px;
  border-radius: 2px;
  font-weight: 500;
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.icon-loading {
  animation: spin 1s linear infinite;
  display: inline-block;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .summary-layout {
    flex-direction: column;
  }
  
  .upload-section {
    width: 100%;
  }
  
  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>