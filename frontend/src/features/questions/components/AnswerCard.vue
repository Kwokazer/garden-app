<!-- Полный код AnswerCard.vue -->
<template>
  <div class="answer-card">
    <div class="card shadow-sm border-0 mb-3" :class="{
      'accepted-answer': answer.is_accepted,
      'regular-user-answer': isRegularUser,
      'expert-answer': isExpert,
      'admin-answer': isAdmin
    }">
      <div class="card-body">
        <div class="d-flex">
          <!-- Панель голосования с уникальным ключом -->
          <div class="voting-section me-3">
            <VotingButtons
              :key="`answer-vote-${answer.id}-${votingKey}`"
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
                <div class="author-info d-flex align-items-center flex-wrap">
                  <small class="text-muted me-2">
                    Автор:
                    <span class="author-name">{{ answer.author?.username || 'Неизвестно' }}</span>
                    <span class="mx-1">•</span>
                    <time :datetime="answer.created_at" :title="getFullDate(answer.created_at)">
                      {{ getRelativeTime(answer.created_at) }}
                    </time>
                  </small>

                  <!-- Бейдж роли автора -->
                  <div class="author-role-badges">
                    <span v-if="isRegularUser" class="badge bg-primary-subtle text-primary me-1">
                      <i class="bi bi-person me-1"></i>
                      Садовод
                    </span>
                    <span v-else-if="isExpert" class="badge bg-success-subtle text-success me-1">
                      <i class="bi bi-award me-1"></i>
                      Эксперт
                    </span>
                    <span v-else-if="isAdmin" class="badge bg-danger-subtle text-danger me-1">
                      <i class="bi bi-shield-check me-1"></i>
                      Администратор
                    </span>
                  </div>
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
import { ref, computed, watch, nextTick } from 'vue';
import { useAuthStore } from '../../auth/store/authStore';
import { useQuestionsStore } from '../store/questionsStore';
import { useConfirm } from '@/composables/useConfirm';
import { useNotificationStore } from '@/stores/notificationStore';
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
const questionsStore = useQuestionsStore();
const { confirmDelete, confirmAction } = useConfirm();
const notificationStore = useNotificationStore();

// Состояние компонента
const isVoting = ref(false);
const isAccepting = ref(false);
const isEditing = ref(false);
const isUpdating = ref(false);
const isDeleting = ref(false);
const votingKey = ref(Date.now()); // Ключ для принудительного ререндера

// Наблюдение за изменениями голосов для принудительного обновления
watch(
  () => [props.answer.votes_up, props.answer.votes_down, props.answer.user_vote],
  ([newUp, newDown, newVote], [oldUp, oldDown, oldVote]) => {
    if (newUp !== oldUp || newDown !== oldDown || newVote !== oldVote) {
      console.log(`🔄 AnswerCard: Vote data changed for answer ${props.answer.id}:`, {
        old: `${oldUp}/${oldDown}/${oldVote}`,
        new: `${newUp}/${newDown}/${newVote}`
      });
      // Принудительно обновляем ключ для ререндера VotingButtons
      votingKey.value = Date.now();
    }
  },
  { immediate: false }
);

// Вычисляемые свойства
const isQuestionAuthor = computed(() => {
  return authStore.isLoggedIn && authStore.user && authStore.user.id === props.questionAuthorId;
});

const canEdit = computed(() => {
  return authStore.isLoggedIn && authStore.user && authStore.user.id === props.answer.author_id;
});

// Вычисляемые свойства для ролей автора ответа
const authorRoles = computed(() => {
  return props.answer.author?.roles || [];
});

const isRegularUser = computed(() => {
  const roles = authorRoles.value;
  if (roles.length === 0) return true; // Если нет ролей, то обычный пользователь

  // Проверяем, есть ли роли кроме "user"
  const hasExpertOrAdminRole = roles.some(role =>
    role === 'plant_expert' || role === 'admin'
  );

  return !hasExpertOrAdminRole;
});

const isExpert = computed(() => {
  return authorRoles.value.includes('plant_expert');
});

const isAdmin = computed(() => {
  return authorRoles.value.includes('admin');
});

// Методы форматирования
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

// Обработка голосования за ответ
async function handleVote(voteData) {
  console.log(`🎯 AnswerCard: Vote received for answer ${props.answer.id}:`, voteData);
  
  if (isVoting.value) {
    console.log('⚠️ AnswerCard: Already voting, ignoring');
    return;
  }
  
  // Проверяем, не пытается ли пользователь голосовать за свой ответ
  if (authStore.isLoggedIn && authStore.user && authStore.user.id === props.answer.author_id) {
    notificationStore.warning('Нельзя голосовать', 'Вы не можете голосовать за свой собственный ответ');
    return;
  }
  
  isVoting.value = true;
  
  try {
    console.log(`🗳️ AnswerCard: Starting vote for answer ${voteData.itemId} with type ${voteData.voteType}`);
    console.log(`📊 AnswerCard: Current answer state:`, {
      votes_up: props.answer.votes_up,
      votes_down: props.answer.votes_down,
      user_vote: props.answer.user_vote
    });
    
    // Вызываем store метод для голосования за ответ
    const result = await questionsStore.voteForAnswer(voteData.itemId, voteData.voteType);
    
    console.log(`✅ AnswerCard: Vote completed successfully:`, result);
    
    // Принудительно обновляем ключ для ререндера VotingButtons
    votingKey.value = Date.now();
    
    // Ожидаем следующий тик для обеспечения обновления компонентов
    await nextTick();
    
    // Эмитим событие для родительского компонента
    emit('vote', voteData);
    
  } catch (error) {
    console.error('❌ AnswerCard: Vote error:', error);

    // Показываем пользователю ошибку
    const errorMessage = error.message || 'Ошибка при голосовании';
    notificationStore.error('Ошибка голосования', errorMessage);

  } finally {
    isVoting.value = false;
    console.log('🏁 AnswerCard: Vote process finished');
  }
}

