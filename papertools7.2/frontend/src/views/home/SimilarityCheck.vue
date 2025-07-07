<template>
  <div class="similarity-check-page">
    <!-- 根据权限显示不同内容 -->
    <div v-if="hasPermission">
      <!-- 新增：选择查重方式 -->
      <div class="option-section">
        <label>选择查重方式：</label>
        <select v-model="selectedOption">
          <option value="webSearch">网络查重</option>
          <option value="localSearch">本地查重</option>
        </select>
      </div>
      <div class="page-header">
        <h2>论文相似度查询</h2>
        <p>上传您的论文并与现有文献进行对比</p>
      </div>

      <div class="function-container">
        <!-- 上传文件模块 -->
        <div class="upload-section">
          <h3>上传文件</h3>
          <!-- 网络查重上传区域 -->
          <div v-if="selectedOption === 'webSearch'"
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
            />
            <label for="fileInput" class="browse-btn">浏览文件</label>

            <!-- 新增：上传进度条 -->
            <div v-if="isUploading" class="upload-progress">
              <div class="progress-bar" :style="{ width: uploadProgress + '%' }">
                {{ uploadProgress }}%
              </div>
            </div>
          
            <!-- 新增：错误提示 -->
            <div v-if="uploadError" class="upload-error">
              <i class="iconfont icon-error"></i>
              <span>{{ uploadError }}</span>
            </div>
            <p class="file-info" v-if="uploadedFile">
              <i class="iconfont icon-file"></i>
              {{ uploadedFile.name }} ({{ formatFileSize(uploadedFile.size) }})
              <button @click.stop="removeFile" class="remove-btn">
                <i class="iconfont icon-close"></i>
              </button>
            </p>
          </div>
          <!-- 本地查重上传区域 -->
          <div v-if="selectedOption === 'localSearch'">
            <div 
              class="upload-area"
              @dragover.prevent="dragOver1 = true"
              @dragleave="dragOver1 = false"
              @drop.prevent="handleLocalFileDrop(1)"
              :class="{ 'drag-over': dragOver1 }"
            >
              <i class="iconfont icon-upload"></i>
              <p>拖拽文件1到此处或</p>
              <input 
                type="file" 
                id="file1"
                @change="handleLocalFileUpload(1)"
                accept=".doc,.docx,.pdf,.txt"
                hidden
              />
              <label for="file1" class="browse-btn">浏览文件</label>

              <p class="file-info" v-if="uploadedFile1">
                <i class="iconfont icon-file"></i>
                {{ uploadedFile1.name }} ({{ formatFileSize(uploadedFile1.size) }})
                <button @click.stop="removeLocalFile(1)" class="remove-btn">
                  <i class="iconfont icon-close"></i>
                </button>
              </p>
            </div>
            <div 
              class="upload-area"
              @dragover.prevent="dragOver2 = true"
              @dragleave="dragOver2 = false"
              @drop.prevent="handleLocalFileDrop(2)"
              :class="{ 'drag-over': dragOver2 }"
            >
              <i class="iconfont icon-upload"></i>
              <p>拖拽文件2到此处或</p>
              <input 
                type="file" 
                id="file2"
                @change="handleLocalFileUpload(2)"
                accept=".doc,.docx,.pdf,.txt"
                hidden
              />
              <label for="file2" class="browse-btn">浏览文件</label>

              <p class="file-info" v-if="uploadedFile2">
                <i class="iconfont icon-file"></i>
                {{ uploadedFile2.name }} ({{ formatFileSize(uploadedFile2.size) }})
                <button @click.stop="removeLocalFile(2)" class="remove-btn">
                  <i class="iconfont icon-close"></i>
                </button>
              </p>
            </div>
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

        <!-- API设置 -->
        <div v-if="selectedOption === 'webSearch'" class="api-settings">
          <h3>API设置</h3>
          <div class="settings-group">
            <div class="setting-item">
              <label>爬取深度</label>
              <select v-model="apiSettings.depth">
                <option value="1">浅</option>
                <option value="2">中</option>
                <option value="3">深</option>
              </select>
            </div>
            <div class="setting-item">
              <label>结果数量</label>
              <input 
                type="number" 
                v-model.number="apiSettings.resultCount" 
                min="1" 
                max="20"
              />
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
                <span>{{ exportStatus.message }}</span>
              </div>

              <!-- 网络查重结果 -->
              <div v-if="selectedOption === 'webSearch'">
                <div class="score">
                  <p class="score-label">综合相似度</p>
                  <div class="score-value">{{ overallSimilarity }}%</div>
                  <div class="score-progress">
                    <div class="progress-bar" :style="{ width: overallSimilarity + '%' }"></div>
                  </div>
                </div>

                <div class="sources-list">
                  <div v-for="(source, index) in sources" :key="index" class="source-item">
                    <div class="source-header">
                      <div class="source-title">{{ source.title }}</div>
                      <div class="source-similarity">{{ (source.similarity).toFixed(1) }}%</div>
                      <button @click="showSimilarFragments(index)" class="view-fragments-btn">查看相似片段</button>
                    </div>
                    <div class="source-url">{{ source.url }}</div>
                    <div class="source-excerpt">
                      {{ source.excerpt }}
                    </div>
                  </div>
                </div>

                <!-- lzj显示相似片段 -->
                <div v-if="showSimilarFragmentDetails" class="similar-fragment-details">
                  <h4>相似段落详情</h4>
                  <div class="fragment-container" v-if="selectedSource.similar_segments && selectedSource.similar_segments.length > 0">
                    <div class="comparison-pairs" v-for="(pair, index) in selectedSource.similar_segments" :key="index">
                      <div class="pair-header">
                        <span class="similarity-badge">相似度: {{ (pair.similarity * 100).toFixed(1) }}%</span>
                      </div>

                      <!-- 原文件（上传论文）的相似段落 -->
                      <div class="fragment-item">
                        <h5>上传文章相似段落</h5>
                        <pre>
                          <span class="highlight-similar">{{ pair.text1_content }}</span>
                        </pre>
                      </div>

                      <!-- 对比文件（文献）的相似段落 -->
                      <div class="fragment-item">
                        <h5>对比文章相似段落</h5>
                        <pre>
                          <span class="highlight-similar">{{ pair.text2_content }}</span>
                        </pre>
                      </div>
                    </div>
                  </div>
                  <p v-else>未找到相似段落</p>
                </div>
              </div>

              <!-- 本地查重结果 -->
                <div v-if="selectedOption === 'localSearch'">
                  <div v-if="comparisonResults.length > 0">
                    <h4>查重结果</h4>
                    <p>综合相似度：{{ comprehensiveSimilarity }}%</p>
                    
                    <!-- 遍历每一组相似段落 -->
                    <div v-for="(source, sourceIndex) in comparisonResults" :key="sourceIndex">
                      <h5>原文件相似段落</h5>
                      
                      <!-- 遍历原文件中的每个相似段落 -->
                      <div v-for="(segment, segmentIndex) in source.similar_segments.original" :key="segmentIndex">
                        <pre>
                          <span class="highlight-similar">{{ segment.content }}</span>
                        </pre>
                      </div>
                      
                      <h5>对比文章相似段落</h5>
                      
                      <!-- 遍历对比文件中的每个相似段落 -->
                      <div v-for="(segment, segmentIndex) in source.similar_segments.comparison" :key="segmentIndex">
                        <pre>
                          <span class="highlight-similar">{{ segment.content }}</span>
                        </pre>
                      
                      </div>
                      
                      <!-- 分隔线 -->
                      <div class="similarity-divider"></div>
                    </div>
                  </div>
      
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-permission">
      <p>您没有权限使用此功能</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { getAuthorId } from '@/utils/auth'; 
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios';

