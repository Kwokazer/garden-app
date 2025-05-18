// frontend/src/features/questions/api/questionsApi.js

// Используем тот же BASE_API_URL как в других API модулях
const BASE_API_URL = "/api/v1"

/**
 * Обрабатывает ответы от API (такая же функция как в authApi.js и plantsApi.js)
 */
async function handleResponse(response) {
  const contentType = response.headers.get("content-type");
  let data;

  if (contentType && contentType.includes("application/json")) {
    data = await response.json();
  } else {
    const textData = await response.text();
    try {
      data = JSON.parse(textData);
    } catch (e) {
      data = { message: textData || response.statusText };
    }
  }

  if (!response.ok) {
    const message =
      data && data.detail
        ? typeof data.detail === "string"
          ? data.detail
          : JSON.stringify(data.detail)
        : data && data.message
        ? data.message
        : response.statusText;
    return Promise.reject({
      success: false,
      message: message,
      status: response.status,
      errorData: data,
    });
  }

  return Promise.resolve({ success: true, data: data });
}

/**
 * Получает токен доступа из localStorage
 */
function getAuthHeaders() {
  const token = localStorage.getItem('accessToken');
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
}

/**
 * API клиент для работы с вопросами
 */
export const questionsApi = {
  /**
   * Получить список вопросов с пагинацией и фильтрацией
   * @param {number} page - Номер страницы (начиная с 1)
   * @param {number} per_page - Количество вопросов на странице
   * @param {Object} filters - Фильтры для поиска
   * @returns {Promise<Object>} - Ответ от сервера со списком вопросов
   */
  async getQuestions(page = 1, per_page = 20, filters = {}) {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('per_page', per_page);
      
      // Добавляем фильтры в запрос
      if (filters.search) {
        params.append('search', filters.search);
      }
      
      if (filters.plant_id) {
        params.append('plant_id', filters.plant_id);
      }
      
      if (filters.author_id) {
        params.append('author_id', filters.author_id);
      }
      
      if (filters.is_solved !== undefined) {
        params.append('is_solved', filters.is_solved);
      }
      
      if (filters.sort_by) {
        params.append('sort_by', filters.sort_by);
      }
      
      if (filters.sort_order) {
        params.append('sort_order', filters.sort_order);
      }
      
      const url = `${BASE_API_URL}/questions?${params.toString()}`;
      console.log('Fetching questions URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error fetching questions list:', error);
      throw error;
    }
  },

  /**
   * Получить вопросы по конкретному растению
   * @param {number} plantId - ID растения
   * @param {number} page - Номер страницы
   * @param {number} per_page - Количество вопросов на странице
   * @param {Object} filters - Дополнительные фильтры
   * @returns {Promise<Object>} - Ответ от сервера со списком вопросов
   */
  async getQuestionsByPlant(plantId, page = 1, per_page = 10, filters = {}) {
    try {
      const params = new URLSearchParams();
      params.append('page', page);
      params.append('per_page', per_page);
      
      // Добавляем дополнительные фильтры
      if (filters.search) {
        params.append('search', filters.search);
      }
      
      if (filters.is_solved !== undefined) {
        params.append('is_solved', filters.is_solved);
      }
      
      if (filters.sort_by) {
        params.append('sort_by', filters.sort_by);
      }
      
      if (filters.sort_order) {
        params.append('sort_order', filters.sort_order);
      }
      
      const url = `${BASE_API_URL}/questions/by-plant/${plantId}?${params.toString()}`;
      console.log('Fetching questions by plant URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error fetching questions for plant ${plantId}:`, error);
      throw error;
    }
  },

  /**
   * Получить детальную информацию о вопросе с ответами
   * @param {number} questionId - ID вопроса
   * @returns {Promise<Object>} - Ответ от сервера с деталями вопроса
   */
  async getQuestionById(questionId) {
    try {
      const url = `${BASE_API_URL}/questions/${questionId}`;
      console.log('Fetching question details URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error fetching question ${questionId}:`, error);
      throw error;
    }
  },

  /**
   * Создать новый вопрос
   * @param {Object} questionData - Данные вопроса
   * @returns {Promise<Object>} - Ответ от сервера с созданным вопросом
   */
  async createQuestion(questionData) {
    try {
      const url = `${BASE_API_URL}/questions`;
      console.log('Creating question URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(questionData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error creating question:', error);
      throw error;
    }
  },

  /**
   * Обновить вопрос
   * @param {number} questionId - ID вопроса
   * @param {Object} questionData - Новые данные вопроса
   * @returns {Promise<Object>} - Ответ от сервера с обновленным вопросом
   */
  async updateQuestion(questionId, questionData) {
    try {
      const url = `${BASE_API_URL}/questions/${questionId}`;
      console.log('Updating question URL:', url);
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(questionData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error updating question ${questionId}:`, error);
      throw error;
    }
  },

  /**
   * Удалить вопрос
   * @param {number} questionId - ID вопроса
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async deleteQuestion(questionId) {
    try {
      const url = `${BASE_API_URL}/questions/${questionId}`;
      console.log('Deleting question URL:', url);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error deleting question ${questionId}:`, error);
      throw error;
    }
  },

  /**
   * Проголосовать за вопрос
   * @param {number} questionId - ID вопроса
   * @param {string} voteType - Тип голоса ('up' или 'down')
   * @returns {Promise<Object>} - Ответ от сервера с обновленным вопросом
   */
  async voteForQuestion(questionId, voteType) {
    try {
      const url = `${BASE_API_URL}/questions/${questionId}/vote`;
      console.log('Voting for question URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ vote_type: voteType })
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error voting for question ${questionId}:`, error);
      throw error;
    }
  }
};

/**
 * API клиент для работы с ответами
 */
export const answersApi = {
  /**
   * Создать новый ответ
   * @param {Object} answerData - Данные ответа
   * @returns {Promise<Object>} - Ответ от сервера с созданным ответом
   */
  async createAnswer(answerData) {
    try {
      const url = `${BASE_API_URL}/answers`;
      console.log('Creating answer URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(answerData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error('Error creating answer:', error);
      throw error;
    }
  },

  /**
   * Обновить ответ
   * @param {number} answerId - ID ответа
   * @param {Object} answerData - Новые данные ответа
   * @returns {Promise<Object>} - Ответ от сервера с обновленным ответом
   */
  async updateAnswer(answerId, answerData) {
    try {
      const url = `${BASE_API_URL}/answers/${answerId}`;
      console.log('Updating answer URL:', url);
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(answerData)
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error updating answer ${answerId}:`, error);
      throw error;
    }
  },

  /**
   * Удалить ответ
   * @param {number} answerId - ID ответа
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async deleteAnswer(answerId) {
    try {
      const url = `${BASE_API_URL}/answers/${answerId}`;
      console.log('Deleting answer URL:', url);
      
      const response = await fetch(url, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error deleting answer ${answerId}:`, error);
      throw error;
    }
  },

  /**
   * Отметить ответ как принятый
   * @param {number} answerId - ID ответа
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async acceptAnswer(answerId) {
    try {
      const url = `${BASE_API_URL}/answers/${answerId}/accept`;
      console.log('Accepting answer URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error accepting answer ${answerId}:`, error);
      throw error;
    }
  },

  /**
   * Отменить принятие ответа
   * @param {number} answerId - ID ответа
   * @returns {Promise<Object>} - Ответ от сервера
   */
  async unacceptAnswer(answerId) {
    try {
      const url = `${BASE_API_URL}/answers/${answerId}/unaccept`;
      console.log('Unaccepting answer URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders()
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error unaccepting answer ${answerId}:`, error);
      throw error;
    }
  },

  /**
   * Проголосовать за ответ
   * @param {number} answerId - ID ответа
   * @param {string} voteType - Тип голоса ('up' или 'down')
   * @returns {Promise<Object>} - Ответ от сервера с обновленным ответом
   */
  async voteForAnswer(answerId, voteType) {
    try {
      const url = `${BASE_API_URL}/answers/${answerId}/vote`;
      console.log('Voting for answer URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ vote_type: voteType })
      });
      
      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error voting for answer ${answerId}:`, error);
      throw error;
    }
  }
};