// src/features/webinars/api/webinarsApi.js

/**
 * API клиент для работы с вебинарами и конференциями
 */

const BASE_API_URL = "/api/v1"; // Основной URL для API

/**
 * Обрабатывает ответы от API
 */
async function handleResponse(response) {
  const contentType = response.headers.get("content-type");
  let data;

  if (contentType && contentType.includes("application/json")) {
    data = await response.json();
  } else {
    const textData = await response.text();
    try {
      data = JSON.parse(textData);
    } catch (e) {
      data = { message: textData || response.statusText };
    }
  }

  if (!response.ok) {
    const message =
      data && data.detail
        ? typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail)
        : data && data.message
        ? data.message
        : response.statusText;
    // Возвращаем объект с ошибкой
    return Promise.reject({
      success: false,
      message: message,
      status: response.status,
      errorData: data,
    });
  }

  // Успешный ответ
  return Promise.resolve({ success: true, data: data });
}

/**
 * Получает токен доступа из localStorage
 */
function getAuthHeaders() {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

/**
 * API клиент для работы с вебинарами и видеоконференциями
 */
export const webinarsApi = {
  /**
   * Получить список вебинаров с пагинацией и фильтрацией
   * @param {number} page - Номер страницы (начиная с 1)
   * @param {number} per_page - Количество вебинаров на странице
   * @param {Object} filters - Фильтры для поиска
   * @returns {Promise<Object>} - Ответ от сервера со списком вебинаров
   */
  async getWebinars(page = 1, per_page = 20, filters = {}) {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('per_page', per_page);
      
      // Добавляем фильтры в запрос
      if (filters.search) {
        params.append('search', filters.search);
      }
      
      if (filters.status) {
        params.append('status', filters.status);
      }
      
      if (filters.plant_id) {
        params.append('plant_id', filters.plant_id);
      }
      
      if (filters.author_id) {
        params.append('author_id', filters.author_id);
      }
      
      if (filters.date_from) {
        params.append('date_from', filters.date_from);
      }
      
      if (filters.date_to) {
        params.append('date_to', filters.date_to);
      }
      
      if (filters.sort_by) {
        params.append('sort_by', filters.sort_by);
      }
      
      if (filters.sort_order) {
        params.append('sort_order', filters.sort_order);
      }
      
      const url = `${BASE_API_URL}/webinars?${params.toString()}`;
      console.log('API: Fetching webinars URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('API: Error fetching webinars list:', error);
      throw error;
    }
  },

  /**
   * Получить детальную информацию о вебинаре
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера с деталями вебинара
   */
  async getWebinarById(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}`;
      console.log('API: Fetching webinar details URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error fetching webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Создать новый вебинар
   * @param {Object} webinarData - Данные вебинара
   * @returns {Promise<Object>} - Ответ от сервера с созданным вебинаром
   */
  async createWebinar(webinarData) {
    try {
      const url = `${BASE_API_URL}/webinars`;
      console.log('API: Creating webinar URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(webinarData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('API: Error creating webinar:', error);
      throw error;
    }
  },

  /**
   * Обновить данные вебинара
   * @param {number} webinarId - ID вебинара
   * @param {Object} webinarData - Новые данные вебинара
   * @returns {Promise<Object>} - Ответ от сервера с обновленным вебинаром
   */
  async updateWebinar(webinarId, webinarData) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}`;
      console.log('API: Updating webinar URL:', url);
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(webinarData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error updating webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Удалить вебинар
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async deleteWebinar(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}`;
      console.log('API: Deleting webinar URL:', url);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error deleting webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Зарегистрироваться на вебинар
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async registerForWebinar(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/register`;
      console.log('API: Registering for webinar URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error registering for webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Отменить регистрацию на вебинар
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async cancelWebinarRegistration(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/register`;
      console.log('API: Canceling webinar registration URL:', url);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error canceling registration for webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Получить JWT токен для участия в конференции
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера с JWT токеном
   */
  async getWebinarJwt(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/jwt`;
      console.log('API: Getting JWT token URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error getting JWT token for webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Начать запись вебинара
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async startWebinarRecording(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/recording/start`;
      console.log('API: Starting webinar recording URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error starting recording for webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Остановить запись вебинара
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async stopWebinarRecording(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/recording/stop`;
      console.log('API: Stopping webinar recording URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error stopping recording for webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Получить список записей вебинара
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера со списком записей
   */
  async getWebinarRecordings(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/recordings`;
      console.log('API: Fetching webinar recordings URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error fetching recordings for webinar ${webinarId}:`, error);
      throw error;
    }
  },

  /**
   * Получить список участников вебинара
   * @param {number} webinarId - ID вебинара
   * @returns {Promise<Object>} - Ответ от сервера со списком участников
   */
  async getWebinarParticipants(webinarId) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/participants`;
      console.log('API: Fetching webinar participants URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error fetching participants for webinar ${webinarId}:`, error);
      throw error;
    }
  }
};

/**
 * Сервис для взаимодействия с Jitsi Meet API
 */
export const jitsiService = {
  /**
   * Генерирует JWT токен для конференции Jitsi Meet
   * @param {Object} payload - Данные для токена
   * @returns {Promise<string>} - JWT токен
   */
  async generateJWT(payload) {
    try {
      const url = `${BASE_API_URL}/jitsi/generate-token`;
      console.log('API: Generating Jitsi JWT token URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload)
      });
      
      const result = await handleResponse(response);
      return result.data.token;
    } catch (error) {
      console.error('API: Error generating Jitsi JWT token:', error);
      throw error;
    }
  },

  /**
   * Создает название комнаты для Jitsi Meet
   * @param {number} webinarId - ID вебинара
   * @param {string} title - Название вебинара
   * @returns {string} - Название комнаты
   */
  createRoomName(webinarId, title) {
    // Создаем уникальное имя комнаты на основе ID и названия вебинара
    // Удаляем все специальные символы и пробелы
    const sanitizedTitle = title
      .toLowerCase()
      .replace(/[^a-zа-яё0-9]/gi, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
    
    return `garden-webinar-${webinarId}-${sanitizedTitle}`;
  },

  /**
   * Настройки конфигурации Jitsi Meet
   * @param {boolean} isHost - Является ли пользователь организатором
   * @returns {Object} - Конфигурация Jitsi Meet
   */
  getJitsiConfig(isHost = false) {
    // Базовая конфигурация для всех пользователей
    const baseConfig = {
      disableDeepLinking: true,
      enableWelcomePage: false,
      prejoinPageEnabled: false,
      enableClosePage: false,
      startWithAudioMuted: false,
      startWithVideoMuted: false,
      fileRecordingsEnabled: true,
      liveStreamingEnabled: false,
      requireDisplayName: true,
      enableNoAudioDetection: true,
      enableNoisyMicDetection: true,
      startAudioOnly: false,
      stereo: true,
      hideConferenceTimer: false,
      disableInviteFunctions: !isHost,
      toolbarButtons: [
        'microphone',
        'camera',
        'desktop',
        'chat',
        'raisehand',
        'videoquality',
        'fullscreen',
        'settings',
        'hangup',
      ]
    };
    
    // Дополнительные настройки для организатора
    if (isHost) {
      baseConfig.toolbarButtons = [
        'microphone',
        'camera',
        'desktop',
        'chat',
        'raisehand',
        'recording',
        'security',
        'participants-pane',
        'videoquality',
        'fullscreen',
        'settings',
        'hangup',
      ];
      
      baseConfig.fileRecordingsEnabled = true;
    }
    
    return baseConfig;
  },

  /**
   * Настройки интерфейса Jitsi Meet
   * @param {boolean} isHost - Является ли пользователь организатором
   * @returns {Object} - Настройки интерфейса
   */
  getJitsiInterfaceConfig(isHost = false) {
    const baseInterfaceConfig = {
      SHOW_JITSI_WATERMARK: false,
      SHOW_WATERMARK_FOR_GUESTS: false,
      MOBILE_APP_PROMO: false,
      HIDE_DEEP_LINKING_LOGO: true,
      HIDE_INVITE_MORE_HEADER: !isHost,
      TOOLBAR_BUTTONS: [
        'microphone',
        'camera',
        'desktop',
        'chat',
        'raisehand',
        'videoquality',
        'fullscreen',
        'settings',
        'hangup',
      ]
    };
    
    // Дополнительные настройки для организатора
    if (isHost) {
      baseInterfaceConfig.TOOLBAR_BUTTONS = [
        'microphone',
        'camera',
        'desktop',
        'chat',
        'raisehand',
        'recording',
        'security',
        'participants-pane',
        'videoquality',
        'fullscreen',
        'settings',
        'hangup',
      ];
    }
    
    return baseInterfaceConfig;
  },
  
  /**
   * Отправляет запись вебинара на сервер
   * @param {number} webinarId - ID вебинара
   * @param {File} recordingFile - Файл записи
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async uploadRecording(webinarId, recordingFile) {
    try {
      const url = `${BASE_API_URL}/webinars/${webinarId}/recordings/upload`;
      console.log('API: Uploading recording URL:', url);
      
      const formData = new FormData();
      formData.append('file', recordingFile);
      
      const headers = getAuthHeaders();
      // Удаляем Content-Type, чтобы браузер установил его автоматически с boundary
      delete headers['Content-Type'];
      
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: formData
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`API: Error uploading recording for webinar ${webinarId}:`, error);
      throw error;
    }
  }
};