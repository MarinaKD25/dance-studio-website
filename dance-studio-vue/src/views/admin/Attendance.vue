<template>
  <div class="attendance-container">
    <h2>Управление посещаемостью</h2>
    
    <!-- Фильтры -->
    <div class="filters">
      <select 
        v-model="selectedClass" 
        @change="loadAttendance"
        class="class-select"
      >
        <option value="">Выберите занятие</option>
        <option 
          v-for="classItem in classes" 
          :key="classItem.id" 
          :value="classItem.id"
        >
          {{ classItem.type }} - {{ classItem.formatted_date }} {{ classItem.formatted_time }} ({{ classItem.teacher_name }})
        </option>
      </select>
    </div>

    <!-- Таблица посещаемости -->
    <table v-if="attendance.length > 0" class="attendance-table">
      <thead>
        <tr>
          <th>Студент</th>
          <th>Статус</th>
          <th>Действия</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in attendance" :key="record.id">
          <td>{{ record.student_name }}</td>
          <td>{{ record.presence }}</td>
          <td>
            <button 
              v-if="record.presence === 'Записан'"
              @click="markAsPresent(record)"
              class="action-button"
              :disabled="record.loading"
            >
              {{ record.loading ? 'Обновление...' : 'Отметить присутствие' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="selectedClass && !loading" class="info-message">
      На это занятие пока никто не записался
    </div>

    <div v-else-if="!selectedClass" class="info-message">
      Выберите занятие для просмотра посещаемости
    </div>

    <!-- Отладочная информация -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { classesApi, attendanceApi } from '@/api'

export default {
  name: 'AttendanceManagement',
  
  data() {
    return {
      classes: [],
      selectedClass: '',
      attendance: [],
      loading: false,
      error: null
    }
  },

  async created() {
    try {
      this.loading = true
      const response = await classesApi.getAll()
      this.classes = response.data
      console.log('Загруженные занятия:', this.classes)
    } catch (error) {
      console.error('Ошибка при загрузке занятий:', error)
      this.error = 'Ошибка при загрузке занятий: ' + error.message
    } finally {
      this.loading = false
    }
  },

  methods: {
    async loadAttendance() {
      if (!this.selectedClass) return

      try {
        this.loading = true
        this.error = null
        console.log('Загрузка посещаемости для занятия:', this.selectedClass)
        const response = await attendanceApi.getClassAttendance(this.selectedClass)
        console.log('Полученные данные посещаемости:', response.data)
        this.attendance = response.data.map(record => ({
          ...record,
          loading: false
        }))
      } catch (error) {
        console.error('Ошибка при загрузке посещаемости:', error)
        this.error = 'Ошибка при загрузке посещаемости: ' + error.message
      } finally {
        this.loading = false
      }
    },

    async markAsPresent(record) {
      try {
        record.loading = true
        console.log('Обновление статуса для записи:', record.id)
        await attendanceApi.updateAttendance(record.id, { presence: 'Присутствовал' })
        await this.loadAttendance()
      } catch (error) {
        console.error('Ошибка при обновлении статуса:', error)
        this.error = 'Ошибка при обновлении статуса: ' + error.message
      } finally {
        record.loading = false
      }
    }
  }
}
</script>

<style scoped>
.attendance-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.filters {
  margin-bottom: 20px;
}

.class-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

.attendance-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.attendance-table th,
.attendance-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.attendance-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.action-button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #45a049;
}

.action-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.info-message {
  padding: 20px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

.error-message {
  padding: 20px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  margin-top: 20px;
  color: #721c24;
}
</style> 