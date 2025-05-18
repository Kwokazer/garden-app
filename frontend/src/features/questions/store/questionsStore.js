// frontend/src/features/questions/store/questionsStore.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { questionsApi, answersApi } from '../api/questionsApi';

/**
 * Хранилище для управления состоянием вопросов и ответов
 */
export const useQuestionsStore = defineStore('questions', () => {
  // State (состояние)
  const questions = ref([]);
  const currentQuestion = ref(null);
  const isLoading = ref(false);
  const error = ref(null);
  const pagination = ref({
    page: 1,
    total_pages: 1,
    total: 0,
    size: 20,
    pages: 1
  });
  const activeFilters = ref({
    search: '',
    plant_id: null,
    author_id: null,
    is_solved: null,
    sort_by: 'created_at',
    sort_order: 'desc'
  });

  // Getters (вычисляемые свойства)
  const getQuestions = computed(() => questions.value);
  const getCurrentQuestion = computed(() => currentQuestion.value);
  const getIsLoading = computed(() => isLoading.value);
  const getError = computed(() => error.value);
  const getPagination = computed(() => pagination.value);
  const getActiveFilters = computed(() => activeFilters.value);

  /**
   * Загрузить список вопросов с фильтрацией и пагинацией
   */
  async function loadQuestions(page = 1, per_page = 20, resetFilters = false) {
    isLoading.value = true;
    error.value = null;

    if (resetFilters) {
      activeFilters.value = {
        search: '',
        plant_id: null,
        author_id: null,
        is_solved: null,
        sort_by: 'created_at',
        sort_order: 'desc'
      };
    }

    try {
      const response = await questionsApi.getQuestions(
        page,
        per_page,
        activeFilters.value
      );
      
      questions.value = response.items || [];
      
      pagination.value = {
        page: response.page || page,
        total_pages: response.pages || 1,
        total: response.total || 0,
        size: response.size || per_page,
        pages: response.pages || 1
      };

      return questions.value;
    } catch (e) {
      error.value = e.message || 'Ошибка при загрузке списка вопросов';
      console.error('Error loading questions list:', e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загрузить вопросы по конкретному растению
   */
  async function loadQuestionsByPlant(plantId, page = 1, per_page = 10, filters = {}) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await questionsApi.getQuestionsByPlant(
        plantId,
        page,
        per_page,
        filters
      );
      
      const plantQuestions = response.items || [];
      
      // Обновляем пагинацию для вопросов по растению
      pagination.value = {
        page: response.page || page,
        total_pages: response.pages || 1,
        total: response.total || 0,
        size: response.size || per_page,
        pages: response.pages || 1
      };

      return plantQuestions;
    } catch (e) {
      error.value = e.message || `Ошибка при загрузке вопросов для растения ${plantId}`;
      console.error(`Error loading questions for plant ${plantId}:`, e);
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Загрузить детальную информацию о вопросе
   */
  async function loadQuestionById(questionId) {
    if (!questionId) {
      error.value = 'ID вопроса не указан';
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const question = await questionsApi.getQuestionById(questionId);
      currentQuestion.value = question;
      return question;
    } catch (e) {
      error.value = e.message || `Ошибка при загрузке вопроса ${questionId}`;
      console.error(`Error loading question ${questionId}:`, e);
      currentQuestion.value = null;
      return null;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Создать новый вопрос
   */
  async function createQuestion(questionData) {
    isLoading.value = true;
    error.value = null;

    try {
      const newQuestion = await questionsApi.createQuestion(questionData);
      
      // Добавляем новый вопрос в начало списка
      questions.value.unshift(newQuestion);
      
      return newQuestion;
    } catch (e) {
      error.value = e.message || 'Ошибка при создании вопроса';
      console.error('Error creating question:', e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Обновить вопрос
   */
  async function updateQuestion(questionId, questionData) {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedQuestion = await questionsApi.updateQuestion(questionId, questionData);
      
      // Если это текущий вопрос, обновляем его
      if (currentQuestion.value && currentQuestion.value.id === questionId) {
        currentQuestion.value = updatedQuestion;
      }
      
      // Обновляем в списке вопросов
      const index = questions.value.findIndex(q => q.id === questionId);
      if (index !== -1) {
        questions.value[index] = updatedQuestion;
      }
      
      return updatedQuestion;
    } catch (e) {
      error.value = e.message || `Ошибка при обновлении вопроса ${questionId}`;
      console.error(`Error updating question ${questionId}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Удалить вопрос
   */
  async function deleteQuestion(questionId) {
    isLoading.value = true;
    error.value = null;

    try {
      await questionsApi.deleteQuestion(questionId);
      
      // Удаляем из списка
      questions.value = questions.value.filter(q => q.id !== questionId);
      
      // Очищаем текущий вопрос, если он был удален
      if (currentQuestion.value && currentQuestion.value.id === questionId) {
        currentQuestion.value = null;
      }
      
      return true;
    } catch (e) {
      error.value = e.message || `Ошибка при удалении вопроса ${questionId}`;
      console.error(`Error deleting question ${questionId}:`, e);
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Проголосовать за вопрос
   */
  async function voteForQuestion(questionId, voteType) {
    try {
      const updatedQuestion = await questionsApi.voteForQuestion(questionId, voteType);
      
      // Обновляем текущий вопрос
      if (currentQuestion.value && currentQuestion.value.id === questionId) {
        currentQuestion.value = updatedQuestion;
      }
      
      // Обновляем в списке вопросов
      const index = questions.value.findIndex(q => q.id === questionId);
      if (index !== -1) {
        questions.value[index] = updatedQuestion;
      }
      
      return updatedQuestion;
    } catch (e) {
      error.value = e.message || `Ошибка при голосовании за вопрос ${questionId}`;
      console.error(`Error voting for question ${questionId}:`, e);
      throw e;
    }
  }

  /**
   * Создать новый ответ
   */
  async function createAnswer(answerData) {
    try {
      const newAnswer = await answersApi.createAnswer(answerData);
      
      // Если это ответ на текущий вопрос, добавляем его к ответам
      if (currentQuestion.value && currentQuestion.value.id === answerData.question_id) {
        if (!currentQuestion.value.answers) {
          currentQuestion.value.answers = [];
        }
        currentQuestion.value.answers.push(newAnswer);
        currentQuestion.value.answers_count = (currentQuestion.value.answers_count || 0) + 1;
      }
      
      return newAnswer;
    } catch (e) {
      error.value = e.message || 'Ошибка при создании ответа';
      console.error('Error creating answer:', e);
      throw e;
    }
  }

  /**
   * Обновить ответ
   */
  async function updateAnswer(answerId, answerData) {
    try {
      const updatedAnswer = await answersApi.updateAnswer(answerId, answerData);
      
      // Обновляем ответ в текущем вопросе
      if (currentQuestion.value && currentQuestion.value.answers) {
        const index = currentQuestion.value.answers.findIndex(a => a.id === answerId);
        if (index !== -1) {
          currentQuestion.value.answers[index] = updatedAnswer;
        }
      }
      
      return updatedAnswer;
    } catch (e) {
      error.value = e.message || `Ошибка при обновлении ответа ${answerId}`;
      console.error(`Error updating answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Удалить ответ
   */
  async function deleteAnswer(answerId) {
    try {
      await answersApi.deleteAnswer(answerId);
      
      // Удаляем ответ из текущего вопроса
      if (currentQuestion.value && currentQuestion.value.answers) {
        currentQuestion.value.answers = currentQuestion.value.answers.filter(a => a.id !== answerId);
        currentQuestion.value.answers_count = Math.max(0, (currentQuestion.value.answers_count || 0) - 1);
      }
      
      return true;
    } catch (e) {
      error.value = e.message || `Ошибка при удалении ответа ${answerId}`;
      console.error(`Error deleting answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Отметить ответ как принятый
   */
  async function acceptAnswer(answerId) {
    try {
      const updatedQuestion = await answersApi.acceptAnswer(answerId);
      
      // Обновляем текущий вопрос полностью
      if (currentQuestion.value && updatedQuestion.id === currentQuestion.value.id) {
        currentQuestion.value = updatedQuestion;
      }
      
      return updatedQuestion;
    } catch (e) {
      error.value = e.message || `Ошибка при принятии ответа ${answerId}`;
      console.error(`Error accepting answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Отменить принятие ответа
   */
  async function unacceptAnswer(answerId) {
    try {
      const updatedQuestion = await answersApi.unacceptAnswer(answerId);
      
      // Обновляем текущий вопрос полностью
      if (currentQuestion.value && updatedQuestion.id === currentQuestion.value.id) {
        currentQuestion.value = updatedQuestion;
      }
      
      return updatedQuestion;
    } catch (e) {
      error.value = e.message || `Ошибка при отмене принятия ответа ${answerId}`;
      console.error(`Error unaccepting answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Проголосовать за ответ
   */
  async function voteForAnswer(answerId, voteType) {
    try {
      const updatedAnswer = await answersApi.voteForAnswer(answerId, voteType);
      
      // Обновляем ответ в текущем вопросе
      if (currentQuestion.value && currentQuestion.value.answers) {
        const index = currentQuestion.value.answers.findIndex(a => a.id === answerId);
        if (index !== -1) {
          currentQuestion.value.answers[index] = updatedAnswer;
        }
      }
      
      return updatedAnswer;
    } catch (e) {
      error.value = e.message || `Ошибка при голосовании за ответ ${answerId}`;
      console.error(`Error voting for answer ${answerId}:`, e);
      throw e;
    }
  }

  /**
   * Обновить фильтры и перезагрузить вопросы
   */
  async function updateFilters(newFilters) {
    Object.keys(newFilters).forEach(key => {
      if (newFilters[key] !== undefined && key in activeFilters.value) {
        activeFilters.value[key] = newFilters[key];
      }
    });
    
    // Сбрасываем на первую страницу при изменении фильтров
    return await loadQuestions(1, pagination.value.size);
  }

  /**
   * Очистить все фильтры и перезагрузить вопросы
   */
  async function clearFilters() {
    return await loadQuestions(1, pagination.value.size, true);
  }

  /**
   * Очистить ошибку
   */
  function clearError() {
    error.value = null;
  }

  /**
   * Очистить текущий вопрос
   */
  function clearCurrentQuestion() {
    currentQuestion.value = null;
  }

  // Возвращаем публичное API хранилища
  return {
    // State
    questions,
    currentQuestion,
    isLoading,
    error,
    pagination,
    activeFilters,
    
    // Getters
    getQuestions,
    getCurrentQuestion,
    getIsLoading,
    getError,
    getPagination,
    getActiveFilters,
    
    // Actions
    loadQuestions,
    loadQuestionsByPlant,
    loadQuestionById,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    voteForQuestion,
    createAnswer,
    updateAnswer,
    deleteAnswer,
    acceptAnswer,
    unacceptAnswer,
    voteForAnswer,
    updateFilters,
    clearFilters,
    clearError,
    clearCurrentQuestion
  };
});