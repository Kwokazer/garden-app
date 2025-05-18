<!-- frontend/src/features/questions/views/QuestionDetailsPage.vue -->
<template>
    <div class="question-details-page">
      <!-- Breadcrumbs -->
      <div class="bg-light py-2">
        <div class="container">
          <nav aria-label="breadcrumb">
            <ol class="breadcrumb mb-0">
              <li class="breadcrumb-item">
                <router-link to="/">Главная</router-link>
              </li>
              <li class="breadcrumb-item">
                <router-link to="/questions">Вопросы</router-link>
              </li>
              <li class="breadcrumb-item active" aria-current="page">
                {{ question ? question.title : 'Загрузка...' }}
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
          <p class="mt-3 text-muted">Загрузка вопроса...</p>
        </div>
  
        <!-- Ошибка -->
        <div v-else-if="error" class="alert alert-danger mt-4">
          <div class="d-flex align-items-center">
            <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
            <div>
              <h5 class="alert-heading">Ошибка загрузки</h5>
              <p class="mb-2">{{ error }}</p>
              <div class="mt-3">
                <button class="btn btn-outline-danger me-2" @click="loadQuestion">
                  Попробовать снова
                </button>
                <router-link to="/questions" class="btn btn-outline-secondary">
                  К списку вопросов
                </router-link>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Вопрос не найден -->
        <div v-else-if="!question" class="text-center py-5">
          <div class="empty-state">
            <i class="bi bi-question-circle display-1 text-muted mb-3"></i>
            <h3>Вопрос не найден</h3>
            <p class="text-muted">Запрашиваемый вопрос не найден или был удален.</p>
            <router-link to="/questions" class="btn btn-primary mt-3">
              К списку вопросов
            </router-link>
          </div>
        </div>
  
        <!-- Контент страницы -->
        <template v-else>
          <!-- Основной вопрос -->
          <div class="question-detail-card">
            <div class="card shadow-sm border-0 mb-4">
              <div class="card-body">
                <div class="d-flex">
                  <!-- Панель голосования -->
                  <div class="voting-section me-4">
                    <VotingButtons
                      type="question"
                      :item-id="question.id"
                      :votes-up="question.votes_up"
                      :votes-down="question.votes_down"
                      :user-vote="question.user_vote"
                      :is-loading="isVoting"
                      :author-id="question.author_id"
                      @vote="handleQuestionVote"
                    />
                  </div>
  
                  <!-- Содержимое вопроса -->
                  <div class="question-content flex-grow-1">
                    <!-- Заголовок и статус -->
                    <div class="d-flex justify-content-between align-items-start mb-3">
                      <h1 class="question-title">{{ question.title }}</h1>
                      <span 
                        v-if="question.is_solved" 
                        class="badge bg-success fs-6"
                        title="Вопрос решен"
                      >
                        <i class="bi bi-check-circle me-1"></i>
                        Решен
                      </span>
                    </div>
  
                    <!-- Текст вопроса -->
                    <div class="question-body">
                      <div v-html="formatQuestionBody(question.body)" class="formatted-content"></div>
                    </div>
  
                    <!-- Связанное растение -->
                    <div v-if="question.plant" class="related-plant mt-3">
                      <router-link
                        :to="{ name: 'PlantDetails', params: { id: question.plant.id } }"
                        class="plant-link d-inline-flex align-items-center text-decoration-none"
                      >
                        <i class="bi bi-flower1 me-2 text-primary"></i>
                        <div>
                          <strong class="text-primary">{{ question.plant.name }}</strong>
                          <small class="text-muted d-block">{{ question.plant.latin_name }}</small>
                        </div>
                      </router-link>
                    </div>
  
                    <!-- Мета-информация -->
                    <div class="question-meta mt-4 pt-3 border-top">
                      <div class="d-flex flex-wrap justify-content-between align-items-center">
                        <div class="d-flex flex-wrap align-items-center">
                          <!-- Просмотры -->
                          <span class="me-3 small text-muted">
                            <i class="bi bi-eye me-1"></i>
                            {{ question.view_count }} {{ getViewsText(question.view_count) }}
                          </span>
  
                          <!-- Количество ответов -->
                          <span class="me-3 small text-muted">
                            <i class="bi bi-chat-dots me-1"></i>
                            {{ question.answers_count || 0 }} {{ getAnswersText(question.answers_count || 0) }}
                          </span>
  
                          <!-- Автор и дата -->
                          <div class="author-info">
                            <small class="text-muted">
                              Автор: 
                              <span class="fw-medium">{{ question.author?.username || 'Неизвестно' }}</span>
                              <span class="mx-1">•</span>
                              <time :datetime="question.created_at" :title="getFullDate(question.created_at)">
                                {{ getRelativeTime(question.created_at) }}
                              </time>
                            </small>
                          </div>
                        </div>
  
                        <!-- Действия (для автора) -->
                        <div v-if="canEditQuestion" class="question-actions">
                          <div class="btn-group" role="group">
                            <router-link
                              :to="{ name: 'EditQuestion', params: { id: question.id } }"
                              class="btn btn-outline-secondary btn-sm"
                            >
                              <i class="bi bi-pencil me-1"></i>
                              Редактировать
                            </router-link>
                            <button
                              class="btn btn-outline-danger btn-sm"
                              @click="handleDeleteQuestion"
                              :disabled="isDeletingQuestion"
                            >
                              <span v-if="isDeletingQuestion" class="spinner-border spinner-border-sm me-1" role="status"></span>
                              <i v-else class="bi bi-trash me-1"></i>
                              Удалить
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
  
          <!-- Раздел ответов -->
          <div class="answers-section">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h2 class="answers-title">
                {{ question.answers_count || 0 }} {{ getAnswersText(question.answers_count || 0) }}
              </h2>
              <div v-if="question.answers && question.answers.length > 1" class="sort-answers">
                <select class="form-select form-select-sm" v-model="answersSortOrder" @change="sortAnswers">
                  <option value="votes">По популярности</option>
                  <option value="date_new">По дате (новые)</option>
                  <option value="date_old">По дате (старые)</option>
                </select>
              </div>
            </div>
  
            <!-- Список ответов -->
            <div v-if="sortedAnswers.length > 0" class="answers-list">
              <AnswerCard
                v-for="answer in sortedAnswers"
                :key="answer.id"
                :answer="answer"
                :question-author-id="question.author_id"
                @vote="handleAnswerVote"
                @accept="handleAcceptAnswer"
                @unaccept="handleUnacceptAnswer"
                @update="handleUpdateAnswer"
                @delete="handleDeleteAnswer"
              />
            </div>
  
            <!-- Форма добавления ответа -->
            <div v-if="authStore.isLoggedIn" class="answer-form-section mt-5">
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-light">
                    <h5 class="mb-0">
                      <i class="bi bi-chat-left-text me-2"></i>
                      Ваш ответ
                    </h5>
                  </div>
                  <div class="card-body">
                    <AnswerForm
                      :question-id="question.id"
                      :is-loading="isCreatingAnswer"
                      :error="answerFormError"
                      @submit="handleCreateAnswer"
                      @clear-error="answerFormError = null"
                    />
                  </div>
                </div>
              </div>
  
            <!-- Призыв к авторизации -->
            <div v-else class="auth-prompt text-center py-4">
              <p class="text-muted mb-3">Войдите в систему, чтобы ответить на вопрос</p>
              <router-link to="/login" class="btn btn-primary me-2">
                <i class="bi bi-box-arrow-in-right me-2"></i>
                Войти
              </router-link>
              <router-link to="/register" class="btn btn-outline-primary">
                <i class="bi bi-person-plus me-2"></i>
                Регистрация
              </router-link>
            </div>
          </div>
  
          <!-- Похожие вопросы -->
          <div v-if="similarQuestions.length > 0" class="similar-questions mt-5">
            <h3 class="mb-4">Похожие вопросы</h3>
            <div class="row g-3">
              <div 
                v-for="similarQuestion in similarQuestions.slice(0, 3)" 
                :key="similarQuestion.id" 
                class="col-md-4"
              >
                <router-link 
                  :to="{ name: 'QuestionDetails', params: { id: similarQuestion.id } }" 
                  class="similar-question-card text-decoration-none"
                >
                  <div class="card h-100 border-0 shadow-sm">
                    <div class="card-body">
                      <h6 class="card-title">{{ similarQuestion.title }}</h6>
                      <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                          {{ similarQuestion.answers_count || 0 }} ответов
                        </small>
                        <span 
                          v-if="similarQuestion.is_solved" 
                          class="badge bg-success"
                        >
                          Решен
                        </span>
                      </div>
                    </div>
                  </div>
                </router-link>
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
  import { useQuestionsStore } from '../store/questionsStore';
  import { useAuthStore } from '../../auth/store/authStore';
  import VotingButtons from '../components/VotingButtons.vue';
  import AnswerCard from '../components/AnswerCard.vue';
  import AnswerForm from '../components/AnswerForm.vue';
  
  const route = useRoute();
  const router = useRouter();
  const questionsStore = useQuestionsStore();
  const authStore = useAuthStore();
  
  // Состояние компонента
  const isLoading = ref(false);
  const error = ref(null);
  const isVoting = ref(false);
  const isDeletingQuestion = ref(false);
  const isCreatingAnswer = ref(false);
  const answerFormError = ref(null);
  const answersSortOrder = ref('votes');
  const similarQuestions = ref([]);
  
  // Вычисляемые свойства
  const question = computed(() => questionsStore.currentQuestion);
  
  const canEditQuestion = computed(() => {
    return authStore.isLoggedIn && 
           authStore.user && 
           question.value &&
           authStore.user.id === question.value.author_id;
  });
  
  const sortedAnswers = computed(() => {
    if (!question.value?.answers) return [];
    
    const answers = [...question.value.answers];
    
    // Сначала всегда показываем принятый ответ
    answers.sort((a, b) => {
      if (a.is_accepted && !b.is_accepted) return -1;
      if (!a.is_accepted && b.is_accepted) return 1;
      
      // Затем сортируем по выбранному критерию
      switch (answersSortOrder.value) {
        case 'votes':
          return (b.votes_up - b.votes_down) - (a.votes_up - a.votes_down);
        case 'date_new':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'date_old':
          return new Date(a.created_at) - new Date(b.created_at);
        default:
          return 0;
      }
    });
    
    return answers;
  });
  
  // Инициализация при создании компонента
  onMounted(async () => {
    const questionId = route.params.id;
    if (!questionId) {
      router.push('/questions');
      return;
    }
    
    await loadQuestion();
    await loadSimilarQuestions();
  });
  
  // Методы
  async function loadQuestion() {
    const questionId = route.params.id;
    isLoading.value = true;
    error.value = null;
    
    try {
      await questionsStore.loadQuestionById(questionId);
      
      if (!questionsStore.currentQuestion) {
        error.value = 'Вопрос не найден';
      }
    } catch (e) {
      error.value = questionsStore.error || 'Не удалось загрузить вопрос';
      console.error('Ошибка при загрузке вопроса:', e);
    } finally {
      isLoading.value = false;
    }
  }
  
  async function loadSimilarQuestions() {
    if (!question.value) return;
    
    try {
      // Здесь должна быть логика загрузки похожих вопросов
      // Пока что используем заглушку
      similarQuestions.value = [];
    } catch (error) {
      console.error('Ошибка при загрузке похожих вопросов:', error);
    }
  }
  
  async function handleQuestionVote(voteData) {
    if (isVoting.value) return;
    
    isVoting.value = true;
    
    try {
      await questionsStore.voteForQuestion(voteData.itemId, voteData.voteType);
    } catch (error) {
      console.error('Ошибка при голосовании за вопрос:', error);
      alert('Ошибка при голосовании: ' + error.message);
    } finally {
      isVoting.value = false;
    }
  }
  
  async function handleAnswerVote(voteData) {
    try {
      await questionsStore.voteForAnswer(voteData.itemId, voteData.voteType);
    } catch (error) {
      console.error('Ошибка при голосовании за ответ:', error);
      alert('Ошибка при голосовании: ' + error.message);
    }
  }
  
  async function handleAcceptAnswer(answerId) {
    try {
      await questionsStore.acceptAnswer(answerId);
    } catch (error) {
      console.error('Ошибка при принятии ответа:', error);
      alert('Ошибка при принятии ответа: ' + error.message);
    }
  }
  
  async function handleUnacceptAnswer(answerId) {
    const confirmed = confirm('Вы уверены, что хотите отменить принятие этого ответа?');
    if (!confirmed) return;
    
    try {
      await questionsStore.unacceptAnswer(answerId);
    } catch (error) {
      console.error('Ошибка при отмене принятия ответа:', error);
      alert('Ошибка при отмене принятия ответа: ' + error.message);
    }
  }
  
    async function handleCreateAnswer(answerData) {
    if (isCreatingAnswer.value) return;
    
    isCreatingAnswer.value = true;
    answerFormError.value = null;
    
    try {
        await questionsStore.createAnswer(answerData);
        // Очищаем форму после успешного создания
        const answerForm = document.getElementById('answerBody');
        if (answerForm) {
        answerForm.value = '';
        }
    } catch (error) {
        console.error('Ошибка при создании ответа:', error);
        answerFormError.value = error.message || 'Не удалось создать ответ';
    } finally {
        isCreatingAnswer.value = false;
    }
    }
  
  async function handleUpdateAnswer(updateData) {
    try {
      await questionsStore.updateAnswer(updateData.id, updateData.data);
    } catch (error) {
      console.error('Ошибка при обновлении ответа:', error);
      alert('Ошибка при обновлении ответа: ' + error.message);
    }
  }
  
  async function handleDeleteAnswer(answerId) {
    const confirmed = confirm('Вы уверены, что хотите удалить этот ответ? Это действие нельзя отменить.');
    if (!confirmed) return;
    
    try {
      await questionsStore.deleteAnswer(answerId);
    } catch (error) {
      console.error('Ошибка при удалении ответа:', error);
      alert('Ошибка при удалении ответа: ' + error.message);
    }
  }
  
  async function handleDeleteQuestion() {
    if (isDeletingQuestion.value) return;
    
    const confirmed = confirm('Вы уверены, что хотите удалить этот вопрос? Это действие нельзя отменить.');
    if (!confirmed) return;
    
    isDeletingQuestion.value = true;
    
    try {
      await questionsStore.deleteQuestion(question.value.id);
      router.push('/questions');
    } catch (error) {
      console.error('Ошибка при удалении вопроса:', error);
      alert('Ошибка при удалении вопроса: ' + error.message);
    } finally {
      isDeletingQuestion.value = false;
    }
  }
  
  function sortAnswers() {
    // Метод вызывается при изменении сортировки
    // sortedAnswers автоматически пересчитается
  }
  
  // Вспомогательные функции
  function formatQuestionBody(body) {
    if (!body) return '';
    
    return body
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');
  }
  
  function getViewsText(count) {
    if (count === 0 || count === 1) return 'просмотр';
    if (count >= 2 && count <= 4) return 'просмотра';
    return 'просмотров';
  }
  
  function getAnswersText(count) {
    if (count === 0) return 'ответов';
    if (count === 1) return 'ответ';
    if (count >= 2 && count <= 4) return 'ответа';
    return 'ответов';
  }
  
  function getRelativeTime(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now - date;
    const diffInSeconds = Math.floor(diffInMs / 1000);
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    
    if (diffInDays > 7) {
      return date.toLocaleDateString('ru-RU');
    } else if (diffInDays > 0) {
      return `${diffInDays} ${diffInDays === 1 ? 'день' : diffInDays <= 4 ? 'дня' : 'дней'} назад`;
    } else if (diffInHours > 0) {
      return `${diffInHours} ${diffInHours === 1 ? 'час' : diffInHours <= 4 ? 'часа' : 'часов'} назад`;
    } else if (diffInMinutes > 0) {
      return `${diffInMinutes} ${diffInMinutes === 1 ? 'минуту' : diffInMinutes <= 4 ? 'минуты' : 'минут'} назад`;
    } else {
      return 'только что';
    }
  }
  
  function getFullDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
  }
  
  // Наблюдаем за изменениями ID в URL
  watch(() => route.params.id, async (newId) => {
    if (newId && newId !== String(question.value?.id)) {
      await loadQuestion();
      await loadSimilarQuestions();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  });
  </script>
  
  <style scoped>
  .question-details-page {
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
  
  .question-title {
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 0;
  }
  
  .voting-section {
    flex-shrink: 0;
  }
  
  .question-content {
    min-width: 0;
  }
  
  .question-body {
    margin: 1.5rem 0;
  }
  
  .formatted-content {
    line-height: 1.7;
    font-size: 1rem;
  }
  
  .formatted-content p {
    margin-bottom: 1rem;
  }
  
  .formatted-content p:last-child {
    margin-bottom: 0;
  }
  
  .related-plant {
    padding: 1rem;
    background-color: rgba(var(--bs-primary-rgb), 0.05);
    border-radius: 0.5rem;
    border: 1px solid rgba(var(--bs-primary-rgb), 0.1);
  }
  
  .plant-link:hover {
    background-color: rgba(var(--bs-primary-rgb), 0.1);
    border-radius: 0.375rem;
    padding: 0.5rem;
    margin: -0.5rem;
    transition: all 0.2s ease;
  }
  
  .question-meta {
    font-size: 0.9rem;
  }
  
  .answers-title {
    font-size: 1.5rem;
    font-weight: 600;
  }
  
  .answers-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .similar-question-card {
    display: block;
    transition: transform 0.3s ease;
  }
  
  .similar-question-card:hover {
    transform: translateY(-5px);
  }
  
  .similar-question-card:hover .card {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
  }
  
  .auth-prompt {
    border: 2px dashed #dee2e6;
    border-radius: 0.5rem;
    padding: 2rem;
    margin-top: 2rem;
  }
  
  /* Анимации */
  .question-detail-card,
  .answers-section,
  .similar-questions {
    animation: fadeInUp 0.5s ease;
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Мобильная адаптивность */
  @media (max-width: 768px) {
    .question-title {
      font-size: 1.5rem;
    }
    
    .card-body .d-flex {
      flex-direction: column;
    }
    
    .voting-section {
      align-self: stretch;
      margin-bottom: 1rem;
      margin-right: 0;
    }
    
    .voting-section .voting-buttons {
      flex-direction: row;
      justify-content: center;
      width: 100%;
    }
    
    .voting-section .voting-buttons > * {
      margin: 0 0.5rem;
    }
    
    .question-meta {
      flex-direction: column;
      gap: 0.75rem;
    }
    
    .question-actions {
      align-self: stretch;
    }
    
    .question-actions .btn-group {
      width: 100%;
    }
    
    .question-actions .btn {
      flex: 1;
    }
  }
  
  /* Стилизация состояний загрузки */
  .answers-list .loading-shimmer {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
  }
  
  @keyframes loading {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }
  
  /* Улучшенные стили для карточек */
  .card {
    transition: all 0.3s ease;
  }
  
  .card:hover {
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  /* Стили для выделения принятого ответа */
  .accepted-answer {
    border-left: 4px solid #28a745;
    background-color: rgba(40, 167, 69, 0.05);
  }
  </style>