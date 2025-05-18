<!-- src/features/plants/components/PlantFilter.vue -->
<template>
    <div class="plant-filters mb-4">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-light py-3">
          <h5 class="mb-0">
            <i class="bi bi-funnel me-2 text-primary"></i>
            Filters and Search
          </h5>
        </div>
        <div class="card-body p-3">
          <!-- Search -->
          <div class="mb-3">
            <label for="searchQuery" class="form-label">Search Plants</label>
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                id="searchQuery" 
                v-model="filters.searchQuery" 
                placeholder="Enter plant name..."
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
              <!-- Category -->
              <div class="col-md-6 mb-3">
                <label for="categoryFilter" class="form-label">Category</label>
                <select 
                  class="form-select" 
                  id="categoryFilter" 
                  v-model="filters.category_id"
                  :disabled="isLoading || !categories.length"
                >
                  <option :value="null">All categories</option>
                  <option 
                    v-for="category in categories" 
                    :key="category.id" 
                    :value="category.id"
                  >
                    {{ category.name }}
                  </option>
                </select>
              </div>
              
              <!-- Climate zone -->
              <div class="col-md-6 mb-3">
                <label for="climateZoneFilter" class="form-label">Climate Zone</label>
                <select 
                  class="form-select" 
                  id="climateZoneFilter" 
                  v-model="filters.climate_zone_id"
                  :disabled="isLoading || !climateZones.length"
                >
                  <option :value="null">All zones</option>
                  <option 
                    v-for="zone in climateZones" 
                    :key="zone.id" 
                    :value="zone.id"
                  >
                    {{ zone.name }}
                  </option>
                </select>
              </div>
            </div>
            
            <!-- Additional filters -->
            <div class="row">
              <!-- Plant type -->
              <div class="col-md-6 mb-3">
                <label for="plantTypeFilter" class="form-label">Plant Type</label>
                <select 
                  class="form-select" 
                  id="plantTypeFilter" 
                  v-model="filters.plant_type"
                >
                  <option :value="null">All types</option>
                  <option value="tree">Tree</option>
                  <option value="shrub">Shrub</option>
                  <option value="flower">Flower</option>
                  <option value="vegetable">Vegetable</option>
                  <option value="fruit">Fruit</option>
                  <option value="herb">Herb</option>
                  <option value="succulent">Succulent</option>
                  <option value="vine">Vine/Climbing</option>
                  <option value="aquatic">Aquatic</option>
                  <option value="fern">Fern</option>
                </select>
              </div>
              
              <!-- Care difficulty -->
              <div class="col-md-6 mb-3">
                <label for="careDifficultyFilter" class="form-label">Care Difficulty</label>
                <select 
                  class="form-select" 
                  id="careDifficultyFilter" 
                  v-model="filters.care_difficulty"
                >
                  <option :value="null">Any</option>
                  <option value="very_easy">Very Easy</option>
                  <option value="easy">Easy</option>
                  <option value="moderate">Moderate</option>
                  <option value="difficult">Difficult</option>
                  <option value="expert">Expert</option>
                </select>
              </div>
            </div>
            
            <!-- Sort options -->
            <div class="row">
              <div class="col-md-6 mb-3">
                <label for="sortBy" class="form-label">Sort by</label>
                <select class="form-select" id="sortBy" v-model="filters.sort_by">
                  <option value="name">Name</option>
                  <option value="created_at">Date Added</option>
                  <option value="popularity">Popularity</option>
                </select>
              </div>
              
              <div class="col-md-6 mb-3">
                <label for="sortDirection" class="form-label">Direction</label>
                <select class="form-select" id="sortDirection" v-model="filters.sort_direction">
                  <option value="asc">Ascending</option>
                  <option value="desc">Descending</option>
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
              {{ showAdvancedFilters ? 'Hide filters' : 'Show advanced filters' }}
            </button>
            
            <div>
              <button 
                class="btn btn-outline-secondary me-2" 
                type="button" 
                @click="resetFilters"
                :disabled="isLoading"
              >
                Reset
              </button>
              <button 
                class="btn btn-primary" 
                type="button" 
                @click="applyFilters"
                :disabled="isLoading"
              >
                <i class="bi bi-funnel me-1"></i>
                Apply
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, reactive, watch, onMounted } from 'vue';
  import { usePlantsStore } from '../store/plantsStore';
  
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
  const categories = ref([]);
  const climateZones = ref([]);
  
  // Default filters (in backend format)
  const defaultFilters = {
    searchQuery: '',
    category_id: null,
    climate_zone_id: null,
    plant_type: null,
    care_difficulty: null,
    sort_by: 'name',
    sort_direction: 'asc'
  };
  
  // Filters state
  const filters = reactive({
    ...defaultFilters,
    ...props.initialFilters
  });
  
  // Debounce timer for search
  let searchTimeout = null;
  
  // Initialize when component is created
  onMounted(async () => {
    await loadFilterData();
  });
  
  // Load data for filters
  async function loadFilterData() {
    try {
      // Load categories if not already in store
      if (!plantsStore.categories.length) {
        await plantsStore.loadCategories();
      }
      categories.value = plantsStore.categories;
      
      // Load climate zones if not already in store
      if (!plantsStore.climateZones.length) {
        await plantsStore.loadClimateZones();
      }
      climateZones.value = plantsStore.climateZones;
    } catch (error) {
      console.error('Error loading filter data:', error);
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
      searchQuery: filters.searchQuery,
      category_id: filters.category_id,
      climate_zone_id: filters.climate_zone_id,
      plant_type: filters.plant_type,
      care_difficulty: filters.care_difficulty,
      sort_by: filters.sort_by,
      sort_direction: filters.sort_direction
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
  .plant-filters .card {
    transition: box-shadow 0.3s ease;
  }
  
  .plant-filters .card:hover {
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
  </style>