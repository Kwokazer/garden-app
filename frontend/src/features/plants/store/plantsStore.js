// src/features/plants/store/plantsStore.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { plantsApi } from '../api/plantsApi';

/**
 * Plants state management store
 */
export const usePlantsStore = defineStore('plants', () => {
  // State
  const plants = ref([]);
  const currentPlant = ref(null);
  const categories = ref([]);
  const climateZones = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    total_pages: 1,
    total_items: 0,
    per_page: 20
  });
  const activeFilters = ref({
    searchQuery: '',
    category_id: null,
    climate_zone_id: null,
    plant_type: null,
    care_difficulty: null,
    light_level: null,
    watering_frequency: null,
    sort_by: 'name',
    sort_direction: 'asc'
  });

  // Getters
  const getPlants = computed(() => plants.value);
  const getCurrentPlant = computed(() => currentPlant.value);
  const getCategories = computed(() => categories.value);
  const getClimateZones = computed(() => climateZones.value);
  const getIsLoading = computed(() => isLoading.value);
  const getError = computed(() => error.value);
  const getPagination = computed(() => pagination.value);
  const getActiveFilters = computed(() => activeFilters.value);

  /**
   * Load plants with filtering and pagination
   */
  async function loadPlants(page = 1, per_page = 20, resetFilters = false) {
    isLoading.value = true;
    error.value = null;

    if (resetFilters) {
      activeFilters.value = {
        searchQuery: '',
        category_id: null,
        climate_zone_id: null,
        plant_type: null,
        care_difficulty: null,
        light_level: null,
        watering_frequency: null,
        sort_by: 'name',
        sort_direction: 'asc'
      };
    }

    try {
      const response = await plantsApi.getPlants(
        page,
        per_page,
        activeFilters.value
      );
      
      // Update plants list from response
      plants.value = response.items || [];
      
      // Update pagination according to backend schema
      pagination.value = {
        page: response.page || page,
        total_pages: response.total_pages || 1,
        total_items: response.total_items || 0,
        per_page: response.per_page || per_page
      };

      return plants.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error loading plants list';
      console.error('Error loading plants list:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Search plants with filtering
   */
  async function searchPlants(query, filters = {}, page = 1, per_page = 20) {
    isLoading.value = true;
    error.value = null;

    try {
      // Combine passed filters with active sort settings
      const searchFilters = {
        ...filters,
        page,
        per_page,
        sort_by: activeFilters.value.sort_by,
        sort_direction: activeFilters.value.sort_direction
      };

      const response = await plantsApi.searchPlants(query, searchFilters);

      plants.value = response.items || [];
      
      pagination.value = {
        page: response.page || page,
        total_pages: response.total_pages || 1,
        total_items: response.total_items || 0,
        per_page: response.per_page || per_page
      };

      return plants.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error searching plants';
      console.error('Error searching plants:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load detailed plant info by ID
   */
  async function loadPlantById(id) {
    if (!id) {
      error.value = 'Plant ID not specified';
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const plant = await plantsApi.getPlantById(id);
      currentPlant.value = plant;
      return plant;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || `Error loading plant with ID ${id}`;
      console.error(`Error loading plant with ID ${id}:`, e);
      currentPlant.value = null;
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load plant categories
   */
  async function loadCategories() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await plantsApi.getCategories();
      // Handle both array response or object with items
      categories.value = Array.isArray(response) ? response : (response.items || []);
      return categories.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error loading plant categories';
      console.error('Error loading plant categories:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load climate zones
   */
  async function loadClimateZones() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await plantsApi.getClimateZones();
      // Handle both array response or object with items
      climateZones.value = Array.isArray(response) ? response : (response.items || []);
      return climateZones.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error loading climate zones';
      console.error('Error loading climate zones:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update filters and load plants
   */
  async function updateFilters(newFilters) {
    // Update only provided filters
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key] !== undefined && key in activeFilters.value) {
        activeFilters.value[key] = newFilters[key];
      }
    });
    
    // If search query was passed, update name filter
    if (newFilters.searchQuery !== undefined) {
      activeFilters.value.searchQuery = newFilters.searchQuery;
    }
    
    // Reset to first page when filters change
    return await loadPlants(1, pagination.value.per_page);
  }

  /**
   * Clear all filters and reload plants
   */
  async function clearFilters() {
    return await loadPlants(1, pagination.value.per_page, true);
  }

  /**
   * Create new plant (admin)
   */
  async function createPlant(plantData) {
    isLoading.value = true;
    error.value = null;

    try {
      const newPlant = await plantsApi.createPlant(plantData);
      // Reload plants list
      await loadPlants(pagination.value.page, pagination.value.per_page);
      return newPlant;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Error creating plant';
      console.error('Error creating plant:', e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update plant (admin)
   */
  async function updatePlant(id, plantData) {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedPlant = await plantsApi.updatePlant(id, plantData);
      
      // If this is the current plant, update it in store
      if (currentPlant.value && currentPlant.value.id === id) {
        currentPlant.value = updatedPlant;
      }
      
      // Update in plants list if present
      const index = plants.value.findIndex(plant => plant.id === id);
      if (index !== -1) {
        plants.value[index] = updatedPlant;
      }
      
      return updatedPlant;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || `Error updating plant with ID ${id}`;
      console.error(`Error updating plant with ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete plant (admin)
   */
  async function deletePlant(id) {
    isLoading.value = true;
    error.value = null;

    try {
      await plantsApi.deletePlant(id);
      
      // Remove from current list
      plants.value = plants.value.filter(plant => plant.id !== id);
      
      // Clear current plant if it's the one being deleted
      if (currentPlant.value && currentPlant.value.id === id) {
        currentPlant.value = null;
      }
      
      return true;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || `Error deleting plant with ID ${id}`;
      console.error(`Error deleting plant with ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Clear error message
   */
  function clearError() {
    error.value = null;
  }

  // Return public store API
  return {
    // State
    plants,
    currentPlant,
    categories,
    climateZones,
    isLoading,
    error,
    pagination,
    activeFilters,
    
    // Getters
    getPlants,
    getCurrentPlant,
    getCategories,
    getClimateZones,
    getIsLoading,
    getError,
    getPagination,
    getActiveFilters,
    
    // Actions
    loadPlants,
    searchPlants,
    loadPlantById,
    loadCategories,
    loadClimateZones,
    updateFilters,
    clearFilters,
    createPlant,
    updatePlant,
    deletePlant,
    clearError
  };
});