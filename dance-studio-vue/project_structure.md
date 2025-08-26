# Структура проекта Vue

## Основные файлы и их функции

### 1. main.js - Главный файл приложения
```javascript
// Основные функции:
- Инициализация Vue приложения
- Подключение Vuex (хранилище состояния)
- Подключение Vue Router (маршрутизация)
- Подключение глобальных стилей
- Подключение глобальных компонентов
```

### 2. App.vue - Корневой компонент
```javascript
// Основные функции:
- Определение основной структуры приложения
- Навигационное меню
- Обработка авторизации
- Маршрутизация (router-view)
- Глобальные стили
```

### 3. src/api/index.js - Настройки API
```javascript
// Основные функции:
- Создание экземпляра axios
- Настройка перехватчиков запросов
- Добавление токена авторизации
- Обработка ошибок
- Определение методов для работы с API:
  - Авторизация
  - Работа с занятиями
  - Работа с преподавателями
  - Работа со студентами
  - Работа с залами
  - Работа с посещаемостью
  - Работа с подписками
  - Работа с платежами
```

### 4. src/store/index.js - Хранилище Vuex
```javascript
// Основные функции:
- Управление состоянием приложения
- Хранение данных пользователя
- Хранение токена авторизации
- Геттеры для проверки авторизации
- Действия для:
  - Входа в систему
  - Выхода из системы
  - Обновления данных пользователя
```

### 5. src/views/ - Компоненты страниц
```javascript
// Login.vue:
- Форма авторизации
- Обработка входа в систему
- Перенаправление по ролям

// Schedule.vue:
- Отображение расписания занятий
- Запись на занятия
- Фильтрация занятий

// Teachers.vue:
- Список преподавателей
- Информация о преподавателях
- Расписание преподавателей

// Students.vue:
- Список студентов
- Информация о студентах
- Посещаемость студентов

// AdminPanel.vue:
- Панель администратора
- Управление занятиями
- Управление пользователями
```

### 6. src/config/index.js - Конфигурация
```javascript
// Основные функции:
- Настройки API
- Базовые URL
- Таймауты
- Заголовки запросов
```

### 7. vue.config.js - Конфигурация Vue CLI
```javascript
// Основные функции:
- Настройки разработки
- Настройки прокси
- Настройки CORS
- Настройки сборки
```

### 8. src/router/index.js - Маршрутизация
```javascript
// Основные функции:
- Определение маршрутов
- Защита маршрутов
- Перенаправления
- Обработка ошибок
```

### 9. src/components/ - Переиспользуемые компоненты
```javascript
// Основные функции:
- Общие компоненты интерфейса
- Формы
- Таблицы
- Модальные окна
- Навигация
```

### 10. src/assets/ - Ресурсы
```javascript
// Основные функции:
- Изображения
- Стили
- Шрифты
- Иконки
```

## Основные принципы работы

### 1. Авторизация
- Пользователь вводит данные в `Login.vue`
- Запрос идет через `api/index.js`
- Токен сохраняется в `localStorage` и `Vuex`
- Состояние обновляется в `store/index.js`

### 2. Запросы к API
- Все запросы идут через `api/index.js`
- Автоматически добавляется токен
- Обрабатываются ошибки
- Данные сохраняются в `Vuex`

### 3. Маршрутизация
- Защищенные маршруты проверяют авторизацию
- Перенаправления зависят от роли пользователя
- Компоненты загружаются по требованию

### 4. Управление состоянием
- Все данные хранятся в `Vuex`
- Компоненты получают данные через геттеры
- Изменения происходят через действия

### 5. Стилизация
- Глобальные стили в `App.vue`
- Компонентные стили в каждом компоненте
- Общие стили в `assets`

## Примеры кода

### main.js
```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

const app = createApp(App)
app.use(router)
app.use(store)
app.mount('#app')
```

### App.vue
```javascript
<template>
  <div id="app">
    <nav>
      <router-link to="/">Главная</router-link> |
      <router-link to="/schedule">Расписание</router-link> |
      <router-link to="/teachers">Преподаватели</router-link> |
      <router-link to="/students">Ученики</router-link> |
      <router-link to="/subscriptions">Мой абонемент</router-link>
      <template v-if="isAdmin">
        | <router-link to="/admin/schedule">Админ-панель</router-link>
      </template>
      <template v-if="isAuthenticated">
        | <a href="#" @click.prevent="handleLogout" class="logout-link">Выход</a>
      </template>
    </nav>
    <router-view/>
  </div>
</template>
```

### api/index.js
```javascript
import axios from 'axios'
import config from '../config'

const api = axios.create({
  ...config.api,
  headers: {
    ...config.api.headers
  }
})

// Перехватчики запросов и ответов
api.interceptors.request.use(...)
api.interceptors.response.use(...)

// API методы
const authApi = {
  login: (credentials) => api.post('/login', credentials),
  getCurrentUser: () => api.get('/students/me')
}

const classesApi = {
  getAll: (params) => api.get('/classes/', { params }),
  create: (classData) => api.post('/classes/', classData),
  // ...
}

// Экспорт методов
export {
  authApi,
  classesApi,
  // ...
}
```

### store/index.js
```javascript
import { createStore } from 'vuex'
import { authApi } from '../api'

export default createStore({
  state: {
    user: null,
    token: null,
    isAdmin: false
  },
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    isAdmin: state => state.isAdmin
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
      state.isAdmin = user?.role === 'admin'
    },
    SET_TOKEN(state, token) {
      state.token = token
    }
  },
  actions: {
    async login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
    },
    logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('SET_USER', null)
    }
  }
})
```

### router/index.js
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminPanel.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // ...
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !store.getters.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !store.getters.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
```

### config/index.js
```javascript
const config = {
  api: {
    baseURL: '/api',
    timeout: 5000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  }
}

module.exports = config
```

### vue.config.js
```javascript
const { defineConfig } = require('@vue/cli-service')
const config = require('./src/config')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      [config.api.baseURL]: {
        target: 'http://localhost:8000',
        changeOrigin: true,
        pathRewrite: {
          [`^${config.api.baseURL}`]: ''
        }
      }
    }
  }
})
``` 