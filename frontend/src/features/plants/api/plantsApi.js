  /**
   * Получает список климатических зон
   * @returns {Promise<Array>} - Массив климатических зон
   */
  
  async getClimateZones() {
    try {
      if (USE_MOCK_DATA) {
        // Используем мок-данные
        const zones = getClimateZones();
        return zones;
      } else {
        // Используем реальный API
        const response = await axios.get('/climate-zones');
        return response.data;
      }
    } catch (error) {
      console.error('Ошибка при получении климатических зон:', error);
      throw error;
    }
  },

  /**
   * Создает новое растение (требуется авторизация с правами администратора)
   * @param {Object} plantData - Данные растения
   * @returns {Promise<Object>} - Ответ от сервера с созданным растением
   */
  async createPlant(plantData) {
    try {
      if (USE_MOCK_DATA) {
        // Мок-реализация не поддерживает создание растений
        throw new Error('Создание растений недоступно в демо-режиме');
      } else {
        // Используем реальный API
        const response = await axios.post('/plants', plantData);
        return response.data;
      }
    } catch (error) {
      console.error('Ошибка при создании растения:', error);
      throw error;
    }
  },

  /**
   * Обновляет растение (требуется авторизация с правами администратора)
   * @param {string|number} id - ID растения
   * @param {Object} plantData - Новые данные растения
   * @returns {Promise<Object>} - Ответ от сервера с обновленным растением
   */
  async updatePlant(id,// src/features/plants/api/plantsApi.js

import axios from '../../../interceptors/axios';

/**
 * API клиент для работы с растениями
 */
export const plantsApi = {
  /**
   * Получает список всех растений с пагинацией
   * @param {number} page - Номер страницы (начиная с 1)
   * @param {number} limit - Количество растений на странице
   * @param {Object} filters - Объект с фильтрами
   * @returns {Promise<Object>} - Ответ от сервера с растениями
   */
  async getPlants(page = 1, limit = 10, filters = {}) {
    let params = {
      page,
      limit,
      ...filters
    };

    try {
      const response = await axios.get('/plants', { params });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении списка растений:', error);
      throw error;
    }
  },

  /**
   * Получает детальную информацию о растении по ID
   * @param {string|number} id - ID растения
   * @returns {Promise<Object>} - Ответ от сервера с детальной информацией о растении
   */
  async getPlantById(id) {
    try {
      const response = await axios.get(`/plants/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при получении растения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Поиск растений по названию или другим параметрам
   * @param {string} searchQuery - Поисковый запрос
   * @param {Object} options - Дополнительные параметры поиска
   * @returns {Promise<Object>} - Ответ от сервера с результатами поиска
   */
  async searchPlants(searchQuery, options = {}) {
    let params = {
      q: searchQuery,
      ...options
    };

    try {
      const response = await axios.get('/plants/search', { params });
      return response.data;
    } catch (error) {
      console.error('Ошибка при поиске растений:', error);
      throw error;
    }
  },

  /**
   * Получает список категорий растений
   * @param {number} parentId - ID родительской категории (необязательно)
   * @returns {Promise<Array>} - Массив категорий растений
   */
  async getCategories(parentId = null) {
    let params = {};
    if (parentId !== null) {
      params.parent_id = parentId;
    }

    try {
      const response = await axios.get('/plant-categories', { params });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении категорий растений:', error);
      throw error;
    }
  },

  /**
   * Получает список климатических зон
   * @returns {Promise<Array>} - Массив климатических зон
   */
  async getClimateZones() {
    try {
      if (USE_MOCK_DATA) {
        // Используем мок-данные
        const zones = getClimateZones();
        return zones;
      } else {
        // Используем реальный API
        const response = await axios.get('/climate-zones');
        return response.data;
      }
    } catch (error) {
      console.error('Ошибка при получении климатических зон:', error);
      throw error;
    }
  },

  /**
   * Создает новое растение (требуется авторизация с правами администратора)
   * @param {Object} plantData - Данные растения
   * @returns {Promise<Object>} - Ответ от сервера с созданным растением
   */
  async createPlant(plantData) {
    try {
      if (USE_MOCK_DATA) {
        // Мок-реализация не поддерживает создание растений
        throw new Error('Создание растений недоступно в демо-режиме');
      } else {
        // Используем реальный API
        const response = await axios.post('/plants', plantData);
        return response.data;
      }
    } catch (error) {
      console.error('Ошибка при создании растения:', error);
      throw error;
    }
  },

  /**
   * Обновляет растение (требуется авторизация с правами администратора)
   * @param {string|number} id - ID растения
   * @param {Object} plantData - Новые данные растения
   * @returns {Promise<Object>} - Ответ от сервера с обновленным растением
   */
  async updatePlant(id, plantData) {
    try {
      if (USE_MOCK_DATA) {
        // Мок-реализация не поддерживает обновление растений
        throw new Error('Обновление растений недоступно в демо-режиме');
      } else {
        // Используем реальный API
        const response = await axios.put(`/plants/${id}`, plantData);
        return response.data;
      }
    } catch (error) {
      console.error(`Ошибка при обновлении растения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Удаляет растение (требуется авторизация с правами администратора)
   * @param {string|number} id - ID растения
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async deletePlant(id) {
    try {
      if (USE_MOCK_DATA) {
        // Мок-реализация не поддерживает удаление растений
        throw new Error('Удаление растений недоступно в демо-режиме');
      } else {
        // Используем реальный API
        const response = await axios.delete(`/plants/${id}`);
        return response.data;
      }
    } catch (error) {
      console.error(`Ошибка при удалении растения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Добавляет изображение к растению (требуется авторизация с правами администратора)
   * @param {string|number} plantId - ID растения
   * @param {FormData} formData - FormData с изображением (поле должно называться 'image')
   * @returns {Promise<Object>} - Ответ от сервера с информацией о добавленном изображении
   */
  async addPlantImage(plantId, formData) {
    try {
      if (USE_MOCK_DATA) {
        // Мок-реализация не поддерживает добавление изображений
        throw new Error('Добавление изображений недоступно в демо-режиме');
      } else {
        // Используем реальный API
        const response = await axios.post(`/plants/${plantId}/images`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        return response.data;
      }
    } catch (error) {
      console.error(`Ошибка при добавлении изображения к растению с ID ${plantId}:`, error);
      throw error;
    }
  },

  /**
   * Удаляет изображение растения (требуется авторизация с правами администратора)
   * @param {string|number} plantId - ID растения
   * @param {string|number} imageId - ID изображения
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async deletePlantImage(plantId, imageId) {
    try {
      if (USE_MOCK_DATA) {
        // Мок-реализация не поддерживает удаление изображений
        throw new Error('Удаление изображений недоступно в демо-режиме');
      } else {
        // Используем реальный API
        const response = await axios.delete(`/plants/${plantId}/images/${imageId}`);
        return response.data;
      }
    } catch (error) {
      console.error(`Ошибка при удалении изображения ${imageId} растения ${plantId}:`, error);
      throw error;
    }
  }
};