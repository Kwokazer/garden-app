<!-- frontend/src/features/questions/components/AnswerCard.vue -->
<template>
    <div class="answer-card">
      <div class="card shadow-sm border-0 mb-3" :class="{ 'accepted-answer': answer.is_accepted }">
        <div class="card-body">
          <div class="d-flex">
            <!-- Панель голосования -->
            <div class="voting-section me-3">
              <VotingButtons
                type="answer"
                :item-id="answer.id"
                :votes-up="answer.votes_up"
                :votes-down="answer.votes_down"
                :user-vote="answer.user_vote"
                :is-loading="isVoting"
                :author-id="answer.author_id"
                @vote="handleVote"
              />
            </div>
            
            <!-- Содержимое ответа -->
            <div class="answer-content flex-grow-1">
              <!-- Метка принятого решения -->
              <div v-if="answer.is_accepted" class="accepted-badge mb-3">
                <span class="badge bg-success py-2 px-3">
                  <i class="bi bi-check-circle me-1"></i>
                  Принятое решение
                </span>
              </div>
              
              <!-- Режим редактирования -->
              <template v-if="isEditing">
                <AnswerForm
                  :initial-data="answer"
                  :is-loading="isUpdating"
                  :show-preview="true"
                  @submit="handleUpdate"
                  @cancel="cancelEdit"
                />
              </template>
              
              <!-- Основной режим отображения -->
              <template v-else>
                <!-- Текст ответа -->
                <div class="answer-text">
                  <div v-html="formatAnswerText(answer.body)" class="formatted-content"></div>
                </div>
                
                <!-- Мета-информация и действия -->
                <div class="answer-meta d-flex flex-wrap justify-content-between align-items-center mt-3">
                  <div class="author-info">
                    <small class="text-muted">
                      Автор: 
                      <span class="author-name">{{ answer.author?.username || 'Неизвестно' }}</span>
                      <span class="mx-1">•</span>
                      <time :datetime="answer.created_at" :title="getFullDate(answer.created_at)">
                        {{ getRelativeTime(answer.created_at) }}
                      </time>
                    </small>
                  </div>
                  
                  <div class="answer-actions d-flex flex-wrap">
                    <!-- Принятие ответа (только для автора вопроса) -->
                    <div v-if="isQuestionAuthor && !answer.is_accepted" class="me-2">
                      <button
                        class="btn btn-outline-success btn-sm"
                        @click="handleAccept"
                        :disabled="isAccepting"
                      >
                        <span v-if="isAccepting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        <i v-else class="bi bi-check-circle me-1"></i>
                        Принять ответ
                      </button>
                    </div>
                    
                    <!-- Отмена принятия (только для автора вопроса) -->
                    <div v-if="isQuestionAuthor && answer.is_accepted" class="me-2">
                      <button
                        class="btn btn-outline-warning btn-sm"
                        @click="handleUnaccept"
                        :disabled="isAccepting"
                      >
                        <span v-if="isAccepting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        <i v-else class="bi bi-x-circle me-1"></i>
                        Отменить принятие
                      </button>
                    </div>
                    
                    <!-- Действия автора ответа -->
                    <div v-if="canEdit" class="author-actions">
                      <button
                        class="btn btn-outline-secondary btn-sm me-2"
                        @click="startEdit"
                      >
                        <i class="bi bi-pencil me-1"></i>
                        Редактировать
                      </button>
                      <button
                        class="btn btn-outline-danger btn-sm"
                        @click="handleDelete"
                        :disabled="isDeleting"
                      >
                        <span v-if="isDeleting" class="spinner-border spinner-border-sm me-1" role="status"></span>
                        <i v-else class="bi bi-trash me-1"></i>
                        Удалить
                      </button>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue';
  import { useAuthStore } from '../../auth/store/authStore';
  import VotingButtons from './VotingButtons.vue';
  import AnswerForm from './AnswerForm.vue';
  
  const props = defineProps({
    answer: {
      type: Object,
      required: true
    },
    questionAuthorId: {
      type: Number,
      default: null
    }
  });
  
  const emit = defineEmits(['vote', 'accept', 'unaccept', 'update', 'delete']);
  
  const authStore = useAuthStore();
  
  // Состояние компонента
  const isVoting = ref(false);
  const isAccepting = ref(false);
  const isEditing = ref(false);
  const isUpdating = ref(false);
  const isDeleting = ref(false);
  
  // Вычисляемые свойства
  const isQuestionAuthor = computed(() => {
    return authStore.isLoggedIn && authStore.user && authStore.user.id === props.questionAuthorId;
  });
  
  const canEdit = computed(() => {
    return authStore.isLoggedIn && authStore.user && authStore.user.id === props.answer.author_id;
  });
  
  // Методы
  function formatAnswerText(text) {
    if (!text) return '';
    
    return text
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');
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
  console.log('AnswerCard: handleVote called with:', voteData);
  
  isVoting.value = true;
  
  try {
    // ИСПРАВЛЕНО: вызываем правильный метод для голосования за ОТВЕТ
    console.log('AnswerCard: Calling store.voteForAnswer');
    const updatedAnswer = await answersStore.voteForAnswer(voteData.itemId, voteData.voteType);
    
    console.log('AnswerCard: Received updated answer:', updatedAnswer);
    
    // Эмитим событие для родительского компонента (если нужно)
    emit('vote', voteData);
    
    console.log('AnswerCard: Vote completed successfully');
  } catch (error) {
    console.error('AnswerCard: Error voting for answer:', error);
    alert('Ошибка при голосовании: ' + error.message);
  } finally {
    isVoting.value = false;
  }
}
  
  async function handleAccept() {
    if (isAccepting.value) return;
    
    isAccepting.value = true;
    
    try {
      emit('accept', props.answer.id);
    } catch (error) {
      console.error('Error accepting answer:', error);
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
      emit('unaccept', props.answer.id);
    } catch (error) {
      console.error('Error unaccepting answer:', error);
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
      emit('update', { id: props.answer.id, data: formData });
      isEditing.value = false;
    } catch (error) {
      console.error('Error updating answer:', error);
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
      emit('delete', props.answer.id);
    } catch (error) {
      console.error('Error deleting answer:', error);
    } finally {
      isDeleting.value = false;
    }
  }
  </script>
  
  <style scoped>
  .answer-card {
    margin-bottom: 1.5rem;
  }
  
  .card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .card:hover {
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
    padding-top: 0.75rem;
    border-top: 1px solid #f0f0f0;
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
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
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
  
  /* Мобильная адаптивность */
  @media (max-width: 576px) {
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
    
    .answer-meta {
      flex-direction: column;
      gap: 0.75rem;
    }
    
    .answer-actions {
      width: 100%;
      justify-content: center;
      margin-top: 0.5rem;
    }
  }
  </style>