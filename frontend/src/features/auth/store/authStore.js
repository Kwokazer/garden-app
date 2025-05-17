import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "../api/authApi.js";
import { useRouter } from "vue-router";

// Функция для декодирования JWT (простая, без проверки подписи)
function parseJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
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
    console.error("Error decoding JWT: ", e);
    return null;
  }
}

export const useAuthStore = defineStore("authStore", () => {
  // Примечание: useRouter() здесь будет работать корректно, если Pinia
  // и Vue Router правильно инициализированы в main.js (Pinia store создается
  // в контексте, где router уже доступен).
  const router = useRouter();

  // State
  const accessToken = ref(localStorage.getItem("accessToken") || null);
  const refreshToken = ref(localStorage.getItem("refreshToken") || null);
  const user = ref(JSON.parse(localStorage.getItem("user")) || null);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const isLoggedIn = computed(() => !!accessToken.value);
  const authUser = computed(() => user.value);
  const getAccessToken = computed(() => accessToken.value);
  const getRefreshToken = computed(() => refreshToken.value);
  const getError = computed(() => error.value);
  const getIsLoading = computed(() => isLoading.value);

  // Actions
  function setUserFromToken(token) {
    if (!token) {
      user.value = null;
      localStorage.removeItem("user");
      return;
    }
    const decodedToken = parseJwt(token);
    if (decodedToken && decodedToken.sub) {
      // TokenResponse от бэкенда не содержит user object, только токены.
      // Мы можем извлечь user_id (sub) и, возможно, роли из токена.
      // Для полного объекта user потребуется отдельный запрос /users/me (предположительно)
      user.value = {
        id: decodedToken.sub,
        roles: decodedToken.roles || [],
        // Другие поля (email, username) нужно будет загружать отдельно
      };
      localStorage.setItem("user", JSON.stringify(user.value));
    } else {
      user.value = null;
      localStorage.removeItem("user");
    }
  }
  // Инициализация user из токена при загрузке store
  if (accessToken.value) {
    setUserFromToken(accessToken.value);
  }

  async function login(credentials) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await authApi.login(
        credentials.email,
        credentials.password
      );
      // Ожидаемый ответ от API (TokenResponse): { access_token, refresh_token, token_type, expires_in }
      if (response.success && response.data.access_token) {
        accessToken.value = response.data.access_token;
        refreshToken.value = response.data.refresh_token;

        localStorage.setItem("accessToken", accessToken.value);
        localStorage.setItem("refreshToken", refreshToken.value);

        setUserFromToken(accessToken.value);

        router.push("/dashboard");
      } else {
        // Это условие может быть избыточным, если handleResponse уже выбросил ошибку
        throw new Error(
          response.message || "Ошибка входа: неверные данные ответа."
        );
      }
    } catch (e) {
      error.value = e.message || "Не удалось выполнить вход.";
      accessToken.value = null;
      refreshToken.value = null;
      user.value = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");
      localStorage.removeItem("user");
    } finally {
      isLoading.value = false;
    }
  }

  async function register(userData) {
    isLoading.value = true;
    error.value = null;
    try {
      // Передаем все данные, включая опциональные first_name, last_name, если они есть в userData
      const response = await authApi.register(
        userData.username,
        userData.email,
        userData.password,
        userData.first_name,
        userData.last_name
      );
      // Ожидаемый ответ (RegistrationResponse): { id, email, username, is_verified, message }
      if (response.success && response.data.id) {
        alert(
          response.data.message || "Регистрация успешна! Пожалуйста, войдите."
        );
        router.push("/login");
      } else {
        throw new Error(
          response.message || "Ошибка регистрации: неверные данные ответа."
        );
      }
    } catch (e) {
      error.value = e.message || "Не удалось зарегистрироваться.";
    } finally {
      isLoading.value = false;
    }
  }

  async function logout() {
    isLoading.value = true;
    error.value = null;
    const currentRefreshToken = refreshToken.value;

    // Сначала очищаем локальные данные, чтобы пользователь сразу считался вышедшим
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("user");
    router.push("/login"); // Перенаправляем немедленно

    try {
      if (currentRefreshToken) {
        await authApi.logout(currentRefreshToken); // Вызов API для инвалидации refresh токена на бэкенде
      }
    } catch (e) {
      // Ошибка на бэкенде при выходе не критична для пользователя, т.к. локально он уже вышел
      console.error("Ошибка при вызове API выхода на бэкенде: ", e.message);
      // Можно сохранить эту ошибку в отдельное состояние, если нужно её где-то показать
    } finally {
      isLoading.value = false; // Завершаем загрузку после API вызова
    }
  }

  async function attemptRefreshToken() {
    isLoading.value = true;
    error.value = null;
    const currentRefreshToken = refreshToken.value;
    if (!currentRefreshToken) {
      error.value = "Нет refresh токена для обновления.";
      isLoading.value = false;
      await logout(); // Если нет refresh токена, разлогиниваем пользователя
      return false;
    }

    try {
      const response = await authApi.refreshToken(currentRefreshToken);
      if (response.success && response.data.access_token) {
        accessToken.value = response.data.access_token;
        // Бэкенд может вернуть новый refresh_token, а может и нет.
        // Если возвращает, обновляем:
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
      // Если обновление токена не удалось (например, refresh токен истек или невалиден),
      // нужно разлогинить пользователя.
      await logout();
      isLoading.value = false;
      return false;
    }
  }

  function clearError() {
    error.value = null;
  }

  return {
    accessToken,
    refreshToken,
    user,
    isLoading,
    error,
    isLoggedIn,
    authUser,
    getAccessToken,
    getRefreshToken,
    getError,
    getIsLoading,
    login,
    register,
    logout,
    clearError,
    attemptRefreshToken,
    setUserFromToken,
  };
});
