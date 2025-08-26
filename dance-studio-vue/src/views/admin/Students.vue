<template>
  <div class="students">
    <h1>Ученики</h1>
    <div class="students-controls">
      <button class="btn" @click="showAddForm = true">Добавить ученика</button>
      <div class="search-box">
        <input type="text" 
               v-model="searchQuery" 
               placeholder="Поиск учеников..." 
               @input="filterStudents">
      </div>
    </div>

    <!-- Отладочная информация -->
    <div v-if="loading" class="loading">Загрузка данных...</div>
    <div v-else-if="error" class="error">
      {{ error }}
      <button @click="loadStudents" class="btn btn-small">Повторить попытку</button>
    </div>
    <div v-else-if="students.length === 0" class="no-data">
      Нет данных об учениках
      <button @click="loadStudents" class="btn btn-small">Обновить</button>
    </div>


    <!-- Таблица студентов -->
    <div v-if="!loading && !error && students.length > 0" class="students-table">
      <table>
        <thead>
          <tr>
            <th>Имя</th>
            <th>Возраст</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in filteredStudents" :key="student.id">
            <td>{{ student.full_name }}</td>
            <td>{{ calculateAge(student.date_of_birth) }}</td>
            <td>{{ student.email }}</td>
            <td>{{ student.phone }}</td>
            <td class="actions">
              <button class="btn btn-small" @click="editStudent(student)">Редактировать</button>
              <button class="btn btn-small btn-danger" @click="deleteStudent(student.id)">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Форма добавления/редактирования ученика -->
    <div v-if="showAddForm" class="modal">
      <div class="modal-content">
        <h2>{{ editingStudent ? 'Редактировать ученика' : 'Добавить ученика' }}</h2>
        <form @submit.prevent="saveStudent">
          <div class="form-group">
            <label>Имя:</label>
            <input type="text" v-model="studentForm.full_name" required>
          </div>
          <div class="form-group">
            <label>Дата рождения:</label>
            <input type="date" v-model="studentForm.date_of_birth" required>
          </div>
          <div class="form-group">
            <label>Пол:</label>
            <select v-model="studentForm.gender" required>
              <option value="M">Мужской</option>
              <option value="F">Женский</option>
            </select>
          </div>
          <div class="form-group">
            <label>Телефон:</label>
            <input type="tel" v-model="studentForm.phone" required pattern="\+7[0-9]{10}" placeholder="+7888888888">
          </div>
          <div class="form-group">
            <label>Email:</label>
            <input type="email" v-model="studentForm.email" required>
          </div>
          <div class="form-group">
            <label>Пароль:</label>
            <input type="password" v-model="studentForm.password" required>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn">{{ editingStudent ? 'Сохранить' : 'Добавить' }}</button>
            <button type="button" class="btn btn-secondary" @click="closeForm">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import config from '../config'
import { studentsApi } from '../api'

export default {
  name: 'StudentsView',
  setup() {
    const students = ref([])
    const loading = ref(true)
    const error = ref(null)
    const apiUrl = `${config.api.baseURL}/students/`
    const showAddForm = ref(false)
    const editingStudent = ref(null)
    const searchQuery = ref('')
    const debugInfo = ref(false)
    const studentForm = ref({
      full_name: '',
      date_of_birth: '',
      gender: 'M',
      phone: '',
      email: '',
      password: ''
    })
    const filteredStudents = ref([])

    const loadStudents = async () => {
      loading.value = true
      error.value = null
      try {
        console.log('Начало загрузки данных...')
        const response = await studentsApi.getAll()
        console.log('Ответ от сервера:', response)
        students.value = response.data
        filteredStudents.value = students.value
        console.log('Загруженные студенты:', students.value)
      } catch (error) {
        console.error('Ошибка при загрузке учеников:', error)
        console.error('Детали ошибки:', {
          message: error.message,
          response: error.response,
          status: error.response?.status,
          data: error.response?.data
        })
        error.value = `Ошибка при загрузке данных: ${error.message}`
      } finally {
        loading.value = false
      }
    }

    const calculateAge = (dateOfBirth) => {
      const today = new Date()
      const birthDate = new Date(dateOfBirth)
      let age = today.getFullYear() - birthDate.getFullYear()
      const monthDiff = today.getMonth() - birthDate.getMonth()
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--
      }
      
      return age
    }

    const filterStudents = () => {
      if (!searchQuery.value) {
        filteredStudents.value = students.value
        return
      }
      const query = searchQuery.value.toLowerCase()
      filteredStudents.value = students.value.filter(student => 
        student.full_name.toLowerCase().includes(query) ||
        (student.email && student.email.toLowerCase().includes(query))
      )
    }

    const editStudent = (student) => {
      editingStudent.value = student
      studentForm.value = { ...student }
      showAddForm.value = true
    }

    const saveStudent = async () => {
      try {
        // Формируем данные для отправки
        const formData = {
          full_name: studentForm.value.full_name,
          date_of_birth: studentForm.value.date_of_birth,
          gender: studentForm.value.gender,
          phone: studentForm.value.phone,
          email: studentForm.value.email,
          password: studentForm.value.password // Используем password вместо password_hash
        }
        
        console.log('Отправляемые данные:', formData)
        if (editingStudent.value) {
          await studentsApi.update(editingStudent.value.id, formData)
        } else {
          await studentsApi.create(formData)
        }
        await loadStudents()
        closeForm()
      } catch (error) {
        console.error('Ошибка при сохранении ученика:', error)
        console.error('Детали ошибки:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        })
        error.value = `Ошибка при сохранении данных: ${error.message}`
      }
    }

    const deleteStudent = async (id) => {
      if (confirm('Вы уверены, что хотите удалить этого ученика?')) {
        try {
          await studentsApi.delete(id)
          await loadStudents()
        } catch (error) {
          console.error('Ошибка при удалении ученика:', error)
          error.value = `Ошибка при удалении данных: ${error.message}`
        }
      }
    }

    const closeForm = () => {
      showAddForm.value = false
      editingStudent.value = null
      studentForm.value = {
        full_name: '',
        date_of_birth: '',
        gender: 'M',
        phone: '',
        email: '',
        password: ''
      }
    }

    const toggleDebug = () => {
      debugInfo.value = !debugInfo.value
    }

    onMounted(async () => {
      await loadStudents()
    })

    return {
      students,
      loading,
      error,
      apiUrl,
      showAddForm,
      editingStudent,
      searchQuery,
      debugInfo,
      studentForm,
      filteredStudents,
      loadStudents,
      calculateAge,
      filterStudents,
      editStudent,
      saveStudent,
      deleteStudent,
      closeForm,
      toggleDebug
    }
  }
}
</script>

<style scoped>
.students {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.students-controls {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 300px;
  margin-left: 20px;
}

.search-box input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.students-table {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #2c3e50;
}

tr:hover {
  background-color: #f9f9f9;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn-small {
  padding: 5px 10px;
  font-size: 0.9em;
}

.btn-danger {
  background-color: #dc3545;
}

.btn-danger:hover {
  background-color: #c82333;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-secondary {
  background-color: #666;
}

.btn-secondary:hover {
  background-color: #555;
}

.loading {
  padding: 20px;
  color: #666;
}

.error {
  padding: 20px;
  color: #dc3545;
  background-color: #f8d7da;
  border-radius: 4px;
  margin: 20px 0;
}

.no-data {
  padding: 20px;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin: 20px 0;
}

.debug-info {
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  margin: 20px 0;
}

.debug-info h3 {
  margin-top: 0;
  color: #666;
}

.debug-info p {
  margin: 5px 0;
  color: #666;
}
</style> 