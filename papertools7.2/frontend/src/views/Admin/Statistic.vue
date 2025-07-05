<template>
  <div class="statistic-container">
    <div class="statistic">
      <h2 class="statistic-title">系统数据统计</h2>
      <div class="statistic-cards">
        <div class="card card-user">
          <div class="card-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <div class="card-label">活跃用户</div>
            <div class="card-value">{{ activeUserCount }}</div>
          </div>
        </div>
        
        <div class="card card-paper">
          <div class="card-icon">
            <i class="fas fa-file-alt"></i>
          </div>
          <div class="card-content">
            <div class="card-label">论文数量</div>
            <div class="card-value">{{ paperCount }}</div>
          </div>
        </div>
        
        <div class="card card-storage">
          <div class="card-icon">
            <i class="fas fa-database"></i>
          </div>
          <div class="card-content">
            <div class="card-label">存储空间</div>
            <div class="card-value">{{ storageSpace }}</div>
          </div>
        </div>
        
        <div class="card card-status">
          <div class="card-icon">
            <i class="fas fa-heartbeat"></i>
          </div>
          <div class="card-content">
            <div class="card-label">系统状态</div>
            <div class="card-value">{{ systemStatus }}</div>
          </div>
        </div>
      </div>
      
      <div class="chart-section">
        <h3>操作类型统计</h3>
        <div class="chart-container">
          <div id="operationChart" class="chart"></div>
          <div v-if="chartError" class="chart-error">{{ chartError }}</div>
        </div>
      </div>
      
      <div class="chart-section">
        <h3>用户登录统计</h3>
        <div class="chart-container">
          <div id="loginChart" class="chart"></div>
          <div v-if="loginChartError" class="chart-error">{{ loginChartError }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

// 数据引用
const activeUserCount = ref(0);
const paperCount = ref(0);
const storageSpace = ref('1GB');
const systemStatus = ref('正常');
const chartError = ref('');
const loginChartError = ref('');
let loginChart = null;
let myChart = null;

// 模拟数据加载动画
const simulateLoading = (ref, target, duration = 1000) => {
  let start = 0;
  const end = parseInt(target);
  const step = end / (duration / 16);
  
  const timer = setInterval(() => {
    start += step;
    if (start >= end) {
      ref.value = end;
      clearInterval(timer);
    } else {
      ref.value = Math.floor(start);
    }
  }, 16);
};

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/user/total_count');
    simulateLoading(activeUserCount, response.data.data.total_count);
  } catch (error) {
    console.error('获取用户总数量失败:', error);
    activeUserCount.value = 'N/A';
  }
  
  try {
    const response = await axios.get('http://localhost:5000/api/paper/total_count');
    simulateLoading(paperCount, response.data.data.total_count);
  } catch (error) {
    console.error('获取论文总数失败:', error);
    paperCount.value = 'N/A';
  }

  // 设置存储空间和系统状态
  storageSpace.value = '1GB';
  systemStatus.value = '正常';

  // 获取操作类型统计数据并渲染柱状图
  try {
    const res = await axios.get('http://localhost:5000/api/operations/type_count');
    const operationData = res.data.data;
    const operationTypes = ["相似度检查", "拼写检查", "文本摘要"];

    if (!operationData || typeof operationData !== 'object') {
      throw new Error('操作类型统计数据格式不正确');
    }

    const counts = [
      operationData.similaritycheck || 0,
      operationData.spellcheck || 0,
      operationData.textsummary || 0
    ];
    
    renderChart(operationTypes, counts);
  } catch (err) {
    console.error('获取操作类型统计数据失败:', err);
    chartError.value = `图表渲染失败: ${err.message}`;
  }

  // 获取登录统计数据
  try {
    const res = await axios.get('http://localhost:5000/api/user/weekly');
    const { dates, counts } = res.data.data;
    renderLoginChart(dates, counts);
  } catch (err) {
    console.error('获取登录统计失败:', err);
    loginChartError.value = err.response?.data?.message || err.message;
  }
});

