// src/interceptors/axios.js
import axios from 'axios';

// Создаем экземпляр axios с базовым URL
const instance = axios.create({
  baseURL: '/api/v1',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Добавляем перехватчик запросов для добавления токена авторизации
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Добавляем перехватчик ответов для обработки ошибок авторизации
instance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Если ошибка 401 (Unauthorized) и запрос еще не повторялся
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Попытка обновить токен
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          // Если нет refresh токена, выходим из системы
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        // Запрос на обновление токена
        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken
        });
        
        if (response.data.access_token) {
          // Сохраняем новые токены
          localStorage.setItem('accessToken', response.data.access_token);
          if (response.data.refresh_token) {
            localStorage.setItem('refreshToken', response.data.refresh_token);
          }
          
          // Повторяем оригинальный запрос с новым токеном
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // В случае ошибки при обновлении токена, выходим из системы
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default instance;