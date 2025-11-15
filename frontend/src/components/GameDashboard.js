import React from "react";
import "../styles/GameDashboard.css";

const GameDashboard = ({ gameState, onMakeDecision }) => {
  // Handle undefined or null gameState
  if (!gameState) {
    return <div className="game-dashboard">Loading game state...</div>;
  }

  const {
    current_step = 0,
    money = 0,
    monthly_income = 0,
    monthly_expenses = 0,
    investments = 0,
    passive_income = 0,
    debts = 0,
    fi_score = 0,
    energy = 0,
    motivation = 0,
    social_life = 0,
    financial_knowledge = 0,
    assets = {},
    game_status = "active"
  } = gameState;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("fi-FI", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (value) => {
    if (value >= 70) return "status-good";
    if (value >= 40) return "status-medium";
    return "status-low";
  };

  const getFIScoreColor = (score) => {
    if (score >= 80) return "fi-excellent";
    if (score >= 60) return "fi-good";
    if (score >= 40) return "fi-medium";
    return "fi-low";
  };

  return (
    <div className="game-dashboard">
      <header className="dashboard-header">
        <h1>🎮 LifeSim: Financial Independence Quest</h1>
        <div className="session-info">
          <span className="step-badge">Step {current_step}</span>
          <span className="status-badge">{game_status}</span>
        </div>
      </header>

      {/* FI Score - Most Important Metric */}
      <div className="fi-score-section">
        <div className="fi-score-card">
          <h2>Financial Independence Score</h2>
          <div className={`fi-score ${getFIScoreColor(fi_score)}`}>
            {fi_score.toFixed(1)}%
          </div>
          <p className="fi-score-description">
            {fi_score >= 100
              ? "🎉 You've achieved Financial Independence!"
              : `${(100 - fi_score).toFixed(0)}% to go until FI!`}
          </p>
          <div className="fi-progress-bar">
            <div
              className="fi-progress-fill"
              style={{ width: `${Math.min(fi_score, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Financial Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <h3>Cash & Savings</h3>
            <p className="metric-value">{formatCurrency(money)}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <h3>Investments</h3>
            <p className="metric-value">{formatCurrency(investments)}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">💵</div>
          <div className="metric-content">
            <h3>Monthly Income</h3>
            <p className="metric-value">{formatCurrency(monthly_income)}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">💸</div>
          <div className="metric-content">
            <h3>Monthly Expenses</h3>
            <p className="metric-value">{formatCurrency(monthly_expenses)}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🌊</div>
          <div className="metric-content">
            <h3>Passive Income</h3>
            <p className="metric-value">{formatCurrency(passive_income)}</p>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">💳</div>
          <div className="metric-content">
            <h3>Debts</h3>
            <p className="metric-value">{formatCurrency(debts)}</p>
          </div>
        </div>
      </div>

      {/* Life Metrics */}
      <div className="life-metrics-section">
        <h2>Life Balance</h2>
        <div className="life-metrics-grid">
          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">⚡</span>
              <span className="life-metric-label">Energy</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(energy)}`}
                style={{ width: `${energy}%` }}
              >
                <span className="life-metric-value">{energy}</span>
              </div>
            </div>
          </div>

          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">🎯</span>
              <span className="life-metric-label">Motivation</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(motivation)}`}
                style={{ width: `${motivation}%` }}
              >
                <span className="life-metric-value">{motivation}</span>
              </div>
            </div>
          </div>

          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">👥</span>
              <span className="life-metric-label">Social Life</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(social_life)}`}
                style={{ width: `${social_life}%` }}
              >
                <span className="life-metric-value">{social_life}</span>
              </div>
            </div>
          </div>

          <div className="life-metric">
            <div className="life-metric-header">
              <span className="life-metric-icon">📚</span>
              <span className="life-metric-label">Financial Knowledge</span>
            </div>
            <div className="life-metric-bar">
              <div
                className={`life-metric-fill ${getStatusColor(
                  financial_knowledge
                )}`}
                style={{ width: `${financial_knowledge}%` }}
              >
                <span className="life-metric-value">{financial_knowledge}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Assets */}
      {assets && Object.keys(assets).length > 0 && (
        <div className="assets-section">
          <h2>Your Assets</h2>
          <div className="assets-list">
            {Object.entries(assets).map(([key, value]) => (
              <div key={key} className="asset-item">
                <span className="asset-key">{key.replace(/_/g, ' ').toUpperCase()}</span>
                <span className="asset-value">
                  {typeof value === 'boolean' 
                    ? (value ? '✓' : '✗') 
                    : typeof value === 'object' 
                      ? JSON.stringify(value) 
                      : value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Button */}
      {game_status === "active" && (
        <div className="action-section">
          <button className="btn-action" onClick={onMakeDecision}>
            Continue Your Journey →
          </button>
        </div>
      )}

      {game_status === "completed" && (
        <div className="completion-message">
          <h2>🎉 Congratulations!</h2>
          <p>You've completed your journey to financial independence!</p>
        </div>
      )}
    </div>
  );
};

export default GameDashboard;
