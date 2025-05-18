<!-- src/features/plants/components/PlantCareInfo.vue -->
<template>
    <div class="plant-care-info">
      <div class="card shadow-sm border-0 rounded-3">
        <div class="card-header bg-light py-3">
          <h5 class="mb-0">
            <i class="bi bi-water me-2 text-primary"></i>
            Care Information
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
                <h6 class="fw-bold mb-1">Watering</h6>
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
                <h6 class="fw-bold mb-1">Light</h6>
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
                <h6 class="fw-bold mb-1">Temperature</h6>
                <div class="care-value mb-1">
                  {{ getTemperatureRange(plant.temperature_min, plant.temperature_max) }}
                </div>
                <div class="progress" style="height: 5px;">
                  <div class="progress-bar bg-danger" style="width: 100%"></div>
                </div>
                <small class="text-muted d-block mt-2">
                  Optimal temperature range for plant growth and development.
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
                    <h6 class="fw-bold mb-0">Humidity</h6>
                  </div>
                  <p class="mb-0">{{ getHumidityLabel(plant.humidity_level) }}</p>
                </div>
              </div>
              
              <!-- Fertilizing -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-flower3 me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Fertilizing</h6>
                  </div>
                  <p class="mb-0">{{ getFertilizingLabel(plant.fertilizing_frequency) }}</p>
                </div>
              </div>
              
              <!-- Repotting -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-arrow-repeat me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Repotting</h6>
                  </div>
                  <p class="mb-0">{{ getRepottingLabel(plant.repotting_frequency) }}</p>
                </div>
              </div>
              
              <!-- Care difficulty -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-clipboard-check me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Care Difficulty</h6>
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
                    <h6 class="fw-bold mb-0">Toxicity</h6>
                  </div>
                  <p v-if="plant.is_toxic" class="text-danger mb-0">
                    <i class="bi bi-exclamation-circle me-1"></i>
                    Toxic to humans and/or animals
                  </p>
                  <p v-else class="text-success mb-0">
                    <i class="bi bi-check-circle me-1"></i>
                    Non-toxic
                  </p>
                </div>
              </div>
              
              <!-- Growth rate -->
              <div class="col-md-4">
                <div class="care-item-sm">
                  <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-graph-up-arrow me-2 text-primary"></i>
                    <h6 class="fw-bold mb-0">Growth Rate</h6>
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
                Care Instructions
              </h6>
              <div class="care-content" v-html="formattedCareInstructions"></div>
            </div>
          </div>
          
          <!-- Care tips -->
          <div class="care-tips mt-4" v-if="plant.care_tips && plant.care_tips.length > 0">
            <div class="care-section">
              <h6 class="section-title">
                <i class="bi bi-lightbulb me-2"></i>
                Tips and Recommendations
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
                Common Problems
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
                      {{ problem.title }}
                    </button>
                  </h2>
                  <div
                    :id="'collapse' + index"
                    class="accordion-collapse collapse"
                    :aria-labelledby="'heading' + index"
                    data-bs-parent="#problemsAccordion"
                  >
                    <div class="accordion-body">
                      <p>{{ problem.description }}</p>
                      <div v-if="problem.solution" class="solution-block">
                        <strong>Solution:</strong> {{ problem.solution }}
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
    if (!frequency) return 'Not specified';
    
    const labels = {
      'daily': 'Daily',
      'twice_a_week': 'Twice a week',
      'weekly': 'Weekly',
      'bi_weekly': 'Every 2 weeks',
      'monthly': 'Monthly',
      'rarely': 'Rarely'
    };
    
    return labels[frequency] || frequency;
  }
  
  function getWateringLevel(frequency) {
    if (!frequency) return '50%';
    
    const levels = {
      'daily': '100%',
      'twice_a_week': '80%',
      'weekly': '60%',
      'bi_weekly': '40%',
      'monthly': '20%',
      'rarely': '10%'
    };
    
    return levels[frequency] || '50%';
  }
  
  function getWateringDescription(frequency) {
    if (!frequency) return 'Watering regime not specified.';
    
    const descriptions = {
      'daily': 'Water the plant daily, keeping the soil slightly moist.',
      'twice_a_week': 'Water the plant 2-3 times a week, allowing the soil to dry slightly between waterings.',
      'weekly': 'Water the plant once a week, allowing the soil to dry between waterings.',
      'bi_weekly': 'Water the plant once every two weeks, allowing the soil to dry well between waterings.',
      'monthly': 'Water the plant approximately once a month, waiting for the soil to completely dry out.',
      'rarely': 'The plant is very drought-tolerant, water only when the soil is completely dry.'
    };
    
    return descriptions[frequency] || 'Watering regime not specified.';
  }
  
  // Functions for light information
  function getLightLabel(level) {
    if (!level) return 'Not specified';
    
    const labels = {
      'full_sun': 'Full sun',
      'partial_sun': 'Partial sun',
      'shade': 'Shade',
      'low_light': 'Low light'
    };
    
    return labels[level] || level;
  }
  
  function getLightLevel(level) {
    if (!level) return '50%';
    
    const levels = {
      'full_sun': '100%',
      'partial_sun': '75%',
      'shade': '50%',
      'low_light': '25%'
    };
    
    return levels[level] || '50%';
  }
  
  function getLightDescription(level) {
    if (!level) return 'Light level not specified.';
    
    const descriptions = {
      'full_sun': 'The plant needs at least 6 hours of direct sunlight daily.',
      'partial_sun': 'The plant prefers 3-6 hours of filtered light or morning sun.',
      'shade': 'The plant thrives in shade without direct sunlight.',
      'low_light': 'The plant grows well in low light conditions, away from windows.'
    };
    
    return descriptions[level] || 'Light level not specified.';
  }
  
  // Functions for temperature information
  function getTemperatureRange(min, max) {
    if (min === undefined || max === undefined) return 'Not specified';
    
    return `${min}°C - ${max}°C`;
  }
  
  // Functions for humidity information
  function getHumidityLabel(level) {
    if (!level) return 'Average (40-60%)';
    
    const labels = {
      'high': 'High (60-80%)',
      'medium': 'Medium (40-60%)',
      'low': 'Low (20-40%)'
    };
    
    return labels[level] || level;
  }
  
  // Functions for fertilizing information
  function getFertilizingLabel(frequency) {
    if (!frequency) return 'Standard schedule';
    
    const labels = {
      'weekly': 'Weekly',
      'bi_weekly': 'Every 2 weeks',
      'monthly': 'Monthly',
      'quarterly': 'Every 3 months',
      'annually': 'Annually',
      'none': 'Not required'
    };
    
    return labels[frequency] || frequency;
  }
  
  // Functions for repotting information
  function getRepottingLabel(frequency) {
    if (!frequency) return 'Every 1-2 years';
    
    const labels = {
      'annually': 'Annually',
      'bi_annually': 'Every 2 years',
      'three_years': 'Every 3 years',
      'rarely': 'Rarely (more than 3 years)'
    };
    
    return labels[frequency] || frequency;
  }
  
  // Functions for care difficulty information
  function getDifficultyLabel(difficulty) {
    if (!difficulty) return 'Moderate';
    
    const labels = {
      'very_easy': 'Very Easy',
      'easy': 'Easy',
      'moderate': 'Moderate',
      'difficult': 'Difficult',
      'expert': 'Expert'
    };
    
    return labels[difficulty] || difficulty;
  }
  
  function getDifficultyLevel(difficulty) {
    if (!difficulty) return 3;
    
    const levels = {
      'very_easy': 1,
      'easy': 2,
      'moderate': 3,
      'difficult': 4,
      'expert': 5
    };
    
    return levels[difficulty] || 3;
  }
  
  // Functions for growth rate information
  function getGrowthRateLabel(rate) {
    if (!rate) return 'Moderate';
    
    const labels = {
      'fast': 'Fast',
      'moderate': 'Moderate',
      'slow': 'Slow'
    };
    
    return labels[rate] || rate;
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