// 渲染柱状图函数
function renderChart(xAxisData, seriesData) {
  try {
    const chartDom = document.getElementById('operationChart');
    if (!chartDom) throw new Error('未找到图表容器');

    myChart = echarts.init(chartDom);
    const option = {
      backgroundColor: 'transparent',
      title: { 
        text: '操作类型分布', 
        left: 'center',
        textStyle: {
          color: '#333',
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      tooltip: { 
        trigger: 'axis', 
        axisPointer: { 
          type: 'shadow',
          shadowStyle: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: '操作次数',
        nameLocation: 'middle',
        nameGap: 25,
        axisLine: {
          lineStyle: {
            color: '#999'
          }
        },
        axisLabel: {
          color: '#666'
        },
        splitLine: {
          lineStyle: {
            color: '#eee'
          }
        }
      },
      yAxis: {
        type: 'category',
        data: xAxisData,
        axisLabel: { 
          interval: 0,
          color: '#666'
        },
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        }
      },
      series: [{
        name: '操作次数',
        type: 'bar',
        data: seriesData,
        barWidth: '40%',
        label: { 
          show: true, 
          position: 'right',
          color: '#333'
        },
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#0078ff' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }]
    };

    myChart.setOption(option);
    
    window.addEventListener('resize', () => {
      if (myChart) myChart.resize();
    });
  } catch (error) {
    console.error('初始化图表失败:', error);
    chartError.value = `初始化图表失败: ${error.message}`;
  }
}

// 渲染登录折线图函数
function renderLoginChart(dates, counts) {
  try {
    const chartDom = document.getElementById('loginChart');
    if (!chartDom) throw new Error('未找到登录图表容器');
    
    loginChart = echarts.init(chartDom);
    const option = {
      backgroundColor: 'transparent',
      title: { 
        text: '用户登录趋势', 
        left: 'center',
        textStyle: {
          color: '#333',
          fontSize: 18,
          fontWeight: 'bold'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        },
        backgroundColor: 'rgba(50, 50, 50, 0.9)',
        borderColor: '#333',
        textStyle: {
          color: '#fff'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: dates,
        axisLine: {
          lineStyle: {
            color: '#999'
          }
        },
        axisLabel: {
          color: '#666'
        }
      },
      yAxis: {
        type: 'value',
        name: '登录用户数',
        axisLine: {
          lineStyle: {
            color: '#999'
          }
        },
        axisLabel: {
          color: '#666'
        },
        splitLine: {
          lineStyle: {
            color: '#eee'
          }
        }
      },
      series: [{
        name: '登录用户',
        type: 'line',
        stack: '总量',
        smooth: true,
        lineStyle: {
          width: 3,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#42d392' },
            { offset: 1, color: '#647eff' }
          ])
        },
        showSymbol: false,
        areaStyle: {
          opacity: 0.8,
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(100, 126, 255, 0.5)' },
            { offset: 1, color: 'rgba(66, 211, 146, 0.1)' }
          ])
        },
        emphasis: {
          focus: 'series'
        },
        data: counts,
        markPoint: {
          data: [
            { type: 'max', name: '最大值' },
            { type: 'min', name: '最小值' }
          ]
        },
        markLine: {
          data: [{ type: 'average', name: '平均值' }]
        }
      }]
    };
    
    loginChart.setOption(option);
    
    window.addEventListener('resize', () => {
      if (loginChart) loginChart.resize();
    });
  } catch (error) {
    console.error('登录图表初始化失败:', error);
    loginChartError.value = error.message;
  }
}

onUnmounted(() => {
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }
  if (loginChart) {
    loginChart.dispose();
    loginChart = null;
  }
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

.statistic-cards {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 40px;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  flex: 1;
  border-left: 4px solid;
  position: relative;
  overflow: hidden;
  min-height: 80px;
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

.card-status {
  border-left-color: #ef476f;
}

.card-status .card-icon {
  background: linear-gradient(135deg, #ef476f, #ff6b8b);
}

.chart-section {
  margin-bottom: 40px;
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.chart-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.chart-section:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.chart-container {
  position: relative;
  width: 100%;
  height: 350px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #ef476f;
  font-weight: 500;
  text-align: center;
  padding: 20px;
  background: rgba(239, 71, 111, 0.1);
  border-radius: 8px;
  max-width: 80%;
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
}

@media (max-width: 480px) {
  .statistic-cards {
    flex-direction: column;
  }
  
  .card {
    min-width: 100%;
  }
}
</style>