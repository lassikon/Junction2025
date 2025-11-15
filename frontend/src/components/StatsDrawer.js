import React from 'react';
import './StatsDrawer.css';

function StatsDrawer({ isOpen, onClose, playerState }) {
  if (!isOpen || !playerState) return null;

  const { name, avatarKey, metrics, assets = [], recentDecisions = [], year, month } = playerState;

  const metricsConfig = [
    { key: 'money', label: 'Money / Net Worth', color: '#10b981', icon: '💰', format: (v) => `€${v.toLocaleString()}`, max: null },
    { key: 'fiScore', label: 'FI Score', color: '#3b82f6', icon: '📈', format: (v) => `${v}%`, max: 100 },
    { key: 'energy', label: 'Energy', color: '#f59e0b', icon: '⚡', format: (v) => `${v}/100`, max: 100 },
    { key: 'motivation', label: 'Motivation', color: '#8b5cf6', icon: '🎯', format: (v) => `${v}/100`, max: 100 },
    { key: 'social', label: 'Social Life', color: '#ec4899', icon: '👥', format: (v) => `${v}/100`, max: 100 },
    { key: 'knowledge', label: 'Financial Knowledge', color: '#06b6d4', icon: '📚', format: (v) => `${v}/100`, max: 100 }
  ];

  return (
    <>
      <div className="stats-drawer-overlay" onClick={onClose} />
      <div className="stats-drawer">
        <div className="stats-drawer-header">
          <h2>Player Stats</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="stats-drawer-content">
          {/* Player Info */}
          <div className="player-profile">
            {avatarKey && (
              <img
                src={`/images/characters/${avatarKey}`}
                alt={name}
                className="player-avatar-large"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            )}
            <div className="player-details">
              <h3>{name}</h3>
              <p className="game-time">Year {year} • Month {month}</p>
            </div>
          </div>

          {/* Metrics */}
          <div className="stats-section">
            <h3 className="section-title">📊 Metrics</h3>
            <div className="metrics-list">
              {metricsConfig.map(({ key, label, color, icon, format, max }) => {
                const value = metrics[key] || 0;
                const percentage = max ? (value / max) * 100 : 100;
                
                return (
                  <div key={key} className="stat-item">
                    <div className="stat-header">
                      <span className="stat-icon">{icon}</span>
                      <div className="stat-info">
                        <span className="stat-label">{label}</span>
                        <span className="stat-value">{format(value)}</span>
                      </div>
                    </div>
                    {max && (
                      <div className="stat-bar-container">
                        <div 
                          className="stat-bar-fill" 
                          style={{ 
                            width: `${Math.min(percentage, 100)}%`,
                            backgroundColor: color
                          }}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Assets */}
          <div className="stats-section">
            <h3 className="section-title">🏠 Current Assets</h3>
            {assets.length > 0 ? (
              <div className="assets-list">
                {assets.map((asset, index) => (
                  <div key={index} className="asset-item">
                    <img
                      src={`/images/game/${asset.image}`}
                      alt={asset.name}
                      className="asset-image"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                    <span className="asset-name">{asset.name}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">No assets acquired yet</p>
            )}
          </div>

          {/* Recent Decisions */}
          <div className="stats-section">
            <h3 className="section-title">📝 Recent Decisions</h3>
            {recentDecisions.length > 0 ? (
              <div className="decisions-list">
                {recentDecisions.map((decision, index) => (
                  <div key={index} className="decision-item">
                    <span className="decision-turn">Turn {decision.turn}</span>
                    <span className="decision-text">{decision.choice}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">No decisions made yet</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default StatsDrawer;

