<!-- src/views/HomePage.vue -->
<template>
    <div class="home-page">
      <!-- Hero-секция -->
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
                <img src="/hero-plants.jpg" alt="Коллекция комнатных растений" class="img-fluid rounded shadow-lg">
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- Основные преимущества -->
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
                  <i class="bi bi-book text-primary"></i>
                </div>
                <h3 class="feature-title h5">База знаний</h3>
                <p class="feature-text">Обширная база данных растений с детальной информацией о каждом виде и рекомендациями по уходу.</p>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
                <div class="feature-icon-wrapper mb-3">
                  <i class="bi bi-chat-dots text-primary"></i>
                </div>
                <h3 class="feature-title h5">Вопросы и ответы</h3>
                <p class="feature-text">Задавайте вопросы и получайте ответы от опытных садоводов и экспертов в нашем сообществе.</p>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="feature-card h-100 text-center p-4 bg-white rounded shadow-sm">
                <div class="feature-icon-wrapper mb-3">
                  <i class="bi bi-camera-video text-primary"></i>
                </div>
                <h3 class="feature-title h5">Вебинары</h3>
                <p class="feature-text">Участвуйте в интерактивных вебинарах и мастер-классах от профессиональных садоводов.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- Популярные растения -->
      <section class="popular-plants-section py-5 bg-light">
        <div class="container">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div>
              <h2 class="section-title mb-1">Популярные растения</h2>
              <p class="section-subtitle">Познакомьтесь с самыми популярными растениями в нашей базе</p>
            </div>
            <router-link to="/plants" class="btn btn-outline-primary">
              Смотреть все растения
            </router-link>
          </div>
          
          <!-- Загрузка -->
          <div v-if="isLoading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Загрузка...</span>
            </div>
            <p class="mt-2 text-muted">Загрузка популярных растений...</p>
          </div>
          
          <!-- Ошибка -->
          <div v-else-if="error" class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            {{ error }}
          </div>
          
          <!-- Список растений -->
          <div v-else-if="popularPlants.length > 0" class="row g-4">
            <div v-for="plant in popularPlants" :key="plant.id" class="col-md-6 col-lg-3">
              <PlantCard :plant="plant" />
            </div>
          </div>
          
          <!-- Нет растений -->
          <div v-else class="text-center py-4">
            <p class="text-muted">Популярные растения пока недоступны.</p>
            <router-link to="/plants" class="btn btn-primary mt-2">
              Перейти к каталогу растений
            </router-link>
          </div>
        </div>
      </section>
      
      <!-- Секция про мобильное приложение -->
      <section class="app-section py-5">
        <div class="container">
          <div class="row align-items-center">
            <div class="col-md-6 order-md-2 mb-4 mb-md-0">
              <div class="app-image text-center">
                <img src="/mobile-app.png" alt="Мобильное приложение Garden" class="img-fluid">
              </div>
            </div>
            <div class="col-md-6 order-md-1">
              <h2 class="section-title">Garden всегда с вами</h2>
              <p class="mb-4">Устанавливайте наше мобильное приложение и получите доступ к базе знаний даже без интернета. Создавайте заметки, получайте напоминания о поливе и многое другое.</p>
              <div class="d-flex flex-wrap">
                <a href="#" class="app-store-badge me-2 mb-2">
                  <img src="/app-store-badge.png" alt="Скачать в App Store" width="140">
                </a>
                <a href="#" class="google-play-badge mb-2">
                  <img src="/google-play-badge.png" alt="Скачать в Google Play" width="140">
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- Отзывы пользователей -->
      <section class="testimonials-section py-5 bg-light">
        <div class="container">
          <div class="text-center mb-5">
            <h2 class="section-title">Что говорят наши пользователи</h2>
            <p class="section-subtitle">Отзывы от садоводов, которые уже используют Garden</p>
          </div>
          
          <div class="row g-4">
            <div class="col-md-4">
              <div class="testimonial-card h-100 p-4 bg-white rounded shadow-sm">
                <div class="d-flex align-items-center mb-3">
                  <div class="testimonial-avatar me-3">
                    <img src="/avatar-1.jpg" alt="Аватар пользователя" class="rounded-circle" width="60" height="60">
                  </div>
                  <div>
                    <h5 class="mb-0">Анна Семенова</h5>
                    <small class="text-muted">Начинающий садовод</small>
                  </div>
                </div>
                <div class="testimonial-rating mb-3">
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                </div>
                <p class="testimonial-text">«Garden стало настоящим спасением для моих растений! Благодаря подробным инструкциям по уходу я наконец-то научилась правильно ухаживать за своими зелеными питомцами. Очень удобное приложение!»</p>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="testimonial-card h-100 p-4 bg-white rounded shadow-sm">
                <div class="d-flex align-items-center mb-3">
                  <div class="testimonial-avatar me-3">
                    <img src="/avatar-2.jpg" alt="Аватар пользователя" class="rounded-circle" width="60" height="60">
                  </div>
                  <div>
                    <h5 class="mb-0">Михаил Петров</h5>
                    <small class="text-muted">Профессиональный флорист</small>
                  </div>
                </div>
                <div class="testimonial-rating mb-3">
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-half text-warning"></i>
                </div>
                <p class="testimonial-text">«Как профессионал, я всегда ищу надежные источники информации о растениях. Garden предоставляет точные данные и полезные советы, которые помогают даже в моей повседневной работе с клиентами. Рекомендую!»</p>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="testimonial-card h-100 p-4 bg-white rounded shadow-sm">
                <div class="d-flex align-items-center mb-3">
                  <div class="testimonial-avatar me-3">
                    <img src="/avatar-3.jpg" alt="Аватар пользователя" class="rounded-circle" width="60" height="60">
                  </div>
                  <div>
                    <h5 class="mb-0">Елена Иванова</h5>
                    <small class="text-muted">Опытный садовод</small>
                  </div>
                </div>
                <div class="testimonial-rating mb-3">
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star-fill text-warning"></i>
                  <i class="bi bi-star text-warning"></i>
                </div>
                <p class="testimonial-text">«Обожаю функцию напоминаний о поливе в Garden! Теперь ни одно из моих растений не страдает от засухи или избытка влаги. База знаний очень обширная, всегда нахожу что-то новое и интересное.»</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- Call to Action -->
      <section class="cta-section py-5">
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
  import PlantCard from '../features/plants/components/PlantCard.vue';
  
  const authStore = useAuthStore();
  const plantsStore = usePlantsStore();
  
  // Состояние компонента
  const isLoading = ref(false);
  const error = ref(null);
  const popularPlants = ref([]);
  
  // Вычисляемые свойства
  const isLoggedIn = computed(() => authStore.isLoggedIn);
  
  // Инициализация при создании компонента
  onMounted(async () => {
    await loadPopularPlants();
  });
  
  // Загрузка популярных растений
  async function loadPopularPlants() {
    isLoading.value = true;
    error.value = null;
    
    try {
      // Загружаем популярные растения через хранилище
      // Используем параметры для получения только популярных растений
      const filters = {
        sort_by: 'popularity',
        sort_direction: 'desc',
        limit: 4 // Ограничиваем до 4 растений
      };
      
      await plantsStore.loadPlants(1, 4, false);
      popularPlants.value = plantsStore.plants;
      
      // Если растений меньше 4, создаем тестовые данные для демонстрации
      if (popularPlants.value.length < 4) {
        createDemoPlants();
      }
    } catch (e) {
      error.value = 'Не удалось загрузить популярные растения: ' + (e.message || 'Неизвестная ошибка');
      console.error('Ошибка при загрузке популярных растений:', e);
      createDemoPlants(); // В случае ошибки создаем демо-данные
    } finally {
      isLoading.value = false;
    }
  }
  
  // Функция для создания демонстрационных растений, если API не работает
  function createDemoPlants() {
    popularPlants.value = [
      {
        id: 1,
        name: 'Монстера Деликатесная',
        latin_name: 'Monstera deliciosa',
        description: 'Популярное комнатное растение с характерными разрезными листьями. Легко выращивать и ухаживать.',
        category: { name: 'Лиственные' },
        images: [
          { url: '/plants/monstera.jpg', alt: 'Монстера Деликатесная' }
        ],
        watering_frequency: 'weekly',
        light_level: 'partial_sun'
      },
      {
        id: 2,
        name: 'Фикус Лирата',
        latin_name: 'Ficus lyrata',
        description: 'Популярное комнатное растение с большими скрипичными листьями. Прекрасно смотрится в интерьере.',
        category: { name: 'Лиственные' },
        images: [
          { url: '/plants/ficus.jpg', alt: 'Фикус Лирата' }
        ],
        watering_frequency: 'weekly',
        light_level: 'partial_sun'
      },
      {
        id: 3,
        name: 'Сансевиерия',
        latin_name: 'Sansevieria trifasciata',
        description: 'Неприхотливое растение, известное своей способностью очищать воздух. Идеально для начинающих.',
        category: { name: 'Суккуленты' },
        images: [
          { url: '/plants/sansevieria.jpg', alt: 'Сансевиерия' }
        ],
        watering_frequency: 'bi_weekly',
        light_level: 'shade'
      },
      {
        id: 4,
        name: 'Замиокулькас',
        latin_name: 'Zamioculcas zamiifolia',
        description: 'Неприхотливое растение с глянцевыми темно-зелеными листьями. Отлично подходит для офисов и квартир.',
        category: { name: 'Лиственные' },
        images: [
          { url: '/plants/zamioculcas.jpg', alt: 'Замиокулькас' }
        ],
        watering_frequency: 'monthly',
        light_level: 'low_light'
      }
    ];
  }
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
  }
  
  .hero-image-container::before {
    content: '';
    position: absolute;
    top: -10px;
    right: -10px;
    width: 100%;
    height: 100%;
    border: 2px dashed var(--bs-primary);
    border-radius: 0.5rem;
    z-index: -1;
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
  
  .feature-icon-wrapper i {
    font-size: 2rem;
  }
  
  .feature-card {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
  }
  
  .testimonial-card {
    transition: transform 0.3s ease;
  }
  
  .testimonial-card:hover {
    transform: translateY(-5px);
  }
  
  .testimonial-avatar img {
    object-fit: cover;
  }
  
  .testimonial-text {
    font-style: italic;
    color: #6c757d;
  }
  
  .testimonial-rating {
    font-size: 1.1rem;
  }
  
  .cta-section {
    padding-top: 5rem;
    padding-bottom: 5rem;
  }
  
  .cta-card {
    background: linear-gradient(135deg, var(--bs-primary) 0%, var(--bs-success) 100%);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .cta-card:hover {
    transform: scale(1.02);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15) !important;
  }
  
  /* Анимации при загрузке страницы */
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
  
  /* Адаптивность для мобильных устройств */
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
    
    .section-subtitle {
      font-size: 1rem;
    }
    
    .feature-icon-wrapper {
      width: 60px;
      height: 60px;
    }
    
    .feature-icon-wrapper i {
      font-size: 1.75rem;
    }
  }
  </style>