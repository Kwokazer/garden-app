// src/features/webinars/api/webinarsApi.js

const BASE_API_URL = "/api/v1";

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
 * Получает заголовки с авторизацией
 */
function getAuthHeaders() {
  const token = localStorage.getItem("accessToken");
  const headers = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return headers;
}

/**
 * API client for working with webinars
 */
export const webinarsApi = {
  /**
   * Get list of webinars with pagination and filtering
   * @param {number} page - Page number (starting from 1)
   * @param {number} per_page - Number of webinars per page
   * @param {Object} filters - Filter object
   * @returns {Promise<Object>} - Server response with webinars
   */
  async getWebinars(page = 1, per_page = 20, filters = {}) {
    try {
      // Ensure page and per_page are valid integers
      const validPage = parseInt(page) || 1;
      const validPerPage = parseInt(per_page) || 20;

      const params = new URLSearchParams();
      params.append("page", validPage);
      params.append("per_page", validPerPage);

      // Добавляем фильтры в запрос
      if (filters.title) {
        params.append("title", filters.title);
      }

      if (filters.host_id) {
        params.append("host_id", filters.host_id);
      }

      if (filters.status) {
        params.append("status", filters.status);
      }

      if (filters.is_public !== undefined && filters.is_public !== null) {
        params.append("is_public", Boolean(filters.is_public));
      }

      if (filters.plant_topic_id) {
        params.append("plant_topic_id", filters.plant_topic_id);
      }

      if (filters.date_from) {
        params.append("date_from", filters.date_from);
      }

      if (filters.date_to) {
        params.append("date_to", filters.date_to);
      }

      const url = `${BASE_API_URL}/webinars/?${params.toString()}`;
      console.log("Fetching URL:", url);

      const response = await fetch(url, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error("Error fetching webinars list:", error);
      throw error;
    }
  },

  /**
   * Get detailed webinar information by ID
   * @param {string|number} id - Webinar ID
   * @returns {Promise<Object>} - Server response with detailed webinar information
   */
  async getWebinarById(id) {
    try {
      const url = `${BASE_API_URL}/webinars/${id}`;
      console.log("Fetching URL:", url);

      const response = await fetch(url, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error fetching webinar with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create new webinar (requires admin or plant_expert authorization)
   * @param {Object} webinarData - Webinar data
   * @returns {Promise<Object>} - Server response with created webinar
   */
  async createWebinar(webinarData) {
    try {
      const url = `${BASE_API_URL}/webinars/`;
      console.log("Creating webinar:", webinarData);

      const response = await fetch(url, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(webinarData),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error("Error creating webinar:", error);
      throw error;
    }
  },

  /**
   * Update webinar (requires host or admin authorization)
   * @param {string|number} id - Webinar ID
   * @param {Object} webinarData - New webinar data
   * @returns {Promise<Object>} - Server response with updated webinar
   */
  async updateWebinar(id, webinarData) {
    try {
      const url = `${BASE_API_URL}/webinars/${id}`;
      console.log("Updating webinar:", id, webinarData);

      const response = await fetch(url, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(webinarData),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error updating webinar with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete webinar (requires host or admin authorization)
   * @param {string|number} id - Webinar ID
   * @returns {Promise<Object>} - Server response
   */
  async deleteWebinar(id) {
    try {
      const url = `${BASE_API_URL}/webinars/${id}`;
      console.log("Deleting webinar:", id);

      const response = await fetch(url, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error deleting webinar with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Join webinar and get connection data
   * @param {string|number} id - Webinar ID
   * @returns {Promise<Object>} - Server response with Jitsi connection data
   */
  async joinWebinar(id) {
    try {
      const url = `${BASE_API_URL}/webinars/${id}/join`;
      console.log("Joining webinar:", id);

      const response = await fetch(url, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error joining webinar with ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get JWT token for Jitsi Meet
   * @param {string|number} id - Webinar ID
   * @returns {Promise<Object>} - Server response with JWT token
   */
  async getJitsiToken(id) {
    try {
      const url = `${BASE_API_URL}/webinars/${id}/jitsi-token`;
      console.log("Getting Jitsi token for webinar:", id);

      const response = await fetch(url, {
        method: "POST",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error(`Error getting Jitsi token for webinar ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get webinars hosted by current user
   * @param {number} page - Page number
   * @param {number} per_page - Number of webinars per page
   * @returns {Promise<Object>} - Server response with hosted webinars
   */
  async getMyHostedWebinars(page = 1, per_page = 20) {
    try {
      // Ensure page and per_page are valid integers
      const validPage = parseInt(page) || 1;
      const validPerPage = parseInt(per_page) || 20;

      const params = new URLSearchParams();
      params.append("page", validPage);
      params.append("per_page", validPerPage);

      const url = `${BASE_API_URL}/webinars/my/hosted?${params.toString()}`;
      console.log("Fetching my hosted webinars:", url);

      const response = await fetch(url, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error("Error fetching my hosted webinars:", error);
      throw error;
    }
  },

  /**
   * Get webinars where current user is participating
   * @param {number} page - Page number
   * @param {number} per_page - Number of webinars per page
   * @returns {Promise<Object>} - Server response with participating webinars
   */
  async getMyParticipatingWebinars(page = 1, per_page = 20) {
    try {
      // Ensure page and per_page are valid integers
      const validPage = parseInt(page) || 1;
      const validPerPage = parseInt(per_page) || 20;

      const params = new URLSearchParams();
      params.append("page", validPage);
      params.append("per_page", validPerPage);

      const url = `${BASE_API_URL}/webinars/my/participating?${params.toString()}`;
      console.log("Fetching my participating webinars:", url);

      const response = await fetch(url, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      const result = await handleResponse(response);
      return result.data;
    } catch (error) {
      console.error("Error fetching my participating webinars:", error);
      throw error;
    }
  },
};
