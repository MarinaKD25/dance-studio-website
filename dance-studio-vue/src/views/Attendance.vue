<template>
  <div class="attendance-container">
    <h1>Мои занятия</h1>
    
    <div class="filters">
      <button
        :class="{ active: status === 'all' }"
        @click="status = 'all'"
      >
        Все
      </button>
      <button
        :class="{ active: status === 'registered' }"
        @click="status = 'registered'"
      >
        Записанные
      </button>
      <button
        :class="{ active: status === 'attended' }"
        @click="status = 'attended'"
      >
        Посещенные
      </button>
    </div>

    <div v-if="loading" class="loading">
      Загрузка...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="filteredAttendance.length === 0" class="no-data">
      Нет занятий для отображения
    </div>

    <div v-else class="attendance-list">
      <div
        v-for="record in filteredAttendance"
        :key="record.id"
        class="attendance-card"
        :class="{ 'attended': record.presence === 'Присутствовал' }"
      >
        <h3>{{ record.class_.type }}</h3>
        <div class="class-info">
          <div>Дата: {{ record.class_.formatted_date }}</div>
          <div>Время: {{ record.class_.formatted_time }}</div>
          <div>Преподаватель: {{ record.class_.teacher_name }}</div>
          <div>Зал: {{ record.class_.hall_number }}</div>
        </div>
        <div class="status" :class="record.presence.toLowerCase()">
          Статус: {{ record.presence }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { attendanceApi } from '@/api'
import { mapState } from 'vuex'

export default {
  name: 'Attendance',
  data() {
    return {
      attendance: [],
      loading: false,
      error: null,
      status: 'all'
    }
  },
  computed: {
    ...mapState(['user']),
    filteredAttendance() {
      if (this.status === 'all') return this.attendance
      return this.attendance.filter(record => {
        if (this.status === 'registered') {
          return record.presence === 'Записан'
        }
        return record.presence === 'Присутствовал'
      })
    }
  },
  methods: {
    async loadAttendance() {
      this.loading = true
      this.error = null
      try {
        const response = await attendanceApi.getStudentAttendance(this.user.student_id)
        this.attendance = response.data
      } catch (err) {
        console.error('Error loading attendance:', err)
        this.error = 'Ошибка при загрузке данных о посещаемости'
      } finally {
        this.loading = false
      }
    }
  },
  created() {
    this.loadAttendance()
  }
}
</script>

<style scoped>
.attendance-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.filters {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.filters button {
  padding: 8px 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.filters button.active {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
}

.attendance-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.attendance-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.attendance-card.attended {
  border-left: 4px solid #4CAF50;
}

.attendance-card h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.class-info {
  margin-bottom: 10px;
}

.class-info div {
  margin: 5px 0;
  color: #666;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.status.записан {
  background-color: #e3f2fd;
  color: #1976d2;
}

.status.присутствовал {
  background-color: #e8f5e9;
  color: #2e7d32;
}
</style> 