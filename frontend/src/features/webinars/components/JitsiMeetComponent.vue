// src/features/webinars/components/JitsiMeetComponent.vue
<template>
  <div class="jitsi-container">
    <!-- Отображение ошибки загрузки -->
    <div v-if="error" class="jitsi-error alert alert-danger">
      <div class="d-flex align-items-center">
        <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
        <div>
          <h5 class="alert-heading">Ошибка загрузки конференции</h5>
          <p class="mb-0">{{ error }}</p>
        </div>
      </div>
      <div class="mt-3">
        <button class="btn btn-outline-danger me-2" @click="initJitsi">
          Попробовать снова
        </button>
        <router-link :to="{ name: 'Webinars' }" class="btn btn-outline-secondary">
          Вернуться к вебинарам
        </router-link>
      </div>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading && !error" class="jitsi-loading text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-3 text-muted">Загрузка видеоконференции...</p>
    </div>

    <!-- Контейнер для Jitsi Meet -->
    <div id="jitsi-container" class="jitsi-meet-container"></div>

    <!-- Информация о записи -->
    <div v-if="isRecording" class="recording-indicator">
      <i class="bi bi-record-circle text-danger"></i>
      Идет запись...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../auth/store/authStore';

// Props
const props = defineProps({
  roomName: {
    type: String,
    required: true
  },
  displayName: {
    type: String,
    default: ''
  },
  domain: {
    type: String,
    default: 'meet.jit.si'
  },
  jwt: {
    type: String,
    default: ''
  },
  userInfo: {
    type: Object,
    default: () => ({})
  },
  configOverwrite: {
    type: Object,
    default: () => ({})
  },
  interfaceConfigOverwrite: {
    type: Object,
    default: () => ({})
  },
  isHost: {
    type: Boolean,
    default: false
  }
});

// Emit events
const emit = defineEmits([
  'loaded', 
  'participantJoined', 
  'participantLeft',
  'recordingStarted',
  'recordingStopped',
  'conferenceJoined',
  'conferenceLeft',
  'error'
]);

// Router and auth store
const route = useRoute();
const authStore = useAuthStore();

// Component state
const isLoading = ref(true);
const error = ref(null);
const api = ref(null);
const isRecording = ref(false);

// Initialize Jitsi when component is mounted
onMounted(async () => {
  // Delay to ensure DOM is fully loaded
  setTimeout(() => {
    loadJitsiScript();
  }, 100);
});

// Cleanup on component unmount
onBeforeUnmount(() => {
  if (api.value) {
    try {
      api.value.dispose();
    } catch (err) {
      console.error('Error disposing Jitsi API:', err);
    }
  }
});

// Load Jitsi script dynamically
function loadJitsiScript() {
  isLoading.value = true;
  error.value = null;
  
  if (window.JitsiMeetExternalAPI) {
    // Script already loaded, initialize Jitsi
    initJitsi();
    return;
  }
  
  // Create script element
  const script = document.createElement('script');
  script.src = `https://${props.domain}/external_api.js`;
  script.async = true;
  script.onload = () => {
    initJitsi();
  };
  script.onerror = (e) => {
    error.value = 'Не удалось загрузить Jitsi Meet API. Проверьте соединение с интернетом и попробуйте снова.';
    isLoading.value = false;
    emit('error', error.value);
    console.error('Error loading Jitsi Meet API:', e);
  };
  
  // Add script to document
  document.body.appendChild(script);
}

