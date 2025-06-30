<template>
  <div class="statistic">
    <h2>统计界面</h2>
    <div class="statistic-cards">
      <div class="card">活跃用户：{{ activeUserCount }}</div>
      <div class="card">文件数：{{ fileCount }}</div>
      <div class="card">存储空间：{{ storageSpace }}</div>
      <div class="card">系统状态：{{ systemStatus }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const activeUserCount = ref(2) 
const fileCount = ref(5) 
const storageSpace = ref('10GB') 
const systemStatus = ref('正常') 

onMounted(() => {
  // 实际可调用接口获取真实统计数据
  // 示例：假设调接口后更新数据
  // activeUserCount.value = apiResponse.activeUserCount
})
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