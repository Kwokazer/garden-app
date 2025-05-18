<!-- frontend/src/features/questions/components/QuestionForm.vue -->
<template>
    <div class="question-form">
      <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
        <div v-if="error" class="alert alert-danger" role="alert">
          {{ error }}
        </div>
        
        <!-- Подсказки -->
        <div class="form-hint">
          <div class="hint-title">
            <i class="bi bi-lightbulb me-2"></i>
            Советы по написанию хорошего вопроса
          </div>
          <ul>
            <li>Используйте четкий и описательный заголовок</li>
            <li>Подробно опишите проблему и что вы уже пробовали</li>
            <li>Приложите фотографии, если это поможет</li>
            <li>Укажите растение, если вопрос связан с конкретным видом</li>
          </ul>
        </div>
        
        <!-- Заголовок вопроса -->
        <div class="mb-3">
          <label for="questionTitle" class="form-label">
            Заголовок вопроса
            <span class="text-danger">*</span>
          </label>
          <input
            type="text"
            class="form-control"
            id="questionTitle"
            v-model="formData.title"
            :class="{ 'is-invalid': errors.title }"
            placeholder="Кратко опишите вашу проблему или вопрос"
            required
            :disabled="isLoading"
            @input="clearFieldError('title')"
          >
          <div v-if="errors.title" class="invalid-feedback">
            {{ errors.title }}
          </div>
          <div class="title-counter" :class="{ 'limit-reached': formData.title.length > 255 }">
            {{ formData.title.length }} / 255
          </div>
        </div>
        
        <!-- Связанное растение -->
        <div class="mb-3">
          <label for="plantSelect" class="form-label">
            Связанное растение (необязательно)
          </label>
          <div class="plant-select-wrapper">
            <select
              class="form-select"
              id="plantSelect"
              v-model="formData.plant_id"
              :disabled="isLoading || isLoadingPlants"
            >
              <option :value="null">Выберите растение (необязательно)</option>
              <option 
                v-for="plant in plants" 
                :key="plant.id" 
                :value="plant.id"
              >
                {{ plant.name }}
              </option>
            </select>
            <div v-if="isLoadingPlants" class="plant-select-loading">
              <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Загрузка...</span>
              </div>
            </div>
          </div>
          <div class="form-text">
            Выберите растение, если ваш вопрос связан с конкретным видом
          </div>
          <!-- Выбранное растение -->
          <div v-if="selectedPlant" class="selected-plant">
            <strong>{{ selectedPlant.name }}</strong>
            <small class="text-muted d-block">{{ selectedPlant.latin_name }}</small>
          </div>
        </div>
        
        <!-- Описание вопроса -->
        <div class="mb-3">
          <label for="questionBody" class="form-label">
            Подробное описание вопроса
            <span class="text-danger">*</span>
          </label>
          <textarea
            id="questionBody"
            v-model="formData.body"
            class="form-control"
            :class="{ 'is-invalid': errors.body }"
            rows="8"
            placeholder="Подробно опишите вашу проблему. Что вы наблюдаете? Что уже пробовали? Какие условия содержания?"
            required
            :disabled="isLoading"
            @input="clearFieldError('body')"
          ></textarea>
          <div v-if="errors.body" class="invalid-feedback">
            {{ errors.body }}
          </div>
          <div class="form-text">
            Минимум 10 символов. Поддерживается простая разметка: **жирный текст**, *курсив*
          </div>
        </div>
        
        <!-- Предпросмотр -->
        <div class="mb-3">
          <button
            type="button"
            class="btn btn-outline-secondary btn-sm"
            @click="togglePreview"
          >
            <i class="bi" :class="isPreviewVisible ? 'bi-eye-slash' : 'bi-eye'"></i>
            {{ isPreviewVisible ? 'Скрыть предпросмотр' : 'Показать предпросмотр' }}
          </button>
        </div>
        
        <!-- Предпросмотр (опционально) -->
        <div v-if="isPreviewVisible" class="question-preview mb-4">
          <div class="card bg-light">
            <div class="card-header py-2">
              <h6 class="mb-0">
                <i class="bi bi-eye me-2"></i>
                Предпросмотр вопроса
              </h6>
            </div>
            <div class="card-body">
              <h5 class="preview-title">{{ formData.title || 'Заголовок вопроса' }}</h5>
              <div v-html="formatPreview(formData.body)" class="preview-content"></div>
              <div v-if="selectedPlant" class="preview-plant">
                <small class="text-muted">
                  <i class="bi bi-flower1 me-1"></i>
                  Связанное растение: {{ selectedPlant.name }}
                </small>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Действия формы -->
        <div class="form-actions">
          <div class="form-info">
            <small class="text-muted">
              <i class="bi bi-info-circle me-1"></i>
              {{ isEditing ? 'Обновите ваш вопрос' : 'Ваш вопрос будет отправлен на модерацию' }}
            </small>
          </div>
          
          <div class="button-group">
            <button
              v-if="showCancel"
              type="button"
              class="btn btn-outline-secondary me-2"
              @click="handleCancel"
              :disabled="isLoading"
            >
              Отмена
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isLoading || !isFormValid"
            >
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              <i v-else class="bi bi-send me-2"></i>
              {{ submitButtonText }}
            </button>
          </div>
        </div>
      </form>
    </div>
  </template>
  
  <script setup>
  import { reactive, computed, watch, onMounted, ref } from 'vue';
  import { usePlantsStore } from '../../plants/store/plantsStore';
  
  const props = defineProps({
    initialData: {
      type: Object,
      default: () => ({})
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    showCancel: {
      type: Boolean,
      default: true
    },
    error: {
      type: String,
      default: null
    }
  });
  
  const emit = defineEmits(['submit', 'cancel']);
  
  // Зависимости
  const plantsStore = usePlantsStore();
  
  // Определяем, является ли форма редактированием
  const isEditing = computed(() => !!props.initialData.id);
  
  // Текст кнопки отправки
  const submitButtonText = computed(() => {
    return isEditing.value ? 'Сохранить изменения' : 'Задать вопрос';
  });
  
  // Состояние компонента
  const isPreviewVisible = ref(false);
  const isLoadingPlants = ref(false);
  const plants = ref([]);
  
  // Данные формы
  const formData = reactive({
    title: props.initialData.title || '',
    body: props.initialData.body || '',
    plant_id: props.initialData.plant_id || null
  });
  
  // Ошибки валидации
  const errors = reactive({
    title: null,
    body: null
  });
  
  // Вычисляемые свойства
  const isFormValid = computed(() => {
    return formData.title.trim().length >= 5 &&
           formData.title.trim().length <= 255 &&
           formData.body.trim().length >= 10;
  });
  
  const selectedPlant = computed(() => {
    if (!formData.plant_id) return null;
    return plants.value.find(plant => plant.id === formData.plant_id);
  });
  
  // Наблюдаем за изменениями в initialData
  watch(() => props.initialData, (newData) => {
    formData.title = newData.title || '';
    formData.body = newData.body || '';
    formData.plant_id = newData.plant_id || null;
  }, { deep: true });
  
  // Инициализация при создании компонента
  onMounted(async () => {
    await loadPlants();
  });
  
  // Методы
  async function loadPlants() {
    isLoadingPlants.value = true;
    try {
      // Загружаем список растений для выпадающего списка
      await plantsStore.loadPlants(1, 100); // Загружаем первые 100 растений
      plants.value = plantsStore.plants.filter(plant => plant.name); // Фильтруем только с названиями
    } catch (error) {
      console.error('Ошибка при загрузке растений:', error);
    } finally {
      isLoadingPlants.value = false;
    }
  }
  
  function clearFieldError(field) {
    errors[field] = null;
  }
  
  function validateForm() {
    errors.title = null;
    errors.body = null;
    
    // Валидация заголовка
    if (!formData.title.trim()) {
      errors.title = 'Заголовок вопроса обязателен';
      return false;
    }
    
    if (formData.title.trim().length < 5) {
      errors.title = 'Заголовок должен содержать минимум 5 символов';
      return false;
    }
    
    if (formData.title.trim().length > 255) {
      errors.title = 'Заголовок не должен превышать 255 символов';
      return false;
    }
    
    // Валидация текста вопроса
    if (!formData.body.trim()) {
      errors.body = 'Описание вопроса обязательно';
      return false;
    }
    
    if (formData.body.trim().length < 10) {
      errors.body = 'Описание должно содержать минимум 10 символов';
      return false;
    }
    
    return true;
  }
  
  function formatPreview(text) {
    if (!text) return '';
    
    return text
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');
  }
  
  function togglePreview() {
    isPreviewVisible.value = !isPreviewVisible.value;
  }
  
  function handleSubmit() {
    if (!validateForm()) {
      return;
    }
    
    const submitData = {
      title: formData.title.trim(),
      body: formData.body.trim(),
      plant_id: formData.plant_id
    };
    
    emit('submit', submitData);
  }
  
  function handleCancel() {
    // Сбрасываем форму к начальным значениям
    formData.title = props.initialData.title || '';
    formData.body = props.initialData.body || '';
    formData.plant_id = props.initialData.plant_id || null;
    errors.title = null;
    errors.body = null;
    isPreviewVisible.value = false;
    
    emit('cancel');
  }
  
  // Очистка ошибок при изменении полей
  watch(() => formData.title, () => {
    if (errors.title) {
      errors.title = null;
    }
  });
  
  watch(() => formData.body, () => {
    if (errors.body) {
      errors.body = null;
    }
  });
  </script>
  
  <style scoped>
  .question-form {
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 2rem;
    border: 1px solid #e9ecef;
  }
  
  .form-label {
    font-weight: 600;
    color: #333;
  }
  
  .form-control,
  .form-select {
    border-radius: 0.375rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
  }
  
  .form-control:focus,
  .form-select:focus {
    border-color: var(--bs-primary);
    box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
  }
  
  .form-text {
    color: #6c757d;
    font-size: 0.875rem;
  }
  
  /* Стилизация селекта растений */
  .plant-select-wrapper {
    position: relative;
  }
  
  .plant-select-loading {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
  }
  
  /* Предпросмотр */
  .question-preview {
    animation: fadeIn 0.3s ease;
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
  
  .preview-title {
    color: #333;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  
  .preview-content {
    line-height: 1.6;
    color: #333;
  }
  
  .preview-content p {
    margin-bottom: 1rem;
  }
  
  .preview-content p:last-child {
    margin-bottom: 0;
  }
  
  .preview-plant {
    border-top: 1px solid #e9ecef;
    padding-top: 0.75rem;
  }
  
  /* Действия формы */
  .form-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e9ecef;
  }
  
  .form-info {
    flex: 1;
  }
  
  .button-group {
    display: flex;
    align-items: center;
  }
  
  .btn {
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.3s ease;
  }
  
  .btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  /* Валидация */
  .is-invalid {
    border-color: #dc3545;
  }
  
  .invalid-feedback {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  /* Мобильная адаптивность */
  @media (max-width: 768px) {
    .question-form {
      padding: 1.5rem;
    }
    
    .form-actions {
      flex-direction: column;
      align-items: stretch;
      gap: 1rem;
    }
    
    .form-info {
      text-align: center;
    }
    
    .button-group {
      justify-content: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    
    .button-group .btn {
      min-width: 120px;
    }
  }
  
  /* Анимация появления формы */
  .question-form {
    animation: slideInUp 0.5s ease;
  }
  
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* Улучшенная стилизация полей */
  .form-control,
  .form-select {
    font-size: 0.95rem;
  }
  
  .form-control[type="text"] {
    height: calc(1.5em + 0.75rem + 2px);
  }
  
  textarea.form-control {
    resize: vertical;
    min-height: 200px;
  }
  
  /* Счетчик символов для заголовка */
  .title-counter {
    text-align: right;
    font-size: 0.8rem;
    color: #6c757d;
    margin-top: 0.25rem;
  }
  
  .title-counter.limit-reached {
    color: #dc3545;
    font-weight: 600;
  }
  
  /* Стилизация выбранного растения */
  .selected-plant {
    margin-top: 0.5rem;
    padding: 0.5rem;
    background-color: rgba(var(--bs-primary-rgb), 0.1);
    border-radius: 0.375rem;
    border: 1px solid rgba(var(--bs-primary-rgb), 0.2);
  }
  
  /* Подсказки */
  .form-hint {
    background-color: #e3f2fd;
    border: 1px solid #b3e5fc;
    border-radius: 0.375rem;
    padding: 1rem;
    margin-bottom: 1.5rem;
  }
  
  .form-hint .hint-title {
    font-weight: 600;
    color: #1976d2;
    margin-bottom: 0.5rem;
  }
  
  .form-hint ul {
    margin-bottom: 0;
    padding-left: 1.5rem;
  }
  
  .form-hint li {
    color: #424242;
    margin-bottom: 0.25rem;
  }
  </style>