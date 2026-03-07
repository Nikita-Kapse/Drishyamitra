import React, { useState } from "react";
import "./ChatbotPage.css";

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! I'm Drishyamitra's AI assistant. Ask me anything about your photos! 🤖" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const userText = input.trim();
    if (!userText) return;

    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setInput("");
    setLoading(true);

    try {
      // Placeholder: replace with actual Groq API call when backend endpoint is ready
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || "http://localhost:5000/api"}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: userText }),
        }
      );
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.reply || "I couldn't process that. Please try again." },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "⚠️ Unable to connect to the AI service right now." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chatbot-page">
      <h1 className="chatbot-title">🤖 AI Chatbot</h1>
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="chat-bubble assistant typing">Thinking…</div>}
      </div>
      <div className="chat-input-row">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message…"
          rows={2}
        />
        <button className="chat-send" onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