// 定义API基础路径（使用环境变量）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const router = useRouter();
const route = useRoute();
// 上传文件状态
const isUploading = ref(false);
const uploadProgress = ref(0);
const title = ref(''); 
const uploadError = ref<string | null>(null);

const dragOver = ref(false);
const dragOver1 = ref(false);
const dragOver2 = ref(false);
const uploadedFile = ref<File | null>(null);
const fileContent = ref('');
const isTextFile = ref(false);
const isPdfFile = ref(false);
const pdfPreviewUrl = ref('');
const fileName = ref<string>('');
const errorMessage = ref<string>('');

// 默认选择网络文献对比
const selectedOption = ref('webSearch'); 

// API设置 - 从localStorage加载或使用默认值
const savedApiSettings = localStorage.getItem('plagiarismApiSettings');
const apiSettings = ref(savedApiSettings ? JSON.parse(savedApiSettings) : {
  depth: '2',
  resultCount: 5
});

// 监听API设置变化，保存到localStorage
watch(apiSettings, (newSettings) => {
  localStorage.setItem('plagiarismApiSettings', JSON.stringify(newSettings));
}, { deep: true });

// 对比结果状态
const showResults = ref(false);
const resultsReady = ref(false);
const overallSimilarity = ref(0);
const sources = ref<any[]>([]);

