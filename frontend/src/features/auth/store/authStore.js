// src/features/auth/store/authStore.js

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "../api/authApi.js";
import { useRouter } from "vue-router";

/**
 * Функция для декодирования JWT токена (без проверки подписи)
 */
function parseJwt(token) {
  try {
    // Разделяем JWT на части и берем payload (вторую часть)
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");

    // Декодируем Base64
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );

    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error("Ошибка декодирования JWT: ", e);
    return null;
  }
}

/**
 * Хранилище для управления состоянием аутентификации
 */
export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();

  // State (состояние)
  const accessToken = ref(localStorage.getItem("accessToken") || null);
  const refreshToken = ref(localStorage.getItem("refreshToken") || null);
  const user = ref(JSON.parse(localStorage.getItem("user")) || null);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters (вычисляемые свойства)
  const isLoggedIn = computed(() => !!accessToken.value);
  const authUser = computed(() => user.value);
  const getAccessToken = computed(() => accessToken.value);
  const getRefreshToken = computed(() => refreshToken.value);
  const getError = computed(() => error.value);
  const getIsLoading = computed(() => isLoading.value);

  /**
   * Устанавливает пользовательские данные из JWT токена
   */
  function setUserFromToken(token) {
    if (!token) {
      user.value = null;
      localStorage.removeItem("user");
      return;
    }

    const decodedToken = parseJwt(token);
    if (decodedToken && decodedToken.sub) {
      // Из токена можем получить базовую информацию
      const userData = {
        id: decodedToken.sub,
        roles: decodedToken.roles || [],
      };

      // Если в токене есть email или username, добавляем их
      if (decodedToken.email) userData.email = decodedToken.email;
      if (decodedToken.username) userData.username = decodedToken.username;

      user.value = userData;
      localStorage.setItem("user", JSON.stringify(userData));
    } else {
      user.value = null;
      localStorage.removeItem("user");
    }
  }

  // Инициализация пользователя из токена при загрузке store
  if (accessToken.value) {
    setUserFromToken(accessToken.value);
    // Обновляем данные пользователя из API при инициализации
    refreshUserData();
  }

  /**
   * Выполняет вход пользователя
   */
  async function login(credentials) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await authApi.login(
        credentials.email,
        credentials.password
      );

      if (response.success && response.data.access_token) {
        // Сохраняем токены
        accessToken.value = response.data.access_token;
        refreshToken.value = response.data.refresh_token;

        localStorage.setItem("accessToken", accessToken.value);
        localStorage.setItem("refreshToken", refreshToken.value);

        // Устанавливаем данные пользователя из токена
        setUserFromToken(accessToken.value);

        // Если нужно, можно запросить дополнительные данные профиля
        try {
          const userResponse = await authApi.getCurrentUser(accessToken.value);
          if (userResponse.success && userResponse.data) {
            // Дополняем данные пользователя полной информацией из профиля
            const fullUserData = {
              ...user.value,
              ...userResponse.data,
            };
            user.value = fullUserData;
            localStorage.setItem("user", JSON.stringify(fullUserData));
          }
        } catch (userError) {
          console.warn(
            "Не удалось получить дополнительные данные пользователя:",
            userError
          );
          // Продолжаем с базовыми данными из токена
        }

        // Перенаправляем на дашборд
        router.push("/dashboard");
        return true;
      } else {
        throw new Error(
          response.message || "Ошибка входа: неверные данные ответа."
        );
      }
    } catch (e) {
      error.value = e.message || "Не удалось выполнить вход.";

      // Очищаем все данные аутентификации при ошибке
      accessToken.value = null;
      refreshToken.value = null;
      user.value = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");

      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Регистрирует нового пользователя
   */
  async function register(userData) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await authApi.register(
        userData.username,
        userData.email,
        userData.password,
        userData.firstName,
        userData.lastName
      );

      if (response.success && response.data.id) {
        // Показываем сообщение об успешной регистрации
        router.push("/login");
        return true;
      } else {
        throw new Error(
          response.message || "Ошибка регистрации: неверные данные ответа."
        );
      }
    } catch (e) {
      error.value = e.message || "Не удалось зарегистрироваться.";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Выполняет выход пользователя
   */
  async function logout() {
    isLoading.value = true;
    error.value = null;
    const currentRefreshToken = refreshToken.value;

    // Сначала очищаем локальные данные
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user");

    // Затем делаем редирект (еще до вызова API)
    router.push("/login");

    try {
      if (currentRefreshToken) {
        await authApi.logout(currentRefreshToken);
      }
    } catch (e) {
      console.error("Ошибка при вызове API выхода: ", e.message);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Пытается обновить токены с помощью refresh-токена
   */
  async function attemptRefreshToken() {
    isLoading.value = true;
    error.value = null;
    const currentRefreshToken = refreshToken.value;

    if (!currentRefreshToken) {
      error.value = "Нет refresh токена для обновления.";
      isLoading.value = false;
      await logout();
      return false;
    }

    try {
      const response = await authApi.refreshToken(currentRefreshToken);
      if (response.success && response.data.access_token) {
        accessToken.value = response.data.access_token;

        if (response.data.refresh_token) {
          refreshToken.value = response.data.refresh_token;
          localStorage.setItem("refreshToken", refreshToken.value);
        }

        localStorage.setItem("accessToken", accessToken.value);
        setUserFromToken(accessToken.value);
        isLoading.value = false;
        return true;
      } else {
        throw new Error(response.message || "Не удалось обновить токен.");
      }
    } catch (e) {
      error.value = e.message || "Ошибка при обновлении токена.";
      await logout();
      isLoading.value = false;
      return false;
    }
  }

  /**
   * Обновляет данные пользователя из API
   */
  async function refreshUserData() {
    if (!accessToken.value) return;

    try {
      const userResponse = await authApi.getCurrentUser(accessToken.value);
      if (userResponse.success && userResponse.data) {
        const fullUserData = {
          ...user.value,
          ...userResponse.data,
        };
        user.value = fullUserData;
        localStorage.setItem("user", JSON.stringify(fullUserData));
      }
    } catch (userError) {
      console.warn("Не удалось обновить данные пользователя:", userError);
    }
  }

  /**
   * Очищает сообщение об ошибке
   */
  function clearError() {
    error.value = null;
  }

  // Возвращаем публичное API хранилища
  return {
    // State
    accessToken,
    refreshToken,
    user,
    isLoading,
    error,

    // Getters
    isLoggedIn,
    authUser,
    getAccessToken,
    getRefreshToken,
    getError,
    getIsLoading,

    // Actions
    login,
    register,
    logout,
    clearError,
    attemptRefreshToken,
    setUserFromToken,
    refreshUserData,
  };
});
