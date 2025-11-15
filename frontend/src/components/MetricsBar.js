import React from "react";
import "../styles/MetricsBar.css";

/**
 * MetricsBar - Display financial metrics in a compact bar
 */
const MetricsBar = ({ gameState }) => {
  const {
    current_age = 25,
    years_passed = 0,
    money = 0,
    monthly_income = 0,
    monthly_expenses = 0,
    investments = 0,
    passive_income = 0,
    debts = 0,
  } = gameState;

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("fi-FI", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="metrics-bar">
      <div className="metric-item">
        <span className="metric-icon">💰</span>
        <div className="metric-info">
          <span className="metric-label">Cash</span>
          <span className="metric-value">{formatCurrency(money)}</span>
        </div>
      </div>

      <div className="metric-item">
        <span className="metric-icon">📈</span>
        <div className="metric-info">
          <span className="metric-label">Investments</span>
          <span className="metric-value">{formatCurrency(investments)}</span>
        </div>
      </div>

      <div className="metric-item">
        <span className="metric-icon">💵</span>
        <div className="metric-info">
          <span className="metric-label">Income</span>
          <span className="metric-value">{formatCurrency(monthly_income)}</span>
        </div>
      </div>

      <div className="metric-item">
        <span className="metric-icon">💸</span>
        <div className="metric-info">
          <span className="metric-label">Expenses</span>
          <span className="metric-value">{formatCurrency(monthly_expenses)}</span>
        </div>
      </div>

      <div className="metric-item">
        <span className="metric-icon">🌊</span>
        <div className="metric-info">
          <span className="metric-label">Passive</span>
          <span className="metric-value">{formatCurrency(passive_income)}</span>
        </div>
      </div>

      <div className="metric-item">
        <span className="metric-icon">💳</span>
        <div className="metric-info">
          <span className="metric-label">Debts</span>
          <span className="metric-value">{formatCurrency(debts)}</span>
        </div>
      </div>
    </div>
  );
};

export default MetricsBar;

