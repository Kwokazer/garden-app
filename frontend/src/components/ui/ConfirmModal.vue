<template>
  <Teleport to="body">
    <Transition name="modal" appear>
      <div v-if="visible" class="modal-overlay" @click="handleOverlayClick">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <div class="modal-icon">
              <i :class="iconClass"></i>
            </div>
            <h3 class="modal-title">{{ title }}</h3>
          </div>
          
          <div class="modal-body">
            <p class="modal-message">{{ message }}</p>
          </div>
          
          <div class="modal-footer">
            <button 
              class="btn btn--secondary"
              @click="handleCancel"
              :disabled="loading"
            >
              {{ cancelText }}
            </button>
            <button 
              :class="[
                'btn',
                `btn--${type}`
              ]"
              @click="handleConfirm"
              :disabled="loading"
            >
              <span v-if="loading" class="loading-spinner"></span>
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ConfirmModal',
  props: {
    title: {
      type: String,
      default: 'Подтверждение'
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Подтвердить'
    },
    cancelText: {
      type: String,
      default: 'Отмена'
    },
    type: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'danger', 'warning', 'success'].includes(value)
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel', 'close'],
  setup(props, { emit }) {
    const visible = ref(false)

    const iconClass = computed(() => {
      const icons = {
        primary: 'bi bi-question-circle-fill',
        danger: 'bi bi-exclamation-triangle-fill',
        warning: 'bi bi-exclamation-triangle-fill',
        success: 'bi bi-check-circle-fill'
      }
      return icons[props.type]
    })

    const handleConfirm = () => {
      emit('confirm')
    }

    const handleCancel = () => {
      emit('cancel')
      close()
    }

    const handleOverlayClick = () => {
      if (!props.loading) {
        handleCancel()
      }
    }

    const close = () => {
      visible.value = false
      setTimeout(() => {
        emit('close')
      }, 300)
    }

    // Обработка клавиши Escape
    const handleKeydown = (event) => {
      if (event.key === 'Escape' && !props.loading) {
        handleCancel()
      }
    }

    onMounted(() => {
      visible.value = true
      document.addEventListener('keydown', handleKeydown)
    })

    return {
      visible,
      iconClass,
      handleConfirm,
      handleCancel,
      handleOverlayClick,
      close
    }
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  },

  // Expose close method for external use
  expose: ['close']
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 400px;
  width: 100%;
  overflow: hidden;
}

.modal-header {
  padding: 24px 24px 16px;
  text-align: center;
}

.modal-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.modal-icon .bi-question-circle-fill {
  color: #3182ce;
}

.modal-icon .bi-exclamation-triangle-fill {
  color: #ed8936;
}

.modal-icon .bi-check-circle-fill {
  color: #38a169;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.modal-body {
  padding: 0 24px 24px;
  text-align: center;
}

.modal-message {
  color: #4a5568;
  line-height: 1.5;
  margin: 0;
}

.modal-footer {
  padding: 16px 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 100px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--secondary {
  background-color: #edf2f7;
  color: #4a5568;
}

.btn--secondary:hover:not(:disabled) {
  background-color: #e2e8f0;
}

.btn--primary {
  background-color: #3182ce;
  color: white;
}

.btn--primary:hover:not(:disabled) {
  background-color: #2c5aa0;
}

.btn--danger {
  background-color: #e53e3e;
  color: white;
}

.btn--danger:hover:not(:disabled) {
  background-color: #c53030;
}

.btn--warning {
  background-color: #ed8936;
  color: white;
}

.btn--warning:hover:not(:disabled) {
  background-color: #dd6b20;
}

.btn--success {
  background-color: #38a169;
  color: white;
}

.btn--success:hover:not(:disabled) {
  background-color: #2f855a;
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
  to {
    transform: rotate(360deg);
  }
}

/* Анимации */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9) translateY(-20px);
}
</style>
