import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm';
import LoginForm from '../components/LoginForm';
import './LandingPage.css';

function LandingPage() {
  const [mode, setMode] = useState('welcome'); // 'welcome', 'login', 'register'
  const navigate = useNavigate();

  const handlePlayAsGuest = () => {
    // Navigate directly to onboarding in test mode
    navigate('/onboarding?mode=guest');
  };

  if (mode === 'register') {
    return (
      <RegisterForm
        onSuccess={() => navigate('/onboarding')}
        onBack={() => setMode('welcome')}
      />
    );
  }

  if (mode === 'login') {
    return (
      <LoginForm
        onSuccess={(hasOnboarding) => {
          // If they've onboarded before, go to start game page
          // If first time, go to onboarding
          if (hasOnboarding) {
            navigate('/start-game');
          } else {
            navigate('/onboarding');
          }
        }}
        onBack={() => setMode('welcome')}
      />
    );
  }

  return (
    <div className="landing-page">
      <div 
        className="landing-background"
        style={{ backgroundImage: 'url(/images/backgrounds/sunny_background.png)' }}
      />
      
      <div className="landing-container">
        <div className="landing-card">
          <h1 className="landing-title">LifeSim</h1>
          <h2 className="landing-subtitle">Financial Independence Quest</h2>
          <p className="landing-description">
            Make life decisions, manage your finances, and achieve financial independence!
          </p>

          <div className="landing-options">
            <button
              className="btn btn-primary btn-large"
              onClick={() => setMode('login')}
            >
              🔐 Login
            </button>

            <button
              className="btn btn-secondary btn-large"
              onClick={() => setMode('register')}
            >
              ✨ Create Account
            </button>

            <div className="divider">
              <span>or</span>
            </div>

            <button
              className="btn btn-outline btn-large"
              onClick={handlePlayAsGuest}
            >
              👤 Play as Guest (Test Mode)
            </button>
            
            <p className="guest-note">
              <small>
                ⚠️ Guest mode progress won't be saved to the leaderboard
              </small>
            </p>
          </div>

          <div className="landing-features">
            <div className="feature">
              <span className="feature-icon">🎮</span>
              <span>Interactive Gameplay</span>
            </div>
            <div className="feature">
              <span className="feature-icon">💰</span>
              <span>Learn Financial Literacy</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🏆</span>
              <span>Compete on Leaderboard</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;

