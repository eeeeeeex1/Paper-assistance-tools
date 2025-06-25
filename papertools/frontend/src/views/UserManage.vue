<template>
  <div class="user-manage">
    <h2>用户管理界面</h2>
    <table border="1" cellpadding="8" cellspacing="0">
      <thead>
        <tr>
          <th>id</th>
          <th>用户名</th>
          <th>最后登录时间</th>
          <th>操作权限管理</th>
          <th>删除用户</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in userList" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.lastLoginTime }}</td>
          <td>
            <div>
              <input type="checkbox" v-model="user.permissions.checkPlagiarism"> 论文查重
            </div>
            <div>
              <input type="checkbox" v-model="user.permissions.checkTypos"> 论文错字检测
            </div>
            <div>
              <input type="checkbox" v-model="user.permissions.extractTheme"> 论文主题提取
            </div>
          </td>
          <td><button @click="deleteUser(user.id)">删除</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const userList = ref([
  {
    id: 1,
    username: 'user1',
    lastLoginTime: '2025-06-25 10:00',
    permissions: {
      checkPlagiarism: true,
      checkTypos: false,
      extractTheme: true
    }
  },
  {
    id: 2,
    username: 'user2',
    lastLoginTime: '2025-06-24 14:30',
    permissions: {
      checkPlagiarism: false,
      checkTypos: true,
      extractTheme: false
    }
  }
])

const deleteUser = (userId) => {
  userList.value = userList.value.filter(user => user.id!== userId)
}
</script>

<style scoped>
.user-manage {
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
select {
  padding: 4px;
}
button {
  margin-top: 10px;
  padding: 6px 12px;
  cursor: pointer;
}
</style>