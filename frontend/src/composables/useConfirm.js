import { createApp, ref } from 'vue'
import ConfirmModal from '@/components/ui/ConfirmModal.vue'

export function useConfirm() {
  const confirm = (options = {}) => {
    return new Promise((resolve) => {
      const {
        title = 'Подтверждение',
        message = 'Вы уверены?',
        confirmText = 'Подтвердить',
        cancelText = 'Отмена',
        type = 'primary'
      } = options

      // Создаем контейнер для модального окна
      const container = document.createElement('div')
      document.body.appendChild(container)

      // Создаем приложение Vue с модальным окном
      const app = createApp(ConfirmModal, {
        title,
        message,
        confirmText,
        cancelText,
        type,
        onConfirm: () => {
          cleanup()
          resolve(true)
        },
        onCancel: () => {
          cleanup()
          resolve(false)
        },
        onClose: () => {
          cleanup()
          resolve(false)
        }
      })

      // Функция очистки
      const cleanup = () => {
        setTimeout(() => {
          app.unmount()
          if (container.parentNode) {
            container.parentNode.removeChild(container)
          }
        }, 300) // Ждем завершения анимации
      }

      // Монтируем приложение
      app.mount(container)
    })
  }

  // Удобные методы для разных типов подтверждений
  const confirmDelete = (message = 'Это действие нельзя будет отменить.') => {
    return confirm({
      title: 'Удалить элемент?',
      message,
      confirmText: 'Удалить',
      cancelText: 'Отмена',
      type: 'danger'
    })
  }

  const confirmAction = (title, message, confirmText = 'Подтвердить') => {
    return confirm({
      title,
      message,
      confirmText,
      cancelText: 'Отмена',
      type: 'primary'
    })
  }

  const confirmWarning = (title, message, confirmText = 'Продолжить') => {
    return confirm({
      title,
      message,
      confirmText,
      cancelText: 'Отмена',
      type: 'warning'
    })
  }

  return {
    confirm,
    confirmDelete,
    confirmAction,
    confirmWarning
  }
}