const paperId = ref<number | null>(null);
const storedFileData = ref<File | null>(null); 

// 导出报告状态
const isExporting = ref(false);
const exportStatus = ref<{
  type: 'info' | 'success' | 'error';
  message: string;
  icon: string;
  downloadUrl?: string;
} | null>(null);

// 获取用户权限
const userPermission = ref<number | null>(null);
// 判断用户是否有权限
const hasPermission = computed(() => {
  return [1, 4, 5, 7].includes(userPermission.value || 0);
});

// 计算属性
const canCompare = computed(() => {
  if (selectedOption.value === 'webSearch') {
    return uploadedFile.value !== null;
  } else if (selectedOption.value === 'localSearch') {
    return uploadedFile1.value !== null && uploadedFile2.value !== null;
  }
  return false;
});

const exportBtnText = computed(() => {
  return isExporting.value ? '生成中...' : '导出报告';
});

const exportBtnIcon = computed(() => {
  return isExporting.value ? 'icon-loading spin' : 'icon-export';
});

// 新增：显示相似片段详情状态
const showSimilarFragmentDetails = ref(false);
const selectedSource = ref<any>(null);

// 新增本地文件引用
const uploadedFile1 = ref<File | null>(null);
const uploadedFile2 = ref<File | null>(null);

// 查重结果
const comparisonResults = ref([]);
const comprehensiveSimilarity = ref(0);

// 在页面加载时获取用户权限
onMounted(() => {
  const userInfo = localStorage.getItem('user');
  if (userInfo) {
    const { permission } = JSON.parse(userInfo);
    userPermission.value = permission;
  }
});

// 文件上传与查重核心函数
const uploadAndCheckPlagiarism = async (file: File) => {
  const formData = new FormData();
  console.group('【查重请求】参数检查');
  console.log('文件对象:', file);
  console.log('文件名:', file.name);

  const compareMethod = selectedOption.value;

  const authorId = getAuthorId();
  console.log('作者ID(localStorage):', authorId);
  if (!authorId) {
    //ElMessage.error('未获取到用户ID');
    return null;
  }
  
  if (storedFileData.value) {
      await uploadFileToBackend(storedFileData.value);
  }

  formData.append('file', file);
  // 附加API设置参数
  formData.append('num_articles', apiSettings.value.resultCount.toString());
  formData.append('user_id', authorId);
  formData.append('checkfunction', compareMethod);
  // 添加爬取深度参数
  formData.append('depth', apiSettings.value.depth);
  formData.append('paper_id',paperId.value.toString());
  try {
    

    console.log('发送查重请求到API...');
    isUploading.value = true;
    uploadProgress.value = 0;
    
    // 注意：根据实际后端API调整路径
    const response = await axios.post(`${API_BASE_URL}/api/paper/plagiarism`, formData, {
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        uploadProgress.value = percentCompleted;
      }
    });
    
    console.log('查重成功:', response.data);
    isUploading.value = false;
    return response.data;
    
  } catch (err: any) {
    console.error('查重失败详情:', {
      message: err.message,
      responseData: err.response?.data,
      responseStatus: err.response?.status
    });
    
    let errorMessage = '查重失败，请重试';
    if (err.response?.status === 404) {
      errorMessage = '未找到匹配结果';
    }
    uploadError.value = errorMessage;
    isUploading.value = false;
    return null;
  }
};

