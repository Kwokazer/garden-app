<!-- src/features/plants/components/PlantPagination.vue -->
<template>
    <nav aria-label="Пагинация по списку растений" class="plant-pagination">
      <ul class="pagination justify-content-center">
        <!-- Кнопка "Первая страница" -->
        <li class="page-item" :class="{ disabled: currentPage <= 1 }">
          <a 
            class="page-link" 
            href="#" 
            @click.prevent="!isLoading && currentPage > 1 && onPageChange(1)"
            aria-label="К первой странице"
            :tabindex="currentPage <= 1 ? -1 : 0"
          >
            <i class="bi bi-chevron-double-left"></i>
          </a>
        </li>
        
        <!-- Кнопка "Предыдущая страница" -->
        <li class="page-item" :class="{ disabled: currentPage <= 1 }">
          <a 
            class="page-link" 
            href="#" 
            @click.prevent="!isLoading && currentPage > 1 && onPageChange(currentPage - 1)"
            aria-label="К предыдущей странице"
            :tabindex="currentPage <= 1 ? -1 : 0"
          >
            <i class="bi bi-chevron-left"></i>
          </a>
        </li>
        
        <!-- Номера страниц -->
        <li 
          v-for="page in displayedPages" 
          :key="page" 
          class="page-item" 
          :class="{ active: page === currentPage, disabled: page === '...' }"
        >
          <template v-if="page === '...'">
            <span class="page-link">...</span>
          </template>
          <a 
            v-else
            class="page-link" 
            href="#" 
            @click.prevent="!isLoading && page !== currentPage && onPageChange(page)"
          >
            {{ page }}
          </a>
        </li>
        
        <!-- Кнопка "Следующая страница" -->
        <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
          <a 
            class="page-link" 
            href="#" 
            @click.prevent="!isLoading && currentPage < totalPages && onPageChange(currentPage + 1)"
            aria-label="К следующей странице"
            :tabindex="currentPage >= totalPages ? -1 : 0"
          >
            <i class="bi bi-chevron-right"></i>
          </a>
        </li>
        
        <!-- Кнопка "Последняя страница" -->
        <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
          <a 
            class="page-link" 
            href="#" 
            @click.prevent="!isLoading && currentPage < totalPages && onPageChange(totalPages)"
            aria-label="К последней странице"
            :tabindex="currentPage >= totalPages ? -1 : 0"
          >
            <i class="bi bi-chevron-double-right"></i>
          </a>
        </li>
      </ul>
      
      <!-- Информация о пагинации -->
      <div class="text-center text-muted small mt-2">
        <span v-if="totalItems > 0">
          Показано {{ firstItemIndex }} - {{ lastItemIndex }} из {{ totalItems }} растений
        </span>
        <span v-else>
          Растения не найдены
        </span>
      </div>
    </nav>
  </template>
  
  <script setup>
  import { ref, computed, watch } from 'vue';
  
  const props = defineProps({
    currentPage: {
      type: Number,
      default: 1
    },
    totalPages: {
      type: Number,
      default: 1
    },
    totalItems: {
      type: Number,
      default: 0
    },
    perPage: {
      type: Number,
      default: 10
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  });
  
  const emit = defineEmits(['page-change']);
  
  // Расчет индексов отображаемых элементов
  const firstItemIndex = computed(() => {
    if (props.totalItems === 0) return 0;
    return (props.currentPage - 1) * props.perPage + 1;
  });
  
  const lastItemIndex = computed(() => {
    return Math.min(props.currentPage * props.perPage, props.totalItems);
  });
  
  // Формирование отображаемых номеров страниц
  const displayedPages = computed(() => {
    const totalPages = props.totalPages;
    const currentPage = props.currentPage;
    const pages = [];
    
    // Если страниц мало, показываем все
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
      return pages;
    }
    
    // Всегда показываем первую страницу
    pages.push(1);
    
    // Решаем, нужен ли эллипсис в начале
    if (currentPage > 3) {
      pages.push('...');
    }
    
    // Вычисляем начальную и конечную страницы для отображения
    let startPage = Math.max(2, currentPage - 1);
    let endPage = Math.min(totalPages - 1, currentPage + 1);
    
    // Корректируем, если мы у начала или конца
    if (currentPage <= 3) {
      endPage = Math.min(5, totalPages - 1);
    } else if (currentPage >= totalPages - 2) {
      startPage = Math.max(totalPages - 4, 2);
    }
    
    // Добавляем промежуточные страницы
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    // Решаем, нужен ли эллипсис в конце
    if (endPage < totalPages - 1) {
      pages.push('...');
    }
    
    // Всегда показываем последнюю страницу
    if (totalPages > 1) {
      pages.push(totalPages);
    }
    
    return pages;
  });
  
  // Обработчик смены страницы
  function onPageChange(page) {
    if (page !== props.currentPage && page > 0 && page <= props.totalPages && !props.isLoading) {
      emit('page-change', page);
    }
  }
  </script>
  
  <style scoped>
  .plant-pagination {
    margin-top: 2rem;
    margin-bottom: 1rem;
  }
  
  .pagination {
    margin-bottom: 0.5rem;
  }
  
  .page-link {
    color: var(--bs-primary);
    border-color: #dee2e6;
    padding: 0.5rem 0.75rem;
    transition: all 0.2s ease;
  }
  
  .page-item.active .page-link {
    background-color: var(--bs-primary);
    border-color: var(--bs-primary);
  }
  
  .page-link:hover {
    color: var(--bs-success);
    background-color: #f8f9fa;
    border-color: #dee2e6;
    transform: translateY(-2px);
  }
  
  .page-item.active .page-link:hover {
    color: #fff;
    background-color: var(--bs-success);
    border-color: var(--bs-success);
  }
  
  .page-item.disabled .page-link {
    color: #6c757d;
    pointer-events: none;
    background-color: #fff;
    border-color: #dee2e6;
  }
  </style>