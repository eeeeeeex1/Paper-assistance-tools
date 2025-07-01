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
        <div class="content-display">
          <div 
            class="text-content" 
            v-html="highlightedContent"
            v-if="checkedContent"
          ></div>
          <div class="text-content" v-else>
            {{ fileContent }}
          </div>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import * as docx from 'docx-preview';
import * as mammoth from 'mammoth';
import { getAuthorId } from '@/utils/auth';
import axios from 'axios';

// 文件处理相关
const fileInput = ref<HTMLInputElement | null>(null);
const fileContent = ref<string>('');
const isChecking = ref<boolean>(false);
const checkedContent = ref<string>('');
const errorPositions = ref<Array<{word: string, suggestions: string[]}>>([]);
const fileName = ref<string>('');
const errorMessage = ref<string>('');
const tab = ref<string>('original');

// 统计信息
const stats = computed(() => {
  const totalWords = fileContent.value ? fileContent.value.split(/\s+/).length : 0;
  const errorCount = errorPositions.value.length;
  const errorRate = totalWords > 0 ? ((errorCount / totalWords) * 100).toFixed(2) : '0.00';
  
  return {
    totalWords,
    errorCount,
    errorRate
  };
});

// 高亮显示错误内容
const highlightedContent = computed(() => {
  if (!fileContent.value || errorPositions.value.length === 0) {
    return fileContent.value;
  }
  
  let content = fileContent.value;
  errorPositions.value.forEach(error => {
    const regex = new RegExp(escapeRegExp(error.word), 'g');
    content = content.replace(regex, `<span class="error-word" title="建议: ${error.suggestions.join(', ')}">${error.word}</span>`);
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
  errorPositions.value = [];
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
        const textContent = container.querySelector('.docx-wrapper')?.textContent || '';
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
  errorMessage.value = '';
  
  try {
    // 创建FormData并添加文件内容
    const formData = new FormData();
    const textFile = new File([fileContent.value], fileName.value, { type: 'text/plain' });
    formData.append('file', textFile);
    
    // 调用后端API
    const response = await axios.post(`http://localhost:5000/api/paper/spelling`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    if (response.data.code === 200) {
      // 处理成功响应
      const data = response.data.data;
      checkedContent.value = data.checked_text || fileContent.value;
      errorPositions.value = data.typo_details || [];
    } else {
      // 处理错误响应
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
  if (!checkedContent.value) return;
  
  const blob = new Blob([checkedContent.value], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  
  // 根据原始文件名生成新文件名
  const originalName = fileName.value.split('.')[0];
  a.download = `${originalName}_corrected.txt`;
  
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 切换标签页
const switchTab = (tabName: string) => {
  tab.value = tabName;
};
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
</style>