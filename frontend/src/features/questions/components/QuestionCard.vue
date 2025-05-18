<!-- frontend/src/features/questions/components/QuestionCard.vue -->
<template>
    <div class="question-card card h-100 border-0 shadow-sm">
      <div class="card-body d-flex">
        <!-- Панель голосования -->
        <div class="voting-section me-3">
          <VotingButtons
            type="question"
            :item-id="question.id"
            :votes-up="question.votes_up"
            :votes-down="question.votes_down"
            :user-vote="question.user_vote"
            :is-loading="isVoting"
            :author-id="question.author_id"
            @vote="handleVote"
          />
        </div>
        
        <!-- Основное содержимое вопроса -->
        <div class="question-content flex-grow-1">
          <!-- Заголовок и статус -->
          <div class="d-flex justify-content-between align-items-start mb-2">
            <router-link 
              :to="{ name: 'QuestionDetails', params: { id: question.id } }"
              class="question-title-link"
            >
              <h5 class="question-title mb-1">{{ question.title }}</h5>
            </router-link>
            
            <!-- Статус решения -->
            <span 
              v-if="question.is_solved" 
              class="badge bg-success ms-2"
              title="Вопрос решен"
            >
              <i class="bi bi-check-circle me-1"></i>
              Решен
            </span>
          </div>
          
          <!-- Превью содержимого -->
          <p class="question-preview text-muted mb-3">
            {{ getQuestionPreview(question.body) }}
          </p>
          
          <!-- Метаинформация -->
          <div class="question-meta d-flex flex-wrap align-items-center">
            <!-- Связанное растение -->
            <router-link
              v-if="question.plant"
              :to="{ name: 'PlantDetails', params: { id: question.plant.id } }"
              class="plant-link me-3 mb-2"
            >
              <span class="badge bg-primary">
                <i class="bi bi-flower1 me-1"></i>
                {{ question.plant.name }}
              </span>
            </router-link>
            
            <!-- Количество ответов -->
            <span class="answers-count me-3 mb-2">
              <i class="bi bi-chat-dots me-1"></i>
              {{ question.answers_count || 0 }} 
              {{ getAnswersText(question.answers_count || 0) }}
            </span>
            
            <!-- Количество просмотров -->
            <span class="views-count me-3 mb-2 text-muted">
              <i class="bi bi-eye me-1"></i>
              {{ question.view_count || 0 }} 
              {{ getViewsText(question.view_count || 0) }}
            </span>
            
            <!-- Автор и дата -->
            <div class="author-info d-flex align-items-center mb-2">
              <small class="text-muted">
                Автор: 
                <span class="author-name">{{ question.author?.username || 'Неизвестно' }}</span>
                <span class="mx-1">•</span>
                <time :datetime="question.created_at" :title="getFullDate(question.created_at)">
                  {{ getRelativeTime(question.created_at) }}
                </time>
              </small>
            </div>
          </div>
          
          <!-- Действия (показываются только для автора) -->
          <div v-if="canEdit" class="question-actions mt-3">
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
                @click="handleDelete"
                :disabled="isDeleting"
              >
                <span v-if="isDeleting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                <i v-else class="bi bi-trash me-1"></i>
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Индикатор загрузки -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import { useAuthStore } from '../../auth/store/authStore';
  import { useQuestionsStore } from '../store/questionsStore';
  import VotingButtons from './VotingButtons.vue';
  
  const props = defineProps({
    question: {
      type: Object,
      required: true
    },
    showActions: {
      type: Boolean,
      default: true
    }
  });
  
  const emit = defineEmits(['vote', 'delete']);
  
  const authStore = useAuthStore();
  const questionsStore = useQuestionsStore();
  
  // Состояние компонента
  const isVoting = ref(false);
  const isDeleting = ref(false);
  const isLoading = ref(false);
  
  // Вычисляемые свойства
  const canEdit = computed(() => {
    return props.showActions && 
           authStore.isLoggedIn && 
           authStore.user && 
           authStore.user.id === props.question.author_id;
  });
  
  // Методы
  function getQuestionPreview(body, maxLength = 150) {
    if (!body) return '';
    if (body.length <= maxLength) return body;
    return body.substring(0, maxLength) + '...';
  }
  
  function getAnswersText(count) {
    if (count === 0) return 'ответов';
    if (count === 1) return 'ответ';
    if (count >= 2 && count <= 4) return 'ответа';
    return 'ответов';
  }
  
  function getViewsText(count) {
    if (count === 0) return 'просмотров';
    if (count === 1) return 'просмотр';
    if (count >= 2 && count <= 4) return 'просмотра';
    return 'просмотров';
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

async function handleVote(voteData) {
  isVoting.value = true;
  
  try {
    await questionsStore.voteForAnswer(voteData.itemId, voteData.voteType);
    emit('vote', voteData);
  } catch (error) {
    console.error('Error voting for answer:', error);
    alert('Ошибка при голосовании: ' + error.message);
  } finally {
    isVoting.value = false;
  }
}

async function handleAccept() {
  if (isAccepting.value) return;
  
  isAccepting.value = true;
  
  try {
    await questionsStore.acceptAnswer(props.answer.id);
    emit('accept', props.answer.id);
  } catch (error) {
    console.error('Error accepting answer:', error);
    alert('Ошибка при принятии ответа: ' + error.message);
  } finally {
    isAccepting.value = false;
  }
}

async function handleUnaccept() {
  if (isAccepting.value) return;
  
  const confirmed = confirm('Вы уверены, что хотите отменить принятие этого ответа?');
  if (!confirmed) return;
  
  isAccepting.value = true;
  
  try {
    await questionsStore.unacceptAnswer(props.answer.id);
    emit('unaccept', props.answer.id);
  } catch (error) {
    console.error('Error unaccepting answer:', error);
    alert('Ошибка при отмене принятия ответа: ' + error.message);
  } finally {
    isAccepting.value = false;
  }
}

function startEdit() {
  isEditing.value = true;
}

function cancelEdit() {
  isEditing.value = false;
}

async function handleUpdate(formData) {
  isUpdating.value = true;
  
  try {
    await questionsStore.updateAnswer(props.answer.id, formData);
    emit('update', { id: props.answer.id, data: formData });
    isEditing.value = false;
  } catch (error) {
    console.error('Error updating answer:', error);
    alert('Ошибка при обновлении ответа: ' + error.message);
  } finally {
    isUpdating.value = false;
  }
}

async function handleDelete() {
  if (isDeleting.value) return;
  
  const confirmed = confirm('Вы уверены, что хотите удалить этот ответ? Это действие нельзя отменить.');
  if (!confirmed) return;
  
  isDeleting.value = true;
  
  try {
    await questionsStore.deleteAnswer(props.answer.id);
    emit('delete', props.answer.id);
  } catch (error) {
    console.error('Error deleting answer:', error);
    alert('Ошибка при удалении ответа: ' + error.message);
  }
}
</script>

<style scoped>
.answer-card {
  margin-bottom: 1.5rem;
}

.answer-card .card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.answer-card .card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
}

