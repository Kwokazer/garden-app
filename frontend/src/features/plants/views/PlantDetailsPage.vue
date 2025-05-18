<!-- src/features/plants/views/PlantDetailsPage.vue -->
<template>
    <div class="plant-details-page">
      <!-- Хлебные крошки -->
      <div class="bg-light py-2">
        <div class="container">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb mb-0">
              <li class="breadcrumb-item">
                <router-link to="/">Главная</router-link>
              </li>
              <li class="breadcrumb-item">
                <router-link :to="{ name: 'PlantsList' }">Растения</router-link>
              </li>
              <li class="breadcrumb-item active" aria-current="page">
                {{ plant ? plant.name : 'Загрузка...' }}
              </li>
            </ol>
          </nav>
        </div>
      </div>
      
      <div class="container py-4">
        <!-- Загрузка -->
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
          <p class="mt-3 text-muted">Загрузка информации о растении...</p>
        </div>
        
        <!-- Ошибка -->
        <div v-else-if="error" class="alert alert-danger mt-4">
          <div class="d-flex align-items-center">
            <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
            <div>
              <h5 class="alert-heading">Ошибка при загрузке</h5>
              <p class="mb-2">{{ error }}</p>
              <div class="mt-3">
                <button class="btn btn-outline-danger me-2" @click="loadPlant">
                  Попробовать снова
                </button>
                <router-link :to="{ name: 'PlantsList' }" class="btn btn-outline-secondary">
                  Вернуться к списку
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Растение не найдено -->
        <div v-else-if="!plant" class="text-center py-5">
          <div class="empty-state">
            <i class="bi bi-question-circle display-1 text-muted mb-3"></i>
            <h3>Растение не найдено</h3>
            <p class="text-muted">Запрашиваемое растение не найдено или было удалено.</p>
            <router-link :to="{ name: 'PlantsList' }" class="btn btn-primary mt-3">
              Вернуться к списку растений
            </router-link>
          </div>
        </div>
        
        <!-- Содержимое страницы -->
        <template v-else>
          <!-- Основная информация о растении -->
          <div class="row gx-5">
            <!-- Галерея изображений (левая колонка) -->
            <div class="col-lg-6 mb-4 mb-lg-0">
              <PlantGallery 
                :images="plant.images || []" 
                @image-change="onImageChange"
              />
              
              <!-- Поделиться и избранное -->
              <div class="d-flex justify-content-between mt-3">
                <div class="share-buttons">
                  <button class="btn btn-outline-secondary btn-sm me-2">
                    <i class="bi bi-share me-1"></i> Поделиться
                  </button>
                  <button class="btn btn-outline-secondary btn-sm me-2">
                    <i class="bi bi-printer me-1"></i> Распечатать
                  </button>
                </div>
                <div>
                  <button 
                    class="btn btn-outline-danger btn-sm favorite-btn" 
                    :class="{ 'active': isFavorite }"
                    @click="toggleFavorite"
                  >
                    <i class="bi" :class="isFavorite ? 'bi-heart-fill' : 'bi-heart'"></i>
                    {{ isFavorite ? 'В избранном' : 'В избранное' }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Информация о растении (правая колонка) -->
            <div class="col-lg-6">
              <div class="plant-details">
                <!-- Заголовок и основная информация -->
                <div class="mb-4">
                  <h1 class="plant-title">{{ plant.name }}</h1>
                  <p class="text-muted latin-name">{{ plant.latin_name }}</p>
                  
                  <!-- Категории и теги -->
                  <div class="d-flex flex-wrap align-items-center mt-3">
                    <span 
                      v-if="plant.category" 
                      class="badge bg-success me-2 mb-2 px-3 py-2"
                    >
                      {{ plant.category.name }}
                    </span>
                    
                    <template v-if="plant.tags && plant.tags.length > 0">
                      <span 
                        v-for="tag in plant.tags" 
                        :key="tag.id" 
                        class="badge bg-light text-dark me-2 mb-2 px-3 py-2"
                      >
                        {{ tag.name }}
                      </span>
                    </template>
                  </div>
                </div>
                
                <!-- Краткое описание -->
                <div class="card bg-light mb-4 border-0">
                  <div class="card-body">
                    <p v-if="plant.description" class="m-0">{{ plant.description }}</p>
                    <p v-else class="text-muted m-0">Описание отсутствует</p>
                  </div>
                </div>
                
                <!-- Основные характеристики -->
                <div class="plant-characteristics mb-4">
                  <h5 class="section-title">
                    <i class="bi bi-info-circle me-2"></i>
                    Основные характеристики
                  </h5>
                  
                  <div class="row">
                    <!-- Тип растения -->
                    <div class="col-md-6 mb-3">
                      <div class="characteristic-item">
                        <span class="characteristic-label">Тип растения:</span>
                        <span class="characteristic-value">{{ getPlantTypeLabel(plant.plant_type) }}</span>
                      </div>
                    </div>
                    
                    <!-- Жизненный цикл -->
                    <div class="col-md-6 mb-3">
                      <div class="characteristic-item">
                        <span class="characteristic-label">Жизненный цикл:</span>
                        <span class="characteristic-value">{{ getLifeCycleLabel(plant.life_cycle) }}</span>
                      </div>
                    </div>
                    
                    <!-- Высота растения -->
                    <div class="col-md-6 mb-3">
                      <div class="characteristic-item">
                        <span class="characteristic-label">Высота:</span>
                        <span class="characteristic-value">
                          {{ plant.height_min && plant.height_max ? `${plant.height_min}-${plant.height_max} см` : 'Не указано' }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- Скорость роста -->
                    <div class="col-md-6 mb-3">
                      <div class="characteristic-item">
                        <span class="characteristic-label">Скорость роста:</span>
                        <span class="characteristic-value">{{ getGrowthRateLabel(plant.growth_rate) }}</span>
                      </div>
                    </div>
                    
                    <!-- Период цветения -->
                    <div class="col-md-6 mb-3">
                      <div class="characteristic-item">
                        <span class="characteristic-label">Период цветения:</span>
                        <span class="characteristic-value">
                          {{ plant.flowering_period ? plant.flowering_period : 'Не указано' }}
                        </span>
                      </div>
                    </div>
                    
                    <!-- Токсичность -->
                    <div class="col-md-6 mb-3">
                      <div class="characteristic-item">
                        <span class="characteristic-label">Токсичность:</span>
                        <span 
                          class="characteristic-value" 
                          :class="{ 'text-danger': plant.is_toxic, 'text-success': !plant.is_toxic }"
                        >
                          <i 
                            class="bi" 
                            :class="plant.is_toxic ? 'bi-exclamation-circle' : 'bi-check-circle'"
                            :title="plant.is_toxic ? 'Токсично' : 'Не токсично'"
                          ></i>
                          {{ plant.is_toxic ? 'Токсично' : 'Не токсично' }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Климатические зоны -->
                  <div class="mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Климатические зоны:</span>
                      <div class="mt-2">
                        <div v-if="plant.climate_zones && plant.climate_zones.length > 0" class="d-flex flex-wrap">
                          <span 
                            v-for="zone in plant.climate_zones" 
                            :key="zone.id" 
                            class="badge bg-info me-2 mb-2 px-3 py-2"
                          >
                            {{ zone.name }}
                          </span>
                        </div>
                        <span v-else class="text-muted">Не указаны</span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Примечания (если есть) -->
                  <div v-if="plant.notes" class="mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Примечания:</span>
                      <p class="mt-2 mb-0">{{ plant.notes }}</p>
                    </div>
                  </div>
                </div>
                
                <!-- Похожие растения -->
                <div v-if="plant.similar_plants && plant.similar_plants.length > 0" class="similar-plants mb-4">
                  <h5 class="section-title">
                    <i class="bi bi-shuffle me-2"></i>
                    Похожие растения
                  </h5>
                  
                  <div class="row g-3">
                    <div 
                      v-for="similarPlant in plant.similar_plants.slice(0, 3)" 
                      :key="similarPlant.id" 
                      class="col-md-4"
                    >
                      <router-link 
                        :to="{ name: 'PlantDetails', params: { id: similarPlant.id } }" 
                        class="similar-plant-card"
                      >
                        <div class="card h-100 border-0 shadow-sm">
                          <div class="similar-img-container">
                            <img 
                              v-if="similarPlant.image_url" 
                              :src="similarPlant.image_url" 
                              :alt="similarPlant.name"
                              class="similar-img"
                              @error="handleImageError"
                            >
                            <div v-else class="img-placeholder d-flex align-items-center justify-content-center h-100 bg-light">
                              <i class="bi bi-flower1 text-muted"></i>
                            </div>
                          </div>
                          <div class="card-body">
                            <h6 class="card-title mb-0">{{ similarPlant.name }}</h6>
                          </div>
                        </div>
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Вкладки с информацией -->
          <div class="plant-tabs mt-5">
            <ul class="nav nav-tabs" id="plantTabs" role="tablist">
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link active" 
                  id="care-tab" 
                  data-bs-toggle="tab" 
                  data-bs-target="#care-tab-pane" 
                  type="button" 
                  role="tab" 
                  aria-controls="care-tab-pane" 
                  aria-selected="true"
                >
                  <i class="bi bi-water me-2"></i>
                  Уход
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  id="growing-tab" 
                  data-bs-toggle="tab" 
                  data-bs-target="#growing-tab-pane" 
                  type="button" 
                  role="tab" 
                  aria-controls="growing-tab-pane" 
                  aria-selected="false"
                >
                  <i class="bi bi-flower1 me-2"></i>
                  Выращивание
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button 
                  class="nav-link" 
                  id="qa-tab" 
                  data-bs-toggle="tab" 
                  data-bs-target="#qa-tab-pane" 
                  type="button" 
                  role="tab" 
                  aria-controls="qa-tab-pane" 
                  aria-selected="false"
                >
                  <i class="bi bi-question-circle me-2"></i>
                  Вопросы и ответы
                </button>
              </li>
            </ul>
            
            <div class="tab-content" id="plantTabsContent">
              <!-- Вкладка ухода -->
              <div 
                class="tab-pane fade show active" 
                id="care-tab-pane" 
                role="tabpanel" 
                aria-labelledby="care-tab"
                tabindex="0"
              >
                <div class="py-4">
                  <PlantCareInfo :plant="plant" />
                </div>
              </div>
              
              <!-- Вкладка выращивания -->
              <div 
                class="tab-pane fade" 
                id="growing-tab-pane" 
                role="tabpanel" 
                aria-labelledby="growing-tab"
                tabindex="0"
              >
                <div class="py-4">
                  <div class="card shadow-sm border-0 rounded-3">
                    <div class="card-header bg-light py-3">
                      <h5 class="mb-0">
                        <i class="bi bi-flower1 me-2 text-primary"></i>
                        Выращивание и размножение
                      </h5>
                    </div>
                    <div class="card-body p-4">
                      <div v-if="plant.propagation_methods && plant.propagation_methods.length > 0">
                        <h6 class="fw-bold mb-3">Методы размножения</h6>
                        <div class="row">
                          <div 
                            v-for="(method, index) in plant.propagation_methods" 
                            :key="index" 
                            class="col-md-6 mb-4"
                          >
                            <div class="propagation-method">
                              <h6 class="method-title mb-2">{{ method.name }}</h6>
                              <p class="method-description">{{ method.description }}</p>
                              <div v-if="method.difficulty" class="method-difficulty">
                                <small class="text-muted me-2">Сложность:</small>
                                <div class="difficulty-stars">
                                  <i 
                                    v-for="i in 5" 
                                    :key="i" 
                                    class="bi" 
                                    :class="i <= method.difficulty ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                                  ></i>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div v-else class="text-center py-4">
                        <i class="bi bi-exclamation-circle text-muted display-4"></i>
                        <p class="mt-3">Информация о методах размножения отсутствует</p>
                      </div>
                      
                      <!-- Инструкции по посадке -->
                      <div class="planting-instructions mt-4" v-if="plant.planting_instructions">
                        <h6 class="fw-bold mb-3">Инструкции по посадке</h6>
                        <div class="planting-content">{{ plant.planting_instructions }}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Вкладка вопросов и ответов -->
              <div 
                class="tab-pane fade" 
                id="qa-tab-pane" 
                role="tabpanel" 
                aria-labelledby="qa-tab"
                tabindex="0"
              >
                <div class="py-4">
                  <div class="card shadow-sm border-0 rounded-3">
                    <div class="card-header bg-light py-3">
                      <h5 class="mb-0">
                        <i class="bi bi-question-circle me-2 text-primary"></i>
                        Вопросы и ответы
                      </h5>
                    </div>
                    <div class="card-body p-4">
                      <!-- Блок со статистикой и кнопкой "Задать вопрос" -->
                      <div class="d-flex justify-content-between align-items-center mb-4">
                        <div class="qa-stats">
                          <span class="text-muted">
                            <strong>0</strong> вопросов | <strong>0</strong> ответов
                          </span>
                        </div>
                        <button class="btn btn-primary">
                          <i class="bi bi-plus-circle me-2"></i>
                          Задать вопрос
                        </button>
                      </div>
                      
                      <!-- Заглушка для вопросов и ответов -->
                      <div class="text-center py-5">
                        <i class="bi bi-chat-dots display-4 text-muted mb-3"></i>
                        <h5>Пока нет вопросов</h5>
                        <p class="text-muted mb-4">Будьте первым, кто задаст вопрос о {{ plant.name }}</p>
                        <button class="btn btn-outline-primary">
                          Задать первый вопрос
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { usePlantsStore } from '../store/plantsStore';
  import { useAuthStore } from '../../auth/store/authStore';
  import PlantGallery from '../components/PlantGallery.vue';
  import PlantCareInfo from '../components/PlantCareInfo.vue';
  
  const route = useRoute();
  const router = useRouter();
  const plantsStore = usePlantsStore();
  const authStore = useAuthStore();
  
  // Состояние компонента
  const currentImageIndex = ref(0);
  const isFavorite = ref(false);
  
  // Вычисляемые свойства
  const plant = computed(() => plantsStore.currentPlant);
  const isLoading = computed(() => plantsStore.isLoading);
  const error = computed(() => plantsStore.error);
  
  // Инициализация при создании компонента
  onMounted(async () => {
    const plantId = route.params.id;
    if (!plantId) {
      router.push({ name: 'PlantsList' });
      return;
    }
    
    // Загружаем растение
    await loadPlant();
    
    // Проверяем, находится ли растение в избранном у пользователя
    if (authStore.isLoggedIn) {
      checkIfFavorite();
    }
  });
  
  // Загрузка данных о растении
  async function loadPlant() {
    const plantId = route.params.id;
    await plantsStore.loadPlantById(plantId);
    
    // Если произошла ошибка, показываем сообщение
    if (plantsStore.error) {
      console.error('Ошибка при загрузке растения:', plantsStore.error);
    }
  }
  
  // Проверка, находится ли растение в избранном
  function checkIfFavorite() {
    // Здесь должна быть логика проверки избранного через API
    // Например:
    // const favorites = await userService.getFavorites();
    // isFavorite.value = favorites.some(fav => fav.id === plant.value.id);
    
    // Заглушка для демонстрации
    const localFavorites = JSON.parse(localStorage.getItem('favoritePlants') || '[]');
    isFavorite.value = localFavorites.includes(plant.value?.id);
  }
  
  // Добавление/удаление из избранного
  function toggleFavorite() {
    if (!authStore.isLoggedIn) {
      // Если пользователь не авторизован, перенаправляем на страницу входа
      router.push({ 
        name: 'Login', 
        query: { 
          redirect: router.currentRoute.value.fullPath 
        } 
      });
      return;
    }
    
    // Здесь должна быть логика добавления/удаления из избранного через API
    // Например:
    // if (isFavorite.value) {
    //   await userService.removeFromFavorites(plant.value.id);
    // } else {
    //   await userService.addToFavorites(plant.value.id);
    // }
    
    // Заглушка для демонстрации
    const localFavorites = JSON.parse(localStorage.getItem('favoritePlants') || '[]');
    if (isFavorite.value) {
      const newFavorites = localFavorites.filter(id => id !== plant.value.id);
      localStorage.setItem('favoritePlants', JSON.stringify(newFavorites));
    } else {
      localFavorites.push(plant.value.id);
      localStorage.setItem('favoritePlants', JSON.stringify(localFavorites));
    }
    
    isFavorite.value = !isFavorite.value;
  }
  
  // Обработка смены изображения в галерее
  function onImageChange(index) {
    currentImageIndex.value = index;
  }
  
  // Функции для получения текстовых меток
  function getPlantTypeLabel(type) {
    if (!type) return 'Не указано';
    
    const typeLabels = {
      'tree': 'Дерево',
      'shrub': 'Кустарник',
      'herb': 'Травянистое',
      'succulent': 'Суккулент',
      'cactus': 'Кактус',
      'vine': 'Лиана',
      'fern': 'Папоротник',
      'aquatic': 'Водное',
      'bulb': 'Луковичное'
    };
    
    return typeLabels[type] || type;
  }
  
  function getLifeCycleLabel(cycle) {
    if (!cycle) return 'Не указано';
    
    const cycleLabels = {
      'annual': 'Однолетнее',
      'biennial': 'Двулетнее',
      'perennial': 'Многолетнее'
    };
    
    return cycleLabels[cycle] || cycle;
  }
  
  function getGrowthRateLabel(rate) {
    if (!rate) return 'Средний';
    
    const rateLabels = {
      'fast': 'Быстрый',
      'moderate': 'Средний',
      'slow': 'Медленный'
    };
    
    return rateLabels[rate] || rate;
  }
  
  // Обработка ошибок загрузки изображений
  function handleImageError(event) {
    event.target.src = '/placeholder-plant.jpg'; // Заменяем на placeholder
    event.target.classList.add('img-error');
  }
  
  // Отслеживаем изменение маршрута для обновления данных при переходе между растениями
  watch(() => route.params.id, async (newId) => {
    if (newId && newId !== String(plant.value?.id)) {
      await loadPlant();
      
      if (authStore.isLoggedIn) {
        checkIfFavorite();
      }
      
      // Прокручиваем страницу вверх
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
  </script>
  
  <style scoped>
  .plant-details-page {
    padding-bottom: 3rem;
  }
  
  .breadcrumb {
    font-size: 0.9rem;
  }
  
  .breadcrumb-item a {
    color: var(--bs-primary);
    text-decoration: none;
  }
  
  .breadcrumb-item.active {
    color: #6c757d;
  }
  
  .plant-title {
    font-size: 2.25rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
  }
  
  .latin-name {
    font-style: italic;
    font-size: 1.15rem;
  }
  
  .section-title {
    margin-bottom: 1.25rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #dee2e6;
    font-weight: 600;
    color: #333;
  }
  
  .characteristic-item {
    margin-bottom: 0.5rem;
  }
  
  .characteristic-label {
    font-weight: 500;
    color: #6c757d;
    display: block;
    margin-bottom: 0.25rem;
  }
  
  .characteristic-value {
    font-weight: 400;
  }
  
  .similar-img-container {
    height: 120px;
    overflow: hidden;
    border-top-left-radius: 0.3rem;
    border-top-right-radius: 0.3rem;
  }
  
  .similar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .similar-plant-card {
    text-decoration: none;
    color: inherit;
    display: block;
    transition: transform 0.3s ease;
  }
  
  .similar-plant-card:hover {
    transform: translateY(-5px);
  }
  
  .similar-plant-card:hover .card {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
  }
  
  .plant-tabs {
    margin-top: 3rem;
  }
  
  .nav-tabs {
    border-bottom: 1px solid #dee2e6;
  }
  
  .nav-tabs .nav-link {
    margin-bottom: -1px;
    border: 1px solid transparent;
    border-top-left-radius: 0.3rem;
    border-top-right-radius: 0.3rem;
    padding: 0.75rem 1.25rem;
    font-weight: 500;
    color: #6c757d;
  }
  
  .nav-tabs .nav-link.active {
    color: var(--bs-primary);
    background-color: #fff;
    border-color: #dee2e6 #dee2e6 #fff;
  }
  
  .nav-tabs .nav-link:hover:not(.active) {
    border-color: #e9ecef #e9ecef #dee2e6;
    color: var(--bs-primary);
  }
  
  .tab-content {
    background-color: #fff;
    border-left: 1px solid #dee2e6;
    border-right: 1px solid #dee2e6;
    border-bottom: 1px solid #dee2e6;
    border-bottom-left-radius: 0.3rem;
    border-bottom-right-radius: 0.3rem;
  }
  
  .favorite-btn {
    transition: all 0.3s ease;
  }
  
  .favorite-btn.active {
    background-color: #dc3545;
    color: white;
    border-color: #dc3545;
  }
  
  .img-error {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
  }
  
  .propagation-method {
    padding: 1.25rem;
    background-color: #f8f9fa;
    border-radius: 8px;
    height: 100%;
  }
  
  .method-title {
    color: var(--bs-primary);
  }
  
  .method-description {
    color: #6c757d;
    font-size: 0.95rem;
  }
  
  .difficulty-stars {
    display: inline-block;
  }
  
  /* Анимации */
  .tab-pane {
    animation: fadeIn 0.5s ease;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Адаптивность для мобильных устройств */
  @media (max-width: 768px) {
    .plant-title {
      font-size: 1.75rem;
    }
    
    .latin-name {
      font-size: 1rem;
    }
    
    .nav-tabs .nav-link {
      padding: 0.5rem 0.75rem;
      font-size: 0.9rem;
    }
  }
  </style>