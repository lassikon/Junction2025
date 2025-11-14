import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import './LoginPage.css';

const AVAILABLE_AVATARS = [
  { key: 'avatar_girl_middle_school.png', label: 'Young Girl' },
  { key: 'avatar_boy_middle_school.png', label: 'Young Boy' },
  { key: 'avatar_girl_highschool-removebg-preview.png', label: 'Teen Girl' },
  { key: 'avatar_boy_highschool.png', label: 'Teen Boy' },
  { key: 'avatar_adult_female.png', label: 'Adult Female' },
  { key: 'avatar_adult_male.png', label: 'Adult Male' }
];

function LoginPage() {
  const [name, setName] = useState('');
  const [selectedAvatar, setSelectedAvatar] = useState(AVAILABLE_AVATARS[0].key);
  const { startGame, loading } = useGame();
  const navigate = useNavigate();

  const handleStartGame = async () => {
    const playerName = name.trim() || 'Player';
    try {
      await startGame(playerName, selectedAvatar);
      navigate('/game');
    } catch (error) {
      console.error('Failed to start game:', error);
    }
  };

  const handleContinueWithoutName = async () => {
    try {
      await startGame('Player', selectedAvatar);
      navigate('/game');
    } catch (error) {
      console.error('Failed to start game:', error);
    }
  };

  return (
    <div className="login-page">
      <div 
        className="login-background"
        style={{ backgroundImage: 'url(/images/backgrounds/sunny_background.png)' }}
      />
      
      <div className="login-container">
        <div className="login-card">
          <h1 className="login-title">LifeSim</h1>
          <h2 className="login-subtitle">Financial Independence Quest</h2>
          <p className="login-description">
            Make life decisions, manage your finances, and achieve financial independence!
          </p>

          <div className="login-form">
            <div className="form-group">
              <label htmlFor="player-name">Your Name</label>
              <input
                id="player-name"
                type="text"
                placeholder="Enter your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={20}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleStartGame();
                  }
                }}
              />
            </div>

            <div className="form-group">
              <label>Choose Your Avatar</label>
              <div className="avatar-grid">
                {AVAILABLE_AVATARS.map((avatar) => (
                  <div
                    key={avatar.key}
                    className={`avatar-option ${selectedAvatar === avatar.key ? 'selected' : ''}`}
                    onClick={() => setSelectedAvatar(avatar.key)}
                  >
                    <img
                      src={`/images/characters/${avatar.key}`}
                      alt={avatar.label}
                      onError={(e) => {
                        e.target.src = '/images/characters/avatar_girl_middle_school.png';
                      }}
                    />
                    <span className="avatar-label">{avatar.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={handleStartGame}
              disabled={loading}
            >
              {loading ? 'Starting...' : '🎮 Start Game'}
            </button>

            <button
              className="btn btn-secondary btn-small"
              onClick={handleContinueWithoutName}
              disabled={loading}
            >
              Continue without name
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;

