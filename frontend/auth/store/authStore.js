import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authApi } from "../api/authApi.js";
import { useRouter } from "vue-router";

export const useAuthStore = defineStore("authStore", () => {
  const router = useRouter();

  // State
  const accessToken = ref(localStorage.getItem("accessToken") || null);
  const user = ref(JSON.parse(localStorage.getItem("user")) || null);
  const isLoading = ref(false);
  const error = ref(null);

  // Getters
  const isLoggedIn = computed(() => !!accessToken.value && !!user.value);
  const authUser = computed(() => user.value);
  const getToken = computed(() => accessToken.value);
  const getError = computed(() => error.value);
  const getIsLoading = computed(() => isLoading.value);

  // Actions
  async function login(credentials) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await authApi.login(
        credentials.email,
        credentials.password
      );
      if (response.success && response.data) {
        accessToken.value = response.data.accessToken;
        user.value = response.data.user;
        localStorage.setItem("accessToken", accessToken.value);
        localStorage.setItem("user", JSON.stringify(user.value));
        router.push("/dashboard");
      } else {
        throw new Error(response.message || "Ошибка входа.");
      }
    } catch (e) {
      error.value = e.message || "Не удалось выполнить вход.";
      localStorage.removeItem("accessToken");
      localStorage.removeItem("user");
      accessToken.value = null;
      user.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  async function register(userData) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await authApi.register(
        userData.username,
        userData.email,
        userData.password
      );
      if (response.success) {
        // Можно сразу логинить пользователя или перенаправлять на страницу входа
        // Пока просто выведем сообщение и перенаправим на логин
        alert(response.data.message || "Регистрация успешна!");
        router.push("/login");
      } else {
        throw new Error(response.message || "Ошибка регистрации.");
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
    try {
      await authApi.logout(); // Вызов API для логаута (даже если он только локальный)
    } catch (e) {
      console.error("Ошибка при вызове API выхода: ", e.message);
      // Продолжаем локальный логаут даже если API вызова не удалось
    } finally {
      accessToken.value = null;
      user.value = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("user");
      isLoading.value = false;
      router.push("/login");
    }
  }

  function clearError() {
    error.value = null;
  }

  return {
    accessToken,
    user,
    isLoading,
    error,
    isLoggedIn,
    authUser,
    getToken,
    getError,
    getIsLoading,
    login,
    register,
    logout,
    clearError,
  };
});
