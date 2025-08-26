<template>
  <div class="admin-cabinet" v-if="currentUser">
    <div class="profile-section">
      <h1>Личный кабинет администратора</h1>
      <div class="user-info">
        <h2>{{ currentUser.name }}</h2>
        <p class="role">Администратор системы</p>
        <p class="email">Email: {{ currentUser.email }}</p>
      </div>
    </div>

    <div class="admin-sections">
      <div class="section">
        <h2>Управление преподавателями</h2>
        <router-link to="/admin/teachers" class="btn">Перейти к преподавателям</router-link>
      </div>
      
      <div class="section">
        <h2>Управление студентами</h2>
        <router-link to="/students" class="btn">Перейти к студентам</router-link>
      </div>
      
      <div class="section">
        <h2>Управление расписанием</h2>
        <router-link to="/admin/schedule" class="btn">Перейти к расписанию</router-link>
      </div>
      <div class="section">
        <h2>Управление посещаемостью</h2>
        <router-link to="/admin/attendance" class="btn">Перейти к посещаемости</router-link>
      </div>
     
      
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'AdminCabinet',
  computed: {
    ...mapState(['user']),
    currentUser() {
      return this.user
    }
  },
  created() {
    if (!this.currentUser) {
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-cabinet {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-section {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.user-info {
  margin-top: 20px;
}

.user-info h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.role {
  color: #42b983;
  font-weight: bold;
  margin-bottom: 5px;
}

.email {
  color: #666;
}

.admin-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section h2 {
  margin-bottom: 15px;
  color: #2c3e50;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #45a049;
}
</style> 