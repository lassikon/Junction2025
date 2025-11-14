import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MockHome.css';

function MockHome() {

  const navigate = useNavigate();

  return (
    <div className="mock-home">
      <div className="home-container">
        <header className="home-header">
          <h1>🏦 Junction Finance</h1>
          <p className="subtitle">AI-Powered Financial Assistant</p>
          <p>Valle on paras</p>
        </header>

        <section className="features">
          <div className="feature-card">
            <h3>💬 Chat with AI</h3>
            <p>Get instant financial advice and insights</p>
          </div>
          <div className="feature-card">
            <h3>📊 Analytics</h3>
            <p>Track and analyze your financial data</p>
          </div>
          <div className="feature-card">
            <h3>🔒 Secure</h3>
            <p>Your data is encrypted and protected</p>
          </div>
        </section>

        <div className="cta-buttons">
          <button className="btn btn-primary"
            onClick={() => navigate('/chat')}
            >
            Start Chatting
          </button>
          <button className="btn btn-secondary">Learn More</button>
        </div>
      </div>
    </div>
  );
}

export default MockHome;