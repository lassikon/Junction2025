import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_URL } from '../config/api';
import '../styles/FloatingChatbot.css';

/**
 * FloatingChatbot - A floating money mentor chatbot
 * 
 * Features:
 * - Toggle open/close button
 * - Game-aware financial advice
 * - Access to current game state and narrative
 * - Clean, modern UI with typewriter effect
 */
const FloatingChatbot = ({ sessionId, isOpen, onToggle, currentNarrative, currentOptions }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('connected');
  const [typingText, setTypingText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const typingIntervalRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive or while typing
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-scroll while typing
  useEffect(() => {
    if (isTyping) {
      scrollToBottom();
    }
  }, [typingText, isTyping]);

  // Check API status on mount
  useEffect(() => {
    axios.get(`${API_URL}/health`)
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('disconnected'));
  }, []);

  // Cleanup typing interval on unmount
  useEffect(() => {
    return () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    };
  }, []);

  // Close on Escape key when open
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onToggle();
      }
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isOpen, onToggle]);

  // Typewriter effect function
  const typewriterEffect = (text, callback) => {
    setIsTyping(true);
    setTypingText('');
    let index = 0;
    
    typingIntervalRef.current = setInterval(() => {
      if (index < text.length) {
        setTypingText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(typingIntervalRef.current);
        setIsTyping(false);
        callback();
      }
    }, 20); // 20ms per character for smooth typing
  };

  // Add welcome message when first opened
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      const hasDecision = currentNarrative && currentOptions && currentOptions.length > 0;
      const welcomeMessage = hasDecision 
        ? "Hi! I'm your Money Mentor. I can see your current situation and the options you're considering. Ask me anything about:\n\n💭 Which option might be best for you\n📊 Financial impacts of each choice\n🎯 Long-term strategy advice\n💡 Understanding the concepts\n\nHow can I help with this decision?"
        : "Hi! I'm your Money Mentor. I can see your current financial situation and help you with:\n\n💰 Investment strategies\n📊 Savings advice\n🎯 Financial independence planning\n💡 Understanding financial concepts\n\nWhat would you like to know?";
      
      typewriterEffect(welcomeMessage, () => {
        setMessages([{
          role: 'assistant',
          content: welcomeMessage
        }]);
      });
    }
  }, [isOpen, currentNarrative, currentOptions]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || loading || isTyping) return;

    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setLoading(true);

    try {
      // Build context-aware message with current narrative/options if available
      let contextualMessage = message;
      if (currentNarrative && currentOptions && currentOptions.length > 0) {
        const optionsText = currentOptions.map((opt, idx) => 
          `${idx + 1}. ${typeof opt === 'string' ? opt : opt.text}`
        ).join('\n');
        
        contextualMessage = `CURRENT SITUATION:\n${currentNarrative}\n\nAVAILABLE OPTIONS:\n${optionsText}\n\nMY QUESTION:\n${message}`;
      }

      const response = await axios.post(`${API_URL}/api/chat`, {
        session_id: sessionId,
        message: contextualMessage,
        model: 'gemini-2.0-flash-exp'
      });

      setLoading(false);
      const aiResponseText = response.data.response;
      
      // Use typewriter effect for AI response
      typewriterEffect(aiResponseText, () => {
        const aiMessage = { 
          role: 'assistant', 
          content: aiResponseText 
        };
        setMessages(prev => [...prev, aiMessage]);
      });
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = { 
        role: 'error', 
        content: error.response?.data?.detail || 'Failed to get response. Please try again.' 
      };
      setMessages(prev => [...prev, errorMessage]);
      setApiStatus('error');
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <>
      {/* Toggle Button - Always visible */}
      <button 
        className={`chatbot-toggle-btn ${isOpen ? 'open' : ''}`}
        onClick={onToggle}
        aria-label="Toggle money mentor"
      >
        {isOpen ? '✕' : '💬'}
        {!isOpen && <span className="chatbot-label">Money Mentor</span>}
      </button>

      {/* Chatbot Window - Shows when open */}
      {isOpen && (
        <>
          {/* Fullscreen overlay to capture outside clicks and close the chat */}
          <div className="chatbot-overlay" onClick={onToggle} />

          <div className="chatbot-container" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-content">
              <h3>💰 Money Mentor</h3>
              <div className={`chatbot-status status-${apiStatus}`}>
                {apiStatus === 'connected' ? '● Online' : '● Offline'}
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="chatbot-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chatbot-message ${msg.role}`}>
                <div className="chatbot-message-content">
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chatbot-message assistant">
                <div className="chatbot-message-content loading">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  Thinking...
                </div>
              </div>
            )}
            {isTyping && typingText && (
              <div className="chatbot-message assistant">
                <div className="chatbot-message-content typing-effect">
                  {typingText}
                  <span className="typing-cursor">|</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="chatbot-input-form">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                currentNarrative && currentOptions?.length > 0
                  ? "Ask about these options or your situation..."
                  : "Ask about investments, savings, FI strategies..."
              }
              disabled={loading || isTyping}
              className="chatbot-input"
              rows="1"
            />
            <button 
              type="submit" 
              disabled={loading || isTyping || !message.trim()} 
              className="chatbot-send-btn"
              aria-label="Send message"
            >
              {loading || isTyping ? '⏳' : '📤'}
            </button>
          </form>
        </div>
        </>
      )}
    </>
  );
};

export default FloatingChatbot;

