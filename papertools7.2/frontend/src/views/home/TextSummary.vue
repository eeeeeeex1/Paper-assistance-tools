<template>
  <div class="summary-container">
    <!-- 检查用户权限 -->
    <div v-if="hasPermission">
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
                accept=".txt,.doc,.docx" 
                style="display: none;"
              />
              <i class="iconfont icon-upload"></i>
              <p>拖放文件到此处或</p>
              <button class="upload-btn" @click="triggerFileInput">选择文件</button>
              <p class="file-format">支持格式: .txt,.docx</p>
            </div>
          </div>

          <div class="file-info" v-if="fileContent">
            <h4>已上传文件</h4>
            <p><strong>文件名:</strong> {{ fileName }}</p>
            <p><strong>大小:</strong> {{ fileSize }} KB</p>
            <p><strong>字数:</strong> {{ wordCount }} 字</p>
            <p><strong>字符数:</strong> {{ charCount }} 个</p>
            <p><strong>英文单词数:</strong> {{ englishWordCount }} 个</p>
            <p v-if="fileParsingError" class="text-error">
              <strong>解析警告:</strong> {{ fileParsingError }}
            </p>
            <p><strong>解析状态:</strong> <span style="color: #10b981;">已解析完成</span></p>
          </div>

          <!-- API选择按钮组 -->
          <div class="button-group">
            <button 
              class="summary-btn" 
              :disabled="!fileContent || isSummarizing || fileContent.length < 10"
              @click="selectedApi = 'ai'; generateThemeSummary()"
              :class="{ active: selectedApi === 'ai' }"
            >
              <i class="iconfont icon-robot"></i> AI智能提取
            </button>
            <button 
              class="summary-btn" 
              :disabled="!fileContent || isSummarizing || fileContent.length < 10"
              @click="selectedApi = 'paper'; generateThemeSummary()"
              :class="{ active: selectedApi === 'paper' }"
            >
              <i class="iconfont icon-document"></i> 传统算法提取
            </button>
          </div>
          
          <!-- 全局错误提示 -->
          <div class="global-error" v-if="errorMessage">
            <i class="iconfont icon-error"></i>
            <span>{{ errorMessage }}</span>
            <button @click="errorMessage = ''">×</button>
          </div>
        </div>

        <!-- 右侧结果预览区域 -->
        <div class="preview-section">
          <div class="preview-header">
            <h3>主题提取结果</h3>
            <button 
              class="export-btn"
              :disabled="!themeResult"
              @click="exportResult"
            >
              <i class="iconfont icon-export"></i> 导出结果
            </button>
          </div>
          
          <!-- 处理中状态 -->
          <div class="loading-preview" v-if="isSummarizing && !themeResult">
            <i class="iconfont icon-loading"></i>
            <p>主题提取中，请稍候...</p>
            <p class="method-indicator">提取方式: {{ apiText }}</p>
          </div>
          
          <div class="preview-content" v-else-if="themeResult">
            <div v-html="formattedResult"></div>
          </div>
          
          <div class="empty-preview" v-else>
            <i class="iconfont icon-summary"></i>
            <p>请上传文件并选择主题提取方式</p>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p>您没有权限使用此功能</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import * as mammoth from 'mammoth';
import axios from 'axios';
import { getAuthorId } from '@/utils/auth';
import { ElMessage } from 'element-plus'

// 定义主题提取结果类型
interface ThemeResult {
  title: string;
  keywords: string[];
  summary: string;
  top_words: [string, number][];
  original_length: number;
  generate_time: string;
  extraction_method: 'ai' | 'paper';
}

// 读取用户权限
const userData = localStorage.getItem('user');
const permission = userData ? JSON.parse(userData).permission : null;
const hasPermission = ref([3, 5, 6, 7].includes(permission));

// 文件处理相关
const fileInput = ref<HTMLInputElement | null>(null);
const fileContent = ref<string>('');
const fileName = ref<string>('');
const fileSize = ref<number>(0);
const isSummarizing = ref<boolean>(false);
const themeResult = ref<ThemeResult | null>(null);
const errorMessage = ref<string>('');
const fileParsingError = ref<string>('');
const selectedApi = ref<'ai' | 'paper'>('ai');
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const paperId = ref<number | null>(null);
const storedFile = ref<File | null>(null); // 新增：存储文件对象
// API文本显示
const apiText = computed(() => {
  return selectedApi.value === 'ai' ? 'AI智能提取' : '传统算法提取';
});

// 更精确的字数统计函数
const getAccurateWordCount = (text: string) => {
  if (!text) return 0;
  
  // 中文字符数量
  const chineseChars = text.match(/[\u4e00-\u9fa5]/g)?.length || 0;
  
  // 英文单词数量（连续的字母、数字、下划线）
  const englishWords = text.match(/\b[a-zA-Z0-9_]+\b/g)?.length || 0;
  
  return chineseChars + englishWords;
};

// 统计信息
const wordCount = computed(() => {
  return fileContent.value ? getAccurateWordCount(fileContent.value) : 0;
});

