// src/features/auth/api/authApi.js

/**
 * API клиент для аутентификации с запросами к бэкенду
 */

const BASE_API_URL = "/api/v1"; // Основной URL для API

/**
 * Обрабатывает ответы от API
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
    // Возвращаем объект с ошибкой
    return Promise.reject({
      success: false,
      message: message,
      status: response.status,
      errorData: data,
    });
  }

  // Успешный ответ
  return Promise.resolve({ success: true, data: data });
}

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
    const response = await fetch(`${BASE_API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response);
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

    const response = await fetch(`${BASE_API_URL}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(registrationData),
    });
    return handleResponse(response);
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

    const response = await fetch(`${BASE_API_URL}/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    return handleResponse(response);
  },

  /**
   * Обновляет токены с помощью refresh токена
   * @param {string} token - refresh токен
   * @returns {Promise<Object>} - ответ от сервера с новыми токенами
   */
  async refreshToken(token) {
    const response = await fetch(`${BASE_API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: token }),
    });
    return handleResponse(response);
  },

  /**
   * Запрашивает сброс пароля
   * @param {string} email - email пользователя
   * @returns {Promise<Object>} - ответ от сервера
   */
  async resetPassword(email) {
    const response = await fetch(`${BASE_API_URL}/auth/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });
    return handleResponse(response);
  },

  /**
   * Подтверждает сброс пароля с новым паролем
   * @param {string} resetToken - токен сброса пароля
   * @param {string} newPassword - новый пароль
   * @returns {Promise<Object>} - ответ от сервера
   */
  async resetPasswordConfirm(resetToken, newPassword) {
    const response = await fetch(
      `${BASE_API_URL}/auth/reset-password-confirm`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          reset_token: resetToken,
          new_password: newPassword,
        }),
      }
    );
    return handleResponse(response);
  },

  /**
   * Подтверждает email пользователя
   * @param {string} verificationToken - токен подтверждения email
   * @returns {Promise<Object>} - ответ от сервера
   */
  async verifyEmail(verificationToken) {
    const response = await fetch(`${BASE_API_URL}/auth/verify-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        verification_token: verificationToken,
      }),
    });
    return handleResponse(response);
  },

  /**
   * Получает текущего пользователя с его профилем
   * @param {string} accessToken - JWT токен доступа
   * @returns {Promise<Object>} - ответ от сервера с данными пользователя
   */
  async getCurrentUser(accessToken) {
    const response = await fetch(`${BASE_API_URL}/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });
    return handleResponse(response);
  },
};
