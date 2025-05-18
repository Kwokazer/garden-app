// src/features/plants/api/plantsApi.js

// Используем тот же BASE_API_URL как в authApi.js
const BASE_API_URL = "/api/v1"

/**
 * Обрабатывает ответы от API (такая же функция как в authApi.js)
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
 * API client for working with plants
 */
export const plantsApi = {
  /**
   * Get list of all plants with pagination and filtering
   * @param {number} page - Page number (starting from 1)
   * @param {number} per_page - Number of plants per page
   * @param {Object} filters - Filter object
   * @returns {Promise<Object>} - Server response with plants
   */
  async getPlants(page = 1, per_page = 20, filters = {}) {
    try {
      // Создаем параметры запроса
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('per_page', per_page);
      
      // Добавляем фильтры в запрос
      if (filters.searchQuery) {
        params.append('name', filters.searchQuery);
      }
      
      if (filters.category_id) {
        params.append('category_id', filters.category_id);
      }
      
      if (filters.climate_zone_id) {
        params.append('climate_zone_id', filters.climate_zone_id);
      }
      
      if (filters.plant_type) {
        params.append('plant_type', filters.plant_type.toUpperCase());
      }
      
      if (filters.care_difficulty) {
        params.append('care_difficulty', filters.care_difficulty);
      }

      if (filters.sort_by) {
        params.append('sort_by', filters.sort_by);
      }
      
      if (filters.sort_direction) {
        params.append('sort_direction', filters.sort_direction);
      }
      
      // Формируем URL с параметрами
      const url = `${BASE_API_URL}/plants?${params.toString()}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error fetching plants list:', error);
      throw error;
    }
  },

  /**
   * Get detailed plant information by ID
   * @param {string|number} id - Plant ID
   * @returns {Promise<Object>} - Server response with detailed plant information
   */
  async getPlantById(id) {
    try {
      const url = `${BASE_API_URL}/plants/${id}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error fetching plant with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Search plants by name or other parameters
   * @param {string} query - Search query
   * @param {Object} options - Additional search parameters
   * @returns {Promise<Object>} - Server response with search results
   */
  async searchPlants(query, options = {}) {
    try {
      // Создаем параметры запроса
      const params = new URLSearchParams();
      params.append('query', query);
      
      // Добавляем дополнительные параметры
      Object.entries(options).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value);
        }
      });
      
      const url = `${BASE_API_URL}/plants/search?${params.toString()}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error searching plants:', error);
      throw error;
    }
  },

  /**
   * Get list of plant categories
   * @param {number} page - Page number
   * @param {number} per_page - Number of items per page
   * @returns {Promise<Array>} - Array of plant categories
   */
  async getCategories(page = 1, per_page = 100) {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('per_page', per_page);
      
      const url = `${BASE_API_URL}/plant-categories?${params.toString()}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error fetching plant categories:', error);
      throw error;
    }
  },

  /**
   * Get list of climate zones
   * @param {number} page - Page number  
   * @param {number} per_page - Number of items per page
   * @returns {Promise<Array>} - Array of climate zones
   */
  async getClimateZones(page = 1, per_page = 100) {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('per_page', per_page);
      
      const url = `${BASE_API_URL}/climate-zones?${params.toString()}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error fetching climate zones:', error);
      throw error;
    }
  },

  /**
   * Create new plant (requires admin authorization)
   * @param {Object} plantData - Plant data
   * @returns {Promise<Object>} - Server response with created plant
   */
  async createPlant(plantData) {
    try {
      const url = `${BASE_API_URL}/plants`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(plantData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error creating plant:', error);
      throw error;
    }
  },

  /**
   * Update plant (requires admin authorization)
   * @param {string|number} id - Plant ID
   * @param {Object} plantData - New plant data
   * @returns {Promise<Object>} - Server response with updated plant
   */
  async updatePlant(id, plantData) {
    try {
      const url = `${BASE_API_URL}/plants/${id}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(plantData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error updating plant with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete plant (requires admin authorization)
   * @param {string|number} id - Plant ID
   * @returns {Promise<Object>} - Server response
   */
  async deletePlant(id) {
    try {
      const url = `${BASE_API_URL}/plants/${id}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error deleting plant with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Add image to plant (requires admin authorization)
   * @param {string|number} plantId - Plant ID
   * @param {Object} imageData - Image data
   * @returns {Promise<Object>} - Server response with added image information
   */
  async addPlantImage(plantId, imageData) {
    try {
      const url = `${BASE_API_URL}/plants/${plantId}/images`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(imageData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error adding image to plant with ID ${plantId}:`, error);
      throw error;
    }
  },

  /**
   * Delete plant image (requires admin authorization)
   * @param {string|number} imageId - Image ID
   * @returns {Promise<Object>} - Server response
   */
  async deletePlantImage(imageId) {
    try {
      const url = `${BASE_API_URL}/plants/images/${imageId}`;
      console.log('Fetching URL:', url);
      
      // Get access token from localStorage
      const token = localStorage.getItem('accessToken');
      const headers = {
        'Content-Type': 'application/json',
      };
      
      // Add Authorization header if token exists
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: headers
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error deleting image ${imageId}:`, error);
      throw error;
    }
  }
};