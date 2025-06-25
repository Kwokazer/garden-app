<!-- frontend/src/features/questions/views/QuestionsListPage.vue -->
<template>
  <div class="questions-list-page">
    <!-- Заголовок страницы -->
    <div class="container py-4">
      <div class="row align-items-center mb-4">
        <div class="col-md-8">
          <h1 class="mb-1">Вопросы и ответы</h1>
          <p class="text-muted mb-0">Найдите ответы на ваши вопросы или поделитесь своими знаниями</p>
        </div>
        <div class="col-md-4 text-md-end mt-3 mt-md-0">
          <router-link to="/questions/ask" class="btn btn-primary">
            <i class="bi bi-plus-circle me-2"></i>
            Задать вопрос
          </router-link>
        </div>
      </div>
      
      <!-- Фильтры -->
      <QuestionFilters 
        :isLoading="isLoading" 
        :initialFilters="questionsStore.activeFilters" 
        @apply="applyFilters"
      />
    </div>
    
    <!-- Результаты -->
    <div class="container pb-5">
      <!-- Состояние загрузки -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загрузка вопросов...</p>
      </div>
      
      <!-- Ошибка -->
      <div v-else-if="error" class="alert alert-danger mt-4">
        <div class="d-flex align-items-center">
          <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
          <div>
            <h5 class="alert-heading">Ошибка загрузки</h5>
            <p class="mb-2">{{ error }}</p>
            <div class="mt-3">
              <button class="btn btn-outline-danger me-2" @click="loadQuestions">
                Попробовать снова
              </button>
              <button class="btn btn-outline-secondary" @click="clearFilters">
                Сбросить фильтры
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Пустой результат -->
      <div v-else-if="questionsWithKeys.length === 0" class="text-center py-5">
        <div class="empty-state">
          <i class="bi bi-chat-dots display-1 text-muted mb-3"></i>
          <h4>Вопросы не найдены</h4>
          <p class="text-muted">
            <span v-if="hasActiveFilters">
              Попробуйте изменить параметры поиска или 
              <button class="btn btn-link p-0" @click="clearFilters">сбросить фильтры</button>
            </span>
            <span v-else>
              Пока что здесь нет ни одного вопроса.
            </span>
          </p>
          <router-link to="/questions/ask" class="btn btn-primary mt-3">
            <i class="bi bi-plus-circle me-2"></i>
            Задать первый вопрос
          </router-link>
        </div>
      </div>
      
      <!-- Список вопросов -->
      <template v-else>
        <!-- Информация о результатах -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <p class="mb-0">
              <span class="fw-medium">{{ questionsStore.pagination.total }}</span>
              {{ getResultText(questionsStore.pagination.total) }}
              <span v-if="hasActiveFilters">найдено</span>
            </p>
          </div>
          
          <!-- Сортировка (быстрая) -->
          <div class="d-flex align-items-center">
            <span class="me-2 small text-muted">Быстрая сортировка:</span>
            <div class="btn-group" role="group">
              <button 
                type="button" 
                class="btn btn-sm" 
                :class="{ 'btn-primary': questionsStore.activeFilters.sort_by === 'created_at', 'btn-outline-primary': questionsStore.activeFilters.sort_by !== 'created_at' }"
                @click="quickSort('created_at')"
              >
                Новые
              </button>
              <button 
                type="button" 
                class="btn btn-sm" 
                :class="{ 'btn-primary': questionsStore.activeFilters.sort_by === 'votes_up', 'btn-outline-primary': questionsStore.activeFilters.sort_by !== 'votes_up' }"
                @click="quickSort('votes_up')"
              >
                Популярные
              </button>
              <button 
                type="button" 
                class="btn btn-sm" 
                :class="{ 'btn-primary': questionsStore.activeFilters.is_solved === false, 'btn-outline-primary': questionsStore.activeFilters.is_solved !== false }"
                @click="quickFilter('unsolved')"
              >
                Нерешенные
              </button>
            </div>
          </div>
        </div>
        
        <!-- Список вопросов с уникальными ключами -->
        <div class="questions-grid">
          <QuestionCard
            v-for="question in questionsWithKeys"
            :key="`question-${question.id}-${question._updateKey}`"
            :question="question"
            :showActions="true"
            @vote="handleVote"
            @delete="handleDelete"
          />
        </div>
        
        <!-- Пагинация -->
        <div class="mt-5">
          <nav aria-label="Questions pagination">
            <ul class="pagination justify-content-center">
              <!-- Первая страница -->
              <li class="page-item" :class="{ disabled: currentPage <= 1 }">
                <a 
                  class="page-link" 
                  href="#" 
                  @click.prevent="!isLoading && currentPage > 1 && changePage(1)"
                  aria-label="First page"
                >
                  <i class="bi bi-chevron-double-left"></i>
                </a>
              </li>
              
              <!-- Предыдущая страница -->
              <li class="page-item" :class="{ disabled: currentPage <= 1 }">
                <a 
                  class="page-link" 
                  href="#" 
                  @click.prevent="!isLoading && currentPage > 1 && changePage(currentPage - 1)"
                  aria-label="Previous page"
                >
                  <i class="bi bi-chevron-left"></i>
                </a>
              </li>
              
              <!-- Страницы -->
              <li 
                v-for="page in displayedPages" 
                :key="page" 
                class="page-item" 
                :class="{ active: page === currentPage, disabled: page === '...' }"
              >
                <template v-if="page === '...'">
                  <span class="page-link">...</span>
                </template>
                <a 
                  v-else
                  class="page-link" 
                  href="#" 
                  @click.prevent="!isLoading && page !== currentPage && changePage(page)"
                >
                  {{ page }}
                </a>
              </li>
              
              <!-- Следующая страница -->
              <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
                <a 
                  class="page-link" 
                  href="#" 
                  @click.prevent="!isLoading && currentPage < totalPages && changePage(currentPage + 1)"
                  aria-label="Next page"
                >
                  <i class="bi bi-chevron-right"></i>
                </a>
              </li>
              
              <!-- Последняя страница -->
              <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
                <a 
                  class="page-link" 
                  href="#" 
                  @click.prevent="!isLoading && currentPage < totalPages && changePage(totalPages)"
                  aria-label="Last page"
                >
                  <i class="bi bi-chevron-double-right"></i>
                </a>
              </li>
            </ul>
          </nav>
          
          <!-- Информация о пагинации -->
          <div class="text-center text-muted small mt-2">
            <span v-if="questionsStore.pagination.total > 0">
              Показаны {{ firstItemIndex }} - {{ lastItemIndex }} из {{ questionsStore.pagination.total }} вопросов
            </span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useQuestionsStore } from '../store/questionsStore';
