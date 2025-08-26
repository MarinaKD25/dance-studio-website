<template>
  <div class="login-container">
    <div class="login-box">
      <h2>Вход в систему</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            required 
            placeholder="Введите ваш email"
          >
        </div>
        <div class="form-group">
          <label for="password">Пароль</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            required 
            placeholder="Введите ваш пароль"
          >
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script>
import { authApi } from '../api'
import { mapActions } from 'vuex'

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    ...mapActions(['login']),
    async handleLogin() {
      this.loading = true
      this.error = null
      
      try {
        const response = await authApi.login({
          email: this.email,
          password: this.password
        })

        if (response.data.access_token) {
          // Сохраняем токен в localStorage
          localStorage.setItem('token', response.data.access_token)
          
          // Получаем информацию о текущем пользователе
          const userResponse = await authApi.getCurrentUser()
          
          // Обновляем состояние Vuex с полной информацией о пользователе
          await this.login({
            token: response.data.access_token,
            user: { 
              id: userResponse.data.id,
              email: this.email, 
              role: response.data.role,
              name: userResponse.data.name,
              student_id: userResponse.data.student_id,
              teacher_id: userResponse.data.teacher_id
            }
          })
          
          // Сохраняем данные пользователя в localStorage
          localStorage.setItem('user', JSON.stringify({
            id: userResponse.data.id,
            email: this.email,
            role: response.data.role,
            name: userResponse.data.name,
            student_id: userResponse.data.student_id,
            teacher_id: userResponse.data.teacher_id
          }))
          
          // Перенаправляем в зависимости от роли
          switch (response.data.role) {
            case 'admin':
              this.$router.push('/admin')
              break
            case 'teacher':
              this.$router.push('/teacher')
              break
            case 'student':
              this.$router.push('/student')
              break
            default:
              this.error = 'Неизвестная роль пользователя'
          }
        }
      } catch (error) {
        console.error('Ошибка авторизации:', error)
        this.error = error.response?.data?.detail || 'Произошла ошибка при входе'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #ff0000;
  margin-top: 1rem;
  text-align: center;
}
</style> 