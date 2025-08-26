<template>
  <div class="schedule-admin">
    <h1>Управление расписанием</h1>
    
    <!-- Форма добавления занятия -->
    <div class="add-class-form">
      <h2>Добавить занятие</h2>
      <form @submit.prevent="addClass">
        <div class="form-group">
          <label>Тип танца:</label>
          <input v-model="newClass.type" required>
        </div>
        <div class="form-group">
          <label>Время:</label>
          <input v-model="newClass.time" type="time" required>
        </div>
        <div class="form-group">
          <label>Дата:</label>
          <input v-model="newClass.date" type="date" required>
        </div>
        <div class="form-group">
          <label>Преподаватель:</label>
          <select v-model="newClass.teacher_id" required>
            <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
              {{ teacher.full_name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label>Зал:</label>
          <select v-model="newClass.hall_id" required>
            <option v-for="hall in halls" :key="hall.id" :value="hall.id">
              Зал {{ hall.hall_number }} (вместимость: {{ hall.capacity }})
            </option>
          </select>
        </div>
        <button type="submit" class="btn">Добавить</button>
      </form>
    </div>
    
    <!-- Список занятий -->
    <div class="classes-list">
      <h2>Расписание занятий</h2>
      <table>
        <thead>
          <tr>
            <th>Тип танца</th>
            <th>Дата и время</th>
            <th>Преподаватель</th>
            <th>Зал</th>
            <th>Текущая заполненность</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="class_ in classes" :key="class_.id">
            <td>{{ class_.type }}</td>
            <td>{{ formatDateTime(class_.date, class_.time) }}</td>
            <td>{{ class_.teacher_name }}</td>
            <td>Зал {{ class_.hall_number }}</td>
            <td>{{ class_.current_capacity }}/{{ class_.hall_capacity }}</td>
            <td>
              <button @click="editClass(class_)" class="btn-edit">Редактировать</button>
              <button @click="deleteClass(class_.id)" class="btn-delete">Удалить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Модальное окно редактирования -->
    <div v-if="editingClass" class="modal">
      <div class="modal-content">
        <h2>Редактировать занятие</h2>
        <form @submit.prevent="updateClass">
          <div class="form-group">
            <label>Тип танца:</label>
            <input v-model="editingClass.type" required>
          </div>
          <div class="form-group">
            <label>Время:</label>
            <input v-model="editingClass.time" type="time" required>
          </div>
          <div class="form-group">
            <label>Дата:</label>
            <input v-model="editingClass.date" type="date" required>
          </div>
          <div class="form-group">
            <label>Преподаватель:</label>
            <select v-model="editingClass.teacher_id" required>
              <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
                {{ teacher.full_name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Зал:</label>
            <select v-model="editingClass.hall_id" required>
              <option v-for="hall in halls" :key="hall.id" :value="hall.id">
                Зал {{ hall.hall_number }} (вместимость: {{ hall.capacity }})
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn">Сохранить</button>
            <button @click="editingClass = null" class="btn-cancel">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { classesApi, teachersApi, hallsApi } from '../../api'

export default {
  name: 'ScheduleAdmin',
  data() {
    return {
      classes: [],
      teachers: [],
      halls: [],
      newClass: {
        type: '',
        time: '',
        date: '',
        teacher_id: null,
        hall_id: null
      },
      editingClass: null
    }
  },
  computed: {
    ...mapState(['user'])
  },
  methods: {
    async fetchClasses() {
      try {
        const response = await classesApi.getAll()
        this.classes = response.data
      } catch (error) {
        console.error('Ошибка при загрузке занятий:', error)
      }
    },
    async fetchTeachers() {
      try {
        const response = await teachersApi.getAll()
        this.teachers = response.data
      } catch (error) {
        console.error('Ошибка при загрузке преподавателей:', error)
      }
    },
    async fetchHalls() {
      try {
        const response = await hallsApi.getAll()
        this.halls = response.data
      } catch (error) {
        console.error('Ошибка при загрузке залов:', error)
      }
    },
    async addClass() {
      try {
        await classesApi.create(this.newClass)
        await this.fetchClasses()
        // Очищаем форму
        this.newClass = {
          type: '',
          time: '',
          date: '',
          teacher_id: null,
          hall_id: null
        }
      } catch (error) {
        console.error('Ошибка при добавлении занятия:', error)
      }
    },
    editClass(class_) {
      this.editingClass = { ...class_ }
    },
    async updateClass() {
      try {
        await classesApi.update(this.editingClass.id, this.editingClass)
        await this.fetchClasses()
        this.editingClass = null
      } catch (error) {
        console.error('Ошибка при обновлении занятия:', error)
      }
    },
    async deleteClass(classId) {
      try {
        await classesApi.delete(classId)
        await this.fetchClasses()
      } catch (error) {
        console.error('Ошибка при удалении занятия:', error)
      }
    },
    formatDateTime(date, time) {
      const dateObj = new Date(date)
      return `${dateObj.toLocaleDateString('ru-RU')} ${time}`
    }
  },
  created() {
    this.fetchClasses()
    this.fetchTeachers()
    this.fetchHalls()
  }
}
</script>

<style scoped>
.schedule-admin {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.add-class-form,
.classes-list {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  color: #666;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
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

.btn {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-edit {
  background-color: #2196F3;
  margin-right: 5px;
}

.btn-delete {
  background-color: #f44336;
}

.btn-cancel {
  background-color: #9e9e9e;
  margin-left: 10px;
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
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style> 