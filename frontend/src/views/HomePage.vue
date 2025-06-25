<!-- src/views/HomePage.vue -->
<template>
  <div class="home-page">
    <!-- Hero section -->
    <section class="hero-section py-5 bg-light">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6 mb-4 mb-lg-0">
            <h1 class="display-4 fw-bold mb-3">Выращивайте растения с удовольствием</h1>
            <p class="lead mb-4">Garden — это ваш верный помощник в выращивании растений. Получите доступ к обширной базе знаний, советам по уходу и сообществу единомышленников.</p>
            <div class="d-grid gap-2 d-md-flex">
              <router-link to="/plants" class="btn btn-primary btn-lg px-4 me-md-2">
                <i class="bi bi-search me-2"></i>
                Изучить растения
              </router-link>
              <router-link v-if="!isLoggedIn" to="/register" class="btn btn-outline-primary btn-lg px-4">
                <i class="bi bi-person-plus me-2"></i>
                Регистрация
              </router-link>
              <router-link v-else to="/dashboard" class="btn btn-outline-primary btn-lg px-4">
                <i class="bi bi-speedometer2 me-2"></i>
                Мой сад
              </router-link>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="hero-image-container text-center">
              <img src="/images/hero-plants-collection.jpg" alt="Коллекция комнатных растений" class="img-fluid rounded shadow-lg" @error="handleImageError($event, 'hero')" />
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Main features -->
    <section class="features-section py-5">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="section-title">Все что нужно для успешного садоводства</h2>
          <p class="section-subtitle">Больше никаких догадок: используйте Garden для получения точной информации о растениях</p>
        </div>
        
        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
              <div class="feature-icon-wrapper mb-3">
                <i class="bi bi-book text-primary display-5"></i>
              </div>
              <h3 class="feature-title h5">База знаний</h3>
              <p class="feature-text">Обширная база данных растений с детальной информацией о каждом виде и рекомендациями по уходу.</p>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
              <div class="feature-icon-wrapper mb-3">
                <i class="bi bi-chat-dots text-primary display-5"></i>
              </div>
              <h3 class="feature-title h5">Вопросы и ответы</h3>
              <p class="feature-text">Задавайте вопросы и получайте ответы от опытных садоводов и экспертов в нашем сообществе.</p>
            </div>
          </div>
          
          <div class="col-md-4">
            <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
              <div class="feature-icon-wrapper mb-3">
                <i class="bi bi-calendar-check text-primary display-5"></i>
              </div>
              <h3 class="feature-title h5">Напоминания и уход</h3>
              <p class="feature-text">Персонализированные напоминания о поливе, удобрении и других важных мероприятиях по уходу за растениями.</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Popular plants -->
    <section class="popular-plants-section py-5 bg-light">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h2 class="section-title mb-1">Популярные растения</h2>
            <p class="section-subtitle">Познакомьтесь с самыми популярными растениями в нашей базе</p>
          </div>
          <router-link to="/plants" class="btn btn-outline-primary">
            Смотреть все растения
            <i class="bi bi-arrow-right ms-2"></i>
          </router-link>
        </div>
        
        <!-- Loading state -->
        <div v-if="isLoading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка...</span>
          </div>
          <p class="mt-2 text-muted">Загрузка популярных растений...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="alert alert-warning">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error }}
        </div>
        
        <!-- Plants grid -->
        <div v-else-if="popularPlants.length > 0" class="row g-4">
          <div v-for="plant in popularPlants" :key="plant.id" class="col-md-6 col-lg-3">
            <div class="plant-card h-100 bg-white rounded shadow-sm overflow-hidden">
              <div class="plant-img-container">
                <img 
                  v-if="plant.images && plant.images.length > 0" 
                  :src="plant.images[0].url" 
                  :alt="plant.name" 
                  class="plant-img w-100"
                  @error="handleImageError($event, 'plant')"
                >
                <div v-else class="plant-img-placeholder d-flex align-items-center justify-content-center">
                  <i class="bi bi-flower1 display-4 text-muted"></i>
                </div>
              </div>
              <div class="p-3">
                <h5 class="card-title text-primary fw-bold mb-1">{{ plant.name }}</h5>
                <p class="text-muted small fst-italic mb-2">{{ plant.latin_name }}</p>
                <p class="card-text small mb-3">{{ truncateText(plant.description, 100) }}</p>
                <router-link :to="{ name: 'PlantDetails', params: { id: plant.id } }" class="btn btn-sm btn-primary">
                  Подробнее
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Empty state -->
        <div v-else class="text-center py-4">
          <p class="text-muted">Популярные растения пока недоступны.</p>
          <router-link to="/plants" class="btn btn-primary mt-2">
            Перейти к каталогу растений
          </router-link>
        </div>
      </div>
    </section>
    
    <!-- Q&A Section -->
    <section class="qa-section py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6 mb-4 mb-lg-0">
            <h2 class="section-title">Вопросы и ответы</h2>
            <p class="mb-4">Задавайте вопросы опытным садоводам и получайте экспертные ответы. Делитесь своими знаниями и помогайте другим участникам сообщества.</p>
            <div class="qa-stats d-flex mb-4">
              <div class="qa-stat me-4">
                <span class="d-block fw-bold text-primary fs-3">1.2K+</span>
                <span class="text-muted">Вопросов</span>
              </div>
              <div class="qa-stat me-4">
                <span class="d-block fw-bold text-primary fs-3">3.5K+</span>
                <span class="text-muted">Ответов</span>
              </div>
              <div class="qa-stat">
                <span class="d-block fw-bold text-primary fs-3">95%</span>
                <span class="text-muted">Решенных вопросов</span>
              </div>
            </div>
            <router-link to="/questions" class="btn btn-primary">
              <i class="bi bi-chat-dots me-2"></i>
              Перейти к вопросам
            </router-link>
          </div>
          <div class="col-lg-6">
            <div class="qa-preview p-4 bg-white rounded shadow-lg">
              <h4 class="mb-3">Популярные вопросы</h4>
              <ul class="list-unstyled qa-list">
                <li v-for="(question, index) in recentQuestions" :key="index" class="qa-item mb-3">
                  <router-link :to="question.link" class="d-block p-3 rounded bg-light text-decoration-none">
                    <h6 class="mb-1 text-primary">{{ question.title }}</h6>
                    <div class="d-flex justify-content-between align-items-center small">
                      <span class="text-muted">{{ question.author }}</span>
                      <span class="badge bg-success" v-if="question.solved">Решен</span>
                    </div>
                  </router-link>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Mobile app section -->
    <section class="app-section py-5 bg-light">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-6 order-md-2 mb-4 mb-md-0">
            <div class="app-image text-center">
              <img src="/images/mobile-app-plants.jpg" alt="Мобильное приложение Garden" class="img-fluid rounded shadow" @error="handleImageError($event, 'app')">
            </div>
          </div>
          <div class="col-md-6 order-md-1">
            <h2 class="section-title">Garden всегда с вами</h2>
            <p class="mb-4">Устанавливайте наше мобильное приложение и получите доступ к базе знаний даже без интернета. Создавайте заметки, получайте напоминания о поливе и многое другое.</p>
            <ul class="app-features-list list-unstyled mb-4">
              <li class="d-flex align-items-center mb-2">
                <i class="bi bi-check-circle-fill text-primary me-2"></i>
                <span>Доступ к базе знаний в оффлайн режиме</span>
              </li>
              <li class="d-flex align-items-center mb-2">
                <i class="bi bi-check-circle-fill text-primary me-2"></i>
                <span>Персонализированные уведомления о поливе</span>
              </li>
              <li class="d-flex align-items-center mb-2">
                <i class="bi bi-check-circle-fill text-primary me-2"></i>
                <span>Инструменты мониторинга роста растений</span>
              </li>
              <li class="d-flex align-items-center">
                <i class="bi bi-check-circle-fill text-primary me-2"></i>
                <span>Сканирование растений для идентификации</span>
              </li>
            </ul>
            <div class="d-flex flex-wrap">
              <a href="#" class="btn btn-dark app-store-badge me-2 mb-2 d-flex align-items-center">
                <i class="bi bi-apple me-2"></i>
                <div class="text-start">
                  <div class="small">Скачать в</div>
                  <div class="fw-bold">App Store</div>
                </div>
              </a>
              <a href="#" class="btn btn-dark google-play-badge mb-2 d-flex align-items-center">
                <i class="bi bi-google-play me-2"></i>
                <div class="text-start">
                  <div class="small">Доступно в</div>
                  <div class="fw-bold">Google Play</div>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Testimonials section -->
    <section class="testimonials-section py-5">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="section-title">Что говорят наши пользователи</h2>
          <p class="section-subtitle">Отзывы от садоводов, которые уже используют Garden</p>
        </div>
        
        <div class="row g-4">
          <div class="col-md-4" v-for="(testimonial, index) in testimonials" :key="index">
            <div class="testimonial-card h-100 p-4 bg-white rounded shadow-sm">
              <div class="d-flex align-items-center mb-3">
                <div class="testimonial-avatar me-3">
                  <img :src="testimonial.avatar" :alt="testimonial.name" class="rounded-circle" width="60" height="60" @error="handleImageError($event, 'avatar')">
                </div>
                <div>
                  <h5 class="mb-0">{{ testimonial.name }}</h5>
                  <small class="text-muted">{{ testimonial.role }}</small>
                </div>
              </div>
              <div class="testimonial-rating mb-3">
                <i class="bi bi-star-fill text-warning" v-for="star in testimonial.stars" :key="star"></i>
                <i class="bi bi-star-half text-warning" v-if="testimonial.halfStar"></i>
                <i class="bi bi-star text-warning" v-for="star in (5 - testimonial.stars - (testimonial.halfStar ? 1 : 0))" :key="'empty'+star"></i>
              </div>
              <p class="testimonial-text">{{ testimonial.text }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Call to Action -->
    <section class="cta-section py-5 bg-light">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="cta-card text-center p-5 bg-primary text-white rounded shadow">
              <h2 class="cta-title mb-3">Начните свое путешествие в мир растений сегодня</h2>
              <p class="cta-text mb-4">Присоединяйтесь к тысячам садоводов, которые уже пользуются преимуществами Garden. Создайте аккаунт прямо сейчас!</p>
              <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                <router-link to="/plants" class="btn btn-light btn-lg px-4 me-md-2">
                  <i class="bi bi-flower1 me-2"></i>
                  Исследовать растения
                </router-link>
                <router-link v-if="!isLoggedIn" to="/register" class="btn btn-outline-light btn-lg px-4">
                  <i class="bi bi-person-plus me-2"></i>
                  Регистрация
                </router-link>
                <router-link v-else to="/dashboard" class="btn btn-outline-light btn-lg px-4">
                  <i class="bi bi-speedometer2 me-2"></i>
                  Мой сад
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../features/auth/store/authStore';
import { usePlantsStore } from '../features/plants/store/plantsStore';


const authStore = useAuthStore();
const plantsStore = usePlantsStore();

// Component state
const isLoading = ref(false);
const error = ref(null);
const popularPlants = ref([]);

// Computed properties
const isLoggedIn = computed(() => authStore.isLoggedIn);

// Initialize on component mount
onMounted(async () => {
  await loadPopularPlants();
});

// Load popular plants
async function loadPopularPlants() {
  isLoading.value = true;
  error.value = null;
  
  try {
    // Load popular plants with popularity sorting
    const filters = {
      sort_by: 'popularity_score',
      sort_direction: 'desc'
    };
    
    await plantsStore.updateFilters(filters);
    await plantsStore.loadPlants(1, 4);
    popularPlants.value = plantsStore.plants;
    
    // If we have less than 4 plants, add some demo data
    if (popularPlants.value.length < 4) {
      createDemoPlants();
    }
  } catch (e) {
    error.value = 'Не удалось загрузить популярные растения: ' + (e.message || 'Неизвестная ошибка');
    console.error('Ошибка при загрузке популярных растений:', e);
    createDemoPlants(); // Create demo data in case of error
  } finally {
    isLoading.value = false;
  }
}

// Helper function to truncate text
function truncateText(text, maxLength) {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Handle image load errors
function handleImageError(event, imageType) {
  // Set appropriate placeholder based on image type
  switch (imageType) {
    case 'hero':
      event.target.src = '/images/hero-plants.jpg';
      break;
    case 'plant':
      event.target.src = 'https://placehold.co/300x200?text=Plant';
      break;
    case 'app':
      event.target.src = mobileAppImage;
      break;
    case 'app-store':
    case 'google-play':
      event.target.src = 'https://placehold.co/140x40?text=' + (imageType === 'app-store' ? 'App+Store' : 'Google+Play');
      break;
    case 'avatar':
      event.target.src = 'https://placehold.co/60x60?text=User';
      break;
    default:
      event.target.src = 'https://placehold.co/400x300?text=Image';
  }
  event.target.classList.add('img-error');
}

// Function to create demo plants if API doesn't work
function createDemoPlants() {
  popularPlants.value = [
    {
      id: 1,
      name: 'Монстера Деликатесная',
      latin_name: 'Monstera deliciosa',
      description: 'Популярное комнатное растение с характерными разрезными листьями. Легко выращивать и ухаживать.',
      images: [{ url: 'https://placehold.co/300x200?text=Monstera' }],
      watering_frequency: 'weekly',
      light_level: 'partial_sun'
    },
    {
      id: 2,
      name: 'Фикус Лирата',
      latin_name: 'Ficus lyrata',
      description: 'Популярное комнатное растение с большими скрипичными листьями. Прекрасно смотрится в интерьере.',
      images: [{ url: 'https://placehold.co/300x200?text=Ficus' }],
      watering_frequency: 'weekly',
      light_level: 'partial_sun'
    },
    {
      id: 3,
      name: 'Сансевиерия',
      latin_name: 'Sansevieria trifasciata',
      description: 'Неприхотливое растение, известное своей способностью очищать воздух. Идеально для начинающих.',
      images: [{ url: 'https://placehold.co/300x200?text=Sansevieria' }],
      watering_frequency: 'bi_weekly',
      light_level: 'shade'
    },
    {
      id: 4,
      name: 'Замиокулькас',
      latin_name: 'Zamioculcas zamiifolia',
      description: 'Неприхотливое растение с глянцевыми темно-зелеными листьями. Отлично подходит для офисов и квартир.',
      images: [{ url: 'https://placehold.co/300x200?text=Zamioculcas' }],
      watering_frequency: 'monthly',
      light_level: 'low_light'
    }
  ];
}

// Sample testimonials data
const testimonials = [
  {
    name: 'Анна Петрова',
    role: 'Начинающий садовод',
    avatar: 'https://placehold.co/60x60?text=Анна',
    stars: 5,
    halfStar: false,
    text: '«Garden стало настоящим спасением для моих растений! Благодаря подробным инструкциям по уходу я наконец-то научилась правильно ухаживать за своими зелеными питомцами.»'
  },
  {
    name: 'Михаил Иванов',
    role: 'Профессиональный флорист',
    avatar: 'https://placehold.co/60x60?text=Михаил',
    stars: 4,
    halfStar: true,
    text: '«Как профессионал, я ищу надежные источники информации о растениях. Garden предоставляет точные данные и полезные советы, которые помогают в моей работе с клиентами.»'
  },
  {
    name: 'Екатерина Смирнова',
    role: 'Опытный садовод',
    avatar: 'https://placehold.co/60x60?text=Екатерина',
    stars: 5,
    halfStar: false,
    text: '«Обожаю функцию напоминаний о поливе! Теперь ни одно из моих растений не страдает от засухи или избытка влаги. База знаний очень обширная и полезная.»'
  }
];

// Sample recent questions
const recentQuestions = [
  {
    title: 'Почему желтеют листья у монстеры?',
    author: 'Иван С., 2 дня назад',
    link: '/questions/1',
    solved: true
  },
  {
    title: 'Как часто поливать кактусы зимой?',
    author: 'Мария Д., 3 дня назад',
    link: '/questions/2',
    solved: true
  },
  {
    title: 'Лучшее удобрение для орхидей?',
    author: 'Алексей В., 5 дней назад',
    link: '/questions/3',
    solved: false
  }
];
</script>

<style scoped>
.home-page {
  overflow-x: hidden;
}

.hero-section {
  padding-top: 4rem;
  padding-bottom: 4rem;
}

.hero-image-container {
  position: relative;
  overflow: hidden;
}

.hero-image-container img {
  transition: transform 0.3s ease;
  border-radius: 1rem !important;
}

.hero-image-container:hover img {
  transform: scale(1.05);
}

.hero-image-container::before {
  content: '';
  position: absolute;
  top: -15px;
  right: -15px;
  width: 100%;
  height: 100%;
  border: 3px dashed var(--bs-primary);
  border-radius: 1rem;
  z-index: -1;
  opacity: 0.3;
}

.section-title {
  font-weight: 700;
  margin-bottom: 1rem;
  color: #333;
}

.section-subtitle {
  font-size: 1.1rem;
  color: #6c757d;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

/* Feature cards */
.feature-icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 70px;
  height: 70px;
  border-radius: 50%;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  margin-bottom: 1.5rem;
}

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
}

/* Plant cards */
.plant-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.plant-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1) !important;
}

