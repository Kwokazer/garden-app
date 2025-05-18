<!-- frontend/src/features/questions/views/CreateQuestionPage.vue -->
<template>
    <div class="create-question-page">
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
                Задать вопрос
              </li>
            </ol>
          </nav>
        </div>
      </div>
    
      <div class="container py-4">
        <div class="row justify-content-center">
          <div class="col-lg-10">
            <!-- Page header -->
            <div class="mb-4 text-center">
              <h1 class="display-6 mb-2">Задать вопрос</h1>
              <p class="text-muted">Поделитесь своим вопросом и получите помощь от сообщества садоводов</p>
            </div>
          
            <!-- Login prompt for unauthorized users -->
            <div v-if="!authStore.isLoggedIn" class="alert alert-info d-flex align-items-center mb-4">
              <i class="bi bi-info-circle-fill fs-4 me-3"></i>
              <div>
                <h5 class="alert-heading">Необходима авторизация</h5>
                <p class="mb-0">Чтобы задать вопрос, необходимо войти в систему.</p>
                <div class="mt-3">
                  <router-link to="/login" class="btn btn-primary me-2">
                    <i class="bi bi-box-arrow-in-right me-1"></i>
                    Войти
                  </router-link>
                  <router-link to="/register" class="btn btn-outline-primary">
                    <i class="bi bi-person-plus me-1"></i>
                    Регистрация
                  </router-link>
                </div>
              </div>
            </div>
          
            <!-- Question form for authorized users -->
            <template v-else>
              <!-- Error message -->
              <div v-if="error" class="alert alert-danger mb-4">
                <div class="d-flex align-items-center">
                  <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
                  <div>
                    <h5 class="alert-heading">Ошибка при создании вопроса</h5>
                    <p class="mb-0">{{ error }}</p>
                  </div>
                </div>
              </div>
              
              <!-- Success message -->
              <div v-if="isSuccess" class="alert alert-success mb-4">
                <div class="d-flex align-items-center">
                  <i class="bi bi-check-circle-fill fs-4 me-3"></i>
                  <div>
                    <h5 class="alert-heading">Вопрос успешно создан!</h5>
                    <p class="mb-0">Ваш вопрос был успешно опубликован. Сейчас вы будете перенаправлены на страницу вопроса.</p>
                  </div>
                </div>
              </div>
              
              <!-- Question form -->
              <QuestionForm
                :initial-data="{}"
                :is-loading="isLoading"
                :error="formError"
                @submit="handleCreateQuestion"
                @cancel="handleCancel"
              />
            </template>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { useAuthStore } from '../../auth/store/authStore';
  import { useQuestionsStore } from '../store/questionsStore';
  import QuestionForm from '../components/QuestionForm.vue';
  
  const router = useRouter();
  const authStore = useAuthStore();
  const questionsStore = useQuestionsStore();
  
  // Component state
  const isLoading = ref(false);
  const error = ref(null);
  const formError = ref(null);
  const isSuccess = ref(false);
  
  // Methods
  async function handleCreateQuestion(questionData) {
    if (!authStore.isLoggedIn) {
      error.value = 'Для создания вопроса необходимо войти в систему';
      return;
    }
    
    isLoading.value = true;
    error.value = null;
    formError.value = null;
    
    try {
      // Create question
      const question = await questionsStore.createQuestion(questionData);
      
      // Show success message
      isSuccess.value = true;
      
      // Wait a moment before redirecting
      setTimeout(() => {
        router.push({ name: 'QuestionDetails', params: { id: question.id } });
      }, 1500);
    } catch (e) {
      // Set error messages
      error.value = 'Не удалось создать вопрос';
      
      if (e.response?.data?.detail || e.message) {
        formError.value = e.response?.data?.detail || e.message;
      }
      
      console.error('Error creating question:', e);
    } finally {
      isLoading.value = false;
    }
  }
  
  function handleCancel() {
    // Redirect back to questions list
    router.push({ name: 'QuestionsList' });
  }
  </script>
  
  <style scoped>
  .create-question-page {
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