import axios from 'axios'
import config from '../config'

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: config.api.baseURL,
  headers: config.api.headers
})

// Добавляем перехватчик для добавления токена к запросам
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      // Добавляем токен в заголовок для всех запросов
      config.headers['token'] = token
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Добавляем перехватчик для обработки ответов
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Если токен истек или недействителен, очищаем localStorage и перенаправляем на страницу входа
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Методы для работы с занятиями
const classesApi = {
  getAll: (params) => api.get('/classes/', { params }),
  create: (classData) => api.post('/classes/', classData),
  update: (classId, classData) => api.put(`/classes/${classId}/`, classData),
  delete: (classId) => api.delete(`/classes/${classId}/`),
  getAvailable: (studentId) => api.get(`/classes/available/${studentId}/`),
  enroll: (studentId, classId) => api.post(`/classes/${classId}/enroll`, null, {
    headers: {
      'token': localStorage.getItem('token'),
      'Content-Type': 'application/json'
    }
  })
}

// Методы для работы с преподавателями
const teachersApi = {
  getAll: () => api.get('/teachers/'),
  getByAdmin:() => api.get('/admin/teachers/'),
  create: (teacher) => api.post('/admin/teachers/', teacher),
  update: (id, teacher) => api.put(`/admin/teachers/${id}/`, teacher),
  delete: (id) => api.delete(`/admin/teachers/${id}`),
  getSchedule: (teacherId) => api.get(`/teachers/${teacherId}/schedule/`)
}

// Методы для работы с учениками
const studentsApi = {
  getAll: () => api.get('/students/'),
  getById: (id) => api.get(`/students/${id}/`),
  create: (student) => api.post('/students/', student),
  update: (id, student) => api.put(`/students/${id}/`, student),
  delete: (id) => api.delete(`/students/${id}/`),
  getMe: () => api.get('/students/me/'),
  getAttendance: (studentId) => api.get(`/attendance/student/${studentId}/`)
}

// Методы для работы с залами
const hallsApi = {
  getAll: () => api.get('/halls/')
}

// Методы для работы с посещаемостью
const attendanceApi = {
  mark: (data) => api.post('/attendance/', data),
  getAll: () => api.get('/admin/attendance/'),
  getStatistics: (params) => api.get('/attendance/statistics/', { params }),
  getStudentAttendance: (studentId) => api.get(`/attendance/student/${studentId}/`),
  getClassAttendance: (classId) => api.get(`/attendance/class/${classId}/`),
  updateAttendance: (attendanceId, data) => api.put(`/attendance/${attendanceId}/`, data)
}

// Методы для работы с подписками
const subscriptionsApi = {
  create: (data) => api.post('/subscriptions/', data),
  //для получения активной подписки студентом
  getActive: (studentId) => api.get(`/subscriptions/${studentId}/`, {
    headers: {
      'token': localStorage.getItem('token')
    }
  })

}

// Методы для аутентификации
const authApi = {
  login: async (credentials) => {
    const response = await api.post('/login', {
      email: credentials.email,
      password: credentials.password
    })
    if (response.data?.access_token) {
      localStorage.setItem('token', response.data.access_token)
    }
    return response
  },
  getCurrentUser: () => api.get('/users/me', {
    headers: {
      'token': localStorage.getItem('token')
    }
  })
}

// Методы для работы с платежами
const paymentsApi = {
  create: (data) => api.post('/payments/', data),
  getById: (id) => api.get(`/payments/${id}/`),
  getByStudent: (studentId) => api.get(`/payments/student/${studentId}/`)
}

export {
  classesApi,
  teachersApi,
  studentsApi,
  hallsApi,
  attendanceApi,
  subscriptionsApi,
  paymentsApi,
  authApi
}

export default api 