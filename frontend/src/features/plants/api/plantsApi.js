// src/features/plants/api/plantsApi.js

import axios from '../../../interceptors/axios';

/**
 * API клиент для работы с растениями
 */
export const plantsApi = {
  /**
   * Получает список всех растений с пагинацией
   * @param {number} page - Номер страницы (начиная с 1)
   * @param {number} per_page - Количество растений на странице
   * @param {Object} filters - Объект с фильтрами
   * @returns {Promise<Object>} - Ответ от сервера с растениями
   */
  async getPlants(page = 1, per_page = 20, filters = {}) {
    let params = {
      page,
      per_page,
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
   * @param {string} query - Поисковый запрос
   * @param {Object} options - Дополнительные параметры поиска
   * @returns {Promise<Object>} - Ответ от сервера с результатами поиска
   */
  async searchPlants(query, options = {}) {
    let params = {
      query: query,
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
   * @param {number} page - Номер страницы
   * @param {number} per_page - Количество записей на странице
   * @returns {Promise<Array>} - Массив категорий растений
   */
  async getCategories(page = 1, per_page = 100) {
    try {
      const response = await axios.get('/plant-categories', { 
        params: { page, per_page } 
      });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении категорий растений:', error);
      throw error;
    }
  },

  /**
   * Получает список климатических зон
   * @param {number} page - Номер страницы  
   * @param {number} per_page - Количество записей на странице
   * @returns {Promise<Array>} - Массив климатических зон
   */
  async getClimateZones(page = 1, per_page = 100) {
    try {
      const response = await axios.get('/climate-zones', { 
        params: { page, per_page } 
      });
      return response.data;
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
      const response = await axios.post('/plants', plantData);
      return response.data;
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
      const response = await axios.put(`/plants/${id}`, plantData);
      return response.data;
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
      const response = await axios.delete(`/plants/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при удалении растения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Добавляет изображение к растению (требуется авторизация с правами администратора)
   * @param {string|number} plantId - ID растения
   * @param {Object} imageData - Данные изображения
   * @returns {Promise<Object>} - Ответ от сервера с информацией о добавленном изображении
   */
  async addPlantImage(plantId, imageData) {
    try {
      const response = await axios.post(`/plants/${plantId}/images`, imageData);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при добавлении изображения к растению с ID ${plantId}:`, error);
      throw error;
    }
  },

  /**
   * Удаляет изображение растения (требуется авторизация с правами администратора)
   * @param {string|number} imageId - ID изображения
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async deletePlantImage(imageId) {
    try {
      const response = await axios.delete(`/plants/images/${imageId}`);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при удалении изображения ${imageId}:`, error);
      throw error;
    }
  }
};