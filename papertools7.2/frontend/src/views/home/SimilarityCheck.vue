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
            </div>
          </div>
          
          <div class="result-content">
            <div v-if="!resultsReady" class="empty-result">
              <i class="iconfont icon-file-search"></i>
              <p>请先上传文件并点击"开始对比"</p>
            </div>
            
            <div v-else class="result-details">
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
                  <div class="fragment-container" v-if="selectedSource.similar_segments && (selectedSource.similar_segments.original.length > 0 || selectedSource.similar_segments.comparison.length > 0)">
                    <!-- 原文件（上传论文）的相似段落 -->
                    <div class="fragment-item">
                      <h5>上传文章相似段落</h5>
                      <div v-for="(segment, index) in selectedSource.similar_segments.original" :key="index">
                        <pre v-html="markedContent(segment.content)" style="color: red;"></pre>
                      </div>
                    </div>

                    <!-- 对比文件（文献）的相似段落 -->
                    <div class="fragment-item">
                      <h5>对比文章相似段落</h5>
                      <div v-for="(segment, index) in selectedSource.similar_segments.comparison" :key="index">
                        <pre v-html="markedContent(segment.content)" style="color: red;"></pre>
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

                  <!-- 新增：全文对比视图（左右布局展示完整内容） -->
                  <div class="full-text-comparison">
                    <h5>全文对比（相似片段已标红）</h5>
                    <div class="full-text-columns">
                      <!-- 左侧：文件1完整内容 -->
                      <div class="full-text-column">
                        <p class="file-name">{{ uploadedFile1?.name || '文件1' }}</p>
                        <div class="full-text-content" v-html="highlightFullText(fileContent1, 'original')"></div>
                      </div>

                      <!-- 右侧：文件2完整内容 -->
                      <div class="full-text-column">
                        <p class="file-name">{{ uploadedFile2?.name || '文件2' }}</p>
                        <div class="full-text-content" v-html="highlightFullText(fileContent2, 'comparison')"></div>
                      </div>
                    </div>
                  </div>

                  <!-- 可选：保留相似片段分组展示（作为补充） -->
                  <div class="similar-segments-group">
                    <h5>相似片段分组</h5>
                    <div v-for="(source, sourceIndex) in comparisonResults" :key="sourceIndex" class="local-similarity-container">
                      <div class="local-similarity-columns">
                        <div v-if="source.similar_segments?.original?.length" class="local-similarity-column">
                          <h6>文件1相似片段</h6>
                          <div v-for="(segment, segmentIndex) in source.similar_segments.original" :key="segmentIndex">
                            <pre><span class="highlight-similar">{{ segment.content }}</span></pre>
                          </div>
                        </div>
                        
                        <div v-if="source.similar_segments?.comparison?.length" class="local-similarity-column">
                          <h6>文件2相似片段</h6>
                          <div v-for="(segment, segmentIndex) in source.similar_segments.comparison" :key="segmentIndex">
                            <pre><span class="highlight-similar">{{ segment.content }}</span></pre>
                          </div>
                        </div>
                      </div>
                      <div class="similarity-divider"></div>
                    </div>
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
import { ref, computed, onUnmounted, onMounted, watch ,Ref} from 'vue';
import { ElMessage } from 'element-plus';
import { getAuthorId } from '@/utils/auth'; 
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios';
import mammoth from 'mammoth';

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

// 存储文件内容
const fileContent1 = ref('');
const fileContent2 = ref('');

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

// 新增：显示相似片段详情状态
const showSimilarFragmentDetails = ref(false);
const selectedSource = ref<any>(null);

// 定义相似段落的类型
interface SimilarSegment {
  content: string; // 段落内容
  similarity?: number; // 相似度
  matched_with?: number; // 匹配的段落索引
}

// 定义每组相似片段的类型
interface SimilarSegmentsGroup {
  original?: SimilarSegment[]; // 原文件的相似段落
  comparison?: SimilarSegment[]; // 对比文件的相似段落
}

// 定义对比结果项的类型
interface ComparisonResultItem {
  similar_segments: SimilarSegmentsGroup; // 相似片段组
}
// 新增本地文件引用
const uploadedFile1 = ref<File | null>(null);
const uploadedFile2 = ref<File | null>(null);

// 查重结果
const comparisonResults = ref<ComparisonResultItem[]>([]);
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
     // 假设后端返回的数据结构中有 sources 字段
    if (response.data.sources) {
      sources.value = response.data.sources;
    }
    console.log(response.data)
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
// 处理本地文件上传（新增读取内容逻辑）
const handleLocalFileUpload = (fileIndex: number) => {
  const inputId = `file${fileIndex}`;
  const input = document.getElementById(inputId) as HTMLInputElement;
  if (input && input.files && input.files.length > 0) {
    const file = input.files[0]; // 获取选中的文件
    if (fileIndex === 1) {
      uploadedFile1.value = file;
      readFileContent(file, fileContent1); // 读取文件1内容到fileContent1
    } else if (fileIndex === 2) {
      uploadedFile2.value = file;
      readFileContent(file, fileContent2); // 读取文件2内容到fileContent2
    }
  }
};

