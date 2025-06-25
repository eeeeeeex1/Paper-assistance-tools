<template>
  <div class="log-manage">
    <h2>日志管理界面</h2>
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>序号</th>
          <th>用户</th>
          <th>时间</th>
          <th>操作</th>
          <th>文件名</th>
          <th>下载</th>
          <th>删除</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(log, index) in logList" :key="log.id">
          <td>{{ index + 1 }}</td>
          <td>{{ log.userId }}</td>
          <td>{{ log.time }}</td>
          <td>{{ log.action }}</td>
          <td>{{ log.fileName }}</td>
          <td><button @click="downloadFile(log.fileName)">下载</button></td>
          <td><button @click="deleteFile(log.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const logList = ref([
  { id: 1, time: '2025-06-25 10:10', action: '论文查重', fileName: 'doc1.pdf', userId: 1 },
  { id: 2, time: '2025-06-25 10:20', action: '论文错字检测', fileName: 'doc2.xlsx', userId: 2 },
  { id: 3, time: '2025-06-25 10:30', action: '论文主题提取', fileName: 'doc3.doc', userId: 3 }
])

const downloadFile = (fileName) => {
  // 这里可结合实际文件存储路径，实现真实下载逻辑（如调用后端接口、a 标签下载等）
  console.log(`模拟下载文件：${fileName}`)
}

const deleteFile = (logId) => {
  logList.value = logList.value.filter(log => log.id!== logId)
}
</script>

<style scoped>
.log-manage {
  background: #fff;
  padding: 20px;
  border-radius: 4px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  text-align: center;
}
button {
  padding: 6px 12px;
  cursor: pointer;
}
</style>