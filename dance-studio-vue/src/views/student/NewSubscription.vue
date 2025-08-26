<template>
  <div class="new-subscription">
    <h1>Оформление новой подписки</h1>
    
    <div class="subscription-form">
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

        <div class="form-actions">
          <button type="submit" class="btn-buy" :disabled="paymentProcessing">
            {{ paymentProcessing ? 'Обработка платежа...' : 'Оплатить' }}
          </button>
          <router-link to="/subscriptions" class="btn-cancel">
            Отмена
          </router-link>
        </div>
      </form>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://127.0.0.1:8000'

export default {
  name: 'NewSubscription',
  setup() {
    const router = useRouter()
    const error = ref(null)
    const paymentProcessing = ref(false)

    const newSubscription = ref({
      numberOfClasses: '8',
      paymentMethod: 'card',
      startDate: new Date().toISOString().split('T')[0]
    })

    const calculatePrice = () => {
      const pricePerClass = 500 // цена за одно занятие
      return pricePerClass * parseInt(newSubscription.value.numberOfClasses)
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
          alert('Абонемент успешно приобретен!')
          router.push(`/subscriptions/${currentUser.student_id}`)
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

    return {
      newSubscription,
      paymentProcessing,
      error,
      calculatePrice,
      buySubscription
    }
  }
}
</script>

<style scoped>
.new-subscription {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.subscription-form {
  background: white;
  padding: 20px;
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
  margin: 20px 0;
  font-size: 20px;
  font-weight: bold;
  text-align: center;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-buy {
  flex: 1;
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

.btn-cancel {
  flex: 1;
  padding: 12px;
  background-color: #f44336;
  color: white;
  text-decoration: none;
  text-align: center;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn-cancel:hover {
  background-color: #d32f2f;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  text-align: center;
}
</style> 