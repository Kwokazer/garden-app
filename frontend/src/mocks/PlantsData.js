// src/mocks/plantsData.js

/**
 * Тестовые данные для растений
 * Используется для демонстрации и разработки, пока бэкенд не готов
 */

// Базовые данные растений
const plants = [
    {
      id: 1,
      name: 'Монстера Деликатесная',
      latin_name: 'Monstera deliciosa',
      description: 'Популярное комнатное растение с характерными разрезными листьями. Монстера деликатесная относится к семейству Ароидных и получила свое название за съедобные плоды, по вкусу напоминающие ананас и банан. В природе встречается в тропических лесах Центральной Америки.',
      category: { id: 1, name: 'Лиственные' },
      tags: [
        { id: 1, name: 'Тропические' },
        { id: 2, name: 'Популярные' }
      ],
      images: [
        { id: 1, url: '/plants/monstera.jpg', alt: 'Монстера Деликатесная', title: 'Монстера Деликатесная' },
        { id: 2, url: '/plants/monstera-2.jpg', alt: 'Лист Монстеры', title: 'Крупный план листа' }
      ],
      plant_type: 'vine',
      life_cycle: 'perennial',
      height_min: 150,
      height_max: 300,
      growth_rate: 'fast',
      watering_frequency: 'weekly',
      light_level: 'partial_sun',
      temperature_min: 18,
      temperature_max: 30,
      humidity_level: 'high',
      is_toxic: true,
      flowering_period: 'Редко цветет в домашних условиях',
      fertilizing_frequency: 'monthly',
      repotting_frequency: 'bi_annually',
      care_difficulty: 'easy',
      climate_zones: [
        { id: 1, name: 'Тропический' },
        { id: 2, name: 'Субтропический' }
      ],
      care_instructions: 'Монстера любит яркий рассеянный свет, но может переносить полутень. Поливайте, когда верхний слой почвы подсохнет. В период активного роста (весна-лето) подкармливайте раз в месяц. Протирайте листья влажной тряпкой для удаления пыли. Обеспечьте опору для роста.',
      care_tips: [
        'Размещайте вдали от прямых солнечных лучей, которые могут вызвать ожоги на листьях',
        'Увеличьте влажность с помощью регулярного опрыскивания или увлажнителя воздуха',
        'Используйте мох на опоре для лучшего крепления воздушных корней'
      ],
      common_problems: [
        {
          title: 'Желтеющие листья',
          description: 'Листья монстеры могут желтеть из-за избыточного полива, недостатка света или питательных веществ.',
          solution: 'Проверьте режим полива, убедитесь что растение получает достаточно света. Подкормите универсальным удобрением.'
        },
        {
          title: 'Отсутствие характерных разрезов на листьях',
          description: 'Молодые или получающие недостаточно света растения могут не формировать типичные разрезы на листьях.',
          solution: 'Увеличьте освещение и будьте терпеливы, с возрастом листья обычно становятся более разрезными.'
        }
      ],
      propagation_methods: [
        {
          name: 'Черенкование',
          description: 'Отрежьте часть стебля с не менее чем одним листом и воздушным корнем. Поставьте в воду или высадите в легкую почву.',
          difficulty: 2
        },
        {
          name: 'Деление куста',
          description: 'При пересадке разделите растение на несколько частей, убедившись, что у каждой есть корни и точки роста.',
          difficulty: 3
        }
      ],
      planting_instructions: 'Используйте рыхлую почвенную смесь с хорошим дренажем. Идеальный состав: 1 часть садовой земли, 1 часть перегноя, 1 часть песка и 1 часть торфа. Выберите горшок достаточно большой, чтобы вместить корневую систему и опору для растения.',
      notes: 'Монстера может выделять сок, который вызывает раздражение при попадании на кожу, поэтому используйте перчатки при обрезке.'
    },
    // Другие растения...
  ];
  
  // Остальные растения импортируются из дополнительного файла для упрощения  
  import { additionalPlants } from './additionalPlantsData';
  plants.push(...additionalPlants);
  
  // Данные для категорий
  const categories = [
    { id: 1, name: 'Лиственные' },
    { id: 2, name: 'Суккуленты' },
    { id: 3, name: 'Цветущие' },
    { id: 4, name: 'Кактусы' },
    { id: 5, name: 'Папоротники' },
    { id: 6, name: 'Пальмы' },
    { id: 7, name: 'Бонсай' }
  ];
  
  // Данные для климатических зон
  const climateZones = [
    { id: 1, name: 'Тропический' },
    { id: 2, name: 'Субтропический' },
    { id: 3, name: 'Аридный' },
    { id: 4, name: 'Континентальный' },
    { id: 5, name: 'Умеренный' },
    { id: 6, name: 'Средиземноморский' }
  ];
  
  // Экспорт данных
  export { plants, categories, climateZones };
  
  // Вспомогательные функции для работы с данными
  
  /**
   * Получить все растения с пагинацией и фильтрацией
   * @param {number} page - номер страницы (начиная с 1)
   * @param {number} limit - количество элементов на странице
   * @param {Object} filters - фильтры для выборки
   * @returns {Object} - объект с данными и метаинформацией
   */
  export function getPlants(page = 1, limit = 10, filters = {}) {
    let filteredPlants = [...plants];
    
    // Применение фильтров
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      filteredPlants = filteredPlants.filter(plant => 
        plant.name.toLowerCase().includes(query) ||
        plant.latin_name.toLowerCase().includes(query) ||
        plant.description.toLowerCase().includes(query)
      );
    }
    
    if (filters.category_id) {
      filteredPlants = filteredPlants.filter(plant => 
        plant.category && plant.category.id === parseInt(filters.category_id)
      );
    }
    
    if (filters.climate_zone_id) {
      filteredPlants = filteredPlants.filter(plant => 
        plant.climate_zones && plant.climate_zones.some(zone => 
          zone.id === parseInt(filters.climate_zone_id)
        )
      );
    }
    
    // Сортировка
    if (filters.sort_by) {
      const direction = filters.sort_direction === 'desc' ? -1 : 1;
      filteredPlants.sort((a, b) => {
        let valueA, valueB;
        
        switch (filters.sort_by) {
          case 'name':
            valueA = a.name;
            valueB = b.name;
            break;
          case 'created_at':
            // Для демонстрации используем ID как суррогат даты создания
            valueA = a.id;
            valueB = b.id;
            break;
          case 'popularity':
            // Для демонстрации используем ID как суррогат популярности (в обратном порядке)
            valueA = 6 - a.id; // Чем меньше ID, тем "популярнее" растение
            valueB = 6 - b.id;
            break;
          default:
            valueA = a.name;
            valueB = b.name;
        }
        
        if (valueA < valueB) return -1 * direction;
        if (valueA > valueB) return 1 * direction;
        return 0;
      });
    }
    
    // Вычисление пагинации
    const startIndex = (page - 1) * limit;
    const endIndex = startIndex + limit;
    const paginatedPlants = filteredPlants.slice(startIndex, endIndex);
    
    return {
      items: paginatedPlants,
      total_items: filteredPlants.length,
      total_pages: Math.ceil(filteredPlants.length / limit),
      page: page,
      per_page: limit
    };
  }
  
  /**
   * Получить растение по ID
   * @param {number|string} id - ID растения
   * @returns {Object|null} - объект растения или null, если не найдено
   */
  export function getPlantById(id) {
    const plantId = parseInt(id);
    const plant = plants.find(p => p.id === plantId);
    
    if (!plant) return null;
    
    // Добавляем похожие растения (для демонстрации)
    const similar = plants
      .filter(p => p.id !== plantId && p.category.id === plant.category.id)
      .slice(0, 3)
      .map(p => ({
        id: p.id,
        name: p.name,
        image_url: p.images && p.images.length > 0 ? p.images[0].url : null
      }));
    
    return {
      ...plant,
      similar_plants: similar
    };
  }
  
  /**
   * Получить все категории
   * @param {number|null} parentId - ID родительской категории (если нужны подкатегории)
   * @returns {Array} - массив категорий
   */
  export function getCategories(parentId = null) {
    // В этой демо-версии мы не поддерживаем иерархию категорий,
    // поэтому просто возвращаем все категории
    return categories;
  }
  
  /**
   * Получить все климатические зоны
   * @returns {Array} - массив климатических зон
   */
  export function getClimateZones() {
    return climateZones;
  }