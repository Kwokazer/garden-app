// src/features/plants/api/plantsApi.js

import axios from '../../../interceptors/axios';

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
      // Convert frontend filter names to backend ones
      const params = {
        page,
        per_page,
      };

      // Map frontend filter properties to backend properties
      if (filters.searchQuery) {
        params.name = filters.searchQuery;
      }
      
      if (filters.category_id) {
        params.category_id = filters.category_id;
      }
      
      if (filters.climate_zone_id) {
        params.climate_zone_id = filters.climate_zone_id;
      }
      
      if (filters.plant_type) {
        params.plant_type = filters.plant_type;
      }
      
      if (filters.care_difficulty) {
        params.care_difficulty = filters.care_difficulty;
      }

      if (filters.sort_by) {
        params.sort_by = filters.sort_by;
      }
      
      if (filters.sort_direction) {
        params.sort_direction = filters.sort_direction;
      }
      
      const response = await axios.get('/plants', { params });
      return response.data;
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
      const response = await axios.get(`/plants/${id}`);
      return response.data;
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
      const params = {
        query: query,
        ...options
      };

      const response = await axios.get('/plants/search', { params });
      return response.data;
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
      const response = await axios.get('/plant-categories', { 
        params: { page, per_page } 
      });
      return response.data;
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
      const response = await axios.get('/climate-zones', { 
        params: { page, per_page } 
      });
      return response.data;
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
      const response = await axios.post('/plants', plantData);
      return response.data;
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
      const response = await axios.put(`/plants/${id}`, plantData);
      return response.data;
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
      const response = await axios.delete(`/plants/${id}`);
      return response.data;
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
      const response = await axios.post(`/plants/${plantId}/images`, imageData);
      return response.data;
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
      const response = await axios.delete(`/plants/images/${imageId}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting image ${imageId}:`, error);
      throw error;
    }
  }
};