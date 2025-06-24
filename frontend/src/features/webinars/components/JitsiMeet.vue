<template>
  <div class="jitsi-meet">
    <!-- Загрузка -->
    <div v-if="isLoading" class="jitsi-loading">
      <div class="loading-spinner"></div>
      <p>Подключение к вебинару...</p>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="jitsi-error">
      <div class="error-icon">⚠️</div>
      <h3>Ошибка подключения</h3>
      <p>{{ error }}</p>
      <div class="error-actions">
        <button
          v-if="jitsiConfig.domain.includes('garden.local')"
          @click="openJitsiInNewTab"
          class="btn btn--secondary"
        >
          Открыть Jitsi сервер
        </button>
        <button @click="retry" class="btn btn--primary">
          Попробовать снова
        </button>
      </div>
    </div>

    <!-- Jitsi Meet iframe -->
    <div v-else class="jitsi-container">
      <div id="jitsi-meet" class="jitsi-iframe"></div>
    </div>

    <!-- Панель управления -->
    <div v-if="isConnected && !error" class="jitsi-controls">
      <div class="controls-info">
        <span class="webinar-title">{{ webinarTitle }}</span>
        <span class="connection-status" :class="{ 'connected': isConnected }">
          {{ isConnected ? 'Подключен' : 'Подключение...' }}
        </span>
      </div>
      
      <div class="controls-actions">
        <button @click="toggleFullscreen" class="control-btn" title="Полноэкранный режим">
          📺
        </button>
        <button @click="leaveWebinar" class="control-btn control-btn--danger" title="Покинуть вебинар">
          🚪
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