// Initialize Jitsi Meet
function initJitsi() {
  if (!window.JitsiMeetExternalAPI) {
    error.value = 'Jitsi Meet API не доступен. Попробуйте перезагрузить страницу.';
    isLoading.value = false;
    emit('error', error.value);
    return;
  }
  
  try {
    // Clear container if it already has content
    const container = document.getElementById('jitsi-container');
    if (container) {
      container.innerHTML = '';
    }
    
    // Get user information
    const user = authStore.user || {};
    
    // Default config
    const defaultConfig = {
      disableDeepLinking: true,
      enableWelcomePage: false,
      prejoinPageEnabled: false,
      enableClosePage: false,
      startWithAudioMuted: false,
      startWithVideoMuted: false,
      fileRecordingsEnabled: true,
      liveStreamingEnabled: true,
      requireDisplayName: true,
      enableNoAudioDetection: true,
      enableNoisyMicDetection: true,
      startAudioOnly: false,
      startWithAudioMuted: false,
      startWithVideoMuted: false,
      stereo: true,
      hideConferenceTimer: false,
      recordingType: 'jibri',
      disableInviteFunctions: false,
      ...(props.isHost ? {} : { toolbarButtons: ['microphone', 'camera', 'chat', 'raisehand', 'fullscreen'] })
    };
    
    // Default interface config
    const defaultInterfaceConfig = {
      SHOW_JITSI_WATERMARK: false,
      SHOW_WATERMARK_FOR_GUESTS: false,
      MOBILE_APP_PROMO: false,
      HIDE_DEEP_LINKING_LOGO: true,
      HIDE_INVITE_MORE_HEADER: true,
      ...(props.isHost ? {} : { 
        TOOLBAR_BUTTONS: ['microphone', 'camera', 'chat', 'raisehand', 'fullscreen'] 
      })
    };
    
    // Merge default configs with provided overrides
    const mergedConfig = {
      ...defaultConfig,
      ...props.configOverwrite,
    };
    
    const mergedInterfaceConfig = {
      ...defaultInterfaceConfig,
      ...props.interfaceConfigOverwrite,
    };
    
    // Initialize Jitsi Meet API
    const options = {
      roomName: props.roomName,
      width: '100%',
      height: '100%',
      parentNode: container,
      configOverwrite: mergedConfig,
      interfaceConfigOverwrite: mergedInterfaceConfig,
      userInfo: {
        displayName: props.displayName || user.first_name || user.username || 'Участник',
        email: user.email || '',
        ...props.userInfo
      }
    };
    
    // Add JWT if provided
    if (props.jwt) {
      options.jwt = props.jwt;
    }
    
    console.log('Initializing Jitsi with options:', options);
    
    // Create Jitsi Meet API instance
    api.value = new window.JitsiMeetExternalAPI(props.domain, options);
    
    // Add event listeners
    setupEventListeners();
    
    isLoading.value = false;
    emit('loaded', api.value);
    
  } catch (err) {
    error.value = 'Ошибка при инициализации Jitsi Meet: ' + err.message;
    isLoading.value = false;
    emit('error', error.value);
    console.error('Error initializing Jitsi Meet:', err);
  }
}

// Setup event listeners for Jitsi Meet
function setupEventListeners() {
  if (!api.value) return;
  
  // Conference joined
  api.value.addListener('videoConferenceJoined', (event) => {
    console.log('Conference joined:', event);
    emit('conferenceJoined', event);
  });
  
  // Conference left
  api.value.addListener('videoConferenceLeft', (event) => {
    console.log('Conference left:', event);
    emit('conferenceLeft', event);
  });
  
  // Participant joined
  api.value.addListener('participantJoined', (event) => {
    console.log('Participant joined:', event);
    emit('participantJoined', event);
  });
  
  // Participant left
  api.value.addListener('participantLeft', (event) => {
    console.log('Participant left:', event);
    emit('participantLeft', event);
  });
  
  // Recording started
  api.value.addListener('recordingStatusChanged', (event) => {
    console.log('Recording status changed:', event);
    isRecording.value = event.on;
    
    if (event.on) {
      emit('recordingStarted', event);
    } else {
      emit('recordingStopped', event);
    }
  });
  
  // Error
  api.value.addListener('error', (event) => {
    console.error('Jitsi error:', event);
    error.value = 'Произошла ошибка в конференции: ' + (event.error || 'Неизвестная ошибка');
    emit('error', error.value);
  });
}

// API methods exposed for parent components
function startRecording(options = {}) {
  if (!api.value) return false;
  
  const recordingOptions = {
    mode: 'file', // 'file' or 'stream'
    dropboxToken: options.dropboxToken,
    shouldShare: options.shouldShare || true,
    ...options
  };
  
  try {
    api.value.executeCommand('startRecording', recordingOptions);
    return true;
  } catch (err) {
    console.error('Error starting recording:', err);
    return false;
  }
}

function stopRecording() {
  if (!api.value) return false;
  
  try {
    api.value.executeCommand('stopRecording');
    return true;
  } catch (err) {
    console.error('Error stopping recording:', err);
    return false;
  }
}

function executeCommand(command, ...args) {
  if (!api.value) return false;
  
  try {
    api.value.executeCommand(command, ...args);
    return true;
  } catch (err) {
    console.error(`Error executing command ${command}:`, err);
    return false;
  }
}

// Expose methods to parent component
defineExpose({
  startRecording,
  stopRecording,
  executeCommand,
  getApi: () => api.value
});
</script>

<style scoped>
.jitsi-container {
  position: relative;
  width: 100%;
  height: 80vh;
  min-height: 500px;
  overflow: hidden;
  background-color: #202124;
  border-radius: 8px;
}

.jitsi-meet-container {
  width: 100%;
  height: 100%;
}

.jitsi-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-width: 600px;
  z-index: 10;
}

.jitsi-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  z-index: 10;
}

.recording-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  z-index: 100;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

/* Адаптивные стили */
@media (max-width: 768px) {
  .jitsi-container {
    height: 60vh;
    min-height: 400px;
  }
  
  .recording-indicator {
    top: 5px;
    right: 5px;
    font-size: 12px;
  }
}
</style>