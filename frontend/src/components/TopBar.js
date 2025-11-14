import React from 'react';
import { useNavigate } from 'react-router-dom';
import './TopBar.css';

function TopBar({ playerName, money, fiScore, onViewStats }) {
  const navigate = useNavigate();

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <h1 className="game-title" onClick={() => navigate('/')}>
          LifeSim: Financial Independence Quest
        </h1>
      </div>
      
      <div className="top-bar-center">
        <nav className="nav-links">
          <button onClick={() => navigate('/game')} className="nav-link">Game</button>
          <button onClick={() => navigate('/settings')} className="nav-link">Settings</button>
        </nav>
      </div>
      
      <div className="top-bar-right">
        {playerName && (
          <div className="player-info">
            <span className="player-name">👤 {playerName}</span>
            {money !== undefined && (
              <span className="money-display">💰 €{money.toLocaleString()}</span>
            )}
            {fiScore !== undefined && (
              <span className="fi-score">FI: {fiScore}%</span>
            )}
            {onViewStats && (
              <button className="view-stats-btn" onClick={onViewStats}>
                📊 View Stats
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default TopBar;

