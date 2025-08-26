<template>
  <div class="student-schedule">
    <h1>Расписание</h1>
    
    <!-- Вкладки -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'studio' }"
        @click="activeTab = 'studio'"
      >
        Расписание студии
      </button>
      <button 
        :class="{ active: activeTab === 'personal' }"
        @click="activeTab = 'personal'"
      >
        Мои записи
      </button>
    </div>

    <!-- Фильтры -->
    <div class="filters">
      <div class="filter-group">
        <label for="view-type">Просмотр:</label>
        <select id="view-type" v-model="viewType">
          <option value="week">На неделю</option>
          <option value="day">На день</option>
        </select>
      </div>
      
      <div class="filter-group" v-if="viewType === 'day'">
        <label for="date">Дата:</label>
        <input 
          type="date" 
          id="date" 
          v-model="selectedDate"
          :min="new Date().toISOString().split('T')[0]"
        >
      </div>
      
      <div class="filter-group" v-else>
        <label for="week">Неделя:</label>
        <input 
          type="week" 
          id="week" 
          v-model="selectedWeek"
          :min="new Date().toISOString().split('T')[0]"
        >
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="loading">
      Загрузка расписания...
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <!-- Расписание студии -->
    <div v-else-if="activeTab === 'studio'" class="schedule-content">
      <div v-if="viewType === 'day'">
        <div v-if="filteredStudioClasses.length === 0" class="no-classes">
          Нет занятий на выбранную дату
        </div>
        <div v-else class="classes-list">
          <div v-for="classItem in filteredStudioClasses" :key="classItem.id" class="class-card">
            <div class="class-info">
              <h3>{{ classItem.type }}</h3>
              <p class="time">{{ formatTime(classItem.time) }}</p>
              <p class="teacher">Преподаватель: {{ classItem.teacher_name }}</p>
              <p class="hall">Зал: {{ classItem.hall_number }}</p>
              <p class="capacity">Записано: {{ classItem.current_capacity }}/{{ classItem.capacity }}</p>
            </div>
            <div class="class-actions">
              <button 
                @click="enrollInClass(classItem)"
                :disabled="isEnrolled(classItem.id) || !hasActiveSubscription || classItem.current_capacity >= classItem.capacity"
                class="enroll-button"
              >
                {{ getEnrollButtonText(classItem) }}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="weekly-schedule">
        <div v-for="day in weekDays" :key="day.date" class="day-schedule">
          <h3>{{ formatDate(day.date) }}</h3>
          <div v-if="getClassesForDay(day.date).length === 0" class="no-classes">
            Нет занятий
          </div>
          <div v-else class="classes-list">
            <div v-for="classItem in getClassesForDay(day.date)" :key="classItem.id" class="class-card">
              <div class="class-info">
                <h3>{{ classItem.type }}</h3>
                <p class="time">{{ formatTime(classItem.time) }}</p>
                <p class="teacher">Преподаватель: {{ classItem.teacher_name }}</p>
                <p class="hall">Зал: {{ classItem.hall_number }}</p>
                <p class="capacity">Записано: {{ classItem.current_capacity }}/{{ classItem.capacity }}</p>
              </div>
              <div class="class-actions">
                <button 
                  @click="enrollInClass(classItem)"
                  :disabled="isEnrolled(classItem.id) || !hasActiveSubscription || classItem.current_capacity >= classItem.capacity"
                  class="enroll-button"
                >
                  {{ getEnrollButtonText(classItem) }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Личное расписание -->
    <div v-else class="schedule-content">
      <div v-if="viewType === 'day'">
        <div v-if="filteredPersonalClasses.length === 0" class="no-classes">
          У вас нет записей на выбранную дату
        </div>
        <div v-else class="classes-list">
          <div v-for="classItem in filteredPersonalClasses" :key="classItem.id" class="class-card">
            <div class="class-info">
              <h3>{{ classItem.type }}</h3>
              <p class="time">{{ formatTime(classItem.time) }}</p>
              <p class="teacher">Преподаватель: {{ classItem.teacher_name }}</p>
              <p class="hall">Зал: {{ classItem.hall_number }}</p>
              <p class="status">Статус: {{ classItem.presence }}</p>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="weekly-schedule">
        <div v-for="day in weekDays" :key="day.date" class="day-schedule">
          <h3>{{ formatDate(day.date) }}</h3>
          <div v-if="getPersonalClassesForDay(day.date).length === 0" class="no-classes">
            Нет записей
          </div>
          <div v-else class="classes-list">
            <div v-for="classItem in getPersonalClassesForDay(day.date)" :key="classItem.id" class="class-card">
              <div class="class-info">
                <h3>{{ classItem.type }}</h3>
                <p class="time">{{ formatTime(classItem.time) }}</p>
                <p class="teacher">Преподаватель: {{ classItem.teacher_name }}</p>
                <p class="hall">Зал: {{ classItem.hall_number }}</p>
                <p class="status">Статус: {{ classItem.presence }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

export default {
  name: 'StudentSchedule',
  setup() {
    const store = useStore()
    const router = useRouter()
    const activeTab = ref('studio')
    const viewType = ref('week')
    const studioClasses = ref([])
    const personalClasses = ref([])
    const loading = ref(true)
    const error = ref(null)
    const selectedDate = ref(new Date().toISOString().split('T')[0])
    const selectedWeek = ref(new Date().toISOString().split('T')[0])
    const hasActiveSubscription = ref(false)
    const enrolledClasses = ref([])

    const fetchStudioClasses = async () => {
      loading.value = true
      error.value = null
      
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          error.value = 'Требуется авторизация'
          router.push('/login')
          return
        }

        const [classesResponse, hallsResponse] = await Promise.all([
          axios({
            method: 'get',
            url: `${API_URL}/classes`,
            headers: {
              'token': token,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }),
          axios({
            method: 'get',
            url: `${API_URL}/halls`,
            headers: {
              'token': token,
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          })
        ])

        if (classesResponse.status === 200 && hallsResponse.status === 200) {
          const halls = hallsResponse.data
          studioClasses.value = classesResponse.data.map(classItem => ({
            ...classItem,
            capacity: halls.find(h => h.id === classItem.hall_id)?.capacity || 0
          }))
        }
      } catch (err) {
        console.error('Ошибка при загрузке расписания студии:', err)
        error.value = 'Произошла ошибка при загрузке расписания'
      } finally {
        loading.value = false
      }
    }

    const fetchPersonalClasses = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        if (!currentUser || !currentUser.student_id) return

        const response = await axios({
          method: 'get',
          url: `${API_URL}/attendance/student/${currentUser.student_id}`,
          headers: {
            'token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        if (response.status === 200) {
          personalClasses.value = response.data.map(item => ({
            id: item.class_id,
            type: item.class_?.type || '',
            time: item.class_?.time || '',
            teacher_name: item.class_?.teacher_name || '',
            hall_number: item.class_?.hall_number || '',
            date: item.class_?.date || '',
            presence: item.presence || 'Записан'
          }))
          enrolledClasses.value = response.data.map(item => item.class_id)
        }
      } catch (err) {
        console.error('Ошибка при загрузке личного расписания:', err)
        error.value = 'Произошла ошибка при загрузке расписания'
        personalClasses.value = []
        enrolledClasses.value = []
      }
    }

    const fetchActiveSubscription = async () => {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        if (!currentUser || !currentUser.student_id) return

        const response = await axios({
          method: 'get',
          url: `${API_URL}/subscriptions/${currentUser.student_id}`,
          headers: {
            'token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        if (response.status === 200 && response.data.length > 0) {
          const activeSubscription = response.data.find(sub => 
            sub.status === 'active' && 
            sub.remaining_classes > 0 &&
            new Date(sub.end_date) >= new Date()
          )
          hasActiveSubscription.value = !!activeSubscription
        }
      } catch (err) {
        console.error('Ошибка при проверке подписки:', err)
        hasActiveSubscription.value = false
      }
    }

    const formatTime = (timeString) => {
      if (!timeString) return ''
      const [hours, minutes] = timeString.split(':')
      return `${hours}:${minutes}`
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const options = { weekday: 'long', day: 'numeric', month: 'long' }
      return date.toLocaleDateString('ru-RU', options)
    }

    const enrollInClass = async (classItem) => {
      try {
        const token = localStorage.getItem('token')
        if (!token) return

        const response = await axios({
          method: 'post',
          url: `${API_URL}/classes/${classItem.id}/enroll`,
          headers: {
            'token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        if (response.status === 200) {
          await Promise.all([
            fetchStudioClasses(),
            fetchPersonalClasses()
          ])
        }
      } catch (err) {
        console.error('Ошибка при записи на занятие:', err)
        error.value = 'Произошла ошибка при записи на занятие'
      }
    }

    const isEnrolled = (classId) => {
      return enrolledClasses.value.includes(classId)
    }

    const getEnrollButtonText = (classItem) => {
      if (isEnrolled(classItem.id)) {
        return 'Вы уже записаны'
      }
      if (!hasActiveSubscription.value) {
        return 'Нет активной подписки'
      }
      if (classItem.current_capacity >= classItem.capacity) {
        return 'Зал заполнен'
      }
      return 'Записаться'
    }

    const weekDays = computed(() => {
      const startDate = new Date(selectedWeek.value)
      const days = []
      for (let i = 0; i < 7; i++) {
        const date = new Date(startDate)
        date.setDate(startDate.getDate() + i)
        days.push({
          date: date.toISOString().split('T')[0],
          dayOfWeek: date.toLocaleDateString('ru-RU', { weekday: 'long' })
        })
      }
      return days
    })

    const filteredStudioClasses = computed(() => {
      if (!studioClasses.value || !Array.isArray(studioClasses.value)) {
        return []
      }
      if (viewType.value === 'day') {
        return studioClasses.value.filter(classItem => {
          return classItem.date === selectedDate.value
        })
      } else {
        const startDate = new Date(selectedWeek.value)
        const endDate = new Date(startDate)
        endDate.setDate(endDate.getDate() + 7)
        
        return studioClasses.value.filter(classItem => {
          const classDate = new Date(classItem.date)
          return classDate >= startDate && classDate < endDate
        })
      }
    })

    const filteredPersonalClasses = computed(() => {
      if (!personalClasses.value || !Array.isArray(personalClasses.value)) {
        return []
      }
      if (viewType.value === 'day') {
        return personalClasses.value.filter(classItem => {
          return classItem.date === selectedDate.value
        })
      } else {
        const startDate = new Date(selectedWeek.value)
        const endDate = new Date(startDate)
        endDate.setDate(endDate.getDate() + 7)
        
        return personalClasses.value.filter(classItem => {
          const classDate = new Date(classItem.date)
          return classDate >= startDate && classDate < endDate
        })
      }
    })

    const getClassesForDay = (date) => {
      if (!studioClasses.value || !Array.isArray(studioClasses.value)) {
        return []
      }
      return studioClasses.value.filter(classItem => classItem.date === date)
    }

    const getPersonalClassesForDay = (date) => {
      if (!personalClasses.value || !Array.isArray(personalClasses.value)) {
        return []
      }
      return personalClasses.value.filter(classItem => classItem.date === date)
    }

    // Добавляем watch для обновления данных при изменении фильтров
    watch([selectedDate, selectedWeek, viewType], async () => {
      if (viewType.value === 'day') {
        // При выборе конкретного дня обновляем данные
        await Promise.all([
          fetchStudioClasses(),
          fetchPersonalClasses()
        ])
      }
    })

    onMounted(async () => {
      if (!store.getters.isAuthenticated) {
        router.push('/login')
      } else {
        await Promise.all([
          fetchStudioClasses(),
          fetchPersonalClasses(),
          fetchActiveSubscription()
        ])
      }
    })

    return {
      activeTab,
      viewType,
      loading,
      error,
      selectedDate,
      selectedWeek,
      weekDays,
      filteredStudioClasses,
      filteredPersonalClasses,
      hasActiveSubscription,
      formatTime,
      formatDate,
      enrollInClass,
      isEnrolled,
      getEnrollButtonText,
      getClassesForDay,
      getPersonalClassesForDay
    }
  }
}
</script>

<style scoped>
.student-schedule {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #f0f0f0;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.tabs button.active {
  background-color: #1976d2;
  color: white;
}

.filters {
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-group label {
  font-weight: bold;
}

.filter-group input,
.filter-group select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.loading, .error, .no-classes {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}

.error {
  color: #c62828;
  background-color: #ffebee;
  border-radius: 4px;
}

.weekly-schedule {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.day-schedule {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.day-schedule h3 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.classes-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.class-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.class-info h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.time {
  font-size: 18px;
  font-weight: bold;
  color: #2196F3;
  margin: 10px 0;
}

.teacher, .hall, .capacity, .status {
  margin: 5px 0;
  color: #666;
}

.class-actions {
  margin-top: 15px;
  text-align: center;
}

.enroll-button {
  width: 100%;
  padding: 10px;
  background-color: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.enroll-button:hover:not(:disabled) {
  background-color: #1565c0;
}

.enroll-button:disabled {
  background-color: #bdbdbd;
  cursor: not-allowed;
}
</style> 