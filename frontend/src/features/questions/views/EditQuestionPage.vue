<!-- frontend/src/features/questions/views/EditQuestionPage.vue -->
<template>
    <div class="edit-question-page">
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
              <li class="breadcrumb-item">
                <router-link v-if="question" :to="{ name: 'QuestionDetails', params: { id: question.id } }">
                  {{ questionTitle }}
                </router-link>
                <span v-else>Вопрос</span>
              </li>
              <li class="breadcrumb-item active" aria-current="page">
                Редактирование
              </li>
            </ol>
          </nav>
        </div>
      </div>
    
      <div class="container py-4">
        <div class="row justify-content-center">
          <div class="col-lg-10">
            <!-- Page header -->
            <div class="mb-4">
              <h1 class="h2 mb-2">Редактирование вопроса</h1>
              <p class="text-muted">Вы можете отредактировать заголовок и содержание вашего вопроса</p>
            </div>
          
            <!-- Loading -->
            <div v-if="isLoading && !question" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
              <p class="mt-3 text-muted">Загрузка вопроса...</p>
            </div>
            
            <!-- Authorization error -->
            <div v-else-if="authError" class="alert alert-danger">
              <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
                <div>
                  <h5 class="alert-heading">Ошибка доступа</h5>
                  <p class="mb-0">{{ authError }}</p>
                  <div class="mt-3">
                    <router-link :to="{ name: 'QuestionsList' }" class="btn btn-outline-secondary">
                      К списку вопросов
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Error message -->
            <div v-else-if="error" class="alert alert-danger mb-4">
              <div class="d-flex align-items-center">
                <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
                <div>
                  <h5 class="alert-heading">Ошибка при загрузке вопроса</h5>
                  <p class="mb-0">{{ error }}</p>
                  <div class="mt-3">
                    <button @click="loadQuestion" class="btn btn-outline-danger me-2">
                      Попробовать снова
                    </button>
                    <router-link :to="{ name: 'QuestionsList' }" class="btn btn-outline-secondary">
                      К списку вопросов
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Success message -->
            <div v-else-if="isSuccess" class="alert alert-success mb-4">
              <div class="d-flex align-items-center">
                <i class="bi bi-check-circle-fill fs-4 me-3"></i>
                <div>
                  <h5 class="alert-heading">Вопрос успешно обновлен!</h5>
                  <p class="mb-0">Ваш вопрос был успешно отредактирован. Сейчас вы будете перенаправлены на страницу вопроса.</p>
                </div>
              </div>
            </div>
            
            <!-- Question form -->
            <template v-else-if="question">
              <QuestionForm
                :initial-data="question"
                :is-loading="isSubmitting"
                :error="formError"
                @submit="handleUpdateQuestion"
                @cancel="handleCancel"
              />
            </template>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { useAuthStore } from '../../auth/store/authStore';
  import { useQuestionsStore } from '../store/questionsStore';
  import QuestionForm from '../components/QuestionForm.vue';
  
  const route = useRoute();
  const router = useRouter();
  const authStore = useAuthStore();
  const questionsStore = useQuestionsStore();
  
  // Component state
  const question = ref(null);
  const isLoading = ref(false);
  const isSubmitting = ref(false);
  const error = ref(null);
  const formError = ref(null);
  const authError = ref(null);
  const isSuccess = ref(false);
  
  // Computed properties
  const questionTitle = computed(() => {
    if (!question.value) return 'Загрузка...';
    return question.value.title.length > 50 
      ? question.value.title.substring(0, 50) + '...' 
      : question.value.title;
  });
  
  // Initialize component
  onMounted(async () => {
    const questionId = parseInt(route.params.id);
    if (!questionId) {
      error.value = 'Не указан ID вопроса';
      return;
    }
    
    await loadQuestion();
  });
  
  // Methods
  async function loadQuestion() {
    const questionId = parseInt(route.params.id);
    if (!questionId) {
      error.value = 'Не указан ID вопроса';
      return;
    }
    
    isLoading.value = true;
    error.value = null;
    authError.value = null;
    
    try {
      await questionsStore.loadQuestionById(questionId);
      question.value = questionsStore.currentQuestion;
      
      // Check if user is the author of the question
      if (!authStore.isLoggedIn) {
        authError.value = 'Для редактирования вопроса необходимо войти в систему';
        return;
      }
      
      if (question.value.author_id !== authStore.user.id) {
        authError.value = 'Вы можете редактировать только свои собственные вопросы';
        return;
      }
    } catch (e) {
      error.value = 'Не удалось загрузить вопрос';
      console.error('Error loading question:', e);
    } finally {
      isLoading.value = false;
    }
  }
  
  async function handleUpdateQuestion(questionData) {
    isSubmitting.value = true;
    formError.value = null;
    
    try {
      // Update question
      await questionsStore.updateQuestion(question.value.id, questionData);
      
      // Show success message
      isSuccess.value = true;
      
      // Wait a moment before redirecting
      setTimeout(() => {
        router.push({ name: 'QuestionDetails', params: { id: question.value.id } });
      }, 1500);
    } catch (e) {
      // Set error messages
      formError.value = e.message || 'Не удалось обновить вопрос';
      console.error('Error updating question:', e);
    } finally {
      isSubmitting.value = false;
    }
  }
  
  function handleCancel() {
    // Redirect back to question details
    router.push({ 
      name: 'QuestionDetails', 
      params: { id: question.value.id } 
    });
  }
  </script>
  
  <style scoped>
  .edit-question-page {
    min-height: calc(100vh - 300px);
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
  
  /* Animations */
  .alert {
    animation: fadeIn 0.5s ease;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  </style>