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
    itemsPerPage: 10
  });
  const activeFilters = ref({
    category: null,
    climateZone: null,
    searchQuery: '',
    sortBy: 'name',
    sortDirection: 'asc'
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
  async function loadPlants(page = 1, limit = 10, resetFilters = false) {
    isLoading.value = true;
    error.value = null;

    if (resetFilters) {
      activeFilters.value = {
        category: null,
        climateZone: null,
        searchQuery: '',
        sortBy: 'name',
        sortDirection: 'asc'
      };
    }

    try {
      const filters = {
        sort_by: activeFilters.value.sortBy,
        sort_direction: activeFilters.value.sortDirection
      };

      if (activeFilters.value.category) {
        filters.category_id = activeFilters.value.category;
      }

      if (activeFilters.value.climateZone) {
        filters.climate_zone_id = activeFilters.value.climateZone;
      }

      // Если есть поисковый запрос, используем метод поиска
      let response;
      if (activeFilters.value.searchQuery) {
        response = await plantsApi.searchPlants(
          activeFilters.value.searchQuery,
          { page, limit, ...filters }
        );
      } else {
        response = await plantsApi.getPlants(page, limit, filters);
      }

      plants.value = response.items || response.data || [];
      
      // Обновляем информацию о пагинации
      pagination.value = {
        currentPage: response.page || page,
        totalPages: response.total_pages || 1,
        totalItems: response.total_items || response.total || plants.value.length,
        itemsPerPage: response.per_page || limit
      };

      return plants.value;
    } catch (e) {
      error.value = e.message || 'Ошибка при загрузке списка растений';
      console.error('Ошибка при загрузке списка растений:', e);
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
      error.value = e.message || `Ошибка при загрузке растения с ID ${id}`;
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
  async function loadCategories(parentId = null) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await plantsApi.getCategories(parentId);
      categories.value = response.items || response;
      return categories.value;
    } catch (e) {
      error.value = e.message || 'Ошибка при загрузке категорий растений';
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
      climateZones.value = response.items || response;
      return climateZones.value;
    } catch (e) {
      error.value = e.message || 'Ошибка при загрузке климатических зон';
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
    activeFilters.value = { ...activeFilters.value, ...newFilters };
    return await loadPlants(1, pagination.value.itemsPerPage); // Сбрасываем на первую страницу при изменении фильтров
  }

  /**
   * Очищает все фильтры и перезагружает растения
   */
  async function clearFilters() {
    return await loadPlants(1, pagination.value.itemsPerPage, true); // Сброс фильтров
  }

  /**
   * Создает новое растение (для администраторов)
   */
  async function createPlant(plantData) {
    isLoading.value = true;
    error.value = null;

    try {
      const newPlant = await plantsApi.createPlant(plantData);
      // Обновляем список растений, добавляя новое
      await loadPlants(pagination.value.currentPage, pagination.value.itemsPerPage);
      return newPlant;
    } catch (e) {
      error.value = e.message || 'Ошибка при создании растения';
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
      error.value = e.message || `Ошибка при обновлении растения с ID ${id}`;
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
      error.value = e.message || `Ошибка при удалении растения с ID ${id}`;
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