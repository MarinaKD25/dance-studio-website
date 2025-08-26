<template>
  <div class="admin-panel">
    <h1>Панель администратора</h1>
    
    <div class="admin-sections">
      <div class="section">
        <h2>Управление преподавателями</h2>
        <router-link to="/admin/teachers" class="btn">Перейти к преподавателям</router-link>
      </div>
      
      <div class="section">
        <h2>Управление студентами</h2>
        <router-link to="/admin/students" class="btn">Перейти к студентам</router-link>
      </div>
      
      <div class="section">
        <h2>Управление расписанием</h2>
        <router-link to="/admin/schedule" class="btn">Перейти к расписанию</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useStore } from 'vuex'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'AdminPanel',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const isAdmin = computed(() => store.getters.isAdmin)
    
    // Проверяем права доступа при создании компонента
    if (!isAdmin.value) {
      router.push('/')
    }
    
    return {
      isAdmin
    }
  }
}
</script>

<style scoped>
.admin-panel {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
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