<template>
  <div class="webinar-form">
    <div class="form-header">
      <h2>{{ isEdit ? 'Редактировать вебинар' : 'Создать новый вебинар' }}</h2>
      <p class="form-subtitle">
        {{ isEdit ? 'Внесите изменения в ваш вебинар' : 'Заполните информацию о вебинаре' }}
      </p>
    </div>

    <form @submit.prevent="handleSubmit" class="form">
      <!-- Основная информация -->
      <div class="form-section">
        <h3 class="section-title">Основная информация</h3>
        
        <div class="form-group">
          <label for="title" class="form-label required">Название вебинара</label>
          <input
            id="title"
            v-model="form.title"
            type="text"
            class="form-input"
            :class="{ 'form-input--error': errors.title }"
            placeholder="Введите название вебинара"
            required
          />
          <span v-if="errors.title" class="form-error">{{ errors.title }}</span>
        </div>

        <div class="form-group">
          <label for="description" class="form-label">Описание</label>
          <textarea
            id="description"
            v-model="form.description"
            class="form-textarea"
            :class="{ 'form-input--error': errors.description }"
            placeholder="Опишите тему и содержание вебинара"
            rows="4"
          ></textarea>
          <span v-if="errors.description" class="form-error">{{ errors.description }}</span>
        </div>
      </div>

      <!-- Расписание -->
      <div class="form-section">
        <h3 class="section-title">Расписание</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="scheduled_at" class="form-label required">Дата и время проведения</label>
            <input
              id="scheduled_at"
              v-model="form.scheduled_at"
              type="datetime-local"
              class="form-input"
              :class="{ 'form-input--error': errors.scheduled_at }"
              :min="minDateTime"
              required
            />
            <span v-if="errors.scheduled_at" class="form-error">{{ errors.scheduled_at }}</span>
          </div>

          <div class="form-group">
            <label for="duration_minutes" class="form-label required">Длительность (минуты)</label>
            <input
              id="duration_minutes"
              v-model.number="form.duration_minutes"
              type="number"
              class="form-input"
              :class="{ 'form-input--error': errors.duration_minutes }"
              min="15"
              max="480"
              placeholder="60"
              required
            />
            <span v-if="errors.duration_minutes" class="form-error">{{ errors.duration_minutes }}</span>
          </div>
        </div>
      </div>

      <!-- Настройки -->
      <div class="form-section">
        <h3 class="section-title">Настройки</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="max_participants" class="form-label">Максимальное количество участников</label>
            <input
              id="max_participants"
              v-model.number="form.max_participants"
              type="number"
              class="form-input"
              :class="{ 'form-input--error': errors.max_participants }"
              min="2"
              max="1000"
              placeholder="Без ограничений"
            />
            <span v-if="errors.max_participants" class="form-error">{{ errors.max_participants }}</span>
          </div>

          <div class="form-group">
            <label for="plant_topic_id" class="form-label">Тема (растение)</label>
            <select
              id="plant_topic_id"
              v-model="form.plant_topic_id"
              class="form-select"
              :class="{ 'form-input--error': errors.plant_topic_id }"
            >
              <option value="">Выберите растение (опционально)</option>
              <option
                v-for="plant in plants"
                :key="plant.id"
                :value="plant.id"
              >
                {{ plant.name }}
              </option>
            </select>
            <span v-if="errors.plant_topic_id" class="form-error">{{ errors.plant_topic_id }}</span>
          </div>
        </div>

        <div class="form-group">
          <div class="checkbox-group">
            <input
              id="is_public"
              v-model="form.is_public"
              type="checkbox"
              class="form-checkbox"
            />
            <label for="is_public" class="checkbox-label">
              Публичный вебинар
              <span class="checkbox-description">
                Публичные вебинары видны всем пользователям и к ним можно присоединиться без приглашения
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Кнопки действий -->
      <div class="form-actions">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn btn--secondary"
          :disabled="isLoading"
        >
          Отмена
        </button>
        
        <button
          type="submit"
          class="btn btn--primary"
          :disabled="isLoading || !isFormValid"
        >
          <span v-if="isLoading" class="loading-spinner"></span>
          {{ isEdit ? 'Сохранить изменения' : 'Создать вебинар' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useWebinarsStore } from '../store/webinarsStore'
import { usePlantsStore } from '@/features/plants/store/plantsStore'

export default {
  name: 'WebinarForm',
  props: {
    webinar: {
      type: Object,
      default: null
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['submit', 'cancel'],
  setup(props, { emit }) {
    const webinarsStore = useWebinarsStore()
    const plantsStore = usePlantsStore()
    
    const form = ref({
      title: '',
      description: '',
      scheduled_at: '',
      duration_minutes: 60,
      max_participants: null,
      is_public: true,
      plant_topic_id: null
    })
    
    const errors = ref({})
    const plants = ref([])
    
    // Computed properties
    const isEdit = computed(() => !!props.webinar)
    
    const minDateTime = computed(() => {
      const now = new Date()
      now.setMinutes(now.getMinutes() + 30) // Минимум через 30 минут
      return now.toISOString().slice(0, 16)
    })
    
    const isFormValid = computed(() => {
      return form.value.title.trim() && 
             form.value.scheduled_at && 
             form.value.duration_minutes >= 15 &&
             Object.keys(errors.value).length === 0
    })
    
    // Methods
    const validateForm = () => {
      errors.value = {}
      
      if (!form.value.title.trim()) {
        errors.value.title = 'Название обязательно'
      } else if (form.value.title.length > 200) {
        errors.value.title = 'Название не должно превышать 200 символов'
      }
      
      if (!form.value.scheduled_at) {
        errors.value.scheduled_at = 'Дата и время обязательны'
      } else {
        const scheduledDate = new Date(form.value.scheduled_at)
        const now = new Date()
        if (scheduledDate <= now) {
          errors.value.scheduled_at = 'Дата должна быть в будущем'
        }
      }
      
      if (form.value.duration_minutes < 15 || form.value.duration_minutes > 480) {
        errors.value.duration_minutes = 'Длительность должна быть от 15 до 480 минут'
      }
      
      if (form.value.max_participants && (form.value.max_participants < 2 || form.value.max_participants > 1000)) {
        errors.value.max_participants = 'Количество участников должно быть от 2 до 1000'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const handleSubmit = () => {
      if (validateForm()) {
        const formData = { ...form.value }
        
        // Очищаем пустые значения
        if (!formData.description) formData.description = null
        if (!formData.max_participants) formData.max_participants = null
        if (!formData.plant_topic_id) formData.plant_topic_id = null
        
        emit('submit', formData)
      }
    }
    
    const loadPlants = async () => {
      try {
        await plantsStore.loadPlants(1, 100) // Загружаем первые 100 растений
        plants.value = plantsStore.getPlants
      } catch (error) {
        console.error('Error loading plants:', error)
      }
    }
    
    const formatDateTimeForInput = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toISOString().slice(0, 16)
    }
    
    // Watchers
    watch(() => props.webinar, (newWebinar) => {
      if (newWebinar) {
        form.value = {
          title: newWebinar.title || '',
          description: newWebinar.description || '',
          scheduled_at: formatDateTimeForInput(newWebinar.scheduled_at),
          duration_minutes: newWebinar.duration_minutes || 60,
          max_participants: newWebinar.max_participants || null,
          is_public: newWebinar.is_public !== false,
          plant_topic_id: newWebinar.plant_topic_id || null
        }
      }
    }, { immediate: true })
    
    // Lifecycle
    onMounted(() => {
      loadPlants()
    })
    
    return {
      form,
      errors,
      plants,
      isEdit,
      minDateTime,
      isFormValid,
      handleSubmit,
      validateForm
    }
  }
}
</script>

<style scoped>
.webinar-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  color: #1a202c;
  margin-bottom: 8px;
}

.form-subtitle {
  color: #718096;
}

.form {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 32px;
}

.form-section {
  margin-bottom: 32px;
}

.section-title {
  color: #2d3748;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #4a5568;
}

.form-label.required::after {
  content: ' *';
  color: #e53e3e;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.form-input--error {
  border-color: #e53e3e;
}

.form-error {
  display: block;
  margin-top: 4px;
  color: #e53e3e;
  font-size: 0.875rem;
}

.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.form-checkbox {
  margin-top: 4px;
}

.checkbox-label {
  flex: 1;
  cursor: pointer;
}

.checkbox-description {
  display: block;
  margin-top: 4px;
  font-size: 0.875rem;
  color: #718096;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background-color: #28a745;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: #218838;
}

.btn--secondary {
  background-color: #edf2f7;
  color: #4a5568;
}

.btn--secondary:hover:not(:disabled) {
  background-color: #e2e8f0;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style>
