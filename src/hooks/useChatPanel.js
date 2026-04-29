import { useState, useCallback } from "react";
import APIService from "../services/apiService";

/**
 * Custom hook for managing chat state and operations
 * @returns {object} - Chat state and handlers
 */
export const useChatPanel = (formData, onFormUpdate) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingText, setThinkingText] = useState("");
  const [error, setError] = useState(null);

  /**
   * Format AI response for display
   */
  const formatAIResponse = useCallback((data) => {
    if (!data || typeof data !== "object") {
      return String(data);
    }

    const parts = [];

    // 🎯 Check if this is a HISTORY response
    if (data.total_interactions !== undefined && data.history) {
      if (data.total_interactions === 0) {
        parts.push(`📋 **History:** ${data.message || "No interaction history found"}`);
      } else {
        parts.push(`📋 **Interaction History for ${data.hcp_name}**`);
        parts.push(`Total Interactions: ${data.total_interactions}`);
        parts.push("━━━━━━━━━━━━━━━━━━━━━━━━━━");
        
        // Display formatted history if available
        if (data.formatted_display) {
          parts.push(data.formatted_display);
        } else {
          // Fallback: build from history array
          data.history.forEach((interaction, idx) => {
            parts.push(`\n📅 Interaction #${idx + 1}`);
            parts.push(`📍 Date: ${interaction.date} | Time: ${interaction.time_recorded}`);
            parts.push(`🔄 Type: ${interaction.type.toUpperCase()}`);
            parts.push(`💬 Summary: ${interaction.summary}`);
            if (interaction.products && interaction.products.length > 0) {
              parts.push(`💊 Products: ${interaction.products.join(", ")}`);
            }
            parts.push(`😊 Sentiment: ${interaction.sentiment.toUpperCase()}`);
            if (interaction.feedback) {
              parts.push(`📝 Feedback: ${interaction.feedback}`);
            }
          });
        }
      }
      return parts.join("\n");
    }

    if (data.follow_up_action) {
      parts.push(`📋 **Follow-up:** ${data.follow_up_action}`);
    }
    if (data.discussion_summary) {
      parts.push(`📝 **Summary:** ${data.discussion_summary}`);
    }
    if (data.hcp_name) {
      parts.push(`👤 **HCP:** ${data.hcp_name}`);
    }
    if (data.sentiment) {
      const sentimentEmoji = {
        positive: "😊",
        neutral: "😐",
        negative: "😟",
      }[data.sentiment] || "📌";
      parts.push(`${sentimentEmoji} **Sentiment:** ${data.sentiment}`);
    }

    return parts.length > 0
      ? parts.join("\n")
      : "✅ Data updated successfully!";
  }, []);

  /**
   * Send message to AI assistant
   */
  const sendMessage = useCallback(
    async (messageText) => {
      if (!messageText.trim()) return;

      // Add user message
      const userMessage = {
        id: Date.now(),
        type: "user",
        content: messageText,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setError(null);

      try {
        setIsLoading(true);
        setIsThinking(true);
        setThinkingText("AI is analyzing your request...");

        // Call API
        const result = await APIService.sendChatMessage(messageText, formData);

        if (!result.success) {
          throw new Error(result.message || "Unknown error occurred");
        }

        // Simulate thinking phase
        await new Promise((resolve) => setTimeout(resolve, 1500));

        // Update form data
        if (onFormUpdate) {
          onFormUpdate(result.data);
        }

        // Add AI message
        const aiMessage = {
          id: Date.now() + 1,
          type: "ai",
          content: formatAIResponse(result.data),
          rawData: result.data,
          thinkingTime: result.thinkingTime,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      } catch (err) {
        console.error("Chat error:", err);
        setError(err.message);

        const errorMessage = {
          id: Date.now() + 1,
          type: "error",
          content: err.message || "Failed to get AI response. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
        setIsThinking(false);
        setThinkingText("");
      }
    },
    [formData, onFormUpdate, formatAIResponse]
  );

  /**
   * Clear chat history
   */
  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  /**
   * Delete a specific message
   */
  const deleteMessage = useCallback((messageId) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
  }, []);

  return {
    messages,
    input,
    setInput,
    isLoading,
    isThinking,
    thinkingText,
    error,
    sendMessage,
    clearChat,
    deleteMessage,
  };
};