// 处理文件选择
const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement;
  if (input.files && input.files.length > 0) {
    uploadedFile.value = input.files[0];
    storedFileData.value=uploadedFile.value;
    previewFile(uploadedFile.value);
  }
  
 
};

// 处理文件拖拽
const handleFileDrop = (e: DragEvent) => {
  dragOver.value = false;
  if (e.dataTransfer?.files) {
    uploadedFile.value = e.dataTransfer.files[0];
    storedFileData.value=uploadedFile.value;
    previewFile(uploadedFile.value);
  }
};

// 处理本地文件上传
const handleLocalFileUpload = (fileIndex: number) => {
  const inputId = `file${fileIndex}`;
  const input = document.getElementById(inputId) as HTMLInputElement;
  if (input && input.files && input.files.length > 0) {
    if (fileIndex === 1) {
      uploadedFile1.value = input.files[0];
    } else if (fileIndex === 2) {
      uploadedFile2.value = input.files[0];
    }
  }

};

// 处理本地文件拖拽
const handleLocalFileDrop = (fileIndex: number, e: DragEvent) => {
  if (fileIndex === 1) {
    dragOver1.value = false;
    if (e.dataTransfer?.files) {
      uploadedFile1.value = e.dataTransfer.files[0];
    }
  } else if (fileIndex === 2) {
    dragOver2.value = false;
    if (e.dataTransfer?.files) {
      uploadedFile2.value = e.dataTransfer.files[0];
    }
  }

};

