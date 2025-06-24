<!-- src/features/plants/components/PlantCareInfo.vue -->
<template>
    <div class="plant-care-info">
      <div class="card shadow-sm border-0 rounded-3">
        <div class="card-header bg-light py-3">
          <h5 class="mb-0">
            <i class="bi bi-water me-2 text-primary"></i>
            Информация по уходу
          </h5>
        </div>
        <div class="card-body p-4">
          <!-- Main care parameters -->
          <div class="row gx-4 gy-3 mb-4">
            <!-- Watering -->
            <div class="col-md-4">
              <div class="care-item">
                <div class="care-icon-wrapper mb-2">
                  <i class="bi bi-droplet-fill care-icon"></i>
                </div>
                <h6 class="fw-bold mb-1">Полив</h6>
                <div class="care-value mb-1">
                  {{ getWateringLabel(plant.watering_frequency) }}
                </div>
                <div class="progress" style="height: 5px;">
                  <div class="progress-bar bg-info" :style="{ width: getWateringLevel(plant.watering_frequency) }"></div>
                </div>
                <small class="text-muted d-block mt-2">
                  {{ getWateringDescription(plant.watering_frequency) }}
                </small>
              </div>
            </div>

            <!-- Light -->
            <div class="col-md-4">
              <div class="care-item">
                <div class="care-icon-wrapper mb-2">
                  <i class="bi bi-brightness-high-fill care-icon"></i>
                </div>
                <h6 class="fw-bold mb-1">Освещение</h6>
                <div class="care-value mb-1">
                  {{ getLightLabel(plant.light_level) }}
                </div>
                <div class="progress" style="height: 5px;">
                  <div class="progress-bar bg-warning" :style="{ width: getLightLevel(plant.light_level) }"></div>
                </div>
                <small class="text-muted d-block mt-2">
                  {{ getLightDescription(plant.light_level) }}
                </small>
              </div>
            </div>

            <!-- Temperature -->
            <div class="col-md-4">
              <div class="care-item">
                <div class="care-icon-wrapper mb-2">
                  <i class="bi bi-thermometer-half care-icon"></i>
                </div>
                <h6 class="fw-bold mb-1">Температура</h6>
                <div class="care-value mb-1">
                  {{ getTemperatureRange(plant.temperature_min, plant.temperature_max) }}
                </div>
                <div class="progress" style="height: 5px;">
                  <div class="progress-bar bg-danger" :style="{ width: getTemperatureLevel(plant.temperature_min, plant.temperature_max) }"></div>
                </div>
                <small class="text-muted d-block mt-2">
                  Оптимальный температурный диапазон для роста и развития растения.
                </small>
              </div>
            </div>
          </div>
          
          <!-- Additional parameters -->
          <div class="additional-care mt-4">
            <div class="row gx-4 gy-3">
              <!-- Humidity -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-cloud-drizzle me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Влажность</h6>
                  </div>
                  <p class="mb-0">{{ getHumidityLabel(plant.humidity_level) }}</p>
                </div>
              </div>

              <!-- Fertilizing -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-flower3 me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Удобрение</h6>
                  </div>
                  <p class="mb-0">{{ getFertilizingLabel(plant.fertilizing_frequency) }}</p>
                </div>
              </div>

              <!-- Repotting -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-arrow-repeat me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Пересадка</h6>
                  </div>
                  <p class="mb-0">{{ getRepottingLabel(plant.repotting_frequency) }}</p>
                </div>
              </div>

              <!-- Care difficulty -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-clipboard-check me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Сложность ухода</h6>
                  </div>
                  <div class="d-flex align-items-center">
                    <div class="difficulty-stars">
                      <i 
                        v-for="i in 5" 
                        :key="i" 
                        class="bi" 
                        :class="i <= getDifficultyLevel(plant.care_difficulty) ? 'bi-star-fill text-warning' : 'bi-star text-muted'"
                      ></i>
                    </div>
                    <span class="ms-2">
                      {{ getDifficultyLabel(plant.care_difficulty) }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Toxicity -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-exclamation-triangle me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Токсичность</h6>
                  </div>
                  <p v-if="plant.is_toxic" class="text-danger mb-0">
                    <i class="bi bi-exclamation-circle me-1"></i>
                    Токсично для людей и/или животных
                  </p>
                  <p v-else class="text-success mb-0">
                    <i class="bi bi-check-circle me-1"></i>
                    Не токсично
                  </p>
                </div>
              </div>

              <!-- Growth rate -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-graph-up-arrow me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Скорость роста</h6>
                  </div>
                  <p class="mb-0">{{ getGrowthRateLabel(plant.growth_rate) }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Care instructions -->
          <div class="care-instructions mt-4" v-if="plant.care_instructions">
            <div class="care-section">
              <h6 class="section-title">
                <i class="bi bi-book me-2"></i>
                Инструкции по уходу
              </h6>
              <div class="care-content" v-html="formattedCareInstructions"></div>
            </div>
          </div>

          <!-- Care tips -->
          <div class="care-tips mt-4" v-if="plant.care_tips && plant.care_tips.length > 0">
            <div class="care-section">
              <h6 class="section-title">
                <i class="bi bi-lightbulb me-2"></i>
                Советы и рекомендации
              </h6>
              <ul class="care-tips-list">
                <li v-for="(tip, index) in plant.care_tips" :key="index">
                  {{ tip }}
                </li>
              </ul>
            </div>
          </div>

          <!-- Common problems -->
          <div class="care-problems mt-4" v-if="plant.common_problems && plant.common_problems.length > 0">
            <div class="care-section">
              <h6 class="section-title">
                <i class="bi bi-patch-exclamation me-2"></i>
                Частые проблемы
              </h6>
              <div class="accordion" id="problemsAccordion">
                <div 
                  v-for="(problem, index) in plant.common_problems" 
                  :key="index" 
                  class="accordion-item"
                >
                  <h2 class="accordion-header" :id="'heading' + index">
                    <button
                      class="accordion-button collapsed"
                      type="button"
                      data-bs-toggle="collapse"
                      :data-bs-target="'#collapse' + index"
                      aria-expanded="false"
                      :aria-controls="'collapse' + index"
                    >
                      {{ problem.problem || problem.title || problem.name || `Проблема ${index + 1}` }}
                    </button>
                  </h2>
                  <div
                    :id="'collapse' + index"
                    class="accordion-collapse collapse"
                    :aria-labelledby="'heading' + index"
                    data-bs-parent="#problemsAccordion"
                  >
                    <div class="accordion-body">
                      <p v-if="problem.description">{{ problem.description }}</p>
                      <p v-else-if="problem.problem" class="text-muted">{{ problem.problem }}</p>
                      <p v-else class="text-muted">Описание проблемы не указано.</p>
                      <div v-if="problem.solution" class="solution-block">
                        <strong>Решение:</strong> {{ problem.solution }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  
  const props = defineProps({
    plant: {
      type: Object,
      required: true
    }
  });
  
  // Format care instructions with support for line breaks
  const formattedCareInstructions = computed(() => {
    if (!props.plant.care_instructions) return '';
    
    return props.plant.care_instructions
      .replace(/\n/g, '<br>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  });
  
  // Functions for watering labels
  function getWateringLabel(frequency) {
    if (!frequency) return 'Не указано';

    const labels = {
      'daily': 'Ежедневно',
      'twice_a_week': 'Дважды в неделю',
      'weekly': 'Еженедельно',
      'bi_weekly': 'Раз в две недели',
      'monthly': 'Ежемесячно',
      'rarely': 'Редко',
      // Добавляем переводы для значений в верхнем регистре
      'DAILY': 'Ежедневно',
      'TWICE_A_WEEK': 'Дважды в неделю',
      'WEEKLY': 'Еженедельно',
      'BI_WEEKLY': 'Раз в две недели',
      'MONTHLY': 'Ежемесячно',
      'RARELY': 'Редко'
    };

    return labels[frequency] || labels[frequency?.toLowerCase()] || frequency;
  }
  
  function getWateringLevel(frequency) {
    if (!frequency) return '50%';

    const levels = {
      'daily': '100%',
      'twice_a_week': '80%',
      'weekly': '60%',
      'bi_weekly': '40%',
      'monthly': '20%',
      'rarely': '10%',
      // Добавляем уровни для значений в верхнем регистре
      'DAILY': '100%',
      'TWICE_A_WEEK': '80%',
      'WEEKLY': '60%',
      'BI_WEEKLY': '40%',
      'MONTHLY': '20%',
      'RARELY': '10%'
    };

    return levels[frequency] || levels[frequency?.toLowerCase()] || '50%';
  }
  
  function getWateringDescription(frequency) {
    if (!frequency) return 'Режим полива не указан.';

    const descriptions = {
      'daily': 'Поливайте растение ежедневно, поддерживая почву слегка влажной.',
      'twice_a_week': 'Поливайте растение 2-3 раза в неделю, позволяя почве слегка подсыхать между поливами.',
      'weekly': 'Поливайте растение раз в неделю, позволяя почве подсыхать между поливами.',
      'bi_weekly': 'Поливайте растение раз в две недели, позволяя почве хорошо просыхать между поливами.',
      'monthly': 'Поливайте растение примерно раз в месяц, дожидаясь полного высыхания почвы.',
      'rarely': 'Растение очень засухоустойчиво, поливайте только когда почва полностью сухая.'
    };

    return descriptions[frequency] || 'Режим полива не указан.';
  }
  
  // Functions for light information
  function getLightLabel(level) {
    if (!level) return 'Не указано';

    const labels = {
      'full_sun': 'Полное солнце',
      'partial_sun': 'Частичное солнце',
      'shade': 'Тень',
      'low_light': 'Слабое освещение',
      // Добавляем переводы для значений в верхнем регистре
      'FULL_SUN': 'Полное солнце',
      'PARTIAL_SUN': 'Частичное солнце',
      'SHADE': 'Тень',
      'LOW_LIGHT': 'Слабое освещение'
    };

    return labels[level] || labels[level?.toLowerCase()] || level;
  }
  
  function getLightLevel(level) {
    if (!level) return '50%';

    const levels = {
      'full_sun': '100%',
      'partial_sun': '75%',
      'shade': '50%',
      'low_light': '25%',
      // Добавляем уровни для значений в верхнем регистре
      'FULL_SUN': '100%',
      'PARTIAL_SUN': '75%',
      'SHADE': '50%',
      'LOW_LIGHT': '25%'
    };

    return levels[level] || levels[level?.toLowerCase()] || '50%';
  }
  
  function getLightDescription(level) {
    if (!level) return 'Уровень освещения не указан.';

    const descriptions = {
      'full_sun': 'Растению необходимо минимум 6 часов прямого солнечного света ежедневно.',
      'partial_sun': 'Растение предпочитает 3-6 часов рассеянного света или утреннего солнца.',
      'shade': 'Растение хорошо растет в тени без прямого солнечного света.',
      'low_light': 'Растение хорошо растет в условиях слабого освещения, вдали от окон.'
    };

    return descriptions[level] || 'Уровень освещения не указан.';
  }
  
  // Functions for temperature information
  function getTemperatureRange(min, max) {
    if (min === undefined || max === undefined) return 'Не указано';

    return `${min}°C - ${max}°C`;
  }

  function getTemperatureLevel(min, max) {
    if (min === undefined || max === undefined) return '50%';

    // Рассчитываем уровень на основе диапазона температур
    // Считаем, что комфортный диапазон 15-25°C = 100%
    // Более широкий диапазон = меньший процент (более требовательное растение)
    // Более узкий диапазон = больший процент (менее требовательное растение)

    const range = max - min;
    const avgTemp = (min + max) / 2;

    // Базовый уровень на основе среднего значения температуры
    let level = 50;

    // Корректировка на основе диапазона
    if (range <= 5) {
      level = 90; // Очень узкий диапазон - требовательное растение
    } else if (range <= 10) {
      level = 75; // Узкий диапазон
    } else if (range <= 15) {
      level = 60; // Средний диапазон
    } else if (range <= 20) {
      level = 45; // Широкий диапазон
    } else {
      level = 30; // Очень широкий диапазон - неприхотливое растение
    }

    // Корректировка на основе средней температуры (оптимум 18-22°C)
    if (avgTemp >= 18 && avgTemp <= 22) {
      level += 10; // Бонус за оптимальную среднюю температуру
    } else if (avgTemp < 10 || avgTemp > 30) {
      level -= 10; // Штраф за экстремальные температуры
    }

    // Ограничиваем значения от 20% до 100%
    level = Math.max(20, Math.min(100, level));

    return `${level}%`;
  }
  
  // Functions for humidity information
  function getHumidityLabel(level) {
    if (!level) return 'Средняя (40-60%)';

    const labels = {
      'high': 'Высокая (60-80%)',
      'medium': 'Средняя (40-60%)',
      'low': 'Низкая (20-40%)',
      // Добавляем переводы для значений в верхнем регистре
      'HIGH': 'Высокая (60-80%)',
      'MEDIUM': 'Средняя (40-60%)',
      'LOW': 'Низкая (20-40%)'
    };

    return labels[level] || labels[level?.toLowerCase()] || level;
  }
  
  // Functions for fertilizing information
  function getFertilizingLabel(frequency) {
    if (!frequency) return 'Стандартный график';

    const labels = {
      'weekly': 'Еженедельно',
      'bi_weekly': 'Раз в 2 недели',
      'monthly': 'Ежемесячно',
      'quarterly': 'Раз в 3 месяца',
      'annually': 'Ежегодно',
      'none': 'Не требуется',
      // Добавляем переводы для значений в верхнем регистре
      'WEEKLY': 'Еженедельно',
      'BI_WEEKLY': 'Раз в 2 недели',
      'MONTHLY': 'Ежемесячно',
      'QUARTERLY': 'Раз в 3 месяца',
      'ANNUALLY': 'Ежегодно',
      'NONE': 'Не требуется'
    };

    return labels[frequency] || labels[frequency?.toLowerCase()] || frequency;
  }
  
  // Functions for repotting information
  function getRepottingLabel(frequency) {
    if (!frequency) return 'Каждые 1-2 года';

    const labels = {
      'annually': 'Ежегодно',
      'bi_annually': 'Каждые 2 года',
      'three_years': 'Каждые 3 года',
      'rarely': 'Редко (более 3 лет)',
      // Добавляем переводы для значений в верхнем регистре
      'ANNUALLY': 'Ежегодно',
      'BI_ANNUALLY': 'Каждые 2 года',
      'THREE_YEARS': 'Каждые 3 года',
      'RARELY': 'Редко (более 3 лет)'
    };

    return labels[frequency] || labels[frequency?.toLowerCase()] || frequency;
  }
  
  // Functions for care difficulty information
  function getDifficultyLabel(difficulty) {
    if (!difficulty) return 'Умеренная';

    const labels = {
      'very_easy': 'Очень легко',
      'easy': 'Легко',
      'moderate': 'Умеренно',
      'difficult': 'Сложно',
      'expert': 'Экспертный',
      // Добавляем переводы для значений в верхнем регистре
      'VERY_EASY': 'Очень легко',
      'EASY': 'Легко',
      'MODERATE': 'Умеренно',
      'DIFFICULT': 'Сложно',
      'EXPERT': 'Экспертный'
    };

    return labels[difficulty] || labels[difficulty?.toLowerCase()] || difficulty;
  }
  
  function getDifficultyLevel(difficulty) {
    if (!difficulty) return 3;

    const levels = {
      'very_easy': 1,
      'easy': 2,
      'moderate': 3,
      'difficult': 4,
      'expert': 5,
      // Добавляем уровни для значений в верхнем регистре
      'VERY_EASY': 1,
      'EASY': 2,
      'MODERATE': 3,
      'DIFFICULT': 4,
      'EXPERT': 5
    };

    return levels[difficulty] || levels[difficulty?.toLowerCase()] || 3;
  }
  
  // Functions for growth rate information
  function getGrowthRateLabel(rate) {
    if (!rate) return 'Умеренная';

    const labels = {
      'fast': 'Быстрая',
      'moderate': 'Умеренная',
      'slow': 'Медленная',
      // Добавляем переводы для значений в верхнем регистре
      'FAST': 'Быстрая',
      'MODERATE': 'Умеренная',
      'SLOW': 'Медленная'
    };

    return labels[rate] || labels[rate.toLowerCase()] || rate;
  }
  </script>
  
  <style scoped>
  .plant-care-info .card {
    transition: box-shadow 0.3s ease;
  }
  
  .plant-care-info .card:hover {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
  }
  
  .care-item {
    padding: 1.25rem;
    border-radius: 8px;
    background-color: #f8f9fa;
    height: 100%;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .care-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  }
  
  .care-icon-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: rgba(var(--bs-primary-rgb), 0.1);
  }
  
  .care-icon {
    font-size: 1.25rem;
    color: var(--bs-primary);
  }
  
  .care-value {
    font-weight: 500;
    font-size: 1.1rem;
  }
  
  .care-item-sm {
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 8px;
    transition: transform 0.3s ease;
  }
  
  .care-item-sm:hover {
    transform: translateY(-3px);
  }
  
  .difficulty-stars {
    font-size: 1rem;
    line-height: 1;
  }
  
  .section-title {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #dee2e6;
    font-weight: 600;
  }
  
  .care-section {
    margin-bottom: 1.5rem;
    padding: 1.25rem;
    background-color: #f8f9fa;
    border-radius: 8px;
  }
  
  .care-tips-list {
    padding-left: 1.5rem;
  }
  
  .care-tips-list li {
    margin-bottom: 0.5rem;
  }
  
  .care-tips-list li:last-child {
    margin-bottom: 0;
  }
  
  .solution-block {
    margin-top: 0.75rem;
    padding: 0.75rem;
    background-color: rgba(var(--bs-primary-rgb), 0.05);
    border-radius: 6px;
    border-left: 3px solid var(--bs-primary);
  }
  
  .accordion-item {
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
  }
  
  .accordion-button {
    font-weight: 500;
  }
  
  .accordion-button:not(.collapsed) {
    background-color: rgba(var(--bs-primary-rgb), 0.1);
    color: var(--bs-primary);
  }
  
  .accordion-button:focus {
    box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb), 0.25);
  }

  .accordion-body {
    background-color: #fff;
    color: #333;
    padding: 1rem;
  }

  .accordion-body p {
    color: #555;
    margin-bottom: 0.75rem;
  }

  .solution-block {
    background-color: #f8f9fa;
    padding: 0.75rem;
    border-radius: 6px;
    border-left: 3px solid var(--bs-success);
  }

  .solution-block strong {
    color: var(--bs-success);
  }
  
  @media (max-width: 768px) {
    .care-item, .care-item-sm, .care-section {
      padding: 1rem;
    }
    
    .care-value {
      font-size: 1rem;
    }
    
    .care-icon-wrapper {
      width: 35px;
      height: 35px;
    }
    
    .care-icon {
      font-size: 1.1rem;
    }
  }
  </style>