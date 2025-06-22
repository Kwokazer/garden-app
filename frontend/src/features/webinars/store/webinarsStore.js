// src/features/webinars/store/webinarsStore.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { webinarsApi } from '../api/webinarsApi';

/**
 * Webinars state management store
 */
export const useWebinarsStore = defineStore('webinars', () => {
  // State
  const webinars = ref([]);
  const currentWebinar = ref(null);
  const myHostedWebinars = ref([]);
  const myParticipatingWebinars = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    total_pages: 1,
    total_items: 0,
    per_page: 20
  });
  const activeFilters = ref({
    title: '',
    host_id: null,
    status: null,
    is_public: null,
    plant_topic_id: null,
    date_from: null,
    date_to: null
  });

  // Jitsi connection data
  const jitsiConnectionData = ref(null);

  // Getters
  const getWebinars = computed(() => webinars.value);
  const getCurrentWebinar = computed(() => currentWebinar.value);
  const getMyHostedWebinars = computed(() => myHostedWebinars.value);
  const getMyParticipatingWebinars = computed(() => myParticipatingWebinars.value);
  const getIsLoading = computed(() => isLoading.value);
  const getError = computed(() => error.value);
  const getPagination = computed(() => pagination.value);
  const getActiveFilters = computed(() => activeFilters.value);
  const getJitsiConnectionData = computed(() => jitsiConnectionData.value);

  /**
   * Load webinars with filtering and pagination
   */
  async function loadWebinars(page = 1, per_page = 20, resetFilters = false) {
    isLoading.value = true;
    error.value = null;

    if (resetFilters) {
      activeFilters.value = {
        title: '',
        host_id: null,
        status: null,
        is_public: null,
        plant_topic_id: null,
        date_from: null,
        date_to: null
      };
    }

    try {
      const response = await webinarsApi.getWebinars(
        page,
        per_page,
        activeFilters.value
      );
      
      webinars.value = response.items || [];
      
      pagination.value = {
        page: response.page || page,
        total_pages: response.total_pages || 1,
        total_items: response.total_items || 0,
        per_page: response.per_page || per_page
      };

      return webinars.value;
    } catch (e) {
      error.value = e.message || 'Ошибка загрузки списка вебинаров';
      console.error('Error loading webinars list:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load detailed webinar info by ID
   */
  async function loadWebinarById(id) {
    if (!id) {
      error.value = 'ID вебинара не указан';
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const webinar = await webinarsApi.getWebinarById(id);
      currentWebinar.value = webinar;
      return webinar;
    } catch (e) {
      error.value = e.message || `Ошибка загрузки вебинара с ID ${id}`;
      console.error(`Error loading webinar with ID ${id}:`, e);
      currentWebinar.value = null;
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Create new webinar
   */
  async function createWebinar(webinarData) {
    isLoading.value = true;
    error.value = null;

    try {
      const newWebinar = await webinarsApi.createWebinar(webinarData);
      // Reload webinars list
      await loadWebinars(pagination.value.page, pagination.value.per_page);
      return newWebinar;
    } catch (e) {
      error.value = e.message || 'Ошибка создания вебинара';
      console.error('Error creating webinar:', e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update webinar
   */
  async function updateWebinar(id, webinarData) {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedWebinar = await webinarsApi.updateWebinar(id, webinarData);
      
      // If this is the current webinar, update it in store
      if (currentWebinar.value && currentWebinar.value.id === id) {
        currentWebinar.value = updatedWebinar;
      }
      
      // Update in webinars list if present
      const index = webinars.value.findIndex(webinar => webinar.id === id);
      if (index !== -1) {
        webinars.value[index] = updatedWebinar;
      }
      
      return updatedWebinar;
    } catch (e) {
      error.value = e.message || `Ошибка обновления вебинара с ID ${id}`;
      console.error(`Error updating webinar with ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete webinar
   */
  async function deleteWebinar(id) {
    isLoading.value = true;
    error.value = null;

    try {
      await webinarsApi.deleteWebinar(id);
      
      // Remove from current list
      webinars.value = webinars.value.filter(webinar => webinar.id !== id);
      
      // Clear current webinar if it's the one being deleted
      if (currentWebinar.value && currentWebinar.value.id === id) {
        currentWebinar.value = null;
      }
      
      return true;
    } catch (e) {
      error.value = e.message || `Ошибка удаления вебинара с ID ${id}`;
      console.error(`Error deleting webinar with ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Join webinar and get connection data
   */
  async function joinWebinar(id) {
    isLoading.value = true;
    error.value = null;

    try {
      const connectionData = await webinarsApi.joinWebinar(id);
      jitsiConnectionData.value = connectionData;
      return connectionData;
    } catch (e) {
      error.value = e.message || `Ошибка присоединения к вебинару с ID ${id}`;
      console.error(`Error joining webinar with ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Get Jitsi token for webinar
   */
  async function getJitsiToken(id) {
    try {
      const tokenData = await webinarsApi.getJitsiToken(id);
      return tokenData;
    } catch (e) {
      error.value = e.message || `Ошибка получения токена для вебинара с ID ${id}`;
      console.error(`Error getting Jitsi token for webinar ${id}:`, e);
      throw e;
    }
  }

  /**
   * Get Jitsi configuration for webinar
   */
  async function getJitsiConfig(id) {
    try {
      const configData = await webinarsApi.getJitsiConfig(id);
      return configData;
    } catch (e) {
      error.value = e.message || `Ошибка получения конфигурации для вебинара с ID ${id}`;
      console.error(`Error getting Jitsi config for webinar ${id}:`, e);
      throw e;
    }
  }

  /**
   * Load webinars hosted by current user
   */
  async function loadMyHostedWebinars(page = 1, per_page = 20) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await webinarsApi.getMyHostedWebinars(page, per_page);
      myHostedWebinars.value = response.items || [];
      return myHostedWebinars.value;
    } catch (e) {
      error.value = e.message || 'Ошибка загрузки моих вебинаров';
      console.error('Error loading my hosted webinars:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load webinars where current user is participating
   */
  async function loadMyParticipatingWebinars(page = 1, per_page = 20) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await webinarsApi.getMyParticipatingWebinars(page, per_page);
      myParticipatingWebinars.value = response.items || [];
      return myParticipatingWebinars.value;
    } catch (e) {
      error.value = e.message || 'Ошибка загрузки вебинаров, в которых я участвую';
      console.error('Error loading my participating webinars:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update filters and load webinars
   */
  async function updateFilters(newFilters) {
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key] !== undefined && key in activeFilters.value) {
        activeFilters.value[key] = newFilters[key];
      }
    });
    
    return await loadWebinars(1, pagination.value.per_page);
  }

  /**
   * Clear all filters and reload webinars
   */
  async function clearFilters() {
    return await loadWebinars(1, pagination.value.per_page, true);
  }

  /**
   * Clear error message
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Clear Jitsi connection data
   */
  function clearJitsiConnectionData() {
    jitsiConnectionData.value = null;
  }

  // Return public store API
  return {
    // State
    webinars,
    currentWebinar,
    myHostedWebinars,
    myParticipatingWebinars,
    isLoading,
    error,
    pagination,
    activeFilters,
    jitsiConnectionData,
    
    // Getters
    getWebinars,
    getCurrentWebinar,
    getMyHostedWebinars,
    getMyParticipatingWebinars,
    getIsLoading,
    getError,
    getPagination,
    getActiveFilters,
    getJitsiConnectionData,
    
    // Actions
    loadWebinars,
    loadWebinarById,
    createWebinar,
    updateWebinar,
    deleteWebinar,
    joinWebinar,
    getJitsiToken,
    getJitsiConfig,
    loadMyHostedWebinars,
    loadMyParticipatingWebinars,
    updateFilters,
    clearFilters,
    clearError,
    clearJitsiConnectionData
  };
});
