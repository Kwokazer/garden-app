// Имитация API клиента для аутентификации

// Имитация задержки сети
const networkDelay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const authApi = {
  async login(email, password) {
    await networkDelay(1000); // Имитация задержки ответа сервера

    // TODO: Заменить на реальный вызов API к бэкенду
    if (email === "test@example.com" && password === "password") {
      return Promise.resolve({
        success: true,
        data: {
          accessToken: "fake-jwt-token-string",
          user: {
            id: "1",
            email: "test@example.com",
            username: "TestUser",
          },
        },
        message: "Вход выполнен успешно.",
      });
    } else {
      return Promise.reject({
        success: false,
        message: "Неверный email или пароль.",
      });
    }
  },

  async register(username, email, password) {
    await networkDelay(1500); // Имитация задержки ответа сервера

    // TODO: Заменить на реальный вызов API к бэкенду
    console.log("API register call with:", { username, email, password });
    // Простая имитация: любой новый email считается успешной регистрацией
    // В реальном приложении здесь будет проверка на существующий email и другие валидации
    if (email === "existing@example.com") {
      return Promise.reject({
        success: false,
        message: "Пользователь с таким email уже существует.",
      });
    }

    return Promise.resolve({
      success: true,
      data: {
        user: {
          id: String(Math.random().toString(36).substr(2, 9)), // случайный ID
          username,
          email,
        },
        message: "Регистрация прошла успешно. Пожалуйста, войдите.",
      },
    });
  },

  async logout() {
    await networkDelay(500);
    // TODO: В реальном приложении здесь может быть вызов на бэкенд для инвалидации токена
    return Promise.resolve({
      success: true,
      message: "Выход выполнен успешно.",
    });
  },
};
