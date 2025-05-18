<!-- src/features/plants/views/PlantsListPage.vue -->
<template>
    <div class="plants-list-page">
      <!-- Заголовок страницы -->
      <div class="container py-4">
        <div class="row align-items-center mb-4">
          <div class="col-md-8">
            <h1 class="mb-1">База знаний растений</h1>
            <p class="text-muted mb-0">Изучите нашу коллекцию растений и получите полезную информацию о выращивании</p>
          </div>
          <div class="col-md-4 text-md-end mt-3 mt-md-0">
            <div class="d-flex justify-content-md-end">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Быстрый поиск..." 
                  v-model="quickSearch"
                  @input="onQuickSearchDebounced"
                  @keyup.enter="applyQuickSearch"
                >
                <button 
                  class="btn btn-primary" 
                  type="button" 
                  @click="applyQuickSearch"
                  :disabled="isLoading"
                >
                  <i class="bi bi-search"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Фильтры -->
        <PlantFilters 
          :isLoading="isLoading" 
          :initialFilters="plantsStore.activeFilters" 
          @apply="applyFilters"
        />
      </div>
      
      <!-- Результаты -->
      <div class="container pb-5">
        <!-- Индикатор загрузки -->
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
          <p class="mt-3 text-muted">Загрузка растений...</p>
        </div>
        
        <!-- Сообщение об ошибке -->
        <div v-else-if="error" class="alert alert-danger mt-4">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          {{ error }}
          <button 
            class="btn btn-outline-danger btn-sm ms-3" 
            @click="loadPlants(1, plantsStore.pagination.itemsPerPage, true)"
          >
            Попробовать снова
          </button>
        </div>
        
        <!-- Пустой результат -->
        <div v-else-if="plants.length === 0" class="text-center py-5">
          <div class="empty-state">
            <i class="bi bi-flower1 display-1 text-muted mb-3"></i>
            <h4>Растения не найдены</h4>
            <p class="text-muted">Попробуйте изменить параметры поиска или фильтрации.</p>
            <button class="btn btn-primary mt-3" @click="clearFilters">Сбросить все фильтры</button>
          </div>
        </div>
        
        <!-- Список растений -->
        <template v-else>
          <!-- Информация о результатах -->
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <p class="mb-0">
                <span class="fw-medium">{{ plantsStore.pagination.totalItems }}</span>
                {{ getResultText(plantsStore.pagination.totalItems) }}
              </p>
            </div>
            
            <!-- Выбор отображения -->
            <div class="btn-group" role="group" aria-label="Переключение отображения">
              <button 
                type="button" 
                class="btn" 
                :class="{ 'btn-primary': viewMode === 'grid', 'btn-outline-primary': viewMode !== 'grid' }"
                @click="setViewMode('grid')"
              >
                <i class="bi bi-grid-3x3-gap"></i>
              </button>
              <button 
                type="button" 
                class="btn" 
                :class="{ 'btn-primary': viewMode === 'list', 'btn-outline-primary': viewMode !== 'list' }"
                @click="setViewMode('list')"
              >
                <i class="bi bi-list-ul"></i>
              </button>
            </div>
          </div>
          
          <!-- Сетка растений -->
          <div v-if="viewMode === 'grid'" class="row g-4">
            <div v-for="plant in plants" :key="plant.id" class="col-md-6 col-lg-4">
              <PlantCard :plant="plant" />
            </div>
          </div>
          
          <!-- Список растений -->
          <div v-else-if="viewMode === 'list'" class="plants-list">
            <div v-for="plant in plants" :key="plant.id" class="card mb-3 border-0 shadow-sm">
              <div class="row g-0">
                <div class="col-md-3">
                  <div class="plant-list-img position-relative h-100">
                    <img 
                      v-if="plant.images && plant.images.length > 0" 
                      :src="plant.images[0].url" 
                      :alt="plant.name"
                      class="list-img"
                      @error="handleImageError"
                    >
                    <div v-else class="img-placeholder d-flex align-items-center justify-content-center h-100 bg-light">
                      <i class="bi bi-flower1 display-4 text-muted"></i>
                    </div>
                    <span v-if="plant.category" class="position-absolute top-0 end-0 m-2 badge bg-success">
                      {{ plant.category.name }}
                    </span>
                  </div>
                </div>
                <div class="col-md-9">
                  <div class="card-body h-100 d-flex flex-column">
                    <div class="d-flex justify-content-between align-items-start">
                      <div>
                        <h5 class="card-title fw-bold text-primary mb-1">{{ plant.name }}</h5>
                        <p class="text-muted small mb-2">{{ plant.latin_name }}</p>
                      </div>
                      <!-- Бейджи для характеристик -->
                      <div>
                        <span class="badge bg-light text-dark me-1">
                          <i class="bi bi-droplet me-1"></i>
                          {{ getWateringLabel(plant.watering_frequency) }}
                        </span>
                        <span class="badge bg-light text-dark">
                          <i class="bi bi-brightness-high me-1"></i>
                          {{ getLightLabel(plant.light_level) }}
                        </span>
                      </div>
                    </div>
                    
                    <p class="card-text mb-3">{{ truncateDescription(plant.description, 200) }}</p>
                    
                    <!-- Климатические зоны -->
                    <div v-if="plant.climate_zones && plant.climate_zones.length > 0" class="mb-3 small">
                      <span class="text-muted me-2">Климатические зоны:</span>
                      <span v-for="(zone, index) in plant.climate_zones" :key="zone.id" class="badge bg-info text-white me-1">
                        {{ zone.name }}
                      </span>
                    </div>
                    
                    <router-link :to="{ name: 'PlantDetails', params: { id: plant.id } }" class="btn btn-outline-primary mt-auto">
                      Подробнее
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Пагинация -->
          <div class="mt-5">
            <PlantPagination 
              :currentPage="plantsStore.pagination.currentPage" 
              :totalPages="plantsStore.pagination.totalPages"
              :totalItems="plantsStore.pagination.totalItems"
              :perPage="plantsStore.pagination.itemsPerPage"
              :isLoading="isLoading"
              @page-change="onPageChange"
            />
          </div>
        </template>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted, watch } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { usePlantsStore } from '../store/plantsStore';
  import PlantFilters from '../components/PlantFilters.vue';
  import PlantCard from '../components/PlantCard.vue';
  import PlantPagination from '../components/PlantPagination.vue';
  
  const route = useRoute();
  const router = useRouter();
  const plantsStore = usePlantsStore();
  
  // Состояние компонента
  const viewMode = ref(localStorage.getItem('plantsViewMode') || 'grid'); // grid или list
  const quickSearch = ref('');
  let quickSearchTimeout = null;
  
  // Вычисляемые свойства
  const plants = computed(() => plantsStore.plants);
  const isLoading = computed(() => plantsStore.isLoading);
  const error = computed(() => plantsStore.error);
  
  // Инициализация при создании компонента
  onMounted(async () => {
    // Загружаем категории и климатические зоны, если их еще нет
    if (!plantsStore.categories.length) {
      await plantsStore.loadCategories();
    }
    
    if (!plantsStore.climateZones.length) {
      await plantsStore.loadClimateZones();
    }
    
    // Применяем параметры из URL (если есть)
    const page = parseInt(route.query.page) || 1;
    
    // Устанавливаем фильтры из URL
    if (route.query.search) {
      quickSearch.value = route.query.search;
      plantsStore.activeFilters.searchQuery = route.query.search;
    }
    
    if (route.query.category) {
      plantsStore.activeFilters.category = route.query.category;
    }
    
    if (route.query.climateZone) {
      plantsStore.activeFilters.climateZone = route.query.climateZone;
    }
    
    if (route.query.sortBy) {
      plantsStore.activeFilters.sortBy = route.query.sortBy;
    }
    
    if (route.query.sortDirection) {
      plantsStore.activeFilters.sortDirection = route.query.sortDirection;
    }
    
    // Загружаем растения
    await loadPlants(page, plantsStore.pagination.itemsPerPage);
  });
  
  // Устанавливаем режим отображения
  function setViewMode(mode) {
    viewMode.value = mode;
    localStorage.setItem('plantsViewMode', mode); // Сохраняем в localStorage
  }
  
  // Загружаем растения
  async function loadPlants(page = 1, limit = 10, resetFilters = false) {
    await plantsStore.loadPlants(page, limit, resetFilters);
    
    // Обновляем URL с параметрами
    updateUrlParams({
      page: page > 1 ? page : undefined,
      search: plantsStore.activeFilters.searchQuery || undefined,
      category: plantsStore.activeFilters.category || undefined,
      climateZone: plantsStore.activeFilters.climateZone || undefined,
      sortBy: plantsStore.activeFilters.sortBy !== 'name' ? plantsStore.activeFilters.sortBy : undefined,
      sortDirection: plantsStore.activeFilters.sortDirection !== 'asc' ? plantsStore.activeFilters.sortDirection : undefined
    });
  }
  
  // Обновление URL-параметров
  function updateUrlParams(params) {
    const query = { ...route.query };
    
    // Обновляем или удаляем параметры
    Object.keys(params).forEach(key => {
      if (params[key] === undefined) {
        delete query[key];
      } else {
        query[key] = params[key];
      }
    });
    
    // Обновляем URL без перезагрузки страницы
    router.replace({ query });
  }
  
  // Обработка смены страницы пагинации
  function onPageChange(page) {
    loadPlants(page, plantsStore.pagination.itemsPerPage);
    // Прокручиваем страницу вверх
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Обработка применения фильтров
  function applyFilters(filters) {
    // Устанавливаем быстрый поиск, если он изменился
    if (filters.searchQuery !== quickSearch.value) {
      quickSearch.value = filters.searchQuery;
    }
    
    // Обновляем фильтры и загружаем растения
    plantsStore.updateFilters(filters);
  }
  
  // Обработка быстрого поиска (с debounce)
  function onQuickSearchDebounced() {
    if (quickSearchTimeout) {
      clearTimeout(quickSearchTimeout);
    }
    
    quickSearchTimeout = setTimeout(() => {
      applyQuickSearch();
    }, 500); // Ждем 500 мс после окончания ввода
  }
  
  // Применяем быстрый поиск
  function applyQuickSearch() {
    plantsStore.updateFilters({ searchQuery: quickSearch.value });
  }
  
  // Очистка всех фильтров
  function clearFilters() {
    quickSearch.value = '';
    plantsStore.clearFilters();
  }
  
  // Функция для склонения слова "растение" в зависимости от количества
  function getResultText(count) {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
      return 'растений';
    }
    
    if (lastDigit === 1) {
      return 'растение';
    }
    
    if (lastDigit >= 2 && lastDigit <= 4) {
      return 'растения';
    }
    
    return 'растений';
  }
  
  // Обрезаем описание до указанной длины
  function truncateDescription(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    
    return text.substring(0, maxLength) + '...';
  }
  
  // Получаем текстовую метку для режима полива
  function getWateringLabel(frequency) {
    if (!frequency) return 'Не указано';
    
    const wateringLabels = {
      'daily': 'Ежедневно',
      'twice_a_week': '2 раза в неделю',
      'weekly': 'Еженедельно',
      'bi_weekly': 'Раз в 2 недели',
      'monthly': 'Ежемесячно',
      'rarely': 'Редко'
    };
    
    return wateringLabels[frequency] || frequency;
  }
  
  // Получаем текстовую метку для уровня освещения
  function getLightLabel(level) {
    if (!level) return 'Не указано';
    
    const lightLabels = {
      'full_sun': 'Прямой свет',
      'partial_sun': 'Полутень',
      'shade': 'Тень',
      'low_light': 'Малое освещение'
    };
    
    return lightLabels[level] || level;
  }
  
  // Обработка ошибок загрузки изображения
  function handleImageError(event) {
    event.target.src = '/placeholder-plant.jpg'; // Заменяем на placeholder
    event.target.classList.add('img-error');
  }
  
  // Отслеживаем изменение маршрута для обновления данных
  watch(() => route.query, (newQuery) => {
    // Если изменилась страница, загружаем новые данные
    const page = parseInt(newQuery.page) || 1;
    if (page !== plantsStore.pagination.currentPage) {
      loadPlants(page, plantsStore.pagination.itemsPerPage);
    }
  }, { deep: true });
  </script>
  
  <style scoped>
  .plants-list-page {
    padding-bottom: 2rem;
  }
  
  .list-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-top-left-radius: 0.3rem;
    border-bottom-left-radius: 0.3rem;
  }
  
  .plant-list-img {
    border-top-left-radius: 0.3rem;
    border-bottom-left-radius: 0.3rem;
    overflow: hidden;
  }
  
  .img-placeholder {
    min-height: 220px;
  }
  
  @media (max-width: 767.98px) {
    .plant-list-img {
      height: 200px;
      border-top-left-radius: 0.3rem;
      border-top-right-radius: 0.3rem;
      border-bottom-left-radius: 0;
    }
    
    .list-img {
      border-radius: 0;
      border-top-left-radius: 0.3rem;
      border-top-right-radius: 0.3rem;
    }
  }
  
  .img-error {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
  }
  
  .empty-state {
    padding: 3rem 0;
  }
  
  /* Анимации при загрузке */
  .plants-list-page .row, .plants-list {
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
  </style>