// Обработка принятия ответа
async function handleAccept() {
  if (isAccepting.value) return;
  
  isAccepting.value = true;
  
  try {
    console.log(`✅ AnswerCard: Accepting answer ${props.answer.id}`);
    emit('accept', props.answer.id);
  } catch (error) {
    console.error('Error accepting answer:', error);
    notificationStore.error('Ошибка принятия', error.message || 'Не удалось принять ответ');
  } finally {
    isAccepting.value = false;
  }
}

// Обработка отмены принятия ответа
async function handleUnaccept() {
  if (isAccepting.value) return;

  const confirmed = await confirmAction(
    'Отменить принятие ответа?',
    'Вы уверены, что хотите отменить принятие этого ответа?',
    'Отменить принятие'
  );
  if (!confirmed) return;

  isAccepting.value = true;

  try {
    console.log(`❌ AnswerCard: Unaccepting answer ${props.answer.id}`);
    emit('unaccept', props.answer.id);
  } catch (error) {
    console.error('Error unaccepting answer:', error);
    notificationStore.error('Ошибка отмены', error.message || 'Не удалось отменить принятие ответа');
  } finally {
    isAccepting.value = false;
  }
}

// Редактирование ответа
function startEdit() {
  isEditing.value = true;
}

function cancelEdit() {
  isEditing.value = false;
}

async function handleUpdate(formData) {
  isUpdating.value = true;
  
  try {
    console.log(`📝 AnswerCard: Updating answer ${props.answer.id}`, formData);
    emit('update', { id: props.answer.id, data: formData });
    isEditing.value = false;
  } catch (error) {
    console.error('Error updating answer:', error);
    notificationStore.error('Ошибка обновления', error.message || 'Не удалось обновить ответ');
  } finally {
    isUpdating.value = false;
  }
}

// Удаление ответа
async function handleDelete() {
  if (isDeleting.value) return;

  const confirmed = await confirmDelete('Вы уверены, что хотите удалить этот ответ? Это действие нельзя отменить.');
  if (!confirmed) return;

  isDeleting.value = true;

  try {
    console.log(`🗑️ AnswerCard: Deleting answer ${props.answer.id}`);
    emit('delete', props.answer.id);
  } catch (error) {
    console.error('Error deleting answer:', error);
    notificationStore.error('Ошибка удаления', error.message || 'Не удалось удалить ответ');
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

.answer-text .formatted-content {
  word-wrap: break-word;
  overflow-wrap: break-word;
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
  
  .voting-section :deep(.voting-buttons) {
    flex-direction: row;
    justify-content: center;
    width: 100%;
  }
  
  .voting-section :deep(.voting-buttons > *) {
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
  
  .answer-actions .btn {
    flex: 1;
    min-width: 120px;
  }
}

/* Улучшенная стилизация кнопок */
.btn-sm {
  font-size: 0.8rem;
  padding: 0.375rem 0.75rem;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Стилизация спиннеров */
.spinner-border-sm {
  width: 0.875rem;
  height: 0.875rem;
}

/* Анимация появления компонента */
.answer-card {
  animation: slideInUp 0.3s ease;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Дополнительные стили для лучшего UX */
.answer-content {
  transition: opacity 0.2s ease;
}

.answer-content:has(.answer-form) {
  opacity: 0.95;
}

.accepted-badge .badge {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(40, 167, 69, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(40, 167, 69, 0);
  }
}

/* Стили для выделения ответов по ролям */
.regular-user-answer {
  border-left: 4px solid #0d6efd !important;
  background: linear-gradient(135deg, rgba(13, 110, 253, 0.02) 0%, rgba(13, 110, 253, 0.05) 100%);
}

.expert-answer {
  border-left: 4px solid #198754 !important;
  background: linear-gradient(135deg, rgba(25, 135, 84, 0.02) 0%, rgba(25, 135, 84, 0.05) 100%);
}

.admin-answer {
  border-left: 4px solid #dc3545 !important;
  background: linear-gradient(135deg, rgba(220, 53, 69, 0.02) 0%, rgba(220, 53, 69, 0.05) 100%);
}

/* Стили для бейджей ролей */
.bg-primary-subtle {
  background-color: rgba(13, 110, 253, 0.1) !important;
}

.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.1) !important;
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.1) !important;
}

.author-role-badges .badge {
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 12px;
  padding: 4px 8px;
}

/* Дополнительное выделение для принятых ответов */
.accepted-answer.regular-user-answer {
  border-left: 4px solid #198754 !important;
  background: linear-gradient(135deg, rgba(25, 135, 84, 0.05) 0%, rgba(25, 135, 84, 0.1) 100%);
}

.accepted-answer.expert-answer {
  background: linear-gradient(135deg, rgba(25, 135, 84, 0.08) 0%, rgba(25, 135, 84, 0.15) 100%);
}

.accepted-answer.admin-answer {
  background: linear-gradient(135deg, rgba(25, 135, 84, 0.08) 0%, rgba(25, 135, 84, 0.15) 100%);
}
</style>