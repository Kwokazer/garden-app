// Исправленный компонент VotingButtons.vue
<template>
  <div class="voting-buttons d-flex flex-column align-items-center">
    <!-- Кнопка за (up) -->
    <button
      class="btn btn-voting btn-vote-up"
      :class="{ 
        'active': isVoteUp,
        'disabled': !canVote || isLoading
      }"
      @click="handleVote('up')"
      :disabled="isLoading || !canVote"
      :title="getButtonTitle('up')"
    >
      <i class="bi bi-chevron-up"></i>
    </button>
    
    <!-- Счетчик голосов с уникальным ключом для принудительного обновления -->
    <div class="vote-count">
      <span 
        class="votes-display" 
        :key="`votes-${itemId}-${votesUp}-${votesDown}-${userVote}-${updateCounter}`"
      >
        {{ totalVotes }}
      </span>
    </div>
    
    <!-- Кнопка против (down) -->
    <button
      class="btn btn-voting btn-vote-down"
      :class="{ 
        'active': isVoteDown,
        'disabled': !canVote || isLoading
      }"
      @click="handleVote('down')"
      :disabled="isLoading || !canVote"
      :title="getButtonTitle('down')"
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
import { computed, watch, ref, onMounted } from 'vue';
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
    type: [String, Number, null],
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

// Счетчик для принудительного обновления
const updateCounter = ref(0);

// Отладка: наблюдение за изменениями userVote
watch(() => props.userVote, (newVote, oldVote) => {
  console.log(`VotingButtons [${props.type}:${props.itemId}]: userVote changed from "${oldVote}" to "${newVote}", type: ${typeof newVote}`);
}, { immediate: true });

// Отладка: вывод значений при монтировании компонента
onMounted(() => {
  console.log(`VotingButtons [${props.type}:${props.itemId}] mounted:`, { 
    userVote: props.userVote, 
    type: typeof props.userVote, 
    isUp: props.userVote === 'up', 
    isDown: props.userVote === 'down',
    votesUp: props.votesUp,
    votesDown: props.votesDown
  });
});

// Отслеживаем изменения для принудительного обновления
watch([() => props.votesUp, () => props.votesDown, () => props.userVote], 
  ([newUp, newDown, newVote], [oldUp, oldDown, oldVote]) => {
    if (newUp !== oldUp || newDown !== oldDown || newVote !== oldVote) {
      updateCounter.value++;
      console.log(`🔄 VotingButtons: Props changed for ${props.type} ${props.itemId}:`, {
        oldVotes: `${oldUp}/${oldDown}`,
        newVotes: `${newUp}/${newDown}`,
        oldVote: oldVote,
        newVote: newVote,
        counter: updateCounter.value
      });
    }
  }
);

// Вычисляемые свойства для более безопасного сравнения
const isVoteUp = computed(() => {
  const result = String(props.userVote) === 'up';
  console.log(`isVoteUp: ${result}, value: ${props.userVote}, type: ${typeof props.userVote}`);
  return result;
});

const isVoteDown = computed(() => {
  const result = String(props.userVote) === 'down';
  console.log(`isVoteDown: ${result}, value: ${props.userVote}, type: ${typeof props.userVote}`);
  return result;
});

// Вычисляемые свойства
const totalVotes = computed(() => {
  const total = props.votesUp - props.votesDown;
  console.log(`📊 VotingButtons: Computed total votes for ${props.type} ${props.itemId}: ${total} (${props.votesUp} - ${props.votesDown})`);
  return total;
});

const canVote = computed(() => {
  // Проверяем авторизацию
  if (!authStore.isLoggedIn) {
    console.log(`VotingButtons: User not logged in, can't vote`);
    return false;
  }
  
  // Проверяем, что это не автор контента
  if (props.authorId && authStore.user && authStore.user.id === props.authorId) {
    console.log(`VotingButtons: User is author (${authStore.user.id} === ${props.authorId}), can't vote for own content`);
    return false;
  }
  
  return true;
});

// Методы
function getButtonTitle(voteType) {
  if (!authStore.isLoggedIn) {
    return 'Войдите в систему для голосования';
  }
  
  if (props.authorId && authStore.user && authStore.user.id === props.authorId) {
    return 'Нельзя голосовать за свой контент';
  }
  
  if (!canVote.value) {
    return 'Голосование недоступно';
  }
  
  if (voteType === 'up' && isVoteUp.value || voteType === 'down' && isVoteDown.value) {
    return 'Отменить голос';
  }
  
  return voteType === 'up' ? 'Голосовать за' : 'Голосовать против';
}

function handleVote(voteType) {
  console.log(`🗳️ VotingButtons: Vote clicked for ${props.type} ${props.itemId} with type ${voteType}`);
  console.log(`📊 VotingButtons: Current state:`, {
    votesUp: props.votesUp,
    votesDown: props.votesDown,
    userVote: props.userVote,
    canVote: canVote.value,
    isLoading: props.isLoading,
    authorId: props.authorId,
    userId: authStore.user?.id
  });
  
  if (!canVote.value || props.isLoading) {
    console.log('⚠️ VotingButtons: Vote blocked - cannot vote or loading');
    
    // Показываем сообщение о том, почему голосование заблокировано
    if (props.authorId && authStore.user && authStore.user.id === props.authorId) {
      alert('Вы не можете голосовать за свой собственный контент');
    } else if (!authStore.isLoggedIn) {
      alert('Для голосования необходимо войти в систему');
    }
    
    return;
  }
  
  // Определяем, отменяем ли мы существующий голос
  const isCancel = (voteType === 'up' && isVoteUp.value) || (voteType === 'down' && isVoteDown.value);
  
  console.log(`✅ VotingButtons: Emitting vote event:`, {
    type: props.type,
    itemId: props.itemId,
    voteType: voteType,
    isCancel: isCancel
  });
  
  // Отправляем событие
  emit('vote', {
    type: props.type,
    itemId: props.itemId,
    voteType: voteType,
    isCancel: isCancel
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

/* Активная кнопка "за" */
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

/* Активная кнопка "против" */
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

/* Анимация изменения */
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

/* Адаптивность */
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
</style>