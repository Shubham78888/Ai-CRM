import { useDispatch, useSelector } from "react-redux";
import { setFormData } from "../redux/formSlice";
import { useState, useRef, useEffect } from "react";
import APIService from "../services/apiService";

const ChatPanel = () => {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [thinkingText, setThinkingText] = useState("");
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const dispatch = useDispatch();

  // 🔥 get full form state
  const formData = useSelector((state) => state.form);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      type: "user",
      content: input,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    const sentInput = input; // Store for API call
    setInput("");

    try {
      setIsLoading(true);
      setIsThinking(true);
      setThinkingText("AI is analyzing your request...");

      // Call API service
      const result = await APIService.sendChatMessage(sentInput, formData);

      if (!result.success) {
        throw new Error(result.message || "Unknown error");
      }

      // Simulate thinking phase
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Update form data with AI response - normalize sentiment to lowercase
      const normalizedData = {
        ...result.data,
        sentiment: result.data.sentiment ? result.data.sentiment.toLowerCase() : ""
      };
      dispatch(setFormData(normalizedData));

      // Add AI message to chat
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
  };

  const formatAIResponse = (data) => {
    if (!data || typeof data !== "object") {
      return String(data);
    }

    const parts = [];
    
    // Normalize sentiment to lowercase for comparison
    const sentiment = data.sentiment ? data.sentiment.toLowerCase() : null;
    
    // SENTIMENT - Display prominently at the top
    if (sentiment) {
      const sentimentEmoji = {
        positive: "😊",
        neutral: "😐",
        negative: "😟",
      }[sentiment] || "📌";
      const sentimentLabel = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
      parts.push(`${sentimentEmoji} **SENTIMENT: ${sentimentLabel}**`);
    }
    
    if (data.hcp_name) {
      parts.push(`👤 **Doctor:** ${data.hcp_name}`);
    }
    
    if (data.discussion_summary) {
      parts.push(`📝 **Summary:** ${data.discussion_summary}`);
    }
    
    if (data.follow_up_action) {
      parts.push(`📋 **Follow-up:** ${data.follow_up_action}`);
    }
    
    if (data.products_discussed && Array.isArray(data.products_discussed) && data.products_discussed.length > 0) {
      parts.push(`💊 **Products:** ${data.products_discussed.join(", ")}`);
    }
    
    if (data.key_points && Array.isArray(data.key_points) && data.key_points.length > 0) {
      parts.push(`⭐ **Key Points:** ${data.key_points.slice(0, 2).join(", ")}`);
    }

    if (data.action_items && Array.isArray(data.action_items) && data.action_items.length > 0) {
      parts.push(`✓ **Actions:** ${data.action_items.slice(0, 2).join(", ")}`);
    }

    return parts.length > 0
      ? parts.join("\n")
      : "✅ Data updated successfully!";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      handleSend();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-lg shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-4 shadow-md">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold text-white">🤖 AI CRM Assistant</h2>
            <p className="text-blue-100 text-sm">Real-time interaction analysis & suggestions</p>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-blue-100 hover:text-white text-xs px-2 py-1 rounded hover:bg-blue-700 transition"
              title="Clear conversation"
            >
              🗑️ Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && !isThinking && (
          <div className="flex items-center justify-center h-full text-gray-400">
            <div className="text-center">
              <p className="text-lg font-semibold mb-2">👋 Welcome to AI Assistant</p>
              <p className="text-sm">Log interactions and I'll help analyze them</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs lg:max-w-md ${
                msg.type === "user"
                  ? "bg-blue-600 text-white rounded-br-none px-4 py-3 rounded-lg shadow-md"
                  : msg.type === "error"
                  ? "bg-red-600 text-white rounded-bl-none px-4 py-3 rounded-lg shadow-md"
                  : "bg-slate-700 text-gray-100 rounded-bl-none border border-cyan-500 p-3 rounded-lg shadow-md"
              }`}
            >
              {/* Show sentiment badge for AI responses */}
              {msg.type === "ai" && msg.rawData?.sentiment && (
                <div className="mb-3">
                  {(() => {
                    const sentiment = msg.rawData.sentiment.toLowerCase();
                    const sentimentEmoji = {
                      positive: "😊",
                      neutral: "😐",
                      negative: "😟",
                    }[sentiment] || "📌";
                    const sentimentColor = {
                      positive: "bg-green-600 text-white",
                      neutral: "bg-yellow-600 text-white",
                      negative: "bg-red-600 text-white",
                    }[sentiment] || "bg-gray-600 text-white";
                    const sentimentLabel = sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
                    
                    return (
                      <div className={`inline-block ${sentimentColor} px-3 py-1 rounded-full text-sm font-bold`}>
                        {sentimentEmoji} {sentimentLabel}
                      </div>
                    );
                  })()}
                </div>
              )}
              
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              <div className="flex justify-between items-center mt-2">
                <p className="text-xs opacity-70">
                  {msg.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
                {msg.type === "ai" && msg.thinkingTime && (
                  <p className="text-xs opacity-70">⏱️ {msg.thinkingTime.toFixed(2)}s</p>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* AI Thinking Indicator */}
        {isThinking && (
          <div className="flex justify-start">
            <div className="bg-slate-700 border border-cyan-500 text-gray-100 px-4 py-3 rounded-lg rounded-bl-none shadow-md">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-lg">✨</span>
                <span className="text-sm font-semibold">AI is thinking...</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" style={{ animationDelay: "0.4s" }}></div>
              </div>
              <p className="text-xs mt-2 text-cyan-300">{thinkingText}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-slate-800 p-4 border-t border-slate-700 space-y-3">
        <textarea
          className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 resize-none"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe the interaction (Ctrl+Enter to send)..."
          rows="3"
          disabled={isLoading}
        />

        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold px-4 py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <span className="animate-spin">⏳</span>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <span>📤</span>
              <span>Send Message</span>
            </>
          )}
        </button>

        <p className="text-xs text-gray-400 text-center">
          💡 Tip: Describe interactions to get AI suggestions and auto-fill form fields
        </p>
      </div>
    </div>
  );
};

export default ChatPanel;
