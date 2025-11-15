import React, { useState } from "react";
import "../styles/ExpensesBreakdown.css";

/**
 * ExpensesBreakdown - Shows detailed breakdown of monthly expenses
 * Displays mandatory and optional expenses with ability to remove optional ones
 */
const ExpensesBreakdown = ({ totalExpenses, onRemoveExpense }) => {
  // Mock data - will be replaced with real backend data later
  const [mandatoryExpenses] = useState([
    { id: "rent", name: "Rent/Mortgage", amount: 800, icon: "🏠" },
    { id: "food", name: "Food & Groceries", amount: 400, icon: "🍕" },
    { id: "utilities", name: "Electricity & Water", amount: 150, icon: "💡" },
    { id: "transport", name: "Transportation", amount: 100, icon: "🚗" },
    { id: "insurance", name: "Insurance", amount: 80, icon: "🛡️" },
  ]);

  const [optionalExpenses, setOptionalExpenses] = useState([
    { id: "netflix", name: "Netflix", amount: 15, icon: "🎬", motivation: 5 },
    { id: "spotify", name: "Spotify", amount: 10, icon: "🎵", motivation: 3 },
    { id: "gym", name: "Gym Membership", amount: 40, icon: "💪", energy: 10, motivation: 5 },
    { id: "dining", name: "Dining Out", amount: 200, icon: "🍽️", social_life: 10, motivation: 3 },
    { id: "hobbies", name: "Hobbies & Fun", amount: 100, icon: "🎮", motivation: 8 },
  ]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("fi-FI", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleRemove = (expense) => {
    setOptionalExpenses(prev => prev.filter(e => e.id !== expense.id));
    if (onRemoveExpense) {
      onRemoveExpense(expense);
    }
  };

  const mandatoryTotal = mandatoryExpenses.reduce((sum, e) => sum + e.amount, 0);
  const optionalTotal = optionalExpenses.reduce((sum, e) => sum + e.amount, 0);

  return (
    <div className="expenses-breakdown">
      <div className="breakdown-header">
        <h3>💸 Monthly Expenses</h3>
        <div className="total-amount">{formatCurrency(mandatoryTotal + optionalTotal)}</div>
      </div>

      {/* Mandatory Expenses */}
      <div className="expense-section">
        <div className="section-title mandatory">
          <span>🔒 Mandatory</span>
          <span className="section-total">{formatCurrency(mandatoryTotal)}</span>
        </div>
        <div className="expense-list">
          {mandatoryExpenses.map((expense) => (
            <div key={expense.id} className="expense-item mandatory-item">
              <span className="expense-icon">{expense.icon}</span>
              <span className="expense-name">{expense.name}</span>
              <span className="expense-amount">{formatCurrency(expense.amount)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Optional Expenses */}
      <div className="expense-section">
        <div className="section-title optional">
          <span>✨ Optional</span>
          <span className="section-total">{formatCurrency(optionalTotal)}</span>
        </div>
        <div className="expense-list">
          {optionalExpenses.length === 0 ? (
            <div className="no-expenses">No optional expenses - maximizing savings! 💰</div>
          ) : (
            optionalExpenses.map((expense) => (
              <div key={expense.id} className="expense-item optional-item">
                <span className="expense-icon">{expense.icon}</span>
                <div className="expense-details">
                  <span className="expense-name">{expense.name}</span>
                  {/* Show stat effects */}
                  <div className="expense-effects">
                    {expense.motivation && <span className="effect">🎯 +{expense.motivation}</span>}
                    {expense.energy && <span className="effect">⚡ +{expense.energy}</span>}
                    {expense.social_life && <span className="effect">👥 +{expense.social_life}</span>}
                  </div>
                </div>
                <span className="expense-amount">{formatCurrency(expense.amount)}</span>
                <button
                  className="remove-btn"
                  onClick={() => handleRemove(expense)}
                  title="Cancel subscription"
                >
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="breakdown-footer">
        <p className="tip">💡 Tip: Removing optional expenses increases savings but may affect your life balance</p>
      </div>
    </div>
  );
};

export default ExpensesBreakdown;