const charCount = computed(() => fileContent.value?.length || 0);
const englishWordCount = computed(() => {
  return fileContent.value?.match(/\b[a-zA-Z0-9_]+\b/g)?.length || 0;
});

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
  themeResult.value = null;
  fileName.value = file.name;
  fileSize.value = Math.round(file.size / 1024); // KB
  fileParsingError.value = '';
  
  // 检查文件大小
  if (file.size > MAX_FILE_SIZE) {
    fileParsingError.value = `文件大小不能超过5MB，当前大小: ${(file.size / 1024 / 1024).toFixed(2)}MB`;
    throw new Error('File too large');
  }
  
  try {
    storedFile.value=file
    //await uploadFileToServer(file);
    if (file.name.endsWith('.txt')) {
      // 处理TXT文件
      fileContent.value = await file.text();
    } else if (file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
      // 处理DOCX/DOC文件
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      fileContent.value = result.value;
    } else {
      fileParsingError.value = '不支持的文件格式，仅支持 .txt, .doc, .docx';
      throw new Error('Unsupported file format');
    }
    
    // 检查内容是否为空
    if (!fileContent.value.trim()) {
      fileParsingError.value = '文件内容为空，请上传有实际内容的文件';
      throw new Error('File content is empty');
    }
    
  } catch (error) {
    console.error('文件解析出错:', error);
    fileParsingError.value = '文件解析失败，请检查文件格式或内容';
  }
};

// 上传文件到服务器
const uploadFileToServer = async (file: File) => {
  try {
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', getAuthorId()); // 假设getAuthorId()获取用户ID
    formData.append('title', file.name);
    formData.append('file_size', file.size.toString());
    
    // 发送POST请求到后端文件上传接口
    const response = await axios.post(
      'http://localhost:5000/api/paper/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('token') || 'test-token'}`
        }
      }
    );
    
    if (response.data.code !== 200) {
      throw new Error(response.data.message || '文件上传失败');
    }
    
    console.log('文件上传成功:', response.data.data);
    paperId.value = response.data.data; // 假设后端返回的数据结构里有paper_id字段
    console.info('paperid',paperId.value)
    // 可以在这里获取后端返回的文件存储信息（如file_id, file_path等）
    // 例如：fileStorageInfo.value = response.data.data;
  } catch (error: any) {
    console.error('文件上传失败:', error);
    throw new Error(error.response?.data?.message || '文件上传失败，请重试');
  }
};

