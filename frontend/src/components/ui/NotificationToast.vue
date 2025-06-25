<template>
  <Transition name="toast" appear>
    <div 
      v-if="visible"
      :class="[
        'toast',
        `toast--${type}`
      ]"
      @click="close"
    >
      <div class="toast__icon">
        <i :class="iconClass"></i>
      </div>
      <div class="toast__content">
        <div class="toast__title">{{ title }}</div>
        <div v-if="message" class="toast__message">{{ message }}</div>
      </div>
      <button class="toast__close" @click.stop="close">
        <i class="bi bi-x"></i>
      </button>
    </div>
  </Transition>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'NotificationToast',
  props: {
    type: {
      type: String,
      default: 'info',
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      default: ''
    },
    duration: {
      type: Number,
      default: 5000
    },
    autoClose: {
      type: Boolean,
      default: true
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const visible = ref(false)
    let timeoutId = null

    const iconClass = computed(() => {
      const icons = {
        success: 'bi bi-check-circle-fill',
        error: 'bi bi-exclamation-circle-fill',
        warning: 'bi bi-exclamation-triangle-fill',
        info: 'bi bi-info-circle-fill'
      }
      return icons[props.type]
    })

    const close = () => {
      visible.value = false
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      setTimeout(() => {
        emit('close')
      }, 300) // Ждем завершения анимации
    }

    onMounted(() => {
      visible.value = true
      
      if (props.autoClose && props.duration > 0) {
        timeoutId = setTimeout(() => {
          close()
        }, props.duration)
      }
    })

    return {
      visible,
      iconClass,
      close
    }
  }
}
</script>

<style scoped>
.toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid;
  cursor: pointer;
  transition: all 0.3s ease;
  max-width: 400px;
  min-width: 300px;
}

.toast:hover {
  transform: translateX(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.toast--success {
  border-left-color: #38a169;
}

.toast--error {
  border-left-color: #e53e3e;
}

.toast--warning {
  border-left-color: #ed8936;
}

.toast--info {
  border-left-color: #3182ce;
}

.toast__icon {
  flex-shrink: 0;
  font-size: 20px;
  margin-top: 2px;
}

.toast--success .toast__icon {
  color: #38a169;
}

.toast--error .toast__icon {
  color: #e53e3e;
}

.toast--warning .toast__icon {
  color: #ed8936;
}

.toast--info .toast__icon {
  color: #3182ce;
}

.toast__content {
  flex: 1;
}

.toast__title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 4px;
}

.toast__message {
  color: #4a5568;
  font-size: 0.875rem;
  line-height: 1.4;
}

.toast__close {
  flex-shrink: 0;
  background: none;
  border: none;
  color: #a0aec0;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.toast__close:hover {
  color: #718096;
  background-color: #f7fafc;
}

/* Анимации */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
