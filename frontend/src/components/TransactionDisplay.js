import React from "react";
import "../styles/TransactionDisplay.css";

/**
 * TransactionDisplay - Shows financial changes in balance sheet format
 * Organized by what comes in (green) and what goes out (red)
 */
const TransactionDisplay = ({ transaction }) => {
  if (!transaction) return null;

  const formatCurrency = (amount) => {
    return `€${Math.abs(amount).toFixed(0)}`;
  };

  // Calculate totals
  const inflows = [];
  const outflows = [];
  
  // One-time changes
  if (transaction.cash_change > 0) {
    inflows.push({ label: "Cash Received", amount: transaction.cash_change });
  } else if (transaction.cash_change < 0) {
    outflows.push({ label: "Cash Spent", amount: Math.abs(transaction.cash_change) });
  }
  
  if (transaction.investment_change > 0) {
    outflows.push({ label: "Invested", amount: transaction.investment_change });
  } else if (transaction.investment_change < 0) {
    inflows.push({ label: "Investment Withdrawn", amount: Math.abs(transaction.investment_change) });
  }
  
  if (transaction.debt_change > 0) {
    outflows.push({ label: "Debt Increased", amount: transaction.debt_change });
  } else if (transaction.debt_change < 0) {
    inflows.push({ label: "Debt Paid Off", amount: Math.abs(transaction.debt_change) });
  }
  
  // Monthly recurring changes
  const monthlyInflows = [];
  const monthlyOutflows = [];
  
  if (transaction.monthly_income_change > 0) {
    monthlyInflows.push({ label: "Income Increase", amount: transaction.monthly_income_change });
  } else if (transaction.monthly_income_change < 0) {
    monthlyOutflows.push({ label: "Income Decrease", amount: Math.abs(transaction.monthly_income_change) });
  }
  
  if (transaction.passive_income_change > 0) {
    monthlyInflows.push({ label: "Passive Income Increase", amount: transaction.passive_income_change });
  } else if (transaction.passive_income_change < 0) {
    monthlyOutflows.push({ label: "Passive Income Decrease", amount: Math.abs(transaction.passive_income_change) });
  }
  
  if (transaction.monthly_expense_change > 0) {
    monthlyOutflows.push({ label: "Expenses Increase", amount: transaction.monthly_expense_change });
  } else if (transaction.monthly_expense_change < 0) {
    monthlyInflows.push({ label: "Expenses Decrease", amount: Math.abs(transaction.monthly_expense_change) });
  }

  const hasOneTimeChanges = inflows.length > 0 || outflows.length > 0;
  const hasMonthlyChanges = monthlyInflows.length > 0 || monthlyOutflows.length > 0;

  if (!hasOneTimeChanges && !hasMonthlyChanges) {
    return (
      <div className="transaction-display">
        <h3>💰 Financial Changes</h3>
        <p className="no-changes">No financial changes this turn</p>
      </div>
    );
  }

  const totalInflow = inflows.reduce((sum, item) => sum + item.amount, 0);
  const totalOutflow = outflows.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="transaction-display">
      <h3>💰 Financial Changes</h3>

      {/* One-time changes */}
      {hasOneTimeChanges && (
        <div className="balance-sheet">
          <div className="balance-sheet-section inflows">
            <h4 className="section-title">💚 Money In</h4>
            {inflows.length > 0 ? (
              <div className="items-list">
                {inflows.map((item, idx) => (
                  <div key={idx} className="balance-item">
                    <span className="item-label">{item.label}</span>
                    <span className="item-amount positive">+{formatCurrency(item.amount)}</span>
                  </div>
                ))}
                <div className="subtotal">
                  <span>Total In:</span>
                  <span className="positive">+{formatCurrency(totalInflow)}</span>
                </div>
              </div>
            ) : (
              <div className="empty-section">No income this turn</div>
            )}
          </div>

          <div className="balance-sheet-section outflows">
            <h4 className="section-title">❤️ Money Out</h4>
            {outflows.length > 0 ? (
              <div className="items-list">
                {outflows.map((item, idx) => (
                  <div key={idx} className="balance-item">
                    <span className="item-label">{item.label}</span>
                    <span className="item-amount negative">-{formatCurrency(item.amount)}</span>
                  </div>
                ))}
                <div className="subtotal">
                  <span>Total Out:</span>
                  <span className="negative">-{formatCurrency(totalOutflow)}</span>
                </div>
              </div>
            ) : (
              <div className="empty-section">No expenses this turn</div>
            )}
          </div>

          <div className="net-change">
            <span>Net Change:</span>
            <span className={totalInflow - totalOutflow >= 0 ? "positive" : "negative"}>
              {totalInflow - totalOutflow >= 0 ? "+" : "-"}
              {formatCurrency(Math.abs(totalInflow - totalOutflow))}
            </span>
          </div>
        </div>
      )}

      {/* Monthly recurring changes */}
      {hasMonthlyChanges && (
        <div className="monthly-changes">
          <h4 className="monthly-title">📅 Monthly Budget Changes</h4>
          <div className="balance-sheet-section monthly-section">
            {monthlyInflows.length > 0 && (
              <div className="monthly-group">
                <div className="monthly-group-title positive">Monthly Income Increases</div>
                {monthlyInflows.map((item, idx) => (
                  <div key={idx} className="balance-item">
                    <span className="item-label">{item.label}</span>
                    <span className="item-amount positive">+{formatCurrency(item.amount)}/mo</span>
                  </div>
                ))}
              </div>
            )}
            
            {monthlyOutflows.length > 0 && (
              <div className="monthly-group">
                <div className="monthly-group-title negative">Monthly Budget Increases</div>
                {monthlyOutflows.map((item, idx) => (
                  <div key={idx} className="balance-item">
                    <span className="item-label">{item.label}</span>
                    <span className="item-amount negative">-{formatCurrency(item.amount)}/mo</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* New balances summary */}
      <div className="balance-summary">
        <h4>New Balances</h4>
        <div className="balance-grid">
          <div className="balance-item">
            <span className="balance-label">Cash</span>
            <span className="balance-value">{formatCurrency(transaction.cash_balance)}</span>
          </div>
          <div className="balance-item">
            <span className="balance-label">Investments</span>
            <span className="balance-value">{formatCurrency(transaction.investment_balance)}</span>
          </div>
          <div className="balance-item">
            <span className="balance-label">Debt</span>
            <span className="balance-value">{formatCurrency(transaction.debt_balance)}</span>
          </div>
        </div>
        <div className="balance-grid monthly-totals">
          <div className="balance-item">
            <span className="balance-label">Monthly Income</span>
            <span className="balance-value positive">{formatCurrency(transaction.monthly_income_total)}/mo</span>
          </div>
          <div className="balance-item">
            <span className="balance-label">Monthly Expenses</span>
            <span className="balance-value negative">{formatCurrency(transaction.monthly_expense_total)}/mo</span>
          </div>
          <div className="balance-item">
            <span className="balance-label">Net Monthly</span>
            <span className={`balance-value ${transaction.monthly_income_total - transaction.monthly_expense_total >= 0 ? "positive" : "negative"}`}>
              {formatCurrency(Math.abs(transaction.monthly_income_total - transaction.monthly_expense_total))}/mo
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransactionDisplay;
