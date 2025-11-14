import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Chat.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    axios.get(`${API_URL}/health`)
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('disconnected'));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message: message,
        model: 'gpt-3.5-turbo'
      });

      const aiMessage = { role: 'assistant', content: response.data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        role: 'error', 
        content: 'Failed to get response from API' 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🤖 AI Hackathon Chat</h1>
          <div className={`status status-${apiStatus}`}>
            API: {apiStatus}
          </div>
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
            <button type="submit" disabled={loading || !message.trim()} className="button">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Chat;