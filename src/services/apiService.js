/**
 * API Service for AI CRM Assistant
 * Handles all backend communication with proper error handling and timeouts
 */

const API_BASE_URL = "http://127.0.0.1:8000";
const REQUEST_TIMEOUT = 30000; // 30 seconds

class APIService {
  /**
   * Send chat request to AI assistant
   * @param {string} text - User input text
   * @param {object} currentData - Current form data context
   * @returns {Promise<object>} - Response with AI analysis and thinking time
   */
  static async sendChatMessage(text, currentData = {}) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

      const response = await fetch(`${API_BASE_URL}/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          current_data: currentData,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        data: data.response,
        thinkingTime: data.thinking_time,
        message: data.message,
      };
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error("Request timeout - AI is taking too long to respond");
      }
      throw new Error(`Failed to communicate with AI: ${error.message}`);
    }
  }

  /**
   * Check API health
   * @returns {Promise<object>} - Health status
   */
  static async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("API health check failed");
      }

      return await response.json();
    } catch (error) {
      throw new Error(`API is unavailable: ${error.message}`);
    }
  }
}

export default APIService;