import { useConfirm } from '@/composables/useConfirm';
import { useNotificationStore } from '@/stores/notificationStore';
import QuestionFilters from '../components/QuestionFilters.vue';
import QuestionCard from '../components/QuestionCard.vue';

const route = useRoute();
const router = useRouter();
const questionsStore = useQuestionsStore();
const { confirmDelete } = useConfirm();
const notificationStore = useNotificationStore();

// Состояние компонента
const isLoading = ref(false);
const error = ref(null);

// Вычисляемые свойства
const questions = computed(() => questionsStore.questions);
const currentPage = computed(() => questionsStore.pagination.page);
const totalPages = computed(() => questionsStore.pagination.pages);

// Добавляем ключи обновления для принудительного ререндера
const questionsWithKeys = computed(() => {
  console.log('📊 QuestionsListPage: Computing questionsWithKeys, count:', questions.value.length);
  return questions.value.map(question => ({
    ...question,
    // Добавляем ключ для принудительного обновления при изменении голосов
    _updateKey: `${question.votes_up || 0}-${question.votes_down || 0}-${question.user_vote || 'null'}`
  }));
});

const hasActiveFilters = computed(() => {
  const filters = questionsStore.activeFilters;
  return filters.search || 
         filters.plant_id !== null || 
         filters.author_id !== null || 
         filters.is_solved !== null;
});

// Вычисляемые значения для пагинации
const firstItemIndex = computed(() => {
  if (questionsStore.pagination.total === 0) return 0;
  return (currentPage.value - 1) * questionsStore.pagination.size + 1;
});

const lastItemIndex = computed(() => {
  return Math.min(
    currentPage.value * questionsStore.pagination.size, 
    questionsStore.pagination.total
  );
});

