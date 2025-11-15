import React, { useState } from "react";
import ExpensesBreakdown from "./ExpensesBreakdown";
import "../styles/MetricsBar.css";

/**
 * MetricsBar - Display financial metrics in a compact bar
 */
const MetricsBar = ({ gameState }) => {
  const [showExpensesBreakdown, setShowExpensesBreakdown] = useState(false);
  const [expenseAdjustment, setExpenseAdjustment] = useState(0);
  const [statAdjustments, setStatAdjustments] = useState({});
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

  const handleRemoveExpense = (expense) => {
    // Update local expense adjustment (will be sent to backend later)
    setExpenseAdjustment(prev => prev + expense.amount);
    
    // Update stat adjustments (will affect life metrics)
    const newAdjustments = { ...statAdjustments };
    if (expense.motivation) {
      newAdjustments.motivation = (newAdjustments.motivation || 0) - expense.motivation;
    }
    if (expense.energy) {
      newAdjustments.energy = (newAdjustments.energy || 0) - expense.energy;
    }
    if (expense.social_life) {
      newAdjustments.social_life = (newAdjustments.social_life || 0) - expense.social_life;
    }
    setStatAdjustments(newAdjustments);

    // TODO: Send to backend API when ready
    console.log("📝 Expense removed (frontend only):", {
      expenseId: expense.id,
      name: expense.name,
      savingsIncrease: expense.amount,
      statChanges: newAdjustments
    });
  };

  // Apply adjustments to display values
  const adjustedExpenses = Math.max(0, monthly_expenses - expenseAdjustment);

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

      <div 
        className={`metric-item expenses-item ${showExpensesBreakdown ? 'active' : ''}`}
        onClick={() => setShowExpensesBreakdown(!showExpensesBreakdown)}
      >
        <span className="metric-icon">💸</span>
        <div className="metric-info">
          <span className="metric-label">
            Expenses
            <span className={`expand-arrow ${showExpensesBreakdown ? 'expanded' : ''}`}>
              ▼
            </span>
          </span>
          <span className="metric-value">
            {formatCurrency(adjustedExpenses)}
            {expenseAdjustment > 0 && (
              <span className="adjustment-badge">-{formatCurrency(expenseAdjustment)}</span>
            )}
          </span>
        </div>
        
        {/* Expenses Breakdown Tooltip */}
        {showExpensesBreakdown && (
          <div 
            className="expenses-tooltip"
            onClick={(e) => e.stopPropagation()}
          >
            <ExpensesBreakdown
              totalExpenses={adjustedExpenses}
              onRemoveExpense={handleRemoveExpense}
            />
          </div>
        )}
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

