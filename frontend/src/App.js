import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [userName, setUserName] = useState("");
  const [userCreated, setUserCreated] = useState(false);
  const [userInput, setUserInput] = useState("");

  useEffect(() => {
    // Check API health on mount
    axios
      .get(`${API_URL}/health`)
      .then(() => setApiStatus("connected"))
      .catch(() => setApiStatus("disconnected"));
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/users`, {
        name: userInput,
      });
      setUserName(response.data.name || userInput);
      setUserCreated(true);
    } catch (error) {
      console.error("Error creating user:", error);
      alert("Failed to create user. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = { role: "user", content: message };
    setMessages((prev) => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: message,
        model: "gemini-2.5-flash-lite",
      });

      const aiMessage = { role: "assistant", content: response.data.response };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        role: "error",
        content: "Failed to get response from API",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // Show user creation form if user hasn't been created yet
  if (!userCreated) {
    return (
      <div className="App">
        <div className="container">
          <header className="header">
            <h1>🤖 AI Hackathon Chat</h1>
            <div className={`status status-${apiStatus}`}>API: {apiStatus}</div>
          </header>

          <div className="chat-container">
            <div className="welcome">
              <h2>Welcome! 👋</h2>
              <p>Please enter your name to get started</p>
              <form onSubmit={handleCreateUser} className="input-form">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  placeholder="Enter your name..."
                  disabled={loading}
                  className="input"
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={loading || !userInput.trim()}
                  className="button"
                >
                  {loading ? "Creating..." : "Create User"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🤖 AI Hackathon Chat</h1>
          <div className={`status status-${apiStatus}`}>API: {apiStatus}</div>
          {userName && <p className="user-name">Logged in as: {userName}</p>}
        </header>

        <div className="chat-container">
          <div className="messages">
            {messages.length === 0 ? (
              <div className="welcome">
                <h2>Welcome to the AI Hackathon! 🚀</h2>
                <p>Start chatting to test the API connection</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))
            )}
            {loading && (
              <div className="message assistant">
                <div className="message-content loading">Thinking...</div>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="input-form">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={loading}
              className="input"
            />
            <button
              type="submit"
              disabled={loading || !message.trim()}
              className="button"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
