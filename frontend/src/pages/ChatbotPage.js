import React, { useState, useRef, useEffect } from "react";
import "./ChatbotPage.css";

const API = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! I'm Drishyamitra's AI assistant 🤖\n\nTry asking:\n• \"Show all my photos\"\n• \"Show photos of Person 1\"\n• \"Show photos from yesterday\"",
      photos: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const sendMessage = async () => {
    const userText = input.trim();
    if (!userText || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: userText, photos: [] }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText }),
      });
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.reply || "I couldn't process that. Please try again.",
          photos: data.photos || [],
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "⚠️ Unable to connect to the AI service right now.",
          photos: [],
        },
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
      <h1 className="chatbot-title">🤖 AI Photo Assistant</h1>
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.role}`}>
            <p className="chat-text">{msg.text}</p>
            {msg.photos && msg.photos.length > 0 && (
              <div className="chat-photos">
                {msg.photos.map((photo) => (
                  <a
                    key={photo.id}
                    href={photo.url}
                    target="_blank"
                    rel="noreferrer"
                    className="chat-photo-link"
                  >
                    <img
                      src={photo.url}
                      alt={`Image ${photo.id}`}
                      className="chat-photo-thumb"
                      onError={(e) => { e.target.style.display = "none"; }}
                    />
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble assistant typing">
            <span className="dot" /><span className="dot" /><span className="dot" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Try "Show photos of Person 1" or "Show all photos"…'
          rows={2}
        />
        <button className="chat-send" onClick={sendMessage} disabled={loading}>
          {loading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
