<template>
  <div class="subscriptions">
    <h1>Мой абонемент</h1>
    
    <div v-if="loading" class="loading">
      Загрузка информации об абонементе...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="subscriptions && subscriptions.length > 0" class="subscription-info">
      <div class="new-subscription-link">
        <router-link to="/subscriptions/new" class="btn-new-subscription">
          Оформить новую подписку
        </router-link>
      </div>
      <div v-for="subscription in subscriptions" :key="subscription.id" class="info-card">
        <h2>Информация об абонементе #{{ subscription.id }}</h2>
        <div class="info-row">
          <span class="label">Статус:</span>
          <span :class="['status', subscription.status]">
            {{ subscription.status === 'active' ? 'Активен' : 'Истек' }}
          </span>
        </div>
        <div class="info-row">
          <span class="label">Дата начала:</span>
          <span>{{ formatDate(subscription.start_date) }}</span>
        </div>
        <div class="info-row">
          <span class="label">Дата окончания:</span>
          <span>{{ formatDate(subscription.end_date) }}</span>
        </div>
        <div class="info-row">
          <span class="label">Количество занятий:</span>
          <span>{{ subscription.number_of_classes }}</span>
        </div>
        <div class="info-row">
          <span class="label">Осталось занятий:</span>
          <span>{{ subscription.remaining_classes }}</span>
        </div>
      </div>
      
     
    </div>
    
    <div v-else class="no-subscription">
      <p>У вас нет активного абонемента</p>
      
      <div class="buy-subscription">
        <h2>Купить новый абонемент</h2>
        <form @submit.prevent="buySubscription">
          <div class="form-group">
            <label for="numberOfClasses">Количество занятий:</label>
            <select id="numberOfClasses" v-model="newSubscription.numberOfClasses">
              <option value="4">4 занятия</option>
              <option value="8">8 занятий</option>
              <option value="12">12 занятий</option>
              <option value="16">16 занятий</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="paymentMethod">Способ оплаты:</label>
            <select id="paymentMethod" v-model="newSubscription.paymentMethod">
              <option value="card">Банковская карта</option>
              <option value="cash">Наличные</option>
              <option value="bank_transfer">Банковский перевод</option>
            </select>
          </div>

          <div class="form-group">
            <label for="startDate">Дата начала:</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="newSubscription.startDate"
              :min="new Date().toISOString().split('T')[0]"
            >
          </div>

          <div class="price-info">
            <p>Стоимость: {{ calculatePrice() }} ₽</p>
          </div>

          <button type="submit" class="btn-buy" :disabled="paymentProcessing">
            {{ paymentProcessing ? 'Обработка платежа...' : 'Оплатить' }}
          </button>
        </form>
      </div>
    </div>


     
   
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

