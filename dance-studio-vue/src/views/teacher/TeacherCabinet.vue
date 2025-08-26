<template>
  <div class="teacher-cabinet" v-if="currentUser">
    <div class="profile-section">
      <h1>Личный кабинет преподавателя</h1>
      <div class="user-info">
        <h2>{{ currentUser.name }}</h2>
        <p class="role">Преподаватель</p>
        <p class="email">Email: {{ currentUser.email }}</p>
      </div>
    </div>

    <div class="teacher-sections">
      <div class="section">
        <h2>Мое расписание</h2>
        <router-link to="/teacher/schedule" class="btn">Просмотреть расписание</router-link>
      </div>
      
      <div class="section">
        <h2>Посещаемость</h2>
        <router-link to="/teacher/attendance" class="btn">Управление посещаемостью</router-link>
      </div>
      
      <div class="section">
        <h2>Мои ученики</h2>
        <router-link to="/teacher/students" class="btn">Список учеников</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'TeacherCabinet',
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
.teacher-cabinet {
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

.teacher-sections {
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