export default {
  name: 'JitsiMeet',
  props: {
    webinarId: {
      type: [String, Number],
      required: true
    },
    webinarTitle: {
      type: String,
      default: 'Вебинар'
    },
    jitsiConfig: {
      type: Object,
      required: true
    },
    jwtToken: {
      type: String,
      required: true
    }
  },
  emits: ['connected', 'disconnected', 'error', 'leave'],
  setup(props, { emit }) {
    const isLoading = ref(true)
    const isConnected = ref(false)
    const error = ref(null)
    const jitsiApi = ref(null)
    
    // Methods
    const initializeJitsi = async () => {
      try {
        isLoading.value = true
        error.value = null

        console.log('Initializing Jitsi with config:', props.jitsiConfig)

        // Проверяем, что Jitsi Meet API загружен
        if (typeof window.JitsiMeetExternalAPI === 'undefined') {
          await loadJitsiScript()
        }

        await nextTick()

        // Ждем, пока элемент появится в DOM
        let jitsiContainer = null
        let attempts = 0
        const maxAttempts = 10

        while (!jitsiContainer && attempts < maxAttempts) {
          jitsiContainer = document.getElementById('jitsi-meet')
          if (!jitsiContainer) {
            await new Promise(resolve => setTimeout(resolve, 100))
            attempts++
          }
        }

        if (!jitsiContainer) {
          throw new Error('Jitsi container element not found after waiting')
        }

        // Конфигурация для Jitsi Meet
        const config = {
          startWithAudioMuted: false,
          startWithVideoMuted: false,
          enableWelcomePage: false,
          enableUserRolesBasedOnToken: true,
          ...props.jitsiConfig.config_overwrite,
          jwt: props.jwtToken
        }

        const interfaceConfig = {
          TOOLBAR_BUTTONS: [
            'microphone', 'camera', 'closedcaptions', 'desktop', 'fullscreen',
            'fodeviceselection', 'hangup', 'profile', 'chat', 'recording',
            'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
            'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
            'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone'
          ],
          ...props.jitsiConfig.interface_config_overwrite
        }

        const options = {
          roomName: props.jitsiConfig.room_name,
          width: '100%',
          height: '100%',
          parentNode: jitsiContainer,
          configOverwrite: config,
          interfaceConfigOverwrite: interfaceConfig,
          userInfo: props.jitsiConfig.user_info || {},
          jwt: props.jwtToken
        }

        console.log('Creating Jitsi API with options:', options)

        // Создаем экземпляр Jitsi Meet
        jitsiApi.value = new window.JitsiMeetExternalAPI(props.jitsiConfig.domain, options)

        // Обработчики событий
        setupEventHandlers()

        isLoading.value = false

      } catch (err) {
        console.error('Error initializing Jitsi Meet:', err)
        error.value = `Не удалось подключиться к вебинару: ${err.message}`
        isLoading.value = false
        emit('error', err)
      }
    }
    
    const loadJitsiScript = () => {
      return new Promise((resolve, reject) => {
        // Проверяем, не загружен ли уже скрипт
        if (document.querySelector('script[src*="external_api.js"]')) {
          console.log('Jitsi script already loaded')
          resolve()
          return
        }

        const script = document.createElement('script')
        // Определяем протокол: если домен содержит localhost, используем HTTP, иначе HTTPS
        const protocol = props.jitsiConfig.domain.includes('localhost') ? 'http' : 'https'
        script.src = `${protocol}://${props.jitsiConfig.domain}/external_api.js`
        script.async = true

        // Добавляем атрибуты для работы с самоподписанными сертификатами
        script.crossOrigin = 'anonymous'

        script.onload = () => {
          console.log('Jitsi Meet External API loaded from:', script.src)
          // Дополнительная проверка, что API действительно загружен
          if (typeof window.JitsiMeetExternalAPI !== 'undefined') {
            resolve()
          } else {
            reject(new Error('JitsiMeetExternalAPI not found after script load'))
          }
        }

        script.onerror = (event) => {
          console.error('Failed to load Jitsi script from:', script.src, event)
          reject(new Error(`Не удалось загрузить Jitsi API. Проверьте, что Jitsi сервер запущен и доступен по адресу ${script.src}`))
        }

        document.head.appendChild(script)

        // Таймаут для загрузки скрипта
        setTimeout(() => {
          if (typeof window.JitsiMeetExternalAPI === 'undefined') {
            reject(new Error('Timeout loading Jitsi Meet External API'))
          }
        }, 10000)
      })
    }
    
    const setupEventHandlers = () => {
      if (!jitsiApi.value) return
      
      // Успешное подключение
      jitsiApi.value.addEventListener('videoConferenceJoined', () => {
        console.log('Joined video conference')
        isConnected.value = true
        emit('connected')
      })
      
      // Отключение
      jitsiApi.value.addEventListener('videoConferenceLeft', () => {
        console.log('Left video conference')
        isConnected.value = false
        emit('disconnected')
      })
      
      // Готовность API
      jitsiApi.value.addEventListener('readyToClose', () => {
        console.log('Jitsi Meet ready to close')
        cleanup()
      })
      
      // Ошибки
      jitsiApi.value.addEventListener('participantKickedOut', (event) => {
        console.log('Participant kicked out:', event)
        error.value = 'Вы были исключены из вебинара'
        emit('error', new Error('Kicked out'))
      })
      
      // Изменение количества участников
      jitsiApi.value.addEventListener('participantJoined', (event) => {
        console.log('Participant joined:', event.id)
      })
      
      jitsiApi.value.addEventListener('participantLeft', (event) => {
        console.log('Participant left:', event.id)
      })
    }
    
    const cleanup = () => {
      if (jitsiApi.value) {
        try {
          jitsiApi.value.dispose()
        } catch (err) {
          console.error('Error disposing Jitsi API:', err)
        }
        jitsiApi.value = null
      }
      isConnected.value = false
    }
    
    const retry = () => {
      cleanup()
      initializeJitsi()
    }
    
    const toggleFullscreen = () => {
      if (jitsiApi.value) {
        const iframe = document.querySelector('#jitsi-meet iframe')
        if (iframe) {
          if (document.fullscreenElement) {
            document.exitFullscreen()
          } else {
            iframe.requestFullscreen()
          }
        }
      }
    }
    
    const leaveWebinar = () => {
      if (jitsiApi.value) {
        jitsiApi.value.executeCommand('hangup')
      }
      emit('leave')
    }

    const openJitsiInNewTab = () => {
      const protocol = props.jitsiConfig.domain.includes('localhost') ? 'http' : 'https'
      window.open(`${protocol}://${props.jitsiConfig.domain}`, '_blank')
    }
    
    // Lifecycle
    onMounted(() => {
      initializeJitsi()
    })
    
    onUnmounted(() => {
      cleanup()
    })
    
    return {
      isLoading,
      isConnected,
      error,
      retry,
      toggleFullscreen,
      leaveWebinar,
      openJitsiInNewTab
    }
  }
}
</script>

<style scoped>
.jitsi-meet {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.jitsi-loading,
.jitsi-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  background: #1a202c;
  color: white;
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #4a5568;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.jitsi-error h3 {
  color: #fed7d7;
  margin-bottom: 12px;
}

.jitsi-error p {
  color: #a0aec0;
  margin-bottom: 24px;
}

.error-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.jitsi-container {
  flex: 1;
  position: relative;
  min-height: 400px;
}

.jitsi-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.jitsi-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  font-size: 0.875rem;
}

.controls-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.webinar-title {
  font-weight: 500;
}

.connection-status {
  padding: 4px 8px;
  border-radius: 4px;
  background: #4a5568;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.connection-status.connected {
  background: #38a169;
}

.controls-actions {
  display: flex;
  gap: 8px;
}

.control-btn {
  padding: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 1rem;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.control-btn--danger:hover {
  background: rgba(229, 62, 62, 0.8);
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
  justify-content: center;
}

.btn--primary {
  background-color: #4299e1;
  color: white;
}

.btn--primary:hover {
  background-color: #3182ce;
}

.btn--secondary {
  background-color: #edf2f7;
  color: #4a5568;
}

.btn--secondary:hover {
  background-color: #e2e8f0;
}

/* Адаптивность */
@media (max-width: 768px) {
  .jitsi-controls {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .controls-info {
    flex-direction: column;
    gap: 8px;
  }
}

/* Полноэкранный режим */
:global(.jitsi-meet iframe:fullscreen) {
  width: 100vw !important;
  height: 100vh !important;
}
</style>