// 导出结果
const exportResult = () => {
  if (!themeResult.value) return;
  
  // 创建一个临时div来提取纯文本
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = formattedResult.value;
  const plainText = tempDiv.textContent || '主题提取结果\n\n' + JSON.stringify(themeResult.value, null, 2);
  
  // 创建Blob对象
  const blob = new Blob([plainText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  
  // 创建下载链接
  const a = document.createElement('a');
  a.href = url;
  a.download = `${fileName.value.replace(/\.[^/.]+$/, '')}_${apiText.value}.txt`;
  
  // 触发下载
  document.body.appendChild(a);
  a.click();
  
  // 清理
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 调用API生成主题提取结果
const generateThemeSummary = async () => {
  if (!hasPermission.value) {
    errorMessage.value = '您没有权限使用此功能';
    return;
  }
  
  if (fileParsingError.value) {
    errorMessage.value = fileParsingError.value;
    return;
  }
  
  const content = fileContent.value.trim();
  if (!content) {
    errorMessage.value = '文件内容为空，无法进行主题提取';
    return;
  }
  
  // 检查内容长度是否适合AI处理
  if (content.length > 20000) {
    if (!confirm('文件内容超过20000字，可能需要较长处理时间，是否继续？')) {
      return;
    }
  }
  
  isSummarizing.value = true;
  errorMessage.value = '';
  
  try {

    if (storedFile.value) {
      await uploadFileToServer(storedFile.value);
    }
    let apiUrl = '';
    let requestData: any = {};
    let headers: any = {};
    
    // 根据选择的API类型准备请求
    if (selectedApi.value === 'ai') {
      // 使用AI API (http://localhost:5000/api/ai/theme_extraction)
      apiUrl = 'http://localhost:5000/api/ai/theme_extraction';
      requestData = {
        content: content,
        file_name: fileName.value,
        user_id: getAuthorId(),
        paper_id: paperId.value,
        parameters: {
          max_tokens: 500,
          temperature: 0.3
        }
      };
      headers = {
        'Content-Type': 'application/json'
      };
    } else {
      // 使用Paper API (http://localhost:5000/api/paper/theme_extraction)
      apiUrl = 'http://localhost:5000/api/paper/theme';
      
      // 创建FormData
      const formData = new FormData();
      const file = fileInput.value?.files[0];
      formData.append('file', file);
      if (file) formData.append('file', file);
      formData.append('user_id', getAuthorId());
      formData.append('content', content);
      formData.append('word_count', wordCount.value.toString());
      formData.append('paper_id', paperId.value.toString());
      
      requestData = formData;
      headers = {
        'Content-Type': 'multipart/form-data'
      };
    }
    
    // 发送请求
    const response = await axios.post(apiUrl, requestData, { headers });
    
    if (response.data.code === 200) {
      // 添加提取方法信息
      themeResult.value = {
        ...response.data.data,
        extraction_method: selectedApi.value
      };
    } else {
      // 显示后端返回的具体错误信息
      errorMessage.value = response.data.message || '主题提取失败';
      console.error('API错误响应:', response.data);
    }
  } catch (error: any) {
    console.error('API调用出错:', error);
    
    // 处理网络错误
    if (error.response) {
      errorMessage.value = error.response.data?.message || `错误状态码: ${error.response.status}`;
      console.error('错误响应数据:', error.response.data);
    } else if (error.request) {
      errorMessage.value = '请求已发出但未收到响应，请检查网络连接';
    } else {
      errorMessage.value = `请求出错: ${error.message}`;
    }
  } finally {
    isSummarizing.value = false;
  }
};

// 格式化结果为HTML
const formattedResult = computed(() => {
  if (!themeResult.value) return '';
  
  // 提取关键信息
  const title = themeResult.value.title || '未提取到标题';
  const keywords = themeResult.value.keywords || [];
  const summary = themeResult.value.summary || '暂无主题概述';
  const top_words = themeResult.value.top_words || [];
  const original_length = themeResult.value.original_length || wordCount.value;
  
  // 方法名称
  const methodName = themeResult.value.extraction_method === 'ai' 
    ? 'AI智能提取' 
    : '传统算法提取';
  
  const keywordList = keywords.map(kw => `<span class="keyword-tag">${kw}</span>`).join(' ');
  const topWordsList = top_words.slice(0, 5).map(([word, count]) => `<li>${word} (${count}次)</li>`).join('');
  
  return `
    <div class="theme-result">
      <h4>文档主题分析</h4>
      <p>生成时间: ${themeResult.value.generate_time || new Date().toLocaleString()}</p>
      <p>提取方式: <span class="method-tag">${methodName}</span></p>
      
      <div class="result-meta">
        <p><strong>文档标题:</strong> ${title}</p>
        <p><strong>关键词:</strong> ${keywordList}</p>
        <p><strong>原文字数:</strong> ${original_length} 字</p>
        <p><strong>摘要字数:</strong> ${summary.length} 字</p>
      </div>
      
      <div class="result-section">
        <h5>主题概述</h5>
        <p>${summary}</p>
      </div>
      
      <div class="result-section">
        <h5>高频词汇</h5>
        <ul>
          ${topWordsList}
        </ul>
      </div>
      
      <div class="result-footer">
        <p>本分析由${methodName}系统生成，仅供参考。</p>
      </div>
      
      <div class="result-source">
        <p><strong>原始文件:</strong> ${fileName.value}</p>
        <p><strong>文件大小:</strong> ${fileSize.value} KB</p>
      </div>
    </div>
  `;
});
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

.text-error {
  color: #ef4444;
}

/* 按钮组样式 */
.button-group {
  position: relative;
  margin-bottom: 1rem;
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
  justify-content: space-between;
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

.api-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  padding: 0.5rem 0;
  display: none;
  z-index: 10;
  margin-top: 0.3rem;
}

.api-menu div {
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
}

.api-menu div:hover {
  background-color: #f8fafc;
}

.api-menu i {
  margin-right: 0.5rem;
  width: 1.2rem;
}

/* 显示时的动画 */
.api-menu.v-show-active {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
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

.loading-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.loading-preview i {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #10b981;
  animation: spin 1s linear infinite;
}

.method-indicator {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #94a3b8;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 总结内容样式 */
.theme-result {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.theme-result h4 {
  color: #1e40af;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.result-meta {
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.result-meta p {
  margin: 0.5rem 0;
}

.keyword-tag {
  background-color: #dbeafe;
  color: #1d4ed8;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  margin-right: 0.5rem;
  display: inline-block;
  margin-bottom: 0.3rem;
}

.method-tag {
  background-color: #ecfccb;
  color: #65a30d;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.result-section {
  margin: 1.5rem 0;
}

.result-section h5 {
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.result-section ul {
  padding-left: 1.5rem;
}

.result-section li {
  margin-bottom: 0.5rem;
}

.result-footer {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px dashed #e5e7eb;
}

.result-source {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #f1f5f9;
  border-radius: 6px;
  font-size: 0.9rem;
}

/* 全局错误提示 */
.global-error {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 0.8rem 1rem;
  border-radius: 6px;
  margin-top: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.global-error i {
  margin-right: 0.5rem;
}

.global-error button {
  background: none;
  border: none;
  color: #991b1b;
  cursor: pointer;
  font-size: 1.2rem;
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

.button-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.summary-btn {
  flex: 1;
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

.summary-btn.active {
  background-color: #059669;
}

.summary-btn:hover:not(:disabled) {
  background-color: #059669;
}

.summary-btn:disabled {
  background-color: #cbd5e1;
  cursor: not-allowed;
}
</style>