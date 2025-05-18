// src/features/plants/store/plantsStore.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { plantsApi } from '../api/plantsApi';

/**
 * Хранилище для управления состоянием растений
 */
export const usePlantsStore = defineStore('plants', () => {
  // State (состояние)
  const plants = ref([]);
  const currentPlant = ref(null);
  const categories = ref([]);
  const climateZones = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    itemsPerPage: 20
  });
  const activeFilters = ref({
    category_id: null,
    climate_zone_id: null,
    name: '',
    plant_type: null,
    care_difficulty: null,
    light_level: null,
    watering_frequency: null,
    sort_by: 'name',
    sort_direction: 'asc'
  });

  // Getters (вычисляемые свойства)
  const getPlants = computed(() => plants.value);
  const getCurrentPlant = computed(() => currentPlant.value);
  const getCategories = computed(() => categories.value);
  const getClimateZones = computed(() => climateZones.value);
  const getIsLoading = computed(() => isLoading.value);
  const getError = computed(() => error.value);
  const getPagination = computed(() => pagination.value);
  const getActiveFilters = computed(() => activeFilters.value);

  /**
   * Загружает список растений с учетом фильтров и пагинации
   */
  async function loadPlants(page = 1, per_page = 20, resetFilters = false) {
    isLoading.value = true;
    error.value = null;

    if (resetFilters) {
      activeFilters.value = {
        category_id: null,
        climate_zone_id: null,
        name: '',
        plant_type: null,
        care_difficulty: null,
        light_level: null,
        watering_frequency: null,
        sort_by: 'name',
        sort_direction: 'asc'
      };
    }

    try {
      // Подготавливаем фильтры, исключая пустые значения
      const filters = {};
      
      if (activeFilters.value.name) {
        filters.name = activeFilters.value.name;
      }
      if (activeFilters.value.category_id) {
        filters.category_id = activeFilters.value.category_id;
      }
      if (activeFilters.value.climate_zone_id) {
        filters.climate_zone_id = activeFilters.value.climate_zone_id;
      }
      if (activeFilters.value.plant_type) {
        filters.plant_type = activeFilters.value.plant_type;
      }
      if (activeFilters.value.care_difficulty) {
        filters.care_difficulty = activeFilters.value.care_difficulty;
      }
      if (activeFilters.value.light_level) {
        filters.light_level = activeFilters.value.light_level;
      }
      if (activeFilters.value.watering_frequency) {
        filters.watering_frequency = activeFilters.value.watering_frequency;
      }
      if (activeFilters.value.sort_by) {
        filters.sort_by = activeFilters.value.sort_by;
      }
      if (activeFilters.value.sort_direction) {
        filters.sort_direction = activeFilters.value.sort_direction;
      }

      const response = await plantsApi.getPlants(page, per_page, filters);

      plants.value = response.items || [];
      
      // Обновляем информацию о пагинации в соответствии со схемой бэкенда
      pagination.value = {
        currentPage: response.page || page,
        totalPages: response.pages || 1,
        totalItems: response.total || 0,
        itemsPerPage: response.size || per_page
      };

      return plants.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Ошибка при загрузке списка растений';
      console.error('Ошибка при загрузке списка растений:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Поиск растений с фильтрацией
   */
  async function searchPlants(query, filters = {}, page = 1, per_page = 20) {
    isLoading.value = true;
    error.value = null;

    try {
      // Объединяем переданные фильтры с активными
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
        currentPage: response.page || page,
        totalPages: response.pages || 1,
        totalItems: response.total || 0,
        itemsPerPage: response.size || per_page
      };

      return plants.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Ошибка при поиске растений';
      console.error('Ошибка при поиске растений:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загружает детальную информацию о растении по ID
   */
  async function loadPlantById(id) {
    if (!id) {
      error.value = 'Не указан ID растения';
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const plant = await plantsApi.getPlantById(id);
      currentPlant.value = plant;
      return plant;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || `Ошибка при загрузке растения с ID ${id}`;
      console.error(`Ошибка при загрузке растения с ID ${id}:`, e);
      currentPlant.value = null;
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загружает список категорий растений
   */
  async function loadCategories() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await plantsApi.getCategories();
      // Обрабатываем как массив или объект с items
      categories.value = Array.isArray(response) ? response : (response.items || []);
      return categories.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Ошибка при загрузке категорий растений';
      console.error('Ошибка при загрузке категорий растений:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загружает список климатических зон
   */
  async function loadClimateZones() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await plantsApi.getClimateZones();
      // Обрабатываем как массив или объект с items
      climateZones.value = Array.isArray(response) ? response : (response.items || []);
      return climateZones.value;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Ошибка при загрузке климатических зон';
      console.error('Ошибка при загрузке климатических зон:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Обновляет фильтры и загружает растения
   */
  async function updateFilters(newFilters) {
    // Обновляем только переданные фильтры
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key] !== undefined && key in activeFilters.value) {
        activeFilters.value[key] = newFilters[key];
      }
    });
    
    // Если был передан поисковый запрос, используем поиск
    if (newFilters.searchQuery !== undefined) {
      activeFilters.value.name = newFilters.searchQuery;
    }
    
    // Сбрасываем на первую страницу при изменении фильтров
    return await loadPlants(1, pagination.value.itemsPerPage);
  }

  /**
   * Очищает все фильтры и перезагружает растения
   */
  async function clearFilters() {
    return await loadPlants(1, pagination.value.itemsPerPage, true);
  }

  /**
   * Создает новое растение (для администраторов)
   */
  async function createPlant(plantData) {
    isLoading.value = true;
    error.value = null;

    try {
      const newPlant = await plantsApi.createPlant(plantData);
      // Обновляем список растений
      await loadPlants(pagination.value.currentPage, pagination.value.itemsPerPage);
      return newPlant;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || 'Ошибка при создании растения';
      console.error('Ошибка при создании растения:', e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Обновляет растение (для администраторов)
   */
  async function updatePlant(id, plantData) {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedPlant = await plantsApi.updatePlant(id, plantData);
      
      // Если это текущее растение, обновляем его в хранилище
      if (currentPlant.value && currentPlant.value.id === id) {
        currentPlant.value = updatedPlant;
      }
      
      // Обновляем список растений
      const index = plants.value.findIndex(plant => plant.id === id);
      if (index !== -1) {
        plants.value[index] = updatedPlant;
      }
      
      return updatedPlant;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || `Ошибка при обновлении растения с ID ${id}`;
      console.error(`Ошибка при обновлении растения с ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Удаляет растение (для администраторов)
   */
  async function deletePlant(id) {
    isLoading.value = true;
    error.value = null;

    try {
      await plantsApi.deletePlant(id);
      
      // Удаляем из текущего списка
      plants.value = plants.value.filter(plant => plant.id !== id);
      
      // Если это текущее растение, очищаем его
      if (currentPlant.value && currentPlant.value.id === id) {
        currentPlant.value = null;
      }
      
      return true;
    } catch (e) {
      error.value = e.response?.data?.detail || e.message || `Ошибка при удалении растения с ID ${id}`;
      console.error(`Ошибка при удалении растения с ID ${id}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Очищает сообщение об ошибке
   */
  function clearError() {
    error.value = null;
  }

  // Возвращаем публичное API хранилища
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