.plant-img-container {
  height: 200px;
  overflow: hidden;
}

.plant-img {
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.plant-card:hover .plant-img {
  transform: scale(1.05);
}

.plant-img-placeholder {
  height: 100%;
  background-color: #f8f9fa;
}

/* Q&A section */
.qa-preview {
  height: 100%;
}

.qa-item {
  transition: transform 0.3s ease;
}

.qa-item:hover {
  transform: translateY(-5px);
}

.qa-list {
  max-height: 350px;
  overflow-y: auto;
}

.qa-stat {
  text-align: center;
}

/* App features */
.app-features-list li {
  padding: 0.5rem 0;
}

.app-store-badge,
.google-play-badge {
  min-width: 140px;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
  border-radius: 8px;
}

.app-store-badge:hover,
.google-play-badge:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* Testimonials */
.testimonial-card {
  transition: transform 0.3s ease;
  border: 1px solid rgba(0,0,0,0.05);
}

.testimonial-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.testimonial-avatar img {
  object-fit: cover;
}

.testimonial-text {
  font-style: italic;
  color: #6c757d;
  line-height: 1.6;
}

.testimonial-rating {
  font-size: 1.1rem;
}

/* CTA section */
.cta-card {
  background: linear-gradient(135deg, var(--bs-primary) 0%, var(--bs-success) 100%);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.cta-card:hover {
  transform: scale(1.02);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15) !important;
}

/* Image error fallbacks */
.img-error {
  border: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

/* Section animations */
.home-page section {
  animation: fadeIn 1s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive styles */
@media (max-width: 768px) {
  .hero-section {
    padding-top: 2rem;
    padding-bottom: 2rem;
  }
  
  .display-4 {
    font-size: 2.5rem;
  }
  
  .section-title {
    font-size: 1.75rem;
  }
  
  .feature-icon-wrapper {
    width: 60px;
    height: 60px;
  }
  
  .plant-img-container {
    height: 150px;
  }
  
  .qa-stats {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .qa-stat {
    width: 50%;
    margin-bottom: 1rem;
  }
}

@media (max-width: 576px) {
  .hero-section {
    text-align: center;
  }
  
  .display-4 {
    font-size: 2rem;
  }
  
  .d-md-flex {
    justify-content: center;
  }
  
  .qa-stat {
    width: 100%;
  }
}
</style>