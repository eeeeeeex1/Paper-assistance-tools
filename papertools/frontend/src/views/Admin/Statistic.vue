<template>
  <div class="statistic">
    <h2>统计界面</h2>
    <div class="statistic-cards">
      <div class="card">活跃用户：{{ activeUserCount }}</div>
      <div class="card">论文数量：{{ paperCount }}</div>
      <div class="card">存储空间：{{ storageSpace }}</div>
      <div class="card">系统状态：{{ systemStatus }}</div>
    </div>
    <!-- 新增折线图容器 -->
    <div class="chart-container">
      <div id="operationChart" style="width: 1400px; height: 350px;"></div>
      <!-- 添加错误提示 -->
      <div v-if="chartError" class="chart-error">{{ chartError }}</div>
    </div>
    <!-- 新增：登录统计折线图 -->
    <div class="chart-container">
      <div id="loginChart" style="width: 1400px; height: 350px;"></div>
      <div v-if="loginChartError" class="chart-error">{{ loginChartError }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted,onUnmounted } from 'vue';
import axios from 'axios';
//lmk-----------------------------------
import * as echarts from 'echarts';  // 引入 ECharts
//lmk-----------------------------------

const activeUserCount = ref(0);
const paperCount = ref(0);
const storageSpace = ref('0GB');
const systemStatus = ref('正常');

//lmk---------------------------------------
const chartError = ref(''); // 图表错误信息
let loginChart = null;  
let myChart = null;  // 用于存储 ECharts 实例
//lmk--------------------------------------

onMounted(async () => {
  try {
      const response = await axios.get('http://localhost:5000/api/user/total_count');
      activeUserCount.value = response.data.data.total_count;
    } catch (error) {
      console.error('获取用户总数量失败:', error);
    }
  try {
      const response = await axios.get('http://localhost:5000/api/paper/total_count');
      PaperCount.value = response.data.data.total_count;
    } catch (error) {
      console.error('获取论文总数失败:', error);
    }
//lmk-----------------------------------------------------------
   // 获取操作类型统计数据并渲染柱状图
  try {
      const res = await axios.get('http://localhost:5000/api/operations/type_count');
      console.log('接口返回数据:', res.data); // 添加日志
      const operationData = res.data.data;
      const operationTypes = ["similaritycheck", "spellcheck", "textsummary"];

      // 验证数据格式
      if (!operationData || typeof operationData !== 'object') {
        throw new Error('操作类型统计数据格式不正确');
      }

      // 提取对应数量，没有的补0
      const counts = operationTypes.map(type => operationData[type] || 0);
      console.log('图表数据:', operationTypes, counts); // 关键调试日志

      renderChart(operationTypes, counts);
    } catch (err) {
      console.error('获取操作类型统计数据失败:', err);
      chartError.value = `图表渲染失败: ${err.message}`;
  }

  try {
    const res = await axios.get('http://localhost:5000/api/user/weekly');
    console.log('登录统计数据:', res.data);
    
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
      title: { text: '操作类型统计', left: 'center' },
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: {
        type: 'value',  // X轴改为数值轴（操作次数）
        name: '数量',
        min: 0,
        boundaryGap: [0, 0.01]
      },
      yAxis: {
        type: 'category',  // Y轴改为分类轴（操作类型）
        data: xAxisData,   // 操作类型数据放入Y轴
        axisLabel: { interval: 0 }
      },
      series: [{
        name: '操作次数',
        type: 'bar',      // 保持柱状图
        data: seriesData,
        label: { 
          show: true, 
          position: 'right'  // 标签显示在柱子右侧
        },
        itemStyle: {
          color: '#409eff'  // 统一柱子颜色
        }
      }]
    };

    myChart.setOption(option);
    
    // 监听窗口大小变化，自适应图表
    window.addEventListener('resize', () => {
      if (myChart) myChart.resize();
    });
  } catch (error) {
    console.error('初始化图表失败:', error);
    chartError.value = `初始化图表失败: ${error.message}`;
  }
}
//渲染折线图函数
function renderLoginChart(dates, counts) {
  try {
    const chartDom = document.getElementById('loginChart');
    if (!chartDom) throw new Error('未找到登录图表容器');
    
    loginChart = echarts.init(chartDom);
    const option = {
      title: { text: '近7天登录用户统计', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: dates,
        name: '日期'
      },
      yAxis: {
        type: 'value',
        name: '登录用户数',
        min: 0
      },
      series: [{
        name: '登录用户数',
        type: 'line',
        data: counts,
        label: { show: true, position: 'top' },
        itemStyle: { color: '#67c23a' },
        areaStyle: { opacity: 0.3 }  // 添加面积图效果
      }]
    };
    
    loginChart.setOption(option);
  } catch (error) {
    console.error('登录图表初始化失败:', error);
    loginChartError.value = error.message;
  }
}

// 组件卸载时销毁 ECharts 实例
onUnmounted(() => {
  if (myChart) {
    myChart.dispose();
    myChart = null;
  }
});
//lmk-------------------------------------------------------------------
</script>

<style scoped>
.statistic {
  background: #fff;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.statistic h2 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin-bottom: 30px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.statistic-cards {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.card {
  width: 220px;
  height: 120px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 15px;
  font-size: 20px;
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.3);
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(64, 158, 255, 0.4);
}
/*lmk---------------------------------------------------*/ 
.chart-container {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  position: relative;
}

.chart-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: red;
  font-weight: bold;
}

/* lmk原有样式保持不变，新增图表容器间距 */
.chart-container {
  margin-top: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
</style>