// 处理本地文件拖拽（新增读取内容逻辑）
const handleLocalFileDrop = (fileIndex: number, e: DragEvent) => {
  e.preventDefault(); // 阻止默认行为（避免浏览器直接打开文件）
  if (fileIndex === 1) {
    dragOver1.value = false;
    if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]; // 获取拖拽的文件
      uploadedFile1.value = file;
      readFileContent(file, fileContent1); // 读取文件1内容到fileContent1
    }
  } else if (fileIndex === 2) {
    dragOver2.value = false;
    if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0]; // 获取拖拽的文件
      uploadedFile2.value = file;
      readFileContent(file, fileContent2); // 读取文件2内容到fileContent2
    }
  }
};

const readFileContent = async (file: File, contentRef: Ref<string>) => {
  if (file.name.endsWith('.docx')) {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const result = await mammoth.extractRawText({ arrayBuffer });
      contentRef.value = result.value; // 关键赋值步骤，确保这里的 contentRef 是对应文件的内容变量
      console.log('成功解析 .docx 文件内容，内容为：', result.value);
    } catch (error) {
      console.error('解析 .docx 文件失败:', error);
      contentRef.value = `[无法解析 .docx 文件]`;
    }
  } 
  if (file.type === 'text/plain') {
    // 处理纯文本文件（保持不变）
    const reader = new FileReader();
    reader.onload = (e) => {
      contentRef.value = e.target?.result as string;
    };
    reader.readAsText(file);
  } else if (file.type === 'application/pdf') {
    // 处理 PDF 文件（保持不变）
    contentRef.value = `[PDF文件] ${file.name}`;
  } else if (file.name.endsWith('.docx')) {
    try {
      // 正确方式：先读取文件为 ArrayBuffer
      const arrayBuffer = await file.arrayBuffer();
      
      // 使用 mammoth 解析 ArrayBuffer
      const result = await mammoth.extractRawText({ arrayBuffer });
      
      contentRef.value = result.value; // 获取纯文本内容
      console.log('成功解析 .docx 文件内容');
    } catch (error) {
      console.error('解析 .docx 文件失败:', error);
      contentRef.value = `[无法解析 .docx 文件]`;
    }
  } else {
    contentRef.value = `[不支持的文件类型] ${file.type}`;
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
      overallSimilarity.value = Number(data.comprehensive_similarity?.toFixed(2) || 0);
      
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
  }
  else if (selectedOption.value === 'localSearch') {
    // 本地查重逻辑
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
      
          // 关键修改：适配后端实际结构（相似段落嵌套在similar_segments中）
    comparisonResults.value = response.data.data.comparison_results.map((item: any) => ({
      // 保留后端返回的其他字段（如标题、相似度，可选）
      article_title: item.article_title,
      similarity_rate: item.similarity_rate,
      // 从similar_segments中提取原始文件和对比文件的相似段落
      similar_segments: {
        // 映射原始文件的相似段落（包含marked_content）
        original: item.similar_segments?.original?.map((seg: any) => ({
          content: seg.content,
          marked_content: seg.marked_content, // 高亮标记内容
          similarity: seg.similarity,
          matched_with: seg.matched_with
        })) || [], // 若字段不存在则默认为空数组
        // 映射对比文件的相似段落（包含marked_content）
        comparison: item.similar_segments?.comparison?.map((seg: any) => ({
          content: seg.content,
          marked_content: seg.marked_content, // 高亮标记内容
          similarity: seg.similarity,
          matched_with: seg.matched_with
        })) || [] // 若字段不存在则默认为空数组
      }
    }));
      
      comprehensiveSimilarity.value = response.data.data.comprehensive_similarity;
      showResults.value = true;
      resultsReady.value = true;
      console.log('本地查重结果:', comparisonResults.value);

      initSimilarTexts(); // 必须调用此函数，否则无法收集相似片段
      // 关键修改：为本地查重单独设置selectedSource，直接显示第一组相似片段
      if (comparisonResults.value.length > 0) {
        selectedSource.value = comparisonResults.value[0];
        showSimilarFragmentDetails.value = true;
      }
    } catch (error) {
      console.error('本地查重失败:', error);
      ElMessage.error('查重失败，请稍后再试');
    }
  }
};

// 修改显示相似片段函数，兼容本地查重和网络查重
const showSimilarFragments = (index: number) => {
  console.log('showSimilarFragments 方法被调用，index:', index);
  try {
    // 关键修改：根据当前查重方式选择数据源
    if (selectedOption.value === 'webSearch') {
      selectedSource.value = sources.value[index];
    } else {
      selectedSource.value = comparisonResults.value[index];
    }
    console.log('selectedSource 已赋值:', selectedSource.value);
    
    // 确保使用标记内容（优先用marked_content）
    if (selectedSource.value && selectedSource.value.similar_segments) {
      const { original, comparison } = selectedSource.value.similar_segments;
      // 处理原始文件段落
      if (original) {
        selectedSource.value.similar_segments.original = original.map((seg: any) => ({
          ...seg,
          content: seg.marked_content || seg.content // 优先使用标记内容
        }));
      }
      // 处理对比文件段落
      if (comparison) {
        selectedSource.value.similar_segments.comparison = comparison.map((seg: any) => ({
          ...seg,
          content: seg.marked_content || seg.content // 优先使用标记内容
        }));
      }
    }
    
    showSimilarFragmentDetails.value = true;
  } catch (error) {
    console.error('显示相似片段时出错:', error);
  }
};

