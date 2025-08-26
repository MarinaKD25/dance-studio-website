<template>
  <div class="home">
    <!-- Приветственный блок -->
    <div class="welcome-section">
      <h1>Добро пожаловать в танцевальную студию!</h1>
      <p>Ваш путь к совершенству в танце начинается здесь</p>
    </div>

    <!-- Быстрый доступ к основным функциям -->
    <div class="quick-actions">
      <router-link to="/schedule" class="action-card">
        <i class="fas fa-calendar-alt"></i>
        <h3>Расписание</h3>
        <p>Просмотр и запись на занятия</p>
      </router-link>
      <router-link v-if="user?.student_id" :to="`/subscriptions/${user.student_id}`" class="action-card">
        <i class="fas fa-ticket-alt"></i>
        <h3>Абонементы</h3>
        <p>Управление подписками</p>
      </router-link>
      <div v-else class="action-card disabled">
        <i class="fas fa-ticket-alt"></i>
        <h3>Абонементы</h3>
        <p>Доступно только для студентов</p>
      </div>
      <router-link to="/teachers" class="action-card">
        <i class="fas fa-chalkboard-teacher"></i>
        <h3>Преподаватели</h3>
        <p>Наши специалисты</p>
      </router-link>

    </div>

    <!-- Блок с текущими занятиями -->
    <div class="current-classes">
      <h2>Ближайшие занятия</h2>
      <div v-if="loading" class="loading">Загрузка...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="upcomingClasses.length === 0" class="no-classes">
        Нет предстоящих занятий
      </div>
      <div v-else class="classes-list">
        <div v-for="class_ in upcomingClasses" :key="class_.id" class="class-card">
          <div class="class-time">{{ formatTime(class_.date) }}</div>
          <div class="class-info">
            <h4>{{ class_.type }}</h4>
            <p>{{ getTeacherName(class_.teacher_id) }}</p>
            <p>Зал {{ getHallNumber(class_.hall_id) }}</p>
          </div>
          <div class="class-actions">
            <button 
              v-if="hasActiveSubscription" 
              class="btn btn-small"
              :disabled="isClassFull(class_)"
              @click="enrollInClass(class_.id)"
            >
              Записаться
            </button>
            <button v-else class="btn btn-small" disabled>
              Требуется абонемент
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Блок с информацией о текущем абонементе -->
    <div v-if="currentSubscription" class="subscription-info">
      <h2>Ваш абонемент</h2>
      <div class="subscription-card">
        <div class="status" :class="currentSubscription.status ? currentSubscription.status.toLowerCase() : ''">
          {{ getStatusText(currentSubscription.status) }}
        </div>
        <div class="details">
          <p>Осталось занятий: {{ currentSubscription.remaining_classes }}/{{ currentSubscription.number_of_classes }}</p>
          <p>Действует до: {{ formatDate(currentSubscription.end_date) }}</p>
        </div>
      </div>
    </div>

    <!-- Блок с новостями и объявлениями -->
    <div class="news-section">
      <h2>Новости и объявления</h2>
      <div class="news-list">
        <div class="news-item">
          <h3>Новый стиль танца</h3>
          <p>С радостью сообщаем о добавлении нового направления - Contemporary!</p>
          <span class="date">15.03.2024</span>
        </div>
        <div class="news-item">
          <h3>Мастер-класс</h3>
          <p>Приглашаем на мастер-класс по Hip-hop с известным хореографом!</p>
          <span class="date">20.03.2024</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { classesApi, teachersApi, hallsApi, subscriptionsApi } from '../api'
import { mapState } from 'vuex'

