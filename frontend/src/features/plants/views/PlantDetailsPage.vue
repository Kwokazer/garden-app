<!-- src/features/plants/views/PlantDetailsPage.vue -->
<template>
  <div class="plant-details-page">
    <!-- Breadcrumbs -->
    <div class="bg-light py-2">
      <div class="container">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb mb-0">
            <li class="breadcrumb-item">
              <router-link to="/">Home</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link :to="{ name: 'PlantsList' }">Plants</router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              {{ plant ? plant.name : 'Loading...' }}
            </li>
          </ol>
        </nav>
      </div>
    </div>
    
    <div class="container py-4">
      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading plant information...</p>
      </div>
      
      <!-- Error -->
      <div v-else-if="error" class="alert alert-danger mt-4">
        <div class="d-flex align-items-center">
          <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
          <div>
            <h5 class="alert-heading">Error loading data</h5>
            <p class="mb-2">{{ error }}</p>
            <div class="mt-3">
              <button class="btn btn-outline-danger me-2" @click="loadPlant">
                Try again
              </button>
              <router-link :to="{ name: 'PlantsList' }" class="btn btn-outline-secondary">
                Return to list
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Plant not found -->
      <div v-else-if="!plant" class="text-center py-5">
        <div class="empty-state">
          <i class="bi bi-question-circle display-1 text-muted mb-3"></i>
          <h3>Plant not found</h3>
          <p class="text-muted">The requested plant was not found or has been deleted.</p>
          <router-link :to="{ name: 'PlantsList' }" class="btn btn-primary mt-3">
            Return to plants list
          </router-link>
        </div>
      </div>
      
      <!-- Page content -->
      <template v-else>
        <!-- Main plant information -->
        <div class="row gx-5">
          <!-- Image gallery (left column) -->
          <div class="col-lg-6 mb-4 mb-lg-0">
            <PlantGallery 
              :images="plant.images || []" 
              @image-change="onImageChange"
            />
            
            <!-- Share and favorite -->
            <div class="d-flex justify-content-between mt-3">
              <div class="share-buttons">
                <button class="btn btn-outline-secondary btn-sm me-2">
                  <i class="bi bi-share me-1"></i> Share
                </button>
                <button class="btn btn-outline-secondary btn-sm me-2">
                  <i class="bi bi-printer me-1"></i> Print
                </button>
              </div>
              <div>
                <button 
                  class="btn btn-outline-danger btn-sm favorite-btn" 
                  :class="{ 'active': isFavorite }"
                  @click="toggleFavorite"
                >
                  <i class="bi" :class="isFavorite ? 'bi-heart-fill' : 'bi-heart'"></i>
                  {{ isFavorite ? 'In favorites' : 'Add to favorites' }}
                </button>
              </div>
            </div>
          </div>
          
          <!-- Plant information (right column) -->
          <div class="col-lg-6">
            <div class="plant-details">
              <!-- Title and main info -->
              <div class="mb-4">
                <h1 class="plant-title">{{ plant.name }}</h1>
                <p class="text-muted latin-name">{{ plant.latin_name }}</p>
                
                <!-- Categories and tags -->
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
              
              <!-- Short description -->
              <div class="card bg-light mb-4 border-0">
                <div class="card-body">
                  <p v-if="plant.description" class="m-0">{{ plant.description }}</p>
                  <p v-else class="text-muted m-0">No description available</p>
                </div>
              </div>
              
              <!-- Main characteristics -->
              <div class="plant-characteristics mb-4">
                <h5 class="section-title">
                  <i class="bi bi-info-circle me-2"></i>
                  Main Characteristics
                </h5>
                
                <div class="row">
                  <!-- Plant type -->
                  <div class="col-md-6 mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Plant type:</span>
                      <span class="characteristic-value">{{ getPlantTypeLabel(plant.plant_type) }}</span>
                    </div>
                  </div>
                  
                  <!-- Life cycle -->
                  <div class="col-md-6 mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Life cycle:</span>
                      <span class="characteristic-value">{{ getLifeCycleLabel(plant.life_cycle) }}</span>
                    </div>
                  </div>
                  
                  <!-- Plant height -->
                  <div class="col-md-6 mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Height:</span>
                      <span class="characteristic-value">
                        {{ plant.height_min && plant.height_max ? `${plant.height_min}-${plant.height_max} cm` : 'Not specified' }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Growth rate -->
                  <div class="col-md-6 mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Growth rate:</span>
                      <span class="characteristic-value">{{ getGrowthRateLabel(plant.growth_rate) }}</span>
                    </div>
                  </div>
                  
                  <!-- Flowering period -->
                  <div class="col-md-6 mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Flowering period:</span>
                      <span class="characteristic-value">
                        {{ plant.flowering_period ? plant.flowering_period : 'Not specified' }}
                      </span>
                    </div>
                  </div>
                  
                  <!-- Toxicity -->
                  <div class="col-md-6 mb-3">
                    <div class="characteristic-item">
                      <span class="characteristic-label">Toxicity:</span>
                      <span 
                        class="characteristic-value" 
                        :class="{ 'text-danger': plant.is_toxic, 'text-success': !plant.is_toxic }"
                      >
                        <i 
                          class="bi" 
                          :class="plant.is_toxic ? 'bi-exclamation-circle' : 'bi-check-circle'"
                          :title="plant.is_toxic ? 'Toxic' : 'Non-toxic'"
                        ></i>
                        {{ plant.is_toxic ? 'Toxic' : 'Non-toxic' }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Climate zones -->
                <div class="mb-3">
                  <div class="characteristic-item">
                    <span class="characteristic-label">Climate zones:</span>
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
                      <span v-else class="text-muted">Not specified</span>
                    </div>
                  </div>
                </div>
                
                <!-- Notes (if any) -->
                <div v-if="plant.notes" class="mb-3">
                  <div class="characteristic-item">
                    <span class="characteristic-label">Notes:</span>
                    <p class="mt-2 mb-0">{{ plant.notes }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Similar plants -->
              <div v-if="plant.similar_plants && plant.similar_plants.length > 0" class="similar-plants mb-4">
                <h5 class="section-title">
                  <i class="bi bi-shuffle me-2"></i>
                  Similar Plants
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
        
        <!-- Information tabs -->
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
                Care
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
                Growing
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
                Q&A
              </button>
            </li>
          </ul>
          
          <div class="tab-content" id="plantTabsContent">
            <!-- Care tab -->
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
            
            <!-- Growing tab -->
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
                      Growing and Propagation
                    </h5>
                  </div>
                  <div class="card-body p-4">
                    <div v-if="plant.propagation_methods && plant.propagation_methods.length > 0">
                      <h6 class="fw-bold mb-3">Propagation Methods</h6>
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
                              <small class="text-muted me-2">Difficulty:</small>
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
                      <p class="mt-3">No information about propagation methods available</p>
                    </div>
                    
                    <!-- Planting instructions -->
                    <div class="planting-instructions mt-4" v-if="plant.planting_instructions">
                      <h6 class="fw-bold mb-3">Planting Instructions</h6>
                      <div class="planting-content">{{ plant.planting_instructions }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Q&A tab -->
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
                      Questions and Answers
                    </h5>
                  </div>
                  <div class="card-body p-4">
                    <!-- Статистика и кнопка "Задать вопрос" -->
                    <div class="d-flex justify-content-between align-items-center mb-4">
                      <div class="qa-stats">
                        <span class="text-muted">
                          <strong>{{ questionsPagination.total }}</strong> {{ questionsPagination.total === 1 ? 'question' : 'questions' }}
                        </span>
                      </div>
                      <button class="btn btn-primary" @click="navigateToAskQuestion">
                        <i class="bi bi-plus-circle me-2"></i>
                        Ask a Question
                      </button>
                    </div>
                    
                    <!-- Загрузка вопросов -->
                    <div v-if="isLoadingQuestions" class="text-center py-4">
                      <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading questions...</span>
                      </div>
                      <p class="mt-3 text-muted">Loading questions...</p>
                    </div>
                    
                    <!-- Ошибка при загрузке вопросов -->
                    <div v-else-if="questionsError" class="alert alert-danger">
                      <i class="bi bi-exclamation-triangle-fill me-2"></i>
                      {{ questionsError }}
                      <button class="btn btn-outline-danger btn-sm ms-3" @click="loadQuestionsForPlant()">
                        Try again
                      </button>
                    </div>
                    
                    <!-- Нет вопросов -->
                    <div v-else-if="plantQuestions.length === 0" class="text-center py-5">
                      <i class="bi bi-chat-dots display-4 text-muted mb-3"></i>
                      <h5>No questions yet</h5>
                      <p class="text-muted mb-4">Be the first to ask a question about {{ plant.name }}</p>
                      <button class="btn btn-outline-primary" @click="navigateToAskQuestion">
                        Ask first question
                      </button>
                    </div>
                    
                    <!-- Список вопросов -->
                    <div v-else class="questions-list">
                      <QuestionCard
                        v-for="question in plantQuestions"
                        :key="question.id"
                        :question="question"
                        :showActions="false"
                      />
                      
                      <!-- Пагинация, если есть больше страниц -->
                      <div v-if="questionsPagination.pages > 1" class="mt-4 d-flex justify-content-center">
                        <nav aria-label="Questions pagination">
                          <ul class="pagination">
                            <!-- Пред. страница -->
                            <li class="page-item" :class="{ disabled: questionsPagination.page <= 1 }">
                              <button
                                class="page-link"
                                @click="loadQuestionsForPlant(questionsPagination.page - 1)"
                                :disabled="questionsPagination.page <= 1 || isLoadingQuestions"
                              >
                                <i class="bi bi-chevron-left"></i>
                              </button>
                            </li>
                            
                            <!-- Страницы -->
                            <li
                              v-for="p in questionsPagination.pages"
                              :key="p"
                              class="page-item"
                              :class="{ active: p === questionsPagination.page }"
                            >
                              <button
                                class="page-link"
                                @click="loadQuestionsForPlant(p)"
                                :disabled="isLoadingQuestions"
                              >
                                {{ p }}
                              </button>
                            </li>
                            
                            <!-- След. страница -->
                            <li class="page-item" :class="{ disabled: questionsPagination.page >= questionsPagination.pages }">
                              <button
                                class="page-link"
                                @click="loadQuestionsForPlant(questionsPagination.page + 1)"
                                :disabled="questionsPagination.page >= questionsPagination.pages || isLoadingQuestions"
                              >
                                <i class="bi bi-chevron-right"></i>
                              </button>
                            </li>
                          </ul>
                        </nav>
                      </div>
                      
                      <!-- Кнопка "Задать вопрос" внизу списка -->
                      <div class="text-center mt-4">
                        <button class="btn btn-outline-primary" @click="navigateToAskQuestion">
                          <i class="bi bi-plus-circle me-2"></i>
                          Ask new question
                        </button>
                      </div>
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
// Импорт для вопросов
import { questionsApi } from '../../questions/api/questionsApi';
import QuestionCard from '../../questions/components/QuestionCard.vue';

const route = useRoute();
const router = useRouter();
const plantsStore = usePlantsStore();
const authStore = useAuthStore();

// Component state
const currentImageIndex = ref(0);
const isFavorite = ref(false);

// Состояние для вопросов
const plantQuestions = ref([]);
const isLoadingQuestions = ref(false);
const questionsError = ref(null);
const questionsPagination = ref({
  page: 1,
  pages: 1,
  total: 0,
  size: 5
});

// Computed properties
const plant = computed(() => plantsStore.currentPlant);
const isLoading = computed(() => plantsStore.isLoading);
const error = computed(() => plantsStore.error);

// Initialize on component mount
onMounted(async () => {
  const plantId = route.params.id;
  if (!plantId) {
    router.push({ name: 'PlantsList' });
    return;
  }
  
  // Load plant
  await loadPlant();
  
  // Check if plant is in favorites (if user is logged in)
  if (authStore.isLoggedIn) {
    checkIfFavorite();
  }
});

// Load plant data
async function loadPlant() {
  const plantId = route.params.id;
  await plantsStore.loadPlantById(plantId);
  
  // Загрузка вопросов для растения
  await loadQuestionsForPlant();
  
  // If error occurred, log it
  if (plantsStore.error) {
    console.error('Error loading plant:', plantsStore.error);
  }
}

// Метод для загрузки вопросов, связанных с растением
async function loadQuestionsForPlant(page = 1, perPage = 5) {
  if (!plant.value || !plant.value.id) return;
  
  isLoadingQuestions.value = true;
  questionsError.value = null;
  
  try {
    const plantId = plant.value.id;
    const filters = {
      sort_by: "created_at",
      sort_order: "desc"
    };
    
    const result = await questionsApi.getQuestionsByPlant(plantId, page, perPage, filters);
    
    plantQuestions.value = result.items || [];
    questionsPagination.value = {
      page: result.page || 1,
      pages: result.pages || 1,
      total: result.total || 0,
      size: result.size || perPage
    };
  } catch (error) {
    console.error('Error loading questions for plant:', error);
    questionsError.value = 'Failed to load questions for this plant';
  } finally {
    isLoadingQuestions.value = false;
  }
}

// Функция для создания вопроса
function navigateToAskQuestion() {
  // Проверяем авторизацию
  if (!authStore.isLoggedIn) {
    router.push({ 
      name: 'Login', 
      query: { 
        redirect: `/questions/ask?plant_id=${plant.value.id}` 
      } 
    });
    return;
  }
  
  // Переходим на страницу создания вопроса с предварительно заполненным ID растения
  router.push({ 
    name: 'CreateQuestion', 
    query: { 
      plant_id: plant.value.id 
    } 
  });
}

// Check if plant is in favorites
function checkIfFavorite() {
  // Here should be logic to check favorites through API
  // For example:
  // const favorites = await userService.getFavorites();
  // isFavorite.value = favorites.some(fav => fav.id === plant.value.id);
  
  // Demo placeholder using localStorage
  const localFavorites = JSON.parse(localStorage.getItem('favoritePlants') || '[]');
  isFavorite.value = localFavorites.includes(plant.value?.id);
}

// Add/remove from favorites
function toggleFavorite() {
  if (!authStore.isLoggedIn) {
    // If user is not logged in, redirect to login page
    router.push({ 
      name: 'Login', 
      query: { 
        redirect: router.currentRoute.value.fullPath 
      } 
    });
    return;
  }
  
  // Here should be logic to add/remove from favorites through API
  // For example:
  // if (isFavorite.value) {
  //   await userService.removeFromFavorites(plant.value.id);
  // } else {
  //   await userService.addToFavorites(plant.value.id);
  // }
  
  // Demo placeholder using localStorage
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

// Handle image change in gallery
function onImageChange(index) {
  currentImageIndex.value = index;
}

// Get label functions
function getPlantTypeLabel(type) {
  if (!type) return 'Not specified';
  
  const typeLabels = {
    'tree': 'Tree',
    'shrub': 'Shrub',
    'herb': 'Herbaceous',
    'succulent': 'Succulent',
    'cactus': 'Cactus',
    'vine': 'Vine',
    'fern': 'Fern',
    'aquatic': 'Aquatic',
    'bulb': 'Bulbous'
  };
  
  return typeLabels[type] || type;
}

function getLifeCycleLabel(cycle) {
  if (!cycle) return 'Not specified';
  
  const cycleLabels = {
    'annual': 'Annual',
    'biennial': 'Biennial',
    'perennial': 'Perennial'
  };
  
  return cycleLabels[cycle] || cycle;
}

function getGrowthRateLabel(rate) {
  if (!rate) return 'Medium';
  
  const rateLabels = {
    'fast': 'Fast',
    'moderate': 'Medium',
    'slow': 'Slow'
  };
  
  return rateLabels[rate] || rate;
}

// Handle image load errors
function handleImageError(event) {
  event.target.src = '/placeholder-plant.jpg'; // Replace with placeholder
  event.target.classList.add('img-error');
}

// Watch route changes to update data when navigating between plants
watch(() => route.params.id, async (newId) => {
  if (newId && newId !== String(plant.value?.id)) {
    await loadPlant();
    
    if (authStore.isLoggedIn) {
      checkIfFavorite();
    }
    
    // Scroll page to top
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
  
  /* Animations */
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
  
  /* Responsive styles for mobile devices */
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