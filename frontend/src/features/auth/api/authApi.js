// src/features/auth/api/authApi.js
import axiosInstance from "../../../interceptors/axios.js";

/**
 * API клиент для аутентификации с запросами к бэкенду
 */

const BASE_API_URL = "/api/v1"; // Основной URL для API

/**
 * API клиент для работы с аутентификацией
 */
export const authApi = {
  /**
   * Выполняет вход пользователя
   * @param {string} email - email пользователя
   * @param {string} password - пароль пользователя
   * @returns {Promise<Object>} - ответ от сервера с токенами
   */
  async login(email, password) {
    try {
      const response = await axiosInstance.post("/auth/login", {
        email,
        password,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Регистрирует нового пользователя
   * @param {string} username - имя пользователя
   * @param {string} email - email пользователя
   * @param {string} password - пароль пользователя
   * @param {string} firstName - имя (опционально)
   * @param {string} lastName - фамилия (опционально)
   * @returns {Promise<Object>} - ответ от сервера
   */
  async register(username, email, password, firstName, lastName) {
    const registrationData = {
      username,
      email,
      password,
    };

    // Добавляем опциональные поля только если они переданы
    if (firstName) registrationData.first_name = firstName;
    if (lastName) registrationData.last_name = lastName;

    try {
      const response = await axiosInstance.post(
        "/auth/register",
        registrationData
      );
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Выполняет выход пользователя (инвалидация refresh токена)
   * @param {string} refreshToken - refresh токен
   * @returns {Promise<Object>} - ответ от сервера
   */
  async logout(refreshToken) {
    if (!refreshToken) {
      console.warn("Попытка выхода без refresh токена.");
      return Promise.resolve({
        success: true,
        data: { message: "Выход выполнен (локально)." },
      });
    }

    try {
      const response = await axiosInstance.post("/auth/logout", {
        refresh_token: refreshToken,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Обновляет токены с помощью refresh токена
   * @param {string} token - refresh токен
   * @returns {Promise<Object>} - ответ от сервера с новыми токенами
   */
  async refreshToken(token) {
    try {
      const response = await axiosInstance.post("/auth/refresh", {
        refresh_token: token,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Запрашивает сброс пароля
   * @param {string} email - email пользователя
   * @returns {Promise<Object>} - ответ от сервера
   */
  async resetPassword(email) {
    try {
      const response = await axiosInstance.post("/auth/reset-password", {
        email,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Подтверждает сброс пароля с новым паролем
   * @param {string} resetToken - токен сброса пароля
   * @param {string} newPassword - новый пароль
   * @returns {Promise<Object>} - ответ от сервера
   */
  async resetPasswordConfirm(resetToken, newPassword) {
    try {
      const response = await axiosInstance.post(
        "/auth/reset-password-confirm",
        {
          reset_token: resetToken,
          new_password: newPassword,
        }
      );
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Подтверждает email пользователя
   * @param {string} verificationToken - токен подтверждения email
   * @returns {Promise<Object>} - ответ от сервера
   */
  async verifyEmail(verificationToken) {
    try {
      const response = await axiosInstance.post("/auth/verify-email", {
        verification_token: verificationToken,
      });
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },

  /**
   * Получает текущего пользователя с его профилем
   * @param {string} accessToken - JWT токен доступа
   * @returns {Promise<Object>} - ответ от сервера с данными пользователя
   */
  async getCurrentUser(accessToken) {
    try {
      // Если токен передан, используем его, иначе axios interceptor добавит токен из localStorage
      const headers = accessToken
        ? { Authorization: `Bearer ${accessToken}` }
        : {};
      const response = await axiosInstance.get("/auth/me", { headers });
      return { success: true, data: response.data };
    } catch (error) {
      return Promise.reject({
        success: false,
        message: error.response?.data?.detail || error.message,
        status: error.response?.status,
        errorData: error.response?.data,
      });
    }
  },
};
