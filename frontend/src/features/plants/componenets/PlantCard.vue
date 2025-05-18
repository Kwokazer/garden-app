<!-- src/features/plants/components/PlantCard.vue -->
<template>
    <div class="card plant-card h-100 border-0 shadow-sm">
      <!-- Изображение растения -->
      <div class="card-img-top-wrapper">
        <img v-if="plant.images && plant.images.length > 0" 
             :src="plant.images[0].url" 
             :alt="plant.name"
             class="card-img-top"
             @error="handleImageError">
        <div v-else class="card-img-placeholder d-flex align-items-center justify-content-center bg-light text-muted">
          <i class="bi bi-flower1 display-3"></i>
        </div>
        
        <!-- Бейдж категории -->
        <span v-if="plant.category" class="position-absolute top-0 end-0 m-2 badge bg-success">
          {{ plant.category.name }}
        </span>
      </div>
      
      <!-- Содержимое карточки -->
      <div class="card-body d-flex flex-column">
        <h5 class="card-title fw-bold text-primary mb-1">{{ plant.name }}</h5>
        <p class="card-text text-muted small mb-1">{{ plant.latin_name }}</p>
        
        <!-- Характеристики растения -->
        <div class="plant-features mb-3">
          <div class="d-flex align-items-center mb-1 small">
            <span class="badge bg-light text-dark me-2">
              <i class="bi bi-thermometer-half me-1"></i>
              {{ getTemperatureLabel(plant.temperature_min, plant.temperature_max) }}
            </span>
            <span class="badge bg-light text-dark me-2">
              <i class="bi bi-droplet me-1"></i>
              {{ getWateringLabel(plant.watering_frequency) }}
            </span>
            <span class="badge bg-light text-dark">
              <i class="bi bi-brightness-high me-1"></i>
              {{ getLightLabel(plant.light_level) }}
            </span>
          </div>
        </div>
        
        <!-- Краткое описание -->
        <p class="card-text plant-description mb-3">
          {{ truncateDescription(plant.description, 100) }}
        </p>
        
        <!-- Климатические зоны -->
        <div v-if="plant.climate_zones && plant.climate_zones.length > 0" class="small mb-3">
          <span class="text-muted me-2">Климатические зоны:</span>
          <span v-for="(zone, index) in plant.climate_zones" :key="zone.id" class="badge bg-info text-white me-1">
            {{ zone.name }}
          </span>
        </div>
        
        <!-- Кнопка подробнее -->
        <router-link 
          :to="{ name: 'PlantDetails', params: { id: plant.id } }" 
          class="btn btn-outline-primary mt-auto">
          Подробнее
        </router-link>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  // Определение входных параметров
  const props = defineProps({
    plant: {
      type: Object,
      required: true
    }
  });
  
  // Обработка ошибок загрузки изображения
  function handleImageError(event) {
    // Заменяем битое изображение на placeholder
    event.target.src = '/placeholder-plant.jpg'; // Предполагаем, что у нас есть такое изображение
    // Или можно использовать класс для отображения placeholder'а
    event.target.classList.add('img-error');
  }
  
  // Обрезаем описание до указанной длины
  function truncateDescription(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    
    return text.substring(0, maxLength) + '...';
  }
  
  // Получаем текстовую метку для диапазона температур
  function getTemperatureLabel(min, max) {
    if (min === undefined || max === undefined) return 'Не указано';
    
    return `${min}°C - ${max}°C`;
  }
  
  // Получаем текстовую метку для частоты полива
  function getWateringLabel(frequency) {
    if (!frequency) return 'Не указано';
    
    const wateringLabels = {
      'daily': 'Ежедневно',
      'twice_a_week': '2 раза в неделю',
      'weekly': 'Еженедельно',
      'bi_weekly': 'Раз в 2 недели',
      'monthly': 'Ежемесячно',
      'rarely': 'Редко'
    };
    
    return wateringLabels[frequency] || frequency;
  }
  
  // Получаем текстовую метку для уровня освещения
  function getLightLabel(level) {
    if (!level) return 'Не указано';
    
    const lightLabels = {
      'full_sun': 'Прямой свет',
      'partial_sun': 'Полутень',
      'shade': 'Тень',
      'low_light': 'Малое освещение'
    };
    
    return lightLabels[level] || level;
  }
  </script>
  
  <style scoped>
  .plant-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .plant-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
  }
  
  .card-img-top-wrapper {
    position: relative;
    height: 200px;
    overflow: hidden;
  }
  
  .card-img-top {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
  }
  
  .plant-card:hover .card-img-top {
    transform: scale(1.05);
  }
  
  .card-img-placeholder {
    width: 100%;
    height: 100%;
    background-color: #f8f9fa;
    color: #adb5bd;
  }
  
  .plant-description {
    font-size: 0.9rem;
    color: #6c757d;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .plant-features {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  /* Стили для различных уровней полива и освещения */
  .badge {
    font-weight: normal;
    padding: 0.35em 0.65em;
  }
  
  .img-error {
    /* Стили для изображений, которые не загрузились */
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
  }
  </style>