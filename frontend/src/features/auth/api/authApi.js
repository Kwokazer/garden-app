// API клиент для аутентификации с реальными запросами к вашему бэкенду

const BASE_API_URL = "/api/v1"; // Общий базовый URL для API

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
    // Сохраняем статус и полные данные ошибки для возможной более детальной обработки
    return Promise.reject({
      success: false,
      message: message,
      status: response.status,
      errorData: data,
    });
  }
  // Успешный ответ, data содержит тело ответа от сервера
  return Promise.resolve({ success: true, data: data });
}

export const authApi = {
  async login(email, password) {
    const response = await fetch(`${BASE_API_URL}/auth/login`, {
      // Путь из auth.py
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // LoginRequest ожидает email и password
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(response); // Ожидаемый ответ: TokenResponse
  },

  async register(username, email, password, firstName, lastName) {
    const registrationData = {
      username,
      email,
      password,
    };
    if (firstName) registrationData.first_name = firstName;
    if (lastName) registrationData.last_name = lastName;

    const response = await fetch(`${BASE_API_URL}/auth/register`, {
      // Путь из auth.py
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // RegistrationRequest ожидает username, email, password и опционально first_name, last_name
      body: JSON.stringify(registrationData),
    });
    return handleResponse(response); // Ожидаемый ответ: RegistrationResponse
  },

  async logout(refreshToken) {
    if (!refreshToken) {
      // Если refresh токена нет, можно просто имитировать успешный выход
      // или вернуть ошибку, что пользователь не был залогинен для выхода.
      console.warn("Попытка выхода без refresh токена.");
      return Promise.resolve({
        success: true,
        data: { message: "Выход выполнен (локально)." },
      });
    }
    const response = await fetch(`${BASE_API_URL}/auth/logout`, {
      // Путь из auth.py
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Logout на бэкенде не требует Authorization заголовка, он инвалидирует переданный refresh_token
      },
      // Logout ожидает RefreshTokenRequest с refresh_token в теле
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    return handleResponse(response); // Ожидаемый ответ: SuccessResponse
  },

  async refreshToken(token) {
    const response = await fetch(`${BASE_API_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: token }),
    });
    return handleResponse(response); // Ожидаемый ответ: TokenResponse
  },
};
