import React, { useState } from "react";
import ExpensesBreakdown from "./ExpensesBreakdown";
import { useUpdateExpenses } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import "../styles/MetricsBar.css";

/**
 * MetricsBar - Display financial metrics in a compact bar
 */
const MetricsBar = ({ gameState }) => {
  const [showExpensesBreakdown, setShowExpensesBreakdown] = useState(false);
  const sessionId = useGameStore((state) => state.sessionId);
  const updateExpensesMutation = useUpdateExpenses();

  const {
    current_age = 25,
    years_passed = 0,
    money = 0,
    monthly_income = 0,
    monthly_expenses = 0,
    expense_housing = 0,
    expense_food = 0,
    expense_transport = 0,
    expense_utilities = 0,
    expense_subscriptions = 0,
    expense_insurance = 0,
    expense_other = 0,
    active_subscriptions = {},
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
    // Calculate stat adjustments for this expense
    const statAdjustments = {};
    if (expense.motivation) {
      statAdjustments.motivation = -expense.motivation;
    }
    if (expense.energy) {
      statAdjustments.energy = -expense.energy;
    }
    if (expense.social_life) {
      statAdjustments.social_life = -expense.social_life;
    }

    // Send to backend API
    updateExpensesMutation.mutate({
      sessionId,
      removedExpenses: [expense.id],
      statAdjustments,
    });

    console.log("📝 Expense removed, updating backend:", {
      expenseId: expense.id,
      name: expense.name,
      savingsIncrease: expense.amount,
      statChanges: statAdjustments
    });
  };

  // Map backend expense data to component structure
  const mandatoryExpenses = [
    { id: "rent", name: "Rent/Mortgage", amount: expense_housing, icon: "🏠" },
    { id: "food", name: "Food & Groceries", amount: expense_food, icon: "🍕" },
    { id: "electricity", name: "Electricity & Water", amount: expense_utilities, icon: "💡" },
    { id: "transportation", name: "Transportation", amount: expense_transport, icon: "🚗" },
    { id: "insurance", name: "Insurance", amount: expense_insurance, icon: "🛡️" },
  ];

  // Optional expenses come from subscriptions + a portion of "other"
  // We'll use the hardcoded structure from ExpensesBreakdown for now
  const optionalExpensesData = {
    totalAmount: expense_subscriptions + expense_other * 0.5, // Rough estimate
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
            {formatCurrency(monthly_expenses)}
          </span>
        </div>
        
        {/* Expenses Breakdown Tooltip */}
        {showExpensesBreakdown && (
          <div 
            className="expenses-tooltip"
            onClick={(e) => e.stopPropagation()}
          >
            <ExpensesBreakdown
              mandatoryExpenses={mandatoryExpenses}
              totalExpenses={monthly_expenses}
              activeSubscriptions={active_subscriptions}
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

