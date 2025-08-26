<template>
  <div class="schedule">
    <h1>Расписание занятий</h1>
    
    <!-- Фильтры -->
    <div class="filters">
      <div class="filter-group">
        <label>Направление:</label>
        <select v-model="selectedDanceType">
          <option value="">Все направления</option>
          <option v-for="type in danceTypes" :key="type" :value="type">{{ type }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Преподаватель:</label>
        <select v-model="selectedTeacher">
          <option value="">Все преподаватели</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.full_name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Расписание -->
    <div class="schedule-container">
      <div v-if="loading" class="loading">Загрузка расписания...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="filteredClasses.length === 0" class="no-classes">
        Нет занятий на выбранный период
      </div>
      <div v-else class="schedule-grid">
        <!-- Группировка по дням -->
        <div v-for="(classes, date) in groupedClasses" :key="date" class="day-schedule">
          <h2 class="day-header">{{ formatDate(date) }}</h2>
          <div class="classes-list">
            <div v-for="class_ in classes" :key="class_.id" class="class-card">
              <div class="class-time">{{ class_.formatted_time }}</div>
              <div class="class-info">
                <h3>{{ class_.type }}</h3>
                <p class="teacher">Преподаватель: {{ class_.teacher_name }}</p>
                <p class="hall">Зал: {{ class_.hall_number }}</p>
                <p class="capacity">
                  Заполненность: {{ class_.current_capacity }}/{{ class_.hall_capacity }}
                </p>
              </div>
              <div class="class-actions">
                <button 
                  v-if="hasActiveSubscription" 
                  class="btn"
                  :disabled="isClassFull(class_)"
                  @click="enrollInClass(class_.id)"
                >
                  Записаться
                </button>
                <button v-else class="btn" disabled>
                  Требуется абонемент
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { classesApi, teachersApi, subscriptionsApi } from '../api'
import { mapState } from 'vuex'

export default {
  name: 'ClassSchedule',
  data() {
    return {
      classes: [],
      teachers: [],
      loading: true,
      error: null,
      selectedDanceType: '',
      selectedTeacher: '',
      hasActiveSubscription: false
    }
  },
  computed: {
    ...mapState(['user']),
    danceTypes() {
      return [...new Set(this.classes.map(c => c.type))]
    },
    filteredClasses() {
      return this.classes.filter(c => {
        if (this.selectedDanceType && c.type !== this.selectedDanceType) return false
        if (this.selectedTeacher && c.teacher_id !== this.selectedTeacher) return false
        return true
      })
    },
    groupedClasses() {
      const groups = {}
      this.filteredClasses.forEach(class_ => {
        const date = class_.formatted_date
        if (!groups[date]) {
          groups[date] = []
        }
        groups[date].push(class_)
      })
      return groups
    }
  },
  watch: {
    user: {
      immediate: true,
      handler(newUser) {
        if (!newUser) {
          // Сброс состояния компонента при выходе пользователя
          this.classes = []
          this.teachers = []
          this.loading = true
          this.error = null
          this.selectedDanceType = ''
          this.selectedTeacher = ''
          this.hasActiveSubscription = false
        } else {
          // Обновление данных при входе пользователя
          this.fetchClasses()
          this.fetchTeachers()
          this.checkSubscription()
        }
      }
    }
  },
  methods: {
    async checkSubscription() {
      try {
        if (!this.user?.student_id) {
          this.hasActiveSubscription = false;
          return;
        }
        const response = await subscriptionsApi.getActive(this.user.student_id);
        this.hasActiveSubscription = response.data !== null;
      } catch (error) {
        console.error('Ошибка при проверке абонемента:', error);
        this.hasActiveSubscription = false;
      }
    },
    async fetchClasses() {
      try {
        const response = await classesApi.getAll({
          date_from: new Date().toISOString().split('T')[0],
          date_to: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        })
        if (response && response.data) {
          this.classes = response.data
        }
      } catch (error) {
        console.error('Ошибка при загрузке занятий:', error)
        this.error = 'Не удалось загрузить расписание'
      } finally {
        this.loading = false
      }
    },
    async fetchTeachers() {
      try {
        const response = await teachersApi.getAll()
        if (response && response.data) {
          this.teachers = response.data
        }
      } catch (error) {
        console.error('Ошибка при загрузке преподавателей:', error)
      }
    },
    formatDate(date) {
      const [day, month, year] = date.split('.')
      const dateObj = new Date(year, month - 1, day)
      const dayOfWeek = dateObj.toLocaleDateString('ru-RU', { weekday: 'long' })
      return `${date} (${dayOfWeek})`
    },
    getRussianDayOfWeek(day) {
      const days = {
        'Monday': 'Понедельник',
        'Tuesday': 'Вторник',
        'Wednesday': 'Среда',
        'Thursday': 'Четверг',
        'Friday': 'Пятница',
        'Saturday': 'Суббота',
        'Sunday': 'Воскресенье'
      }
      return days[day] || day
    },
    isClassFull(class_) {
      return class_.current_capacity >= class_.hall_capacity
    },
    async enrollInClass(classId) {
      try {
        if (!this.user?.student_id) {
          alert('Ошибка: ID студента не найден')
          return
        }

        await classesApi.enroll(this.user.student_id, classId)
        alert('Вы успешно записаны на занятие!')
        await this.fetchClasses()
      } catch (error) {
        console.error('Ошибка при записи на занятие:', error)
        if (error.response?.data?.detail) {
          // Если сервер вернул детализированную ошибку
          if (Array.isArray(error.response.data.detail)) {
            // Если ошибка в формате массива
            error.response.data.detail.forEach(err => {
              alert(err)
            })
          } else if (typeof error.response.data.detail === 'object') {
            // Если ошибка в формате объекта с полями message и errors
            if (error.response.data.detail.message) {
              alert(error.response.data.detail.message)
            }
            if (error.response.data.detail.errors) {
              error.response.data.detail.errors.forEach(err => {
                alert(err)
              })
            }
          } else {
            // Если ошибка в виде строки
            alert(error.response.data.detail)
          }
        } else {
          alert('Произошла ошибка при записи на занятие')
        }
      }
    }
  },
  async created() {
    await Promise.all([
      this.fetchClasses(),
      this.fetchTeachers(),
      this.checkSubscription()
    ])
  }
}
</script>

<style scoped>
.schedule {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.filters {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: bold;
  color: #2c3e50;
}

.filter-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
}

.schedule-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.schedule-grid {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.day-schedule {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.day-header {
  background: #f8f9fa;
  padding: 15px;
  margin: 0;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
}

.classes-list {
  padding: 15px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.class-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.class-time {
  font-size: 1.2em;
  font-weight: bold;
  color: #2c3e50;
}

.class-info h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.class-info p {
  margin: 5px 0;
  color: #666;
}

.teacher {
  color: #42b983;
  font-weight: bold;
}

.class-actions {
  margin-top: auto;
  text-align: right;
}

.btn {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:hover:not(:disabled) {
  background-color: #45a049;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.loading,
.error,
.no-classes {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
}
</style> 