<template>
  <div class="spell-check-container">
    <!-- 文件上传/预览区域 -->
    <div class="file-section">
      <div v-if="!fileContent" class="upload-area">
        <h3>上传文件</h3>
        <div class="upload-box" @dragover.prevent="dragover" @drop.prevent="drop">
          <input 
            type="file" 
            id="fileInput" 
            ref="fileInput" 
            @change="handleFileUpload" 
            accept=".txt,.doc,.docx" 
            style="display: none;"
          />
          <i class="iconfont icon-upload"></i>
          <p>拖放文件到此处或</p>
          <button class="upload-btn" @click="triggerFileInput">选择文件</button>
          <p class="file-format">支持格式: .txt, .doc, .docx</p>
        </div>
      </div>
      
      <div v-else class="preview-area">
        <h3>预览修改内容</h3>
        
        <!-- 新增：标签页切换 -->
        <div class="tabs" v-if="checkedContent">
          <button 
            :class="{ 'active-tab': activeTab === 'original' }"
            @click="switchTab('original')"
          >
            原文
          </button>
          <button 
            :class="{ 'active-tab': activeTab === 'corrected' }"
            @click="switchTab('corrected')"
          >
          </button>
        </div>
        
        <div class="content-display">
          <div v-if="fileContent && !checkedContent" class="empty-content">
            <p>文件内容已加载，点击"开始纠正"按钮进行错字检测</p>
          </div>
          
          <!-- 根据标签页切换显示不同内容 -->
          <div 
            class="text-content" 
            v-html="activeTab === 'original' ? highlightedContent : checkedContent"
            v-if="checkedContent"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- 操作按钮区域 -->
    <div class="action-section">
      <button 
        v-if="!isChecking && !checkedContent" 
        class="action-btn check-btn" 
        :disabled="!fileContent"
        @click="checkSpelling"
      >
        开始纠正
      </button>
      
      <button 
        v-if="isChecking" 
        class="action-btn checking-btn" 
        disabled
      >
        <i class="iconfont icon-loading"></i> 正在检测中...
      </button>
      
      <button 
        v-if="checkedContent && !isChecking" 
        class="action-btn export-btn" 
        @click="exportResult"
      >
        导出纠正结果
      </button>
    </div>
    
    <!-- 导出结果预览 -->
    <div v-if="exportedResult" class="export-result-box">
      <h4>导出结果文本预览</h4>
      <div class="export-result-content" v-html="exportedResult"></div>
    </div>

    <!-- 错误统计信息 -->
    <div v-if="checkedContent" class="stats-section">
      <div class="stat-item">
        <span class="stat-label">总字数:</span>
        <span class="stat-value">{{ stats.totalWords }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">错误数:</span>
        <span class="stat-value error-count">{{ stats.errorCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">错误率:</span>
        <span class="stat-value">{{ stats.errorRate }}%</span>
      </div>
    </div>
    
    <!-- 错误消息提示 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    
    <!-- 新增：错字列表详情 -->
    <div v-if="typoDetails.length > 0" class="typo-details">
      <h3>错字详情</h3>
      <ul>
        <li v-for="(typo, index) in typoDetails" :key="index">
          <span class="typo-word">{{ typo.word }}</span>
          <span class="typo-suggestion">→ {{ typo.suggestions[0] || '无建议' }}</span>
          <span class="typo-position">(位置: {{ typo.position }})</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import * as docx from 'docx-preview';
import * as mammoth from 'mammoth';
import axios from 'axios';
import { getAuthorId } from '@/utils/auth';
// 定义错字详情类型
interface TypoDetail {
  position: number;     // 错字起始位置
  word: string;         // 错误词
  length: number;       // 错字长度
  suggestions: string[]; // 修正建议
}

// 文件处理相关
const fileInput = ref<HTMLInputElement | null>(null);
const fileContent = ref<string>('');
const isChecking = ref<boolean>(false);
const checkedContent = ref<string>('');
const typoDetails = ref<TypoDetail[]>([]); // 存储错字详情
const fileName = ref<string>('');
const errorMessage = ref<string>('');
const exportedResult = ref<string>(''); // 存导出结果
const activeTab = ref<string>('original'); // 新增：用于切换原始/修正视图

// 统计信息
const stats = computed(() => {
  const totalWords = fileContent.value ? 
    fileContent.value.replace(/\s/g, '').length : 0; // 更准确的字数统计
  const errorCount = typoDetails.value.length;
  const errorRate = totalWords > 0 ? ((errorCount / totalWords) * 100).toFixed(2) : '0.00';
  
  return {
    totalWords,
    errorCount,
    errorRate
  };
});

// 高亮显示错误内容
const highlightedContent = computed(() => {
  if (!fileContent.value || typoDetails.value.length === 0) {
    return fileContent.value;
  }
  
  let content = fileContent.value;
  
  // 按位置倒序处理错字（从后往前，避免替换后位置偏移）
  const sortedTypos = [...typoDetails.value].sort((a, b) => b.position - a.position);
  
  sortedTypos.forEach(typo => {
    const { position, word, length, suggestions } = typo;
    
    // 验证错字位置和内容
    if (
      position < 0 || 
      position + length > content.length || 
      content.substr(position, length) !== word
    ) {
      console.warn(`错字位置无效: ${word} (位置: ${position}, 长度: ${length})`);
      return;
    }
    
    // 生成高亮标签
    const suggestionText = suggestions.length > 0 ? suggestions[0] : '无建议';
    const highlightTag = `<span class="error-word" title="建议: ${suggestionText}">${word}</span>`;
    
    // 替换错字（使用切片确保位置准确）
    content = content.substring(0, position) + 
              highlightTag + 
              content.substring(position + length);
  });
  
  return content;
});

// 生成导出格式的内容
const exportableContent = computed(() => {
  if (!fileContent.value || typoDetails.value.length === 0) {
    return fileContent.value;
  }
  
  let content = fileContent.value;
  
  // 按位置倒序处理错字
  const sortedTypos = [...typoDetails.value].sort((a, b) => b.position - a.position);
  
  sortedTypos.forEach(typo => {
    const { position, word, suggestions } = typo;
    const suggestion = suggestions.length > 0 ? suggestions[0] : word;
    
    // 生成导出格式：错误文本[正确文本]
    const exportTag = `${word}[${suggestion}]`;
    
    content = content.substring(0, position) + 
              exportTag + 
              content.substring(position + word.length);
  });
  
  return content;
});

// 转义正则特殊字符（保留用于兼容旧格式）
const escapeRegExp = (string: string | undefined) => {
  if (!string) return '';
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click();
};

// 处理拖放事件
const dragover = (event: DragEvent) => {
  (event.currentTarget as HTMLElement)?.classList.add('dragover');
};

const drop = (event: DragEvent) => {
  (event.currentTarget as HTMLElement)?.classList.remove('dragover');
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
  checkedContent.value = '';
  typoDetails.value = [];
  fileName.value = file.name;
  
  try {
    if (file.name.endsWith('.txt')) {
      // 处理TXT文件
      const content = await file.text();
      fileContent.value = content;
    } else if (file.name.endsWith('.docx')) {
      // 处理DOCX文件
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      fileContent.value = result.value;
    } else if (file.name.endsWith('.doc')) {
      // 处理DOC文件 - 使用docx-preview解析
      const arrayBuffer = await file.arrayBuffer();
      const result = await parseDocFile(arrayBuffer);
      fileContent.value = result;
    } else {
      alert('不支持的文件格式，请上传.txt、.doc或.docx文件');
    }
  } catch (error) {
    console.error('文件解析出错:', error);
    alert('文件解析失败，请重试');
  }
};

// 解析DOC文件
const parseDocFile = (arrayBuffer: ArrayBuffer): Promise<string> => {
  return new Promise((resolve, reject) => {
    try {
      // 创建一个临时容器元素
      const container = document.createElement('div');
      // 隐藏这个元素，不显示在页面上
      container.style.display = 'none';
      document.body.appendChild(container);
      
      docx.renderAsync(arrayBuffer, container, undefined, {
        ignoreLastRenderedPageBreak: true
      }).then(() => {
        // 获取解析后的文本内容
        let textContent = container.querySelector('.docx-wrapper')?.textContent || '';
        
        // 清理多余空白和换行
        textContent = textContent
          .replace(/\s+/g, ' ')  // 合并连续空白
          .replace(/\n+/g, '\n')  // 合并连续换行
          .trim();
        
        // 清理临时容器
        document.body.removeChild(container);
        resolve(textContent);
      }).catch(error => {
        // 确保在出错时也清理临时容器
        document.body.removeChild(container);
        reject(error);
      });
    } catch (error) {
      reject(error);
    }
  });
};

// 调用后端API检查拼写
const checkSpelling = async () => {
  if (!fileContent.value) {
    errorMessage.value = '请先上传并解析文件';
    return;
  }
  
  isChecking.value = true;
  errorMessage.value = '正在进行错字检测...';
  
  try {
    const formData = new FormData();
    const textFile = new File([fileContent.value], fileName.value, { type: 'text/plain' });
    const authorId = getAuthorId();
    formData.append('user_id', authorId);
    formData.append('file', textFile);
    
    const response = await axios.post(`http://localhost:5000/api/paper/spelling`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    if (response.data.code === 200) {
      const data = response.data.data;
      checkedContent.value = data.checked_text || fileContent.value;
      typoDetails.value = data.typo_details || []; // 关键：更新错字详情
      
      errorMessage.value = '';
      exportedResult.value = exportableContent.value; // 使用计算属性生成导出内容
    } else {
      errorMessage.value = response.data.message || '拼写检查失败';
    }
  } catch (error: any) {
    console.error('API调用出错:', error);
    errorMessage.value = error.response?.data?.message || '网络错误，请稍后重试';
  } finally {
    isChecking.value = false;
  }
};

// 导出结果
const exportResult = () => {
  if (!exportableContent.value) return;
  
  const blob = new Blob([exportableContent.value], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  
  const originalName = fileName.value.split('.')[0];
  a.download = `${originalName}_corrected.txt`;
  
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 切换标签页
const switchTab = (tabName: string) => {
  activeTab.value = tabName;
};

// 监听错字详情变化，用于调试
watch(typoDetails, (newVal) => {
  console.log('错字详情更新:', newVal);
}, { deep: true });
</script>

<style scoped>
.spell-check-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.file-section {
  margin-bottom: 2rem;
}

.upload-area, .preview-area {
  border: 2px dashed #e2e8f0;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s;
}

.upload-area h3, .preview-area h3 {
  margin-top: 0;
  color: #334155;
  margin-bottom: 1.5rem;
}

.upload-box {
  cursor: pointer;
}

.upload-box.dragover {
  background-color: #f8fafc;
  border-color: #94a3b8;
}

.upload-box i {
  font-size: 3rem;
  color: #94a3b8;
  margin-bottom: 1rem;
}

.upload-box p {
  color: #64748b;
  margin: 0.5rem 0;
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

.content-display {
  max-height: 400px;
  overflow-y: auto;
  text-align: left;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #f8fafc;
}

.text-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.action-section {
  text-align: center;
  margin-bottom: 2rem;
}

.action-btn {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.check-btn {
  background-color: #4f46e5;
  color: white;
}

.check-btn:hover {
  background-color: #4338ca;
}

.check-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
}

.checking-btn {
  background-color: #e2e8f0;
  color: #64748b;
}

.export-btn {
  background-color: #10b981;
  color: white;
}

.export-btn:hover {
  background-color: #059669;
}

.stats-section {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.5rem;
}

.stat-item {
  text-align: center;
  padding: 0.5rem 1rem;
  background-color: #f8fafc;
  border-radius: 6px;
}

.stat-label {
  display: block;
  color: #64748b;
  font-size: 0.9rem;
}

.stat-value {
  display: block;
  font-weight: 600;
  color: #1e293b;
  font-size: 1.2rem;
}

.error-count {
  color: #ef4444;
}

/* 错误词高亮样式 */
.error-word {
  background-color: #fee2e2;
  color: #dc2626;
  padding: 0 2px;
  border-radius: 2px;
  border-bottom: 1px dashed #dc2626;
  cursor: pointer;
  position: relative;
}

.error-word:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background-color: #1e293b;
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  z-index: 10;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .spell-check-container {
    padding: 1rem;
  }
  
  .stats-section {
    flex-direction: column;
    gap: 0.5rem;
  }
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.icon-loading {
  animation: spin 1s linear infinite;
  display: inline-block;
  margin-right: 0.5rem;
}

.error-message {
  color: #ef4444;
  text-align: center;
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #fee2e2;
  border-radius: 6px;
}

.empty-content {
  color: #64748b;
  text-align: center;
  padding: 2rem 0;
  border: 1px dashed #e2e8f0;
  border-radius: 6px;
}

.export-result-box {
  margin: 1rem 0;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #f8fafc;
}

.export-result-box h4 {
  margin-top: 0;
  color: #334155;
  margin-bottom: 0.5rem;
}

.export-result-content {
  white-space: pre-wrap;
  line-height: 1.6;
  max-height: 200px;
  overflow-y: auto;
}

.tabs {
  display: flex;
  margin-bottom: 1rem;
}

.tabs button {
  padding: 0.5rem 1rem;
  margin-right: 0.5rem;
  border: none;
  background-color: #f0f0f0;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
}

.tabs button.active-tab {
  background-color: #4f46e5;
  color: white;
}

.typo-details {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 8px;
}

.typo-details h3 {
  margin-top: 0;
  color: #334155;
}

.typo-details ul {
  list-style: none;
  padding: 0;
}

.typo-details li {
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.typo-word {
  color: #ef4444;
  font-weight: bold;
}

.typo-suggestion {
  color: #10b981;
  margin-left: 0.5rem;
}

.typo-position {
  color: #64748b;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}
</style>