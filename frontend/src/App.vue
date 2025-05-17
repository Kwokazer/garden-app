<template>
  <div class="app-container">
    <header class="mb-4">
      <!-- Здесь может быть навигационная панель, логотип и т.д. -->
    </header>
    
    <main class="container">
      <!-- Router View отображает компонент, соответствующий текущему маршруту -->
      <router-view />
    </main>
    
    <footer class="mt-5 py-3 text-center">
      <!-- Подвал сайта -->
      <p>© {{ currentYear }} Garden - приложение для садоводов</p>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Текущий год для футера
const currentYear = computed(() => new Date().getFullYear())
</script>

<style>
/* Глобальные стили можно добавить здесь */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  color: #333;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}
</style> 