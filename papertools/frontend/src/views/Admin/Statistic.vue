<template>
  <div class="statistic">
    <h2>统计界面</h2>
    <div class="statistic-cards">
      <div class="card">活跃用户：{{ activeUserCount }}</div>
      <div class="card">论文数量：{{ paperCount }}</div>
      <div class="card">存储空间：{{ storageSpace }}</div>
      <div class="card">系统状态：{{ systemStatus }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const activeUserCount = ref(0);
const paperCount = ref(0);
const storageSpace = ref('0GB');
const systemStatus = ref('正常');

onMounted(async () => {
  try {
    // 获取活跃用户数量
    const userResponse = await axios.get('http://localhost:5000/api/users/getall?page=1&per_page=1000');
    activeUserCount.value = userResponse.data.data.total;

    // 获取论文数量
    const paperResponse = await axios.get('http://localhost:5000/api/paper');
    paperCount.value = paperResponse.data.data.papers.length;

    // 这里假设存储空间和系统状态可以通过接口获取
    // 实际中需要根据后端接口实现
    // const storageResponse = await axios.get('/api/storage');
    // storageSpace.value = storageResponse.data.data.space;
    // const statusResponse = await axios.get('/api/status');
    // systemStatus.value = statusResponse.data.data.status;
  } catch (error) {
    console.error('获取统计数据失败:', error);
  }
});
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
</style>