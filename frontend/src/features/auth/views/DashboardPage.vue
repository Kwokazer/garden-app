<!-- src/features/auth/views/DashboardPage.vue -->
<template>
    <div class="container mt-4">
      <!-- Приветствие и сводка -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card shadow-sm border-0 rounded-3">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h2 class="fw-bold text-primary mb-1">Добро пожаловать, {{ displayName }}!</h2>
                  <p class="text-muted">{{ greeting }}</p>
                </div>
                <button @click="handleLogout" class="btn btn-outline-danger" :disabled="auth.isLoading">
                  <i class="bi bi-box-arrow-right me-2"></i>
                  <span v-if="auth.isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ auth.isLoading ? 'Выход...' : 'Выйти' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Основное содержимое профиля -->
      <div class="row">
        <!-- Профиль пользователя -->
        <div class="col-lg-4 mb-4">
          <div class="card shadow-sm h-100 border-0 rounded-3">
            <div class="card-header bg-light border-0 py-3">
              <h5 class="mb-0">
                <i class="bi bi-person-circle me-2 text-primary"></i>
                Профиль
              </h5>
            </div>
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <div class="avatar-placeholder mb-3">
                  <i class="bi bi-person display-1 text-muted"></i>
                </div>
                <h5 class="fw-bold mb-1">{{ auth.user?.username || 'Пользователь' }}</h5>
                <p class="text-muted mb-0">{{ auth.user?.email || 'Email не указан' }}</p>
              </div>
              
              <ul class="list-group list-group-flush">
                <li class="list-group-item d-flex justify-content-between px-0">
                  <span class="text-muted">ID:</span>
                  <span class="fw-medium">{{ auth.user?.id || 'Не указан' }}</span>
                </li>
                <li class="list-group-item d-flex justify-content-between px-0">
                  <span class="text-muted">Имя:</span>
                  <span class="fw-medium">{{ auth.user?.first_name || 'Не указано' }}</span>
                </li>
                <li class="list-group-item d-flex justify-content-between px-0">
                  <span class="text-muted">Фамилия:</span>
                  <span class="fw-medium">{{ auth.user?.last_name || 'Не указана' }}</span>
                </li>
                <li class="list-group-item d-flex justify-content-between px-0">
                  <span class="text-muted">Статус:</span>
                  <span class="badge bg-success py-2">Активен</span>
                </li>
                <li class="list-group-item d-flex justify-content-between px-0">
                  <span class="text-muted">Роли:</span>
                  <div>
                    <span v-if="auth.user?.roles?.length" v-for="role in auth.user.roles" :key="role" 
                          class="badge bg-info me-1 py-2">
                      {{ role }}
                    </span>
                    <span v-else class="badge bg-secondary py-2">Пользователь</span>
                  </div>
                </li>
              </ul>
              
              <div class="d-grid gap-2 mt-4">
                <button class="btn btn-outline-primary">
                  <i class="bi bi-pencil-square me-2"></i>
                  Редактировать профиль
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Быстрые действия -->
        <div class="col-lg-8 mb-4">
          <div class="card shadow-sm h-100 border-0 rounded-3">
            <div class="card-header bg-light border-0 py-3">
              <h5 class="mb-0">
                <i class="bi bi-grid-3x3-gap-fill me-2 text-primary"></i>
                Быстрый доступ
              </h5>
            </div>
            <div class="card-body p-4">
              <div class="row g-4">
                <div class="col-md-6">
                  <div class="d-flex align-items-center p-3 rounded border h-100">
                    <div class="flex-shrink-0 me-3">
                      <span class="avatar bg-primary-subtle text-primary rounded-circle p-3">
                        <i class="bi bi-book fs-4"></i>
                      </span>
                    </div>
                    <div>
                      <h6 class="fw-bold mb-1">База растений</h6>
                      <p class="text-muted mb-0 small">Изучите нашу базу данных растений и советы по выращиванию</p>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="d-flex align-items-center p-3 rounded border h-100">
                    <div class="flex-shrink-0 me-3">
                      <span class="avatar bg-success-subtle text-success rounded-circle p-3">
                        <i class="bi bi-chat-dots fs-4"></i>
                      </span>
                    </div>
                    <div>
                      <h6 class="fw-bold mb-1">Вопросы и ответы</h6>
                      <p class="text-muted mb-0 small">Задайте вопрос или найдите ответы от других садоводов</p>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="d-flex align-items-center p-3 rounded border h-100">
                    <div class="flex-shrink-0 me-3">
                      <span class="avatar bg-warning-subtle text-warning rounded-circle p-3">
                        <i class="bi bi-camera fs-4"></i>
                      </span>
                    </div>
                    <div>
                      <h6 class="fw-bold mb-1">Мой сад</h6>
                      <p class="text-muted mb-0 small">Добавьте растения в свой виртуальный сад и отслеживайте их рост</p>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="d-flex align-items-center p-3 rounded border h-100">
                    <div class="flex-shrink-0 me-3">
                      <span class="avatar bg-info-subtle text-info rounded-circle p-3">
                        <i class="bi bi-calendar-event fs-4"></i>
                      </span>
                    </div>
                    <div>
                      <h6 class="fw-bold mb-1">Вебинары</h6>
                      <p class="text-muted mb-0 small">Зарегистрируйтесь на предстоящие вебинары и мастер-классы</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Рекомендации -->
      <div class="row">
        <div class="col-12">
          <div class="card shadow-sm border-0 rounded-3">
            <div class="card-header bg-light border-0 py-3">
              <h5 class="mb-0">
                <i class="bi bi-lightning-charge me-2 text-primary"></i>
                Рекомендации для вас
              </h5>
            </div>
            <div class="card-body p-4">
              <div class="text-center py-4">
                <img src="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/icons/flower1.svg" alt="Plant" width="64" height="64" class="mb-3 text-secondary opacity-50">
                <p class="text-muted">
                  Здесь будут отображаться персонализированные рекомендации на основе ваших предпочтений и активности в приложении.
                </p>
                <button class="btn btn-outline-primary mt-2">
                  <i class="bi bi-sliders me-2"></i>
                  Настроить предпочтения
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  import { useAuthStore } from '../store/authStore.js';
  
  const auth = useAuthStore();
  
  // Вычисляемое имя для отображения
  const displayName = computed(() => {
    if (auth.user?.first_name) {
      return auth.user.first_name;
    }
    return auth.user?.username || 'Пользователь';
  });
  
  // Динамическое приветствие в зависимости от времени суток
  const greeting = computed(() => {
    const hour = new Date().getHours();
    
    if (hour >= 5 && hour < 12) {
      return 'Доброе утро! Что планируете посадить сегодня?';
    } else if (hour >= 12 && hour < 18) {
      return 'Добрый день! Самое время заняться садом.';
    } else if (hour >= 18 && hour < 23) {
      return 'Добрый вечер! Как прошел ваш день в саду?';
    } else {
      return 'Доброй ночи! Отдыхайте, завтра ждет новый день в саду.';
    }
  });
  
  // Обработчик выхода из системы
  async function handleLogout() {
    await auth.logout();
    // Редирект происходит в методе logout хранилища
  }
  </script>
  
  <style scoped>
  .card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08) !important;
  }
  
  .avatar-placeholder {
    width: 100px;
    height: 100px;
    background-color: #f8f9fa;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
  }
  
  .avatar {
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .bg-primary-subtle {
    background-color: rgba(var(--bs-primary-rgb), 0.1) !important;
  }
  
  .bg-success-subtle {
    background-color: rgba(var(--bs-success-rgb), 0.1) !important;
  }
  
  .bg-warning-subtle {
    background-color: rgba(40, 167, 69, 0.1) !important;
  }
  
  .bg-info-subtle {
    background-color: rgba(23, 162, 184, 0.1) !important;
  }
  
  .rounded-circle {
    border-radius: 50% !important;
  }
  
  .list-group-item {
    border-left: 0;
    border-right: 0;
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
  
  .list-group-item:first-child {
    border-top: 0;
  }
  
  .list-group-item:last-child {
    border-bottom: 0;
  }
  </style>