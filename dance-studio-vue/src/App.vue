<template>
  <div id="app">
    <nav>
      <router-link to="/">Главная</router-link>
     
   
      <template v-if="isAdmin">
       | <router-link to="/admin/schedule">Управление расписанием</router-link>  
       | <router-link to="/admin">Админ-панель</router-link> 
      </template>
      <template v-if="isTeacher">
       | <router-link to="/teacher">Личный кабинет</router-link>
      </template>
      <template v-if="isStudent">
     
       | <router-link to="/student">Личный кабинет</router-link>
      </template>
      <template v-if="isAuthenticated">
       | <router-link to="/schedule">Расписание</router-link> 
       | <a href="#" @click.prevent="handleLogout" class="logout-link">Выход</a>
      </template>
    </nav>
    <router-view/>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex'

export default {
  name: 'App',
  computed: {
    ...mapGetters(['isAdmin', 'isTeacher', 'isStudent', 'isAuthenticated']),
    ...mapState(['user'])
  },
  methods: {
    handleLogout() {
      this.$store.dispatch('logout')
      this.$router.replace('/login')
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.logout-link {
  color: #dc3545 !important;
  cursor: pointer;
}

.logout-link:hover {
  text-decoration: underline !important;
}
</style>
