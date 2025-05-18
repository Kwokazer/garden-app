<!-- frontend/src/features/questions/components/AnswerForm.vue -->
<template>
    <div class="answer-form">
      <form @submit.prevent="handleSubmit" class="needs-validation" novalidate>
        <!-- Answer text -->
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
            @input="clearFieldError('body')"
          ></textarea>
          <div v-if="errors.body" class="invalid-feedback">
            {{ errors.body }}
          </div>
          <div class="form-text">
            Минимум 10 символов. Поддерживается простая разметка: **жирный текст**, *курсив*
          </div>
        </div>
        
        <!-- Preview button and preview -->
        <div v-if="showPreview" class="mb-3">
          <button
            type="button"
            class="btn btn-outline-secondary btn-sm"
            @click="togglePreview"
          >
            <i class="bi" :class="isPreviewVisible ? 'bi-eye-slash' : 'bi-eye'"></i>
            {{ isPreviewVisible ? 'Скрыть предпросмотр' : 'Показать предпросмотр' }}
          </button>
          
          <!-- Preview content -->
          <div v-if="isPreviewVisible" class="answer-preview mt-3">
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
        </div>
        
        <!-- Action buttons -->
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
      </form>
    </div>
  </template>
  
  <script setup>
  import { reactive, computed, ref, watch } from 'vue';
  
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
    }
  });
  
  const emit = defineEmits(['submit', 'cancel', 'clear-error']);
  
  // Determine if the form is for editing
  const isEditing = computed(() => !!props.initialData.body);
  
  // Preview visibility state
  const isPreviewVisible = ref(false);
  
  // Submit button text
  const submitButtonText = computed(() => {
    return isEditing.value ? 'Сохранить изменения' : 'Отправить ответ';
  });
  
  // Form data
  const formData = reactive({
    body: props.initialData.body || '',
    question_id: props.questionId || props.initialData.question_id
  });
  
  // Validation errors
  const errors = reactive({
    body: null
  });
  
  // Watch for changes in initialData
  watch(() => props.initialData, (newData) => {
    formData.body = newData.body || '';
    formData.question_id = props.questionId || newData.question_id;
  }, { deep: true });
  
  // Form validation
  const isFormValid = computed(() => {
    return formData.body.trim().length >= 10;
  });
  
  // Methods
  function validateForm() {
    errors.body = null;
    
    // Validate answer body
    if (!formData.body.trim()) {
      errors.body = 'Описание ответа обязательно';
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
  
  function togglePreview() {
    isPreviewVisible.value = !isPreviewVisible.value;
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
    // Reset form to initial values
    formData.body = props.initialData.body || '';
    formData.question_id = props.questionId || props.initialData.question_id;
    errors.body = null;
    isPreviewVisible.value = false;
    
    emit('cancel');
  }
  
  // Clear errors when body changes
  watch(() => formData.body, () => {
    if (errors.body) {
      errors.body = null;
    }
  });
  </script>
  
  <style scoped>
  .answer-form {
    width: 100%;
  }
  
  .form-label {
    font-weight: 600;
    color: #333;
  }
  
  .form-control {
    border-radius: 0.375rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
  }
  
  .form-control:focus {
    border-color: var(--bs-primary);
    box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
  }
  
  .form-text {
    color: #6c757d;
    font-size: 0.875rem;
  }
  
  /* Preview */
  .answer-preview {
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
  
  /* Form actions */
  .form-actions {
    align-items: center;
    margin-top: 1.5rem;
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
  
  /* Validation */
  .is-invalid {
    border-color: #dc3545;
  }
  
  .invalid-feedback {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
  
  /* Mobile responsiveness */
  @media (max-width: 768px) {
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
    }
  }
  
  textarea.form-control {
    resize: vertical;
    min-height: 120px;
  }
  </style>