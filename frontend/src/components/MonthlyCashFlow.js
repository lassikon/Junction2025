import React from "react";
import "../styles/MonthlyCashFlow.css";

/**
 * MonthlyCashFlow - Shows the monthly income/expense flow for the turn
 */
const MonthlyCashFlow = ({ cashFlow }) => {
  if (!cashFlow) return null;

  const formatCurrency = (amount) => {
    return `€${Math.abs(amount).toFixed(0)}`;
  };

  // If cash flow wasn't applied (phase 2 or 3), show time indicator instead
  if (!cashFlow.applied) {
    return (
      <div className="monthly-cash-flow time-indicator">
        <h3>📅 {cashFlow.month_phase_name} {cashFlow.month_name}</h3>
        <p className="phase-description">
          {cashFlow.month_phase === 2 ? "Mid-month decisions and daily expenses" : "End of month - manage remaining budget"}
        </p>
      </div>
    );
  }

  const isPositiveNet = cashFlow.net_change >= 0;

  return (
    <div className="monthly-cash-flow">
      <h3>💰 New Month: {cashFlow.month_name}</h3>
      
      <div className="cash-flow-breakdown">
        <div className="flow-item income">
          <span className="flow-label">💰 Income Received</span>
          <span className="flow-amount positive">+{formatCurrency(cashFlow.income_received)}</span>
        </div>
        
        <div className="flow-item expenses">
          <span className="flow-label">💸 Monthly Expenses Paid</span>
          <span className="flow-amount negative">-{formatCurrency(cashFlow.expenses_paid)}</span>
        </div>
        
        {cashFlow.debt_from_deficit > 0 && (
          <div className="flow-item deficit">
            <span className="flow-label">⚠️ Deficit Converted to Debt</span>
            <span className="flow-amount negative">+{formatCurrency(cashFlow.debt_from_deficit)}</span>
          </div>
        )}
        
        <div className="flow-divider"></div>
        
        <div className="flow-item net">
          <span className="flow-label">Net Monthly Cash Flow</span>
          <span className={`flow-amount net-amount ${isPositiveNet ? 'positive' : 'negative'}`}>
            {isPositiveNet ? '+' : '-'}{formatCurrency(cashFlow.net_change)}
          </span>
        </div>
      </div>
      
      <p className="month-start-hint">
        💡 This is your budget for {cashFlow.month_name}. Make wise spending decisions throughout the month!
      </p>
    </div>
  );
};

export default MonthlyCashFlow;
