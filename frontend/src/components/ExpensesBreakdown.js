import React from "react";
import "../styles/ExpensesBreakdown.css";

// All possible optional expenses (defined outside component to avoid recreation)
// Note: Stat values show per-step benefits (applied every turn you have the subscription)
const ALL_OPTIONAL_EXPENSES = [
  { id: "netflix", name: "Netflix", amount: 15, icon: "🎬", motivation: 1 },
  { id: "spotify", name: "Spotify", amount: 10, icon: "🎵", motivation: 1 },
  { id: "gym", name: "Gym Membership", amount: 40, icon: "💪", energy: 2, motivation: 1 },
  { id: "dining", name: "Dining Out", amount: 200, icon: "🍽️", social_life: 2 },
  { id: "hobbies", name: "Hobbies & Fun", amount: 100, icon: "🎮", motivation: 2 },
];

/**
 * ExpensesBreakdown - Shows detailed breakdown of monthly expenses
 * Displays mandatory and optional expenses with ability to remove optional ones
 */
const ExpensesBreakdown = ({ mandatoryExpenses, totalExpenses, activeSubscriptions, onRemoveExpense }) => {
  // Compute optional expenses directly from props (no local state)
  // This ensures it always reflects the backend state
  const optionalExpenses = React.useMemo(() => {
    if (!activeSubscriptions || Object.keys(activeSubscriptions).length === 0) {
      return [];
    }
    return ALL_OPTIONAL_EXPENSES.filter(expense => activeSubscriptions[expense.id]);
  }, [activeSubscriptions]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("fi-FI", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleRemove = (expense) => {
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
        <div style={{ fontSize: "0.75rem", color: "#666", padding: "0 15px 5px", fontStyle: "italic" }}>
          Benefits apply each turn you have the subscription
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
                    {expense.motivation && <span className="effect">🎯 +{expense.motivation}/turn</span>}
                    {expense.energy && <span className="effect">⚡ +{expense.energy}/turn</span>}
                    {expense.social_life && <span className="effect">👥 +{expense.social_life}/turn</span>}
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

