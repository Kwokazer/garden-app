<!-- frontend/src/features/questions/components/AnswerForm.vue -->
<template>
    <div class="answer-form">
      <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
        <!-- Текст ответа -->
        <div class="mb-3">
          <label for="answerBody" class="form-label">
            {{ isEditing ? 'Редактирование ответа' : 'Ваш ответ' }}
            <span class="text-danger">*</span>
          </label>
          <textarea
            id="answerBody"
            v-model="formData.body"
            class="form-control"
            :class="{ 'is-invalid': errors.body }"
            rows="6"
            placeholder="Напишите подробный и полезный ответ на вопрос..."
            required
            :disabled="isLoading"
          ></textarea>
          <div v-if="errors.body" class="invalid-feedback">
            {{ errors.body }}
          </div>
          <div class="form-text">
            Минимум 10 символов. Поддерживается простая разметка: **жирный текст**, *курсив*
          </div>
        </div>
        
        <!-- Кнопки действий -->
        <div class="form-actions d-flex justify-content-between">
          <div class="form-info">
            <small class="text-muted">
              <i class="bi bi-info-circle me-1"></i>
              Ваш ответ поможет другим пользователям решить их проблемы
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
        
        <!-- Предпросмотр (опционально) -->
        <div v-if="showPreview && formData.body" class="answer-preview mt-3">
          <div class="card bg-light">
            <div class="card-header py-2">
              <h6 class="mb-0">
                <i class="bi bi-eye me-2"></i>
                Предпросмотр
              </h6>
            </div>
            <div class="card-body">
              <div v-html="formatPreview(formData.body)" class="preview-content"></div>
            </div>
          </div>
        </div>
      </form>
    </div>
  </template>
  
  <script setup>
import { reactive, computed, watch } from 'vue';

const props = defineProps({
  questionId: {
    type: Number,
    default: null
  },
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
  showPreview: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['submit', 'cancel', 'clear-error']);

// Определяем, является ли форма редактированием
const isEditing = computed(() => !!props.initialData.body);

// Текст кнопки отправки
const submitButtonText = computed(() => {
  return isEditing.value ? 'Сохранить изменения' : 'Отправить ответ';
});

// Данные формы
const formData = reactive({
  body: props.initialData.body || '',
  question_id: props.questionId || props.initialData.question_id
});

// Ошибки валидации
const errors = reactive({
  body: null
});

// Наблюдаем за изменениями в initialData
watch(() => props.initialData, (newData) => {
  formData.body = newData.body || '';
  formData.question_id = props.questionId || newData.question_id;
}, { deep: true });

// Валидация формы
const isFormValid = computed(() => {
  return formData.body.trim().length >= 10;
});

// Методы
function validateForm() {
  errors.body = null;
  
  // Валидация текста ответа
  if (!formData.body.trim()) {
    errors.body = 'Текст ответа обязателен';
    return false;
  }
  
  if (formData.body.trim().length < 10) {
    errors.body = 'Ответ должен содержать минимум 10 символов';
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

function clearFieldError(field) {
  errors[field] = null;
  emit('clear-error');
}

function handleSubmit() {
  if (!validateForm()) {
    return;
  }
  
  const submitData = {
    body: formData.body.trim(),
    question_id: formData.question_id
  };
  
  emit('submit', submitData);
}

function handleCancel() {
  // Сбрасываем форму к начальным значениям
  formData.body = props.initialData.body || '';
  formData.question_id = props.questionId || props.initialData.question_id;
  errors.body = null;
  
  emit('cancel');
}

// Очистка ошибок при изменении полей
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