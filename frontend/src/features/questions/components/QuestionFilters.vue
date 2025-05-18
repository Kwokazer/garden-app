<!-- frontend/src/features/questions/components/QuestionFilters.vue -->
<template>
    <div class="question-filters mb-4">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-light py-3">
          <h5 class="mb-0">
            <i class="bi bi-funnel me-2 text-primary"></i>
            Поиск и фильтры
          </h5>
        </div>
        <div class="card-body p-3">
          <!-- Search input -->
          <div class="mb-3">
            <label for="searchQuery" class="form-label">Поиск вопросов</label>
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                id="searchQuery" 
                v-model="filters.search" 
                placeholder="Введите ключевые слова для поиска..."
                @input="onSearchDebounced"
              >
              <button class="btn btn-primary" type="button" @click="applyFilters">
                <i class="bi bi-search"></i>
              </button>
            </div>
          </div>
          
          <!-- Collapsible advanced filters -->
          <div class="collapse" :class="{ show: showAdvancedFilters }" id="advancedFilters">
            <div class="row">
              <!-- Plants filter -->
              <div class="col-md-6 mb-3">
                <label for="plantFilter" class="form-label">Растение</label>
                <select 
                  class="form-select" 
                  id="plantFilter" 
                  v-model="filters.plant_id"
                  :disabled="isLoading || !plants.length"
                >
                  <option :value="null">Все растения</option>
                  <option 
                    v-for="plant in plants" 
                    :key="plant.id" 
                    :value="plant.id"
                  >
                    {{ plant.name }}
                  </option>
                </select>
              </div>
              
              <!-- Status filter -->
              <div class="col-md-6 mb-3">
                <label for="statusFilter" class="form-label">Статус</label>
                <select 
                  class="form-select" 
                  id="statusFilter" 
                  v-model="filters.is_solved"
                >
                  <option :value="null">Все статусы</option>
                  <option :value="true">Решенные</option>
                  <option :value="false">Нерешенные</option>
                </select>
              </div>
            </div>
            
            <!-- Sort options -->
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="sortBy" class="form-label">Сортировать по</label>
                <select class="form-select" id="sortBy" v-model="filters.sort_by">
                  <option value="created_at">Дате создания</option>
                  <option value="votes_up">Рейтингу</option>
                  <option value="view_count">Просмотрам</option>
                </select>
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="sortOrder" class="form-label">Направление</label>
                <select class="form-select" id="sortOrder" v-model="filters.sort_order">
                  <option value="desc">По убыванию</option>
                  <option value="asc">По возрастанию</option>
                </select>
              </div>
            </div>
          </div>
          
          <!-- Filter controls -->
          <div class="d-flex justify-content-between">
            <button 
              class="btn btn-link text-decoration-none p-0" 
              type="button" 
              data-bs-toggle="collapse" 
              data-bs-target="#advancedFilters" 
              aria-expanded="false" 
              aria-controls="advancedFilters"
              @click="toggleAdvancedFilters"
            >
              <i class="bi" :class="showAdvancedFilters ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
              {{ showAdvancedFilters ? 'Скрыть фильтры' : 'Расширенный поиск' }}
            </button>
            
            <div>
              <button 
                class="btn btn-outline-secondary me-2" 
                type="button" 
                @click="resetFilters"
                :disabled="isLoading"
              >
                Сбросить
              </button>
              <button 
                class="btn btn-primary" 
                type="button" 
                @click="applyFilters"
                :disabled="isLoading"
              >
                <i class="bi bi-funnel me-1"></i>
                Применить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, watch, onMounted } from 'vue';
  import { usePlantsStore } from '../../plants/store/plantsStore';
  
  const props = defineProps({
    isLoading: {
      type: Boolean,
      default: false
    },
    initialFilters: {
      type: Object,
      default: () => ({})
    }
  });
  
  const emit = defineEmits(['update:filters', 'apply']);
  
  // Component state
  const showAdvancedFilters = ref(false);
  const plantsStore = usePlantsStore();
  const plants = ref([]);
  let searchTimeout = null;
  
  // Default filters
  const defaultFilters = {
    search: '',
    plant_id: null,
    author_id: null,
    is_solved: null,
    sort_by: 'created_at',
    sort_order: 'desc'
  };
  
  // Filters state
  const filters = reactive({
    ...defaultFilters,
    ...props.initialFilters
  });
  
  // Initialize when component is created
  onMounted(async () => {
    await loadPlants();
  });
  
  // Load plants for filter dropdown
  async function loadPlants() {
    try {
      // Load plants if not already in store
      if (!plantsStore.plants.length) {
        await plantsStore.loadPlants(1, 100);
      }
      plants.value = plantsStore.plants;
    } catch (error) {
      console.error('Error loading plants for filters:', error);
    }
  }
  
  // Toggle advanced filters
  function toggleAdvancedFilters() {
    showAdvancedFilters.value = !showAdvancedFilters.value;
  }
  
  // Debounce for search
  function onSearchDebounced() {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    searchTimeout = setTimeout(() => {
      applyFilters();
    }, 500); // Wait 500 ms after typing stops
  }
  
  // Apply filters
  function applyFilters() {
    // Create filters in the format expected by backend
    const backendFilters = {
      search: filters.search,
      plant_id: filters.plant_id,
      author_id: filters.author_id,
      is_solved: filters.is_solved,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order
    };
    
    emit('update:filters', backendFilters);
    emit('apply', backendFilters);
  }
  
  // Reset filters
  function resetFilters() {
    Object.keys(defaultFilters).forEach(key => {
      filters[key] = defaultFilters[key];
    });
    applyFilters();
  }
  
  // Update filters when input props change
  watch(() => props.initialFilters, (newFilters) => {
    Object.keys(newFilters).forEach(key => {
      if (key in filters) {
        filters[key] = newFilters[key];
      }
    });
  }, { deep: true });
  </script>
  
  <style scoped>
  .question-filters .card {
    transition: box-shadow 0.3s ease;
  }
  
  .question-filters .card:hover {
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
  }
  
  .form-select, .form-control {
    border-radius: 0.3rem;
  }
  
  .form-select:focus, .form-control:focus {
    border-color: var(--bs-primary);
    box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
  }
  
  .btn-link {
    color: var(--bs-primary);
  }
  
  .btn-link:hover {
    color: var(--bs-success);
  }
  
  /* Mobile responsiveness */
  @media (max-width: 768px) {
    .d-flex.justify-content-between {
      flex-direction: column;
      gap: 1rem;
    }
    
    .d-flex.justify-content-between > div {
      width: 100%;
      display: flex;
      justify-content: center;
    }
    
    .d-flex.justify-content-between > div .btn {
      flex: 1;
    }
  }
  </style>