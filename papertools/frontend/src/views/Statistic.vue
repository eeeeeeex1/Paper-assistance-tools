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
  padding: 20px;
  border-radius: 4px;
}
.statistic-cards {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}
.card {
  width: 200px;
  height: 80px;
  background: #409eff;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  font-size: 16px;
}
</style>