export default {
  name: 'HomeView',
  data() {
    return {
      loading: true,
      error: null,
      upcomingClasses: [],
      teachers: [],
      halls: [],
      currentSubscription: null,
      hasActiveSubscription: false
    }
  },
  computed: {
    ...mapState(['user']),
    currentUser() {
      return this.user
    }
  },
  async created() {
    await this.loadData()
    await this.checkSubscription()
  },
  methods: {
    getRoleName(role) {
      const roleNames = {
        'admin': 'Администратор',
        'teacher': 'Преподаватель',
        'student': 'Ученик'
      }
      return roleNames[role] || role
    },
    async loadData() {
      try {
        const [classesResponse, teachersResponse, hallsResponse] = await Promise.all([
          classesApi.getAll({ date_from: new Date() }),
          teachersApi.getAll(),
          hallsApi.getAll()
        ])
        this.upcomingClasses = classesResponse.data.slice(0, 3) // Показываем только ближайшие 3 занятия
        this.teachers = teachersResponse.data
        this.halls = hallsResponse.data
      } catch (error) {
        this.error = 'Ошибка при загрузке данных'
        console.error('Ошибка при загрузке данных:', error)
      } finally {
        this.loading = false
      }
    },
    async checkSubscription() {
      try {
        if (!this.user?.student_id) {
          this.currentSubscription = null;
          this.hasActiveSubscription = false;
          return;
        }
        const response = await subscriptionsApi.getActive(this.user.student_id)
        this.currentSubscription = response.data
        this.hasActiveSubscription = response.data !== null
      } catch (error) {
        console.error('Ошибка при проверке абонемента:', error)
        this.currentSubscription = null;
        this.hasActiveSubscription = false;
      }
    },
    formatTime(date) {
      return new Date(date).toLocaleTimeString('ru-RU', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('ru-RU')
    },
    getTeacherName(teacherId) {
      const teacher = this.teachers.find(t => t.id === teacherId)
      return teacher ? teacher.full_name : 'Неизвестно'
    },
    getHallNumber(hallId) {
      const hall = this.halls.find(h => h.id === hallId)
      return hall ? hall.hall_number : 'Неизвестно'
    },
    isClassFull(class_) {
      const hall = this.halls.find(h => h.id === class_.hall_id)
      return hall && class_.current_capacity >= hall.capacity
    },
    async enrollInClass(classId) {
      if (!this.user?.student_id) {
        this.$toast.error('Для записи на занятие необходимо быть студентом')
        return
      }
      try {
        await classesApi.enroll(this.user.student_id, classId)
        await this.loadData()
        this.$toast.success('Вы успешно записались на занятие')
      } catch (error) {
        console.error('Ошибка при записи на занятие:', error)
        if (error.response?.status === 400) {
          this.$toast.error('Не удалось записаться на занятие: ' + error.response.data.message)
        } else {
          this.$toast.error('Произошла ошибка при записи на занятие')
        }
      }
    },
    getStatusText(status) {
      if (!status) return 'Неизвестно'
      const statusTexts = {
        'active': 'Активен',
        'expired': 'Истек',
        'pending': 'Ожидает активации'
      }
      return statusTexts[status.toLowerCase()] || status
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.welcome-section h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.welcome-section p {
  color: #666;
  font-size: 1.2em;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s;
}

.action-card:hover {
  transform: translateY(-5px);
}

.action-card i {
  font-size: 2em;
  margin-bottom: 15px;
  color: #42b983;
}

.action-card h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.action-card p {
  margin: 0;
  color: #666;
  text-align: center;
}

.action-card.disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #f8f9fa;
}

.action-card.disabled i {
  color: #999;
}

.action-card.disabled h3 {
  color: #999;
}

.action-card.disabled p {
  color: #999;
}

.current-classes,
.subscription-info,
.news-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.classes-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.class-card {
  display: flex;
  flex-direction: column;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.class-time {
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.class-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.class-info p {
  margin: 0;
  color: #666;
  font-size: 0.9em;
}

.class-actions {
  margin-top: 15px;
  text-align: right;
}

.subscription-card {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.status {
  font-weight: bold;
  margin-bottom: 10px;
}

.status.active {
  color: #28a745;
}

.status.expired {
  color: #dc3545;
}

.status.cancelled {
  color: #6c757d;
}

.news-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.news-item {
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.news-item h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
}

.news-item p {
  margin: 0 0 10px 0;
  color: #666;
}

.news-item .date {
  color: #999;
  font-size: 0.9em;
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

.btn-small {
  padding: 5px 10px;
  font-size: 0.9em;
}
</style> 