const displayedPages = computed(() => {
  const total = totalPages.value;
  const current = currentPage.value;
  const pages = [];
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i);
    }
    return pages;
  }
  
  pages.push(1);
  
  if (current > 3) {
    pages.push('...');
  }
  
  let startPage = Math.max(2, current - 1);
  let endPage = Math.min(total - 1, current + 1);
  
  if (current <= 3) {
    endPage = Math.min(5, total - 1);
  } else if (current >= total - 2) {
    startPage = Math.max(total - 4, 2);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  if (endPage < total - 1) {
    pages.push('...');
  }
  
  if (total > 1) {
    pages.push(total);
  }
  
  return pages;
});

// Отслеживаем изменения в store для отладки
watch(() => questionsStore.questions, (newQuestions, oldQuestions) => {
  console.log('🔄 QuestionsListPage: Store questions changed:', {
    oldCount: oldQuestions?.length || 0,
    newCount: newQuestions?.length || 0,
    example: newQuestions[0] ? {
      id: newQuestions[0].id,
      votes_up: newQuestions[0].votes_up,
      votes_down: newQuestions[0].votes_down,
      user_vote: newQuestions[0].user_vote
    } : null
  });
}, { deep: true });

// Инициализация при создании компонента
onMounted(async () => {
  console.log('🚀 QuestionsListPage: Component mounted');
  
  // Применяем параметры из URL
  const page = parseInt(route.query.page) || 1;
  
  // Устанавливаем фильтры из URL
  if (route.query.search) {
    questionsStore.activeFilters.search = route.query.search;
  }
  
  if (route.query.plant_id) {
    questionsStore.activeFilters.plant_id = parseInt(route.query.plant_id);
  }
  
  if (route.query.author_id) {
    questionsStore.activeFilters.author_id = parseInt(route.query.author_id);
  }
  
  if (route.query.is_solved !== undefined) {
    questionsStore.activeFilters.is_solved = route.query.is_solved === 'true';
  }
  
  if (route.query.sort_by) {
    questionsStore.activeFilters.sort_by = route.query.sort_by;
  }
  
  if (route.query.sort_order) {
    questionsStore.activeFilters.sort_order = route.query.sort_order;
  }
  
  // Загружаем вопросы
  await loadQuestions(page, questionsStore.pagination.size);
});

// Методы
async function loadQuestions(page = 1, perPage = 20, resetFilters = false) {
  console.log(`📥 QuestionsListPage: Loading questions (page ${page})`);
  
  isLoading.value = true;
  error.value = null;
  
  try {
    await questionsStore.loadQuestions(page, perPage, resetFilters);
    
    console.log(`✅ QuestionsListPage: Questions loaded, count: ${questionsStore.questions.length}`);
    
    // Обновляем URL с параметрами
    updateUrlParams({
      page: page > 1 ? page : undefined,
      search: questionsStore.activeFilters.search || undefined,
      plant_id: questionsStore.activeFilters.plant_id || undefined,
      author_id: questionsStore.activeFilters.author_id || undefined,
      is_solved: questionsStore.activeFilters.is_solved !== null ? questionsStore.activeFilters.is_solved : undefined,
      sort_by: questionsStore.activeFilters.sort_by !== 'created_at' ? questionsStore.activeFilters.sort_by : undefined,
      sort_order: questionsStore.activeFilters.sort_order !== 'desc' ? questionsStore.activeFilters.sort_order : undefined
    });
  } catch (e) {
    error.value = questionsStore.error || 'Не удалось загрузить вопросы';
    console.error('❌ QuestionsListPage: Error loading questions:', e);
  } finally {
    isLoading.value = false;
  }
}

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

