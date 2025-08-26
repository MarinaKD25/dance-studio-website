<template>
  <div class="teachers">
    <h1>Наши преподаватели</h1>

    <!-- Поиск -->
    <div class="search-box">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Поиск по имени или специализации..."
        @input="filterTeachers"
      >
    </div>

    <!-- Список преподавателей -->
    <div class="teachers-grid">
      <div v-for="teacher in filteredTeachers" :key="teacher.id" class="teacher-card">
        <div class="teacher-header">
          <h3>{{ teacher.full_name }}</h3>
          <div class="teacher-specialization">{{ teacher.specialization }}</div>
        </div>
        <div class="teacher-info">
          <div class="info-item">
            <i class="fas fa-graduation-cap"></i>
            <span>Опыт: {{ teacher.experience }} лет</span>
          </div>
          <div class="info-item">
            <i class="fas fa-envelope"></i>
            <span>{{ teacher.email }}</span>
          </div>
          <div class="info-item">
            <i class="fas fa-phone"></i>
            <span>{{ teacher.phone }}</span>
          </div>
        </div>
        
      </div>
    </div>


  </div>
</template>

<script>
import { teachersApi } from '../api'

export default {
  name: 'TeachersView',
  data() {
    return {
      teachers: [],
      searchQuery: '',
      showForm: false,
      editingTeacher: null,
      showDeleteConfirm: false,
      teacherToDelete: null,
      danceTypes: ['Jazz-funk', 'High heels', 'Hip-hop', 'Contemporary', 'Dancemix', 'Voge', 'Latina solo'],
      teacherForm: {
        full_name: '',
        specialization: '',
        experience: 0,
        email: '',
        phone: ''
      }
    }
  },
  computed: {
    filteredTeachers() {
      const query = this.searchQuery.toLowerCase()
      return this.teachers.filter(teacher => 
        teacher.full_name.toLowerCase().includes(query) ||
        teacher.specialization.toLowerCase().includes(query)
      )
    }
  },
  async created() {
    await this.loadTeachers()
  },
  methods: {
    async loadTeachers() {
      try {
        const response = await teachersApi.getAll()
        this.teachers = response.data
      } catch (error) {
        console.error('Ошибка при загрузке преподавателей:', error)
      }
    },
    filterTeachers() {
      // Фильтрация происходит автоматически через computed свойство
    },
    showAddForm() {
      this.editingTeacher = null
      this.teacherForm = {
        full_name: '',
        specialization: '',
        experience: 0,
        email: '',
        phone: ''
      }
      this.showForm = true
    },
    editTeacher(teacher) {
      this.editingTeacher = teacher
      this.teacherForm = { ...teacher }
      this.showForm = true
    },
    async saveTeacher() {
      try {
        if (this.editingTeacher) {
          await teachersApi.update(this.editingTeacher.id, this.teacherForm)
        } else {
          await teachersApi.create(this.teacherForm)
        }
        await this.loadTeachers()
        this.closeForm()
      } catch (error) {
        console.error('Ошибка при сохранении преподавателя:', error)
      }
    },
    closeForm() {
      this.showForm = false
      this.editingTeacher = null
      this.teacherForm = {
        full_name: '',
        specialization: '',
        experience: 0,
        email: '',
        phone: ''
      }
    },
    confirmDelete(teacher) {
      this.teacherToDelete = teacher
      this.showDeleteConfirm = true
    },
    cancelDelete() {
      this.teacherToDelete = null
      this.showDeleteConfirm = false
    },
    async deleteTeacher() {
      try {
        await teachersApi.delete(this.teacherToDelete.id)
        await this.loadTeachers()
        this.cancelDelete()
      } catch (error) {
        console.error('Ошибка при удалении преподавателя:', error)
      }
    }
  }
}
</script>

<style scoped>
.teachers {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.search-box {
  margin-bottom: 20px;
}

.search-box input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.teachers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.teacher-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s;
}

.teacher-card:hover {
  transform: translateY(-5px);
}

.teacher-header {
  margin-bottom: 15px;
}

.teacher-header h3 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.teacher-specialization {
  color: #42b983;
  font-weight: bold;
}

.teacher-info {
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #666;
}

.info-item i {
  margin-right: 10px;
  color: #42b983;
  width: 20px;
}

.teacher-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.add-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.2s;
}

.add-button:hover {
  background-color: #3aa876;
}

.add-button i {
  font-size: 1.2em;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-danger {
  background-color: #dc3545;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-secondary {
  background-color: #6c757d;
}

.btn-secondary:hover {
  background-color: #5a6268;
}
</style> 