/* Стилизация принятого ответа */
.accepted-answer {
  border-left: 4px solid #28a745 !important;
  background: linear-gradient(to right, rgba(40, 167, 69, 0.05), transparent);
}

.accepted-badge {
  animation: fadeInScale 0.5s ease;
}

.voting-section {
  flex-shrink: 0;
}

.answer-content {
  min-width: 0; /* Для корректного переноса текста */
}

.answer-text {
  line-height: 1.6;
  font-size: 0.95rem;
}

.answer-text p {
  margin-bottom: 1rem;
}

.answer-text p:last-child {
  margin-bottom: 0;
}

.answer-meta {
  font-size: 0.875rem;
  border-top: 1px solid #f0f0f0;
  padding-top: 0.75rem;
}

.author-name {
  font-weight: 500;
  color: var(--bs-primary);
}

.answer-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.author-actions {
  border-left: 1px solid #e9ecef;
  padding-left: 0.75rem;
  margin-left: 0.5rem;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* Анимации */
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.answer-card {
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
@media (max-width: 576px) {
  .answer-card .card-body .d-flex {
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
  
  .answer-meta {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .answer-actions {
    justify-content: flex-start;
  }
  
  .author-actions {
    border-left: none;
    padding-left: 0;
    margin-left: 0;
    border-top: 1px solid #e9ecef;
    padding-top: 0.5rem;
    margin-top: 0.5rem;
  }
}

/* Стилизация кнопок действий */
.answer-actions .btn {
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
}

.answer-actions .btn:hover {
  transform: translateY(-1px);
}

/* Принятый ответ - особая стилизация */
.accepted-answer .accepted-badge .badge {
  font-size: 0.875rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
}

/* Темная тема (если потребуется) */
@media (prefers-color-scheme: dark) {
  .answer-meta {
    border-top-color: #495057;
  }
  
  .author-actions {
    border-left-color: #495057;
  }
  
  .accepted-answer {
    background: linear-gradient(to right, rgba(40, 167, 69, 0.1), transparent);
  }
}
</style>