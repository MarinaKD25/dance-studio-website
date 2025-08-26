import { createStore } from 'vuex'
import { authApi } from '../api'

export default createStore({
  state: {
    user: null,
    token: localStorage.getItem('token') || null,
    isAdmin: false
  },
  getters: {
    isAuthenticated: state => !!state.token,
    currentUser: state => state.user,
    isAdmin: state => state.user?.role === 'admin',
    isTeacher: state => state.user?.role === 'teacher',
    isStudent: state => state.user?.role === 'student',
    hasActiveSubscription: state => {
      if (!state.user) return false
      return state.user.subscription && 
             state.user.subscription.status === 'active' && 
             new Date(state.user.subscription.end_date) > new Date()
    }
  },
  mutations: {
    SET_USER(state, user) {
      state.user = user
    },
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    CLEAR_AUTH(state) {
      state.user = null
      state.token = null
    }
  },
  actions: {
    async login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
    },
    logout({ commit }) {
      commit('SET_TOKEN', null)
      commit('CLEAR_AUTH')
    },
    clearAuth({ commit }) {
      commit('SET_TOKEN', null)
      commit('CLEAR_AUTH')
    },
    async initializeApp({ commit }) {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          const response = await authApi.getCurrentUser()
          commit('SET_USER', response.data)
          commit('SET_TOKEN', token)
        } catch (error) {
          console.error('Ошибка при восстановлении сессии:', error)
          commit('CLEAR_AUTH')
        }
      }
    },
    setUser({ commit }, user) {
      commit('SET_USER', user)
    },
    setToken({ commit }, token) {
      commit('SET_TOKEN', token)
    }
  }
}) 