export default {
  name: 'UserSubscriptions',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    const subscriptions = ref([])
    const loading = ref(true)
    const error = ref(null)
    const enrollLoading = ref(false)
    const enrollError = ref(null)
    const paymentProcessing = ref(false)
    const hasActiveSubscription = ref(false)

    const newSubscription = ref({
      numberOfClasses: '8',
      paymentMethod: 'card',
      startDate: new Date().toISOString().split('T')[0]
    })

    const calculatePrice = () => {
      const pricePerClass = 500 // цена за одно занятие
      return pricePerClass * parseInt(newSubscription.value.numberOfClasses)
    }

    const fetchSubscriptions = async () => {
      loading.value = true
      error.value = null
      
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          error.value = 'Требуется авторизация'
          router.push('/login')
          return
        }

        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        console.log('Current user:', currentUser)

        if (!currentUser || !currentUser.id) {
          error.value = 'Данные пользователя не найдены'
          router.push('/login')
          return
        }

        // Получаем student_id из URL или из данных пользователя
        const studentId = route.params.student_id || currentUser.student_id
        console.log('Student ID from URL:', route.params.student_id)
        console.log('Student ID from user:', currentUser.student_id)
        console.log('Final student ID:', studentId)

        if (!studentId) {
          error.value = 'ID студента не найден'
          return
        }

        // Проверяем доступ
        if (currentUser.role === 'student' && currentUser.student_id !== parseInt(studentId)) {
          error.value = 'У вас нет доступа к этой странице'
          return
        }

        const url = `${API_URL}/subscriptions/${studentId}`
        console.log('Making request to:', url)
        
        const headers = {
          'token': token,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
        console.log('Request headers:', headers)

        const response = await axios({
          method: 'get',
          url: url,
          headers: headers
        })

        console.log('Response status:', response.status)
        console.log('Response headers:', response.headers)
        console.log('Response data:', response.data)

        if (response.status === 200 && Array.isArray(response.data)) {
          subscriptions.value = response.data
          hasActiveSubscription.value = response.data.length > 0
        } else {
          subscriptions.value = []
          error.value = 'Активные подписки не найдены'
        }
      } catch (err) {
        console.error('Error fetching subscriptions:', err)
        console.error('Error details:', {
          message: err.message,
          status: err.response?.status,
          statusText: err.response?.statusText,
          data: err.response?.data,
          headers: err.response?.headers
        })

        if (err.response) {
          const errorData = err.response.data
          console.log('Error response data:', errorData)
          
          if (errorData.detail) {
            if (Array.isArray(errorData.detail)) {
              error.value = errorData.detail.map(err => {
                if (typeof err === 'object') {
                  const field = err.loc ? err.loc[err.loc.length - 1] : 'неизвестное поле'
                  const message = err.msg || 'Неизвестная ошибка'
                  const type = err.type || ''
                  
                  let userMessage = message
                  if (type === 'value_error.missing') {
                    userMessage = `Отсутствует обязательное поле: ${field}`
                  } else if (type === 'type_error.none.not_allowed') {
                    userMessage = `Поле ${field} не может быть пустым`
                  }
                  return userMessage
                }
                return err
              }).join(', ')
            } else if (typeof errorData.detail === 'object') {
              error.value = errorData.detail.message || 'Произошла ошибка'
            } else {
              error.value = errorData.detail
            }
          } else {
            error.value = 'Произошла ошибка при получении данных'
          }
        } else {
          error.value = 'Ошибка сети или сервера'
        }
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const buySubscription = async () => {
      paymentProcessing.value = true
      error.value = null

      try {
        const token = localStorage.getItem('token')
        if (!token) {
          throw new Error('Требуется авторизация')
        }

        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        if (!currentUser || !currentUser.student_id) {
          throw new Error('ID студента не найден')
        }

        const requestData = {
          student_id: currentUser.student_id,
          amount: calculatePrice(),
          payment_method: newSubscription.value.paymentMethod,
          number_of_classes: parseInt(newSubscription.value.numberOfClasses),
          start_date: newSubscription.value.startDate
        }

        console.log('Sending subscription request:', requestData)

        const response = await axios({
          method: 'post',
          url: `${API_URL}/payments/create-with-subscription`,
          headers: {
            'token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          data: requestData
        })

        if (response.status === 200) {
          // Обновляем список подписок
          await fetchSubscriptions()
          alert('Абонемент успешно приобретен!')
        }
      } catch (err) {
        console.error('Ошибка при покупке абонемента:', err)
        
        if (err.response?.data?.detail) {
          const errorData = err.response.data.detail
          if (typeof errorData === 'object' && errorData.message) {
            error.value = `${errorData.message}: ${errorData.errors?.join(', ') || ''}`
          } else {
            error.value = errorData
          }
        } else {
          error.value = 'Произошла ошибка при покупке абонемента'
        }
      } finally {
        paymentProcessing.value = false
      }
    }

    const enrollInClass = async (classId) => {
      if (!subscriptions.value.length) {
        error.value = 'Для записи на занятие необходим активный абонемент'
        return
      }

      enrollLoading.value = true
      enrollError.value = null

      try {
        const token = localStorage.getItem('token')
        if (!token) {
          throw new Error('Требуется авторизация')
        }

        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        if (!currentUser || !currentUser.student_id) {
          throw new Error('ID студента не найден')
        }

        const response = await axios({
          method: 'post',
          url: `${API_URL}/classes/${classId}/enroll`,
          headers: {
            'token': token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        })

        if (response.status === 200) {
          // Обновляем информацию о подписке
          await fetchSubscriptions()
          alert('Вы успешно записались на занятие!')
        }
      } catch (err) {
        console.error('Ошибка при записи на занятие:', err)
        
        if (err.response?.data?.detail) {
          const errorData = err.response.data.detail
          if (typeof errorData === 'object' && errorData.message) {
            enrollError.value = `${errorData.message}: ${errorData.errors?.join(', ') || ''}`
          } else {
            enrollError.value = errorData
          }
        } else {
          enrollError.value = 'Произошла ошибка при записи на занятие'
        }
      } finally {
        enrollLoading.value = false
      }
    }

    onMounted(() => {
      if (!store.getters.isAuthenticated) {
        router.push('/login')
      } else {
        fetchSubscriptions()
      }
    })

    return {
      subscriptions,
      loading,
      error,
      enrollLoading,
      enrollError,
      formatDate,
      buySubscription,
      enrollInClass,
      newSubscription,
      paymentProcessing,
      hasActiveSubscription,
      calculatePrice
    }
  }
}
</script>

<style scoped>
.subscriptions {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.subscription-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.info-card {
  max-width: 500px;
  margin: 0 auto;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  color: #666;
}

.status {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}

.status.active {
  background-color: #4CAF50;
  color: white;
}

.status.expired {
  background-color: #f44336;
  color: white;
}

.no-subscription {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.buy-subscription {
  max-width: 400px;
  margin: 20px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.price-info {
  margin: 15px 0;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.btn-buy {
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn-buy:hover {
  background-color: #45a049;
}

.btn-buy:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.new-subscription-link {
  margin-top: 30px;
  text-align: center;
}

.btn-new-subscription {
  display: inline-block;
  padding: 12px 24px;
  background-color: #2196F3;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-new-subscription:hover {
  background-color: #1976D2;
}

.btn-new-subscription:active {
  background-color: #0D47A1;
}
</style> 