import React from "react";
import "../styles/TransactionLog.css";

/**
 * TransactionLog - Shows the last 10 financial events in the main game view
 */
const TransactionLog = ({ transactions, currentMonthsPassed, currentMonthPhase }) => {
  if (!transactions || transactions.length === 0) {
    return null;
  }

  const formatCurrency = (amount) => {
    const absAmount = Math.abs(amount);
    return amount >= 0 ? `+€${absAmount.toFixed(0)}` : `-€${absAmount.toFixed(0)}`;
  };

  const getChangeIcon = (amount) => {
    return amount >= 0 ? "💰" : "💸";
  };

  const getMonthName = (monthsPassed) => {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return months[monthsPassed % 12];
  };

  const getPhaseName = (phase) => {
    return { 1: "Early", 2: "Mid", 3: "Late" }[phase] || "Early";
  };

  // Add timestamps to transactions if they don't have them
  const transactionsWithTimestamp = transactions.map((t, idx) => {
    if (t.timestamp) return t;
    // For old transactions without timestamp, use current time as fallback
    return {
      ...t,
      timestamp: `${getPhaseName(currentMonthPhase)} ${getMonthName(currentMonthsPassed)}`
    };
  });

  return (
    <div className="transaction-log">
      <h4 className="log-title">📊 Recent Changes</h4>
      <div className="log-items">
        {transactionsWithTimestamp.slice(-10).reverse().map((transaction, index) => (
          <div key={index} className="log-item">
            <span className="log-timestamp">{transaction.timestamp}</span>
            <span className="log-icon">{getChangeIcon(transaction.cash_change)}</span>
            <span className="log-description">{transaction.description}</span>
            <span className={`log-amount ${transaction.cash_change >= 0 ? 'positive' : 'negative'}`}>
              {formatCurrency(transaction.cash_change)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TransactionLog;
