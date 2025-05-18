<!-- src/features/plants/views/PlantsListPage.vue -->
<template>
    <div class="plants-list-page">
      <!-- Page header -->
      <div class="container py-4">
        <div class="row align-items-center mb-4">
          <div class="col-md-8">
            <h1 class="mb-1">Plants Knowledge Base</h1>
            <p class="text-muted mb-0">Explore our plant collection and get useful growing information</p>
          </div>
          <div class="col-md-4 text-md-end mt-3 mt-md-0">
            <div class="d-flex justify-content-md-end">
              <div class="input-group">
                <input 
                  type="text" 
                  class="form-control" 
                  placeholder="Quick search..." 
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
        
        <!-- Filters -->
        <PlantFilters 
          :isLoading="isLoading" 
          :initialFilters="plantsStore.activeFilters" 
          @apply="applyFilters"
        />
      </div>
      
      <!-- Results -->
      <div class="container pb-5">
        <!-- Loading indicator -->
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-muted">Loading plants...</p>
        </div>
        
        <!-- Error message -->
        <div v-else-if="error" class="alert alert-danger mt-4">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          {{ error }}
          <button 
            class="btn btn-outline-danger btn-sm ms-3" 
            @click="loadPlants(1, plantsStore.pagination.per_page, true)"
          >
            Try again
          </button>
        </div>
        
        <!-- Empty result -->
        <div v-else-if="plants.length === 0" class="text-center py-5">
          <div class="empty-state">
            <i class="bi bi-flower1 display-1 text-muted mb-3"></i>
            <h4>No plants found</h4>
            <p class="text-muted">Try changing your search or filter parameters.</p>
            <button class="btn btn-primary mt-3" @click="clearFilters">Reset all filters</button>
          </div>
        </div>
        
        <!-- Plants list -->
        <template v-else>
          <!-- Results information -->
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <p class="mb-0">
                <span class="fw-medium">{{ plantsStore.pagination.total_items }}</span>
                {{ getResultText(plantsStore.pagination.total_items) }}
              </p>
            </div>
            
            <!-- View type toggle -->
            <div class="btn-group" role="group" aria-label="View toggle">
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
          
          <!-- Grid view -->
          <div v-if="viewMode === 'grid'" class="row g-4">
            <div v-for="plant in plants" :key="plant.id" class="col-md-6 col-lg-4">
              <PlantCard :plant="plant" />
            </div>
          </div>
          
          <!-- List view -->
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
                      <!-- Characteristic badges -->
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
                    
                    <!-- Climate zones -->
                    <div v-if="plant.climate_zones && plant.climate_zones.length > 0" class="mb-3 small">
                      <span class="text-muted me-2">Climate zones:</span>
                      <span v-for="zone in plant.climate_zones" :key="zone.id" class="badge bg-info text-white me-1">
                        {{ zone.name }}
                      </span>
                    </div>
                    
                    <router-link :to="{ name: 'PlantDetails', params: { id: plant.id } }" class="btn btn-outline-primary mt-auto">
                      Details
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pagination -->
          <div class="mt-5">
            <PlantPagination 
              :currentPage="plantsStore.pagination.page" 
              :totalPages="plantsStore.pagination.total_pages"
              :totalItems="plantsStore.pagination.total_items"
              :perPage="plantsStore.pagination.per_page"
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
  import PlantFilters from '../components/PlantFilter.vue';
  import PlantCard from '../components/PlantCard.vue';
  import PlantPagination from '../components/PlantPagination.vue';
  
  const route = useRoute();
  const router = useRouter();
  const plantsStore = usePlantsStore();
  
  // Component state
  const viewMode = ref(localStorage.getItem('plantsViewMode') || 'grid'); // grid or list
  const quickSearch = ref('');
  let quickSearchTimeout = null;
  
  // Computed properties
  const plants = computed(() => plantsStore.plants);
  const isLoading = computed(() => plantsStore.isLoading);
  const error = computed(() => plantsStore.error);
  
  // Initialize on component mount
  onMounted(async () => {
    // Load categories and climate zones if not already loaded
    if (!plantsStore.categories.length) {
      await plantsStore.loadCategories();
    }
    
    if (!plantsStore.climateZones.length) {
      await plantsStore.loadClimateZones();
    }
    
    // Apply URL parameters (if any)
    const page = parseInt(route.query.page) || 1;
    
    // Set filters from URL
    if (route.query.search) {
      quickSearch.value = route.query.search;
      plantsStore.activeFilters.searchQuery = route.query.search;
    }
    
    if (route.query.category) {
      plantsStore.activeFilters.category_id = parseInt(route.query.category);
    }
    
    if (route.query.climateZone) {
      plantsStore.activeFilters.climate_zone_id = parseInt(route.query.climateZone);
    }
    
    if (route.query.sortBy) {
      plantsStore.activeFilters.sort_by = route.query.sortBy;
    }
    
    if (route.query.sortDirection) {
      plantsStore.activeFilters.sort_direction = route.query.sortDirection;
    }
    
    // Load plants
    await loadPlants(page, plantsStore.pagination.per_page);
  });
  
  // Set view mode
  function setViewMode(mode) {
    viewMode.value = mode;
    localStorage.setItem('plantsViewMode', mode); // Save to localStorage
  }
  
  // Load plants
  async function loadPlants(page = 1, limit = 20, resetFilters = false) {
    await plantsStore.loadPlants(page, limit, resetFilters);
    
    // Update URL with parameters
    updateUrlParams({
      page: page > 1 ? page : undefined,
      search: plantsStore.activeFilters.searchQuery || undefined,
      category: plantsStore.activeFilters.category_id || undefined,
      climateZone: plantsStore.activeFilters.climate_zone_id || undefined,
      sortBy: plantsStore.activeFilters.sort_by !== 'name' ? plantsStore.activeFilters.sort_by : undefined,
      sortDirection: plantsStore.activeFilters.sort_direction !== 'asc' ? plantsStore.activeFilters.sort_direction : undefined
    });
  }
  
  // Update URL parameters
  function updateUrlParams(params) {
    const query = { ...route.query };
    
    // Update or remove parameters
    Object.keys(params).forEach(key => {
      if (params[key] === undefined) {
        delete query[key];
      } else {
        query[key] = params[key];
      }
    });
    
    // Update URL without page reload
    router.replace({ query });
  }
  
  // Handle pagination page change
  function onPageChange(page) {
    loadPlants(page, plantsStore.pagination.per_page);
    // Scroll page to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  
  // Handle filter application
  function applyFilters(filters) {
    // Update quick search if it changed
    if (filters.searchQuery !== quickSearch.value) {
      quickSearch.value = filters.searchQuery;
    }
    
    // Update filters and load plants
    plantsStore.updateFilters(filters);
  }
  
  // Handle quick search with debounce
  function onQuickSearchDebounced() {
    if (quickSearchTimeout) {
      clearTimeout(quickSearchTimeout);
    }
    
    quickSearchTimeout = setTimeout(() => {
      applyQuickSearch();
    }, 500); // Wait 500 ms after typing stops
  }
  
  // Apply quick search
  function applyQuickSearch() {
    plantsStore.updateFilters({ searchQuery: quickSearch.value });
  }
  
  // Clear all filters
  function clearFilters() {
    quickSearch.value = '';
    plantsStore.clearFilters();
  }
  
  // Word form for "plant" based on count
  function getResultText(count) {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
      return 'plants';
    }
    
    if (lastDigit === 1) {
      return 'plant';
    }
    
    if (lastDigit >= 2 && lastDigit <= 4) {
      return 'plants';
    }
    
    return 'plants';
  }
  
  // Truncate description to specified length
  function truncateDescription(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    
    return text.substring(0, maxLength) + '...';
  }
  
  // Get text label for watering frequency
  function getWateringLabel(frequency) {
    if (!frequency) return 'Not specified';
    
    const wateringLabels = {
      'daily': 'Daily',
      'twice_a_week': 'Twice a week',
      'weekly': 'Weekly',
      'bi_weekly': 'Every 2 weeks',
      'monthly': 'Monthly',
      'rarely': 'Rarely'
    };
    
    return wateringLabels[frequency] || frequency;
  }
  
  // Get text label for light level
  function getLightLabel(level) {
    if (!level) return 'Not specified';
    
    const lightLabels = {
      'full_sun': 'Full sun',
      'partial_sun': 'Partial sun',
      'shade': 'Shade',
      'low_light': 'Low light'
    };
    
    return lightLabels[level] || level;
  }
  
  // Handle image load errors
  function handleImageError(event) {
    // Replace broken image with placeholder
    event.target.src = '/placeholder-plant.jpg';
    event.target.classList.add('img-error');
  }
  
  // Watch route changes to update data
  watch(() => route.query, (newQuery) => {
    // If page changed, load new data
    const page = parseInt(newQuery.page) || 1;
    if (page !== plantsStore.pagination.page) {
      loadPlants(page, plantsStore.pagination.per_page);
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
  
  /* Loading animations */
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