// 预览文件
const previewFile = (file: File) => {
  if (file.type === 'text/plain') {
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

const removeLocalFile = (fileIndex: number) => {
  if (fileIndex === 1) {
    uploadedFile1.value = null;
  } else if (fileIndex === 2) {
    uploadedFile2.value = null;
  }
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

//lzj对比功能（修改后 - 直接调用上传和查重函数）
const startComparison = async () => {
  if (selectedOption.value === 'webSearch') {
    // 1. 强化非空校验（确保文件已上传）
    if (!canCompare.value || !uploadedFile.value) {
      //ElMessage.error('请先上传有效的论文文件');
      return;
    }
    
    showResults.value = true;
    resultsReady.value = false;
    
    try {

      // 2. 类型断言：明确 uploadedFile.value 为 File 类型（已通过非空校验）
      const result = await uploadAndCheckPlagiarism(uploadedFile.value as File);
      if (!result) return;
      
      const data = result.data;
      overallSimilarity.value = data.comprehensive_similarity || 0;
      
      // 处理结果，包含相似片段
      sources.value = data.comparison_results.map((item: any) => ({
        title: item.article_title,
        url: item.url,
        similarity: item.similarity_rate,
        authors: item.authors,
        similar_segments: item.similar_segments || { original: '', comparison: '' }
      }));
      
      resultsReady.value = true;
      //ElMessage.success('查重完成');
    } catch (error: any) {
      console.error('查重处理失败:', error);
      uploadError.value = '查重分析失败，请稍后重试';
    }
  } else if (selectedOption.value === 'localSearch') {
    if (!uploadedFile1.value || !uploadedFile2.value) {
      ElMessage.error('请上传两个文件');
      return;
    }
    const formData = new FormData();
    formData.append('file1', uploadedFile1.value);
    formData.append('file2', uploadedFile2.value);
    formData.append('user_id', getAuthorId());
  
    try {
      const response = await axios.post(`${API_BASE_URL}/api/paper/check_local_plagiarism`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      comparisonResults.value = response.data.data.comparison_results;
      if(comparisonResults.value)console.info(comparisonResults.value);
      comprehensiveSimilarity.value = response.data.data.comprehensive_similarity;
      if(comprehensiveSimilarity.value)console.info(comprehensiveSimilarity.value);
      showResults.value = true;
      resultsReady.value = true;
      //ElMessage.success('查重完成');
    } catch (error) {
      //ElMessage.error('查重失败，请稍后再试');
    }
  }
};

// 导出报告功能（保持逻辑不变，后续可扩展）
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

//lzj 新增：显示相似片段函数
const showSimilarFragments = (index: number) => {
  console.log('showSimilarFragments 方法被调用，index:', index);
  try {
    selectedSource.value = sources.value[index];
    console.log('selectedSource 已赋值:', selectedSource.value);
    // 输出 selectedSource 的值到控制台
    console.log('selectedSource:', selectedSource.value);
    showSimilarFragmentDetails.value = true;
  } catch (error) {
    console.error('显示相似片段时出错:', error);
  }
};


// 上传文件到后端
const uploadFileToBackend = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // 获取用户ID（假设通过JWT获取）
    const authorId = getAuthorId();
    if (authorId) {
      formData.append('user_id', authorId.toString());
    }
    
    // 添加文件标题（使用文件名）
    fileName.value=file.name;
    formData.append('title', fileName.value);
    
    // 调用后端上传接口（假设接口为/api/paper/upload）
    const response = await axios.post(
      `${API_BASE_URL}/api/paper/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    if (response.data.code === 200) {
      console.log('文件上传成功:', response.data.data);
      // 可以在这里添加成功提示
      paperId.value = response.data.data; // 假设后端返回的数据结构里有paper_id字段
      console.info('paperid',paperId.value)
      //ElMessage.success('文件上传成功');
    } else {
      console.error('文件上传失败:', response.data.message);
      errorMessage.value = response.data.message || '文件上传失败';
    }
  } catch (error: any) {
    console.error('上传文件到后端出错:', error);
    errorMessage.value = error.response?.data?.message || '网络错误，文件上传失败';
  }
};
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
  grid-template-columns: 1fr; /* 修改为单栏布局 */
  gap: 2rem;
  margin-bottom: 2rem;
}

.upload-section {
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

.upload-progress {
  margin-top: 1rem;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  width: 100%;
}

.upload-progress .progress-bar {
  height: 100%;
  background: #4f46e5;
  transition: width 0.1s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.75rem;
}

.upload-error {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fee2e2;
  border-radius: 4px;
  color: #991b1b;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}

.upload-error i {
  margin-right: 0.5rem;
}

.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 1rem;
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

/* API设置样式 */
.api-settings {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.settings-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
}

.setting-item label {
  margin-bottom: 0.5rem;
  color: #64748b;
  font-size: 0.9rem;
}

.setting-item select,
.setting-item input {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
}

.setting-item input:focus,
.setting-item select:focus {
  outline: none;
  border-color: #4f46e5;
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

.view-fragments-btn {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.view-fragments-btn:hover {
  background: #4338ca;
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

/* 显示相似片段详情样式 */
.similar-fragment-details {
  margin-top: 2rem;
  background: #f8fafc;
  border-radius: 10px;
  padding: 1.5rem;
}

.fragment-container {
  display: flex;
  gap: 1rem;
}

.fragment-item {
  flex: 1;
  margin-bottom: 0;
}

.fragment-item h5 {
  font-size: 1rem;
  color: #1e293b;
  margin-bottom: 0.5rem;
}

.fragment-item pre {
  white-space: pre-wrap;
  font-family: inherit;
  margin: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 1rem;
  height: 100%;
  box-sizing: border-box;
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
  
  .settings-group {
    grid-template-columns: 1fr;
  }

  .fragment-container {
    flex-direction: column;
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

.no-permission {
  text-align: center;
  color: red;
  font-size: 18px;
  margin-top: 50px;
}

.fragment-container {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}
.fragment-item {
  flex: 1;
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #eee;
}
.fragment-item h5 {
  color: #333;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #666;
  line-height: 1.6;
}
</style>