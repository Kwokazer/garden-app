<!-- frontend/src/features/questions/components/VotingButtons.vue -->
<template>
    <div class="voting-buttons d-flex flex-column align-items-center">
      <!-- Кнопка за (up) -->
      <button
        class="btn btn-voting btn-vote-up"
        :class="{ 
          'active': userVote === 'up',
          'disabled': !canVote || isLoading
        }"
        @click="handleVote('up')"
        :disabled="isLoading || !canVote"
        :title="userVote === 'up' ? 'Отменить голос' : 'Голосовать за'"
      >
        <i class="bi bi-chevron-up"></i>
      </button>
      
      <!-- Счетчик голосов -->
      <div class="vote-count">
        <span class="votes-display" :key="`${votesUp}-${votesDown}`">{{ totalVotes }}</span>
      </div>
      
      <!-- Кнопка против (down) -->
      <button
        class="btn btn-voting btn-vote-down"
        :class="{ 
          'active': userVote === 'down',
          'disabled': !canVote || isLoading
        }"
        @click="handleVote('down')"
        :disabled="isLoading || !canVote"
        :title="userVote === 'down' ? 'Отменить голос' : 'Голосовать против'"
      >
        <i class="bi bi-chevron-down"></i>
      </button>
      
      <!-- Индикатор загрузки -->
      <div v-if="isLoading" class="vote-loader mt-2">
        <div class="spinner-border spinner-border-sm text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed, watch } from 'vue';
  import { useAuthStore } from '../../auth/store/authStore';
  
  const props = defineProps({
    // Тип элемента для голосования
    type: {
      type: String,
      required: true,
      validator: (value) => ['question', 'answer'].includes(value)
    },
    // ID элемента
    itemId: {
      type: Number,
      required: true
    },
    // Количество голосов за
    votesUp: {
      type: Number,
      default: 0
    },
    // Количество голосов против
    votesDown: {
      type: Number,
      default: 0
    },
    // Текущий голос пользователя
    userVote: {
      type: [String, null],
      default: null
    },
    // Состояние загрузки
    isLoading: {
      type: Boolean,
      default: false
    },
    // ID автора (чтобы запретить голосование за свой контент)
    authorId: {
      type: Number,
      default: null
    }
  });
  
  const emit = defineEmits(['vote']);
  
  const authStore = useAuthStore();
  
  // Следим за изменениями userVote для отладки
  watch(() => props.userVote, (newVote, oldVote) => {
    if (newVote !== oldVote) {
      console.log(`VotingButtons: userVote changed for ${props.type} ${props.itemId}: ${oldVote} -> ${newVote}`);
    }
  }, { immediate: true });
  
  // Вычисляемые свойства
  const totalVotes = computed(() => {
    return props.votesUp - props.votesDown;
  });
  
  const canVote = computed(() => {
    // Проверяем, что пользователь авторизован
    if (!authStore.isLoggedIn) {
      return false;
    }
    
    // Проверяем, что это не автор контента
    if (props.authorId && authStore.user && authStore.user.id === props.authorId) {
      return false;
    }
    
    return true;
  });
  
  // Методы
  function handleVote(voteType) {
    if (!canVote.value || props.isLoading) {
      return;
    }
    
    // Если пользователь не авторизован, показываем сообщение
    if (!authStore.isLoggedIn) {
      alert('Для голосования необходимо войти в систему');
      return;
    }
    
    // Если пользователь голосует за свой контент
    if (props.authorId && authStore.user && authStore.user.id === props.authorId) {
      alert('Вы не можете голосовать за свой собственный контент');
      return;
    }
    
    // Отправляем событие родительскому компоненту
    emit('vote', {
      type: props.type,
      itemId: props.itemId,
      voteType: voteType,
      // Если пользователь уже голосовал таким же образом, отменяем голос
      isCancel: props.userVote === voteType
    });
  }
  </script>
  
  <style scoped>
  .voting-buttons {
    width: 50px;
    padding: 0.5rem 0;
  }
  
  .btn-voting {
    background: transparent;
    border: 1px solid #dee2e6;
    color: #6c757d;
    border-radius: 0.25rem;
    width: 40px;
    height: 35px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    transition: all 0.2s ease;
    margin: 2px 0;
  }
  
  .btn-voting:hover:not(.disabled):not(:disabled) {
    background-color: #f8f9fa;
    border-color: #adb5bd;
    transform: translateY(-1px);
  }
  
  .btn-voting:focus {
    box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
  }
  
  .btn-voting.disabled,
  .btn-voting:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* Стилизация кнопки голосования "за" */
  .btn-vote-up.active {
    background-color: #28a745 !important;
    border-color: #28a745 !important;
    color: white !important;
    transform: scale(1.05);
    box-shadow: 0 2px 4px rgba(40, 167, 69, 0.3);
  }
  
  .btn-vote-up:hover:not(.disabled):not(:disabled):not(.active) {
    background-color: rgba(40, 167, 69, 0.1);
    border-color: #28a745;
    color: #28a745;
  }
  
  /* Стилизация кнопки голосования "против" */
  .btn-vote-down.active {
    background-color: #dc3545 !important;
    border-color: #dc3545 !important;
    color: white !important;
    transform: scale(1.05);
    box-shadow: 0 2px 4px rgba(220, 53, 69, 0.3);
  }
  
  .btn-vote-down:hover:not(.disabled):not(:disabled):not(.active) {
    background-color: rgba(220, 53, 69, 0.1);
    border-color: #dc3545;
    color: #dc3545;
  }
  
  /* Счетчик голосов */
  .vote-count {
    margin: 0.5rem 0;
    text-align: center;
  }
  
  .votes-display {
    font-weight: 600;
    font-size: 1.1rem;
    color: #333;
    display: block;
    line-height: 1;
    transition: all 0.3s ease;
  }
  
  /* Анимация изменения счетчика */
  .votes-display {
    position: relative;
  }
  
  /* Индикатор загрузки */
  .vote-loader {
    position: absolute;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  /* Адаптивность для мобильных устройств */
  @media (max-width: 768px) {
    .voting-buttons {
      width: 45px;
    }
    
    .btn-voting {
      width: 35px;
      height: 30px;
      font-size: 1rem;
    }
    
    .votes-display {
      font-size: 1rem;
    }
  }
  
  /* Темная тема (если потребуется) */
  @media (prefers-color-scheme: dark) {
    .btn-voting {
      border-color: #495057;
      color: #adb5bd;
    }
    
    .btn-voting:hover:not(.disabled):not(:disabled) {
      background-color: #343a40;
      border-color: #6c757d;
    }
    
    .votes-display {
      color: #f8f9fa;
    }
  }
  </style>