import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'
import NewSubscription from '../views/student/NewSubscription.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/admin',
    name: 'AdminCabinet',
    component: () => import('../views/admin/AdminCabinet.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/schedule',
    name: 'AdminSchedule',
    component: () => import('../views/admin/Schedule.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },

  {
    path: '/admin/teachers',
    name: 'AdminTeachers',
    component: () => import('../views/admin/Teachers.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/teacher',
    name: 'TeacherCabinet',
    component: () => import('../views/teacher/TeacherCabinet.vue'),
    meta: { requiresAuth: true, requiresTeacher: true }
  },
  {
    path: '/student',
    name: 'StudentCabinet',
    component: () => import('../views/student/StudentCabinet.vue'),
    meta: { requiresAuth: true, requiresStudent: true }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('../views/Schedule.vue'),
    meta: { requiresAuth: true }
  },

  {
    path: '/subscriptions/:studentId',
    name: 'StudentSubscription',
    component: () => import('../views/student/Subscriptions.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/subscriptions/new',
    name: 'NewSubscription',
    component: NewSubscription,
    meta: { requiresAuth: true }
  },
  {
    path: '/teachers',
    name: 'Teachers',
    component: () => import('../views/Teachers.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/students',
    name: 'Students',
    component: () => import('../views/Students.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/attendance',
    name: 'AttendanceStudent',
    component: () => import('../views/Attendance.vue'),
    meta: { requiresAuth: true, requiresStudent: true }
  },
  {
    path: '/admin/attendance',
    name: 'Attendance',
    component: () => import('../views/admin/Attendance.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/teacher/schedule',
    name: 'TeacherSchedule',
    component: () => import('../views/teacher/Schedule.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/student/schedule',
    name: 'StudentSchedule',
    component: () => import('../views/student/Schedule.vue'),
    meta: { requiresAuth: true, role: 'student' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters.isAuthenticated
  const user = store.state.user

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && user?.role !== 'admin') {
    next('/')
  } else if (to.meta.requiresTeacher && user?.role !== 'teacher') {
    next('/')
  } else if (to.meta.requiresStudent && user?.role !== 'student') {
    next('/')
  } else {
    next()
  }
})

export default router 