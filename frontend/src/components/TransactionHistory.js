import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { API_URL } from "../config/api";
import "../styles/TransactionHistory.css";

/**
 * TransactionHistory - Full transaction log viewer
 * Shows all financial decisions and their impacts
 */
const TransactionHistory = ({ sessionId, onClose }) => {
  const { data: transactions, isLoading, isError } = useQuery({
    queryKey: ["transactions", sessionId],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/transactions/${sessionId}`);
      return response.data;
    },
    enabled: !!sessionId,
  });

  const formatCurrency = (amount) => {
    return `€${Math.abs(amount).toFixed(0)}`;
  };

  const getChangeClass = (amount, isExpenseOrDebt = false) => {
    if (amount === 0) return "neutral";
    // For expenses and debt, positive is bad (red), negative is good (green)
    if (isExpenseOrDebt) {
      return amount > 0 ? "negative" : "positive";
    }
    // For everything else, positive is good (green), negative is bad (red)
    return amount > 0 ? "positive" : "negative";
  };

  const formatChange = (amount, isExpenseOrDebt = false) => {
    if (amount === 0) return null;
    const sign = amount > 0 ? "+" : "";
    const className = getChangeClass(amount, isExpenseOrDebt);
    return (
      <span className={`change ${className}`}>
        {sign}
        {formatCurrency(amount)}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="transaction-history-modal" onClick={(e) => e.stopPropagation()}>
          <div className="loading">Loading transaction history...</div>
        </div>
      </div>
    );
  }

  if (isError || !transactions) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="transaction-history-modal" onClick={(e) => e.stopPropagation()}>
          <button className="modal-close" onClick={onClose}>×</button>
          <div className="error">Failed to load transaction history</div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="transaction-history-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <h2>📊 Transaction History</h2>
        <p className="subtitle">Track all your financial decisions</p>

        {transactions.length === 0 ? (
          <div className="no-transactions">
            No transactions yet. Start making decisions to see your financial journey!
          </div>
        ) : (
          <div className="transactions-list">
            {transactions.map((transaction, index) => (
              <div key={index} className="transaction-card">
                <div className="transaction-header">
                  <div className="step-info">
                    <span className="step-number">Step {transaction.step_number}</span>
                    <span className="event-type">{transaction.event_type.replace(/_/g, " ")}</span>
                  </div>
                  <div className="transaction-date">
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="transaction-choice">
                  <strong>Choice:</strong> {transaction.chosen_option}
                </div>

                <div className="transaction-changes">
                  {transaction.cash_change !== 0 && (
                    <div className="change-row">
                      <span>Cash:</span>
                      {formatChange(transaction.cash_change)}
                    </div>
                  )}
                  {transaction.investment_change !== 0 && (
                    <div className="change-row">
                      <span>Investments:</span>
                      {formatChange(transaction.investment_change)}
                    </div>
                  )}
                  {transaction.debt_change !== 0 && (
                    <div className="change-row">
                      <span>Debt:</span>
                      {formatChange(transaction.debt_change, true)}
                    </div>
                  )}
                  {transaction.monthly_income_change !== 0 && (
                    <div className="change-row">
                      <span>Monthly Income:</span>
                      {formatChange(transaction.monthly_income_change)}/mo
                    </div>
                  )}
                  {transaction.monthly_expense_change !== 0 && (
                    <div className="change-row">
                      <span>Monthly Expenses:</span>
                      {formatChange(transaction.monthly_expense_change, true)}/mo
                    </div>
                  )}
                  {transaction.passive_income_change !== 0 && (
                    <div className="change-row">
                      <span>Passive Income:</span>
                      {formatChange(transaction.passive_income_change)}/mo
                    </div>
                  )}
                </div>

                <div className="transaction-balances">
                  <div className="balance-item">
                    <span>Cash:</span>
                    <strong>{formatCurrency(transaction.cash_balance)}</strong>
                  </div>
                  <div className="balance-item">
                    <span>Investments:</span>
                    <strong>{formatCurrency(transaction.investment_balance)}</strong>
                  </div>
                  <div className="balance-item">
                    <span>Debt:</span>
                    <strong>{formatCurrency(transaction.debt_balance)}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        <button className="btn-close-history" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default TransactionHistory;