// 处理后端返回的标记内容（保持不变，但确保<mark>标签被正确解析）
const markedContent = (content: string) => {
  if (content && content.includes('<mark>')) {
    // 将 <mark> 标签内的文本颜色设置为红色
    return content.replace(/<mark>/g, '<mark style="color: red;">');
  }
  return `<span style="color: red;">${content}</span>`;
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
//--------------------------------------------------------
// 存储所有相似片段内容（用于全文标红）
const allSimilarTexts = ref<{
  original: string[]; // 文件1的所有相似片段
  comparison: string[]; // 文件2的所有相似片段
}>({ original: [], comparison: [] });

// 初始化：从对比结果中收集所有相似片段
const initSimilarTexts = () => {
  allSimilarTexts.value = { original: [], comparison: [] };
  
  comparisonResults.value.forEach(source => {
    source.similar_segments?.original?.forEach((seg: any) => {
      if (seg.content && typeof seg.content === 'string') {
        allSimilarTexts.value.original.push(seg.content);
      }
    });
    
    source.similar_segments?.comparison?.forEach((seg: any) => {
      if (seg.content && typeof seg.content === 'string') {
        allSimilarTexts.value.comparison.push(seg.content);
      }
    });
  });
  
  // 打印具体内容（关键！）
  console.log('收集到的相似文本数量:', {
    original: allSimilarTexts.value.original.length, // 文件1的相似片段数量
    comparison: allSimilarTexts.value.comparison.length // 文件2的相似片段数量
  });
  console.log('文件1的相似片段示例:', allSimilarTexts.value.original.slice(0, 1)); // 打印第一个片段
  console.log('文件2的相似片段示例:', allSimilarTexts.value.comparison.slice(0, 1));
};

// 高亮全文中的相似片段
const highlightFullText = (content: string, type: 'original' | 'comparison') => {
  if (!content) {
    console.log('------------------------------------')
    return '<p>文件内容为空</p>'; // 内容为空时的提示
  }
  console.log('------------------------------------')
  console.log('开始输出')
  let fullText = content;
  const targetSegments = type === 'original' 
    ? allSimilarTexts.value.original 
    : allSimilarTexts.value.comparison;

  if (targetSegments.length === 0) {
    return fullText; // 没有相似片段时直接返回原文
  }

  // 按片段长度排序（优先替换长片段）
  const sortedSegments = [...targetSegments].sort((a, b) => b.length - a.length);

  sortedSegments.forEach(segment => {
    if (segment && fullText.includes(segment)) {
      // 转义特殊字符
      const escapedSegment = segment.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      // 全局替换并标红
      fullText = fullText.replace(
        new RegExp(escapedSegment, 'g'),
        `<span class="highlighted">${segment}</span>`
      );
    }
  });

  return fullText;
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
  flex-direction: row; /* 确保为水平布局 */
  gap: 2rem;
  margin-top: 1rem;
}

.fragment-item {
  flex: 1;
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #eee;
  height: auto; /* 高度自适应 */
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

::v-deep mark {
  background-color: #ffcccb; /* 浅红色背景 */
  color: #990000; /* 深红色文本 */
  font-weight: bold;
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

  /* 仅在小屏幕上恢复为垂直布局 */
  @media (max-width: 480px) {
    .fragment-container {
      flex-direction: column; 
    }
  }
}

@media (max-width: 480px) {
  .similarity-check-page {
    padding: 1rem;
  }
  
  .upload-area {
    padding: 1.5rem;
  }
  
  .compare-btn {
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
.local-similarity-container {
  margin-bottom: 1.5rem;
}

.local-similarity-columns {
  display: flex;
  gap: 1.5rem;
}

.local-similarity-column {
  flex: 1;
  background: #fff;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #eee;
}

/* 在 <style scoped> 中添加以下样式 */
.full-text-comparison {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.full-text-columns {
  display: flex;
  gap: 1.5rem;
  margin-top: 1rem;
}

.full-text-column {
  flex: 1; /* 左右宽度平分 */
  background: #fff;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #eee;
}

.file-name {
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #475569;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.full-text-content {
  max-height: 600px; /* 固定高度，超出滚动 */
  overflow-y: auto;
  line-height: 1.8;
  white-space: pre-wrap; /* 保留换行和空格 */
  font-family: inherit;
  font-size: 0.95rem;
}

/* 相似片段高亮样式 */
::v-deep .highlighted {
  color: #dc2626 !important;
  background-color: #fee2e2 !important;
  padding: 0 2px;
  border-radius: 3px;
  font-weight: 500;
}
/* 相似片段分组标题 */
.similar-segments-group {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}
</style>