async function changePage(page) {
  await loadQuestions(page, questionsStore.pagination.size);
  // Прокручиваем страницу наверх
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function applyFilters(filters) {
  console.log('🔍 QuestionsListPage: Applying filters:', filters);
  // Обновляем фильтры в store
  await questionsStore.updateFilters(filters);
}

async function clearFilters() {
  console.log('🗑️ QuestionsListPage: Clearing filters');
  await questionsStore.clearFilters();
}

async function quickSort(sortBy) {
  const filters = {
    ...questionsStore.activeFilters,
    sort_by: sortBy,
    sort_order: sortBy === questionsStore.activeFilters.sort_by && questionsStore.activeFilters.sort_order === 'desc' ? 'asc' : 'desc'
  };
  await questionsStore.updateFilters(filters);
}

async function quickFilter(filterType) {
  let filters = { ...questionsStore.activeFilters };
  
  if (filterType === 'unsolved') {
    // Переключаем фильтр нерешенных вопросов
    filters.is_solved = filters.is_solved === false ? null : false;
  }
  
  await questionsStore.updateFilters(filters);
}

// Обработка голосования с подробной отладкой
async function handleVote(voteData) {
  console.log(`🎯 QuestionsListPage: Vote received:`, voteData);
  
  try {
    // Сохраняем состояние до
    const questionBefore = questionsStore.questions.find(q => q.id === voteData.itemId);
    console.log('📊 QuestionsListPage: Before vote:', questionBefore ? {
      votes_up: questionBefore.votes_up,
      votes_down: questionBefore.votes_down,
      user_vote: questionBefore.user_vote
    } : 'not found');
    
    // Вызываем голосование через store
    await questionsStore.voteForQuestion(voteData.itemId, voteData.voteType);
    
    // Проверяем состояние после
    const questionAfter = questionsStore.questions.find(q => q.id === voteData.itemId);
    console.log('✅ QuestionsListPage: After vote:', questionAfter ? {
      votes_up: questionAfter.votes_up,
      votes_down: questionAfter.votes_down,
      user_vote: questionAfter.user_vote
    } : 'not found');
    
  } catch (error) {
    console.error('❌ QuestionsListPage: Vote error:', error);
    notificationStore.error('Ошибка голосования', error.message || 'Не удалось проголосовать');
  }
}

async function handleDelete(questionId) {
  const confirmed = await confirmDelete('Вы уверены, что хотите удалить этот вопрос? Это действие нельзя отменить.');
  if (!confirmed) return;

  try {
    await questionsStore.deleteQuestion(questionId);
    // Перезагружаем текущую страницу
    await loadQuestions(currentPage.value, questionsStore.pagination.size);
    notificationStore.success('Вопрос удален', 'Вопрос был успешно удален');
  } catch (error) {
    console.error('Error deleting question:', error);
    notificationStore.error('Ошибка удаления', error.message || 'Не удалось удалить вопрос');
  }
}

// Склонение слова "вопрос"
function getResultText(count) {
  const lastDigit = count % 10;
  const lastTwoDigits = count % 100;
  
  if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
    return 'вопросов';
  }
  
  if (lastDigit === 1) {
    return 'вопрос';
  }
  
  if (lastDigit >= 2 && lastDigit <= 4) {
    return 'вопроса';
  }
  
  return 'вопросов';
}

// Наблюдаем за изменениями в query параметрах URL
watch(() => route.query, (newQuery) => {
  const page = parseInt(newQuery.page) || 1;
  if (page !== currentPage.value) {
    loadQuestions(page, questionsStore.pagination.size);
  }
}, { deep: true });
</script>

<style scoped>
.questions-list-page {
  padding-bottom: 2rem;
}

.empty-state {
  padding: 3rem 0;
}

.questions-grid {
  display: grid;
  gap: 1.5rem;
}

/* Анимации */
.questions-grid {
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

/* Пагинация */
.pagination {
  margin-bottom: 0.5rem;
}

.page-link {
  color: var(--bs-primary);
  border-color: #dee2e6;
  padding: 0.5rem 0.75rem;
  transition: all 0.2s ease;
}

.page-item.active .page-link {
  background-color: var(--bs-primary);
  border-color: var(--bs-primary);
}

.page-link:hover {
  color: var(--bs-success);
  background-color: #f8f9fa;
  border-color: #dee2e6;
  transform: translateY(-2px);
}

.page-item.active .page-link:hover {
  color: #fff;
  background-color: var(--bs-success);
  border-color: var(--bs-success);
}

.page-item.disabled .page-link {
  color: #6c757d;
  pointer-events: none;
  background-color: #fff;
  border-color: #dee2e6;
}

/* Быстрые фильтры */
.btn-group .btn {
  font-size: 0.875rem;
  padding: 0.25rem 0.75rem;
}

/* Адаптивность */
@media (max-width: 768px) {
  .d-flex.justify-content-between.align-items-center {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .btn-group {
    justify-content: center;
  }
  
  .pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination .page-item {
    margin: 0.1rem;
  }
}
</style>