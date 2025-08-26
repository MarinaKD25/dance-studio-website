import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import api from './api'

// Добавляем перехватчики для авторизации
api.interceptors.request.use(config => {
  const token = store.state.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      store.dispatch('logout')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

// Создаем приложение
const app = createApp(App)

// Предоставляем api глобально
app.config.globalProperties.$api = api

// Инициализация приложения
store.dispatch('initializeApp').then(() => {
  app.use(router)
  app.use(store)
  app.mount('#app')
})
