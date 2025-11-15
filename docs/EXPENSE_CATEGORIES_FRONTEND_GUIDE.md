# Expense Categories Frontend Implementation Guide

## Overview

This guide covers how to implement the frontend UI for the expense categories feature. The backend is fully implemented and ready to provide expense breakdown data and handle category modifications.

## What's Already Done (Backend)

✅ Database schema includes 7 expense categories:
- `expense_housing` - Rent/mortgage
- `expense_food` - Groceries and dining
- `expense_transport` - Public transport, car costs, fuel
- `expense_utilities` - Electricity, water, internet, phone
- `expense_subscriptions` - Netflix, Spotify, gym, etc.
- `expense_insurance` - Health, car, home insurance
- `expense_other` - Pet costs, personal care, miscellaneous

✅ `GameStateResponse` includes all expense category fields  
✅ AI can generate options that modify specific expense categories  
✅ `apply_decision_effects()` recalculates total `monthly_expenses` from category sum  
✅ Transaction summaries include expense category changes  

## Implementation Steps

### Step 1: Display Expense Breakdown in UI

**Location:** `frontend/src/components/MetricsBar.js` or create new `ExpenseBreakdown.js` component

**Goal:** Show players their current expense breakdown

```jsx
// frontend/src/components/ExpenseBreakdown.js
import React from 'react';
import '../styles/ExpenseBreakdown.css';

export default function ExpenseBreakdown({ gameState }) {
  const expenses = [
    { label: 'Housing', value: gameState.expense_housing, icon: '🏠' },
    { label: 'Food', value: gameState.expense_food, icon: '🍽️' },
    { label: 'Transport', value: gameState.expense_transport, icon: '🚗' },
    { label: 'Utilities', value: gameState.expense_utilities, icon: '💡' },
    { label: 'Subscriptions', value: gameState.expense_subscriptions, icon: '📺' },
    { label: 'Insurance', value: gameState.expense_insurance, icon: '🛡️' },
    { label: 'Other', value: gameState.expense_other, icon: '📦' }
  ];

  const total = expenses.reduce((sum, expense) => sum + expense.value, 0);

  return (
    <div className="expense-breakdown">
      <h3>Monthly Expenses: €{total.toFixed(0)}</h3>
      <div className="expense-list">
        {expenses.map(expense => (
          <div key={expense.label} className="expense-item">
            <span className="expense-icon">{expense.icon}</span>
            <span className="expense-label">{expense.label}</span>
            <span className="expense-value">€{expense.value.toFixed(0)}</span>
            <div 
              className="expense-bar"
              style={{ width: `${(expense.value / total) * 100}%` }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
```

**CSS:** `frontend/src/styles/ExpenseBreakdown.css`

```css
.expense-breakdown {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
}

.expense-breakdown h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #fff;
}

.expense-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.expense-item {
  display: grid;
  grid-template-columns: 30px 120px 80px 1fr;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  position: relative;
}

.expense-icon {
  font-size: 20px;
}

.expense-label {
  color: #fff;
  font-size: 14px;
}

.expense-value {
  color: #ffd700;
  font-weight: bold;
  text-align: right;
}

.expense-bar {
  height: 4px;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  border-radius: 2px;
  transition: width 0.3s ease;
}
```

**Integration:** Add to `GameDashboard.js`

```jsx
import ExpenseBreakdown from './ExpenseBreakdown';

// Inside GameDashboard component
<ExpenseBreakdown gameState={gameState} />
```

---

### Step 2: Show Expense Changes in Transaction Log

**Location:** `frontend/src/components/GameDashboard.js`

**Goal:** Display expense category changes in the transaction history

**Update the transaction rendering logic:**

```jsx
// In the transaction history rendering section
{transaction.expense_housing_change && (
  <div className="transaction-detail expense-change">
    🏠 Housing: €{transaction.expense_housing_change > 0 ? '+' : ''}{transaction.expense_housing_change}
  </div>
)}
{transaction.expense_food_change && (
  <div className="transaction-detail expense-change">
    🍽️ Food: €{transaction.expense_food_change > 0 ? '+' : ''}{transaction.expense_food_change}
  </div>
)}
{transaction.expense_transport_change && (
  <div className="transaction-detail expense-change">
    🚗 Transport: €{transaction.expense_transport_change > 0 ? '+' : ''}{transaction.expense_transport_change}
  </div>
)}
{transaction.expense_utilities_change && (
  <div className="transaction-detail expense-change">
    💡 Utilities: €{transaction.expense_utilities_change > 0 ? '+' : ''}{transaction.expense_utilities_change}
  </div>
)}
{transaction.expense_subscriptions_change && (
  <div className="transaction-detail expense-change">
    📺 Subscriptions: €{transaction.expense_subscriptions_change > 0 ? '+' : ''}{transaction.expense_subscriptions_change}
  </div>
)}
{transaction.expense_insurance_change && (
  <div className="transaction-detail expense-change">
    🛡️ Insurance: €{transaction.expense_insurance_change > 0 ? '+' : ''}{transaction.expense_insurance_change}
  </div>
)}
{transaction.expense_other_change && (
  <div className="transaction-detail expense-change">
    📦 Other: €{transaction.expense_other_change > 0 ? '+' : ''}{transaction.expense_other_change}
  </div>
)}
```

**CSS Addition:** `frontend/src/styles/GameDashboard.css`

```css
.transaction-detail.expense-change {
  font-size: 12px;
  color: #ffd700;
  margin-left: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.transaction-detail.expense-change.positive {
  color: #f44336; /* Red for increased expenses */
}

.transaction-detail.expense-change.negative {
  color: #4CAF50; /* Green for reduced expenses */
}
```

---

### Step 3: Add Tooltips/Info for Each Category

**Location:** `frontend/src/components/ExpenseBreakdown.js`

**Goal:** Help players understand what each category includes

```jsx
const EXPENSE_INFO = {
  Housing: 'Rent or mortgage payments',
  Food: 'Groceries, restaurants, dining out',
  Transport: 'Public transport, car payments, fuel, parking',
  Utilities: 'Electricity, water, internet, phone bills',
  Subscriptions: 'Netflix, Spotify, gym membership, streaming services',
  Insurance: 'Health, car, home, and other insurance premiums',
  Other: 'Pet costs, personal care, miscellaneous expenses'
};

// In the expense item rendering
<div key={expense.label} className="expense-item" title={EXPENSE_INFO[expense.label]}>
  {/* ... existing content ... */}
</div>
```

Or for a better UX, install a tooltip library:

```bash
npm install react-tooltip
```

```jsx
import { Tooltip } from 'react-tooltip';

<div 
  key={expense.label} 
  className="expense-item"
  data-tooltip-id="expense-tooltip"
  data-tooltip-content={EXPENSE_INFO[expense.label]}
>
  {/* ... existing content ... */}
</div>

<Tooltip id="expense-tooltip" />
```

---

### Step 4: Create Expense Management Modal (Optional Advanced Feature)

**Location:** Create `frontend/src/components/ExpenseManagementModal.js`

**Goal:** Let players proactively adjust expenses (not just through game choices)

```jsx
import React, { useState } from 'react';
import '../styles/ExpenseManagementModal.css';

export default function ExpenseManagementModal({ gameState, onClose, onAdjust }) {
  const [adjustments, setAdjustments] = useState({});

  const handleSliderChange = (category, newValue) => {
    setAdjustments(prev => ({
      ...prev,
      [category]: newValue - gameState[`expense_${category}`]
    }));
  };

  const handleSubmit = () => {
    // This would need a new backend endpoint: POST /api/adjust-expenses
    onAdjust(adjustments);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="expense-modal" onClick={e => e.stopPropagation()}>
        <h2>Adjust Your Expenses</h2>
        <p className="warning">⚠️ Reducing expenses may have consequences on your wellbeing</p>
        
        {/* Slider controls for each category */}
        <div className="expense-sliders">
          {/* ... sliders for each category ... */}
        </div>

        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleSubmit} className="primary">Apply Changes</button>
        </div>
      </div>
    </div>
  );
}
```

**Note:** This would require a new backend endpoint to handle proactive expense adjustments outside of the normal game flow.

---

### Step 5: Highlight Expense-Related Choices

**Location:** `frontend/src/components/ChoiceList.js`

**Goal:** Visually indicate when a choice affects specific expense categories

```jsx
// Add expense indicators to choice options
{option.effects && Object.keys(option.effects).some(key => key.startsWith('expense_')) && (
  <div className="choice-expense-indicator">
    💰 Affects expenses
  </div>
)}
```

---

## Testing the Implementation

### Test Scenario 1: Display Expense Breakdown
1. Start a new game
2. Navigate to the game dashboard
3. Verify all 7 expense categories are displayed
4. Check that the total matches `monthly_expenses`
5. Verify percentages look reasonable (housing ~40%, food ~25%, etc.)

### Test Scenario 2: Expense Category Changes
1. Look for an AI-generated option like "Cancel your Netflix subscription"
2. Choose that option
3. Verify the consequence shows `expense_subscriptions` decreased
4. Check transaction log shows the subscription change
5. Verify total `monthly_expenses` decreased accordingly

### Test Scenario 3: City/Asset Variations
1. Create games in different cities (Helsinki vs Tampere)
2. Verify Helsinki has higher housing expenses
3. Create a game with a car vs without
4. Verify transport and insurance expenses differ

### Test Scenario 4: Tooltip Information
1. Hover over each expense category
2. Verify tooltips show helpful descriptions
3. Check that players understand what each category includes

---

## Backend API Reference

### GameStateResponse Fields

```typescript
interface GameStateResponse {
  // ... existing fields ...
  expense_housing: number;
  expense_food: number;
  expense_transport: number;
  expense_utilities: number;
  expense_subscriptions: number;
  expense_insurance: number;
  expense_other: number;
}
```

### TransactionSummary Fields

```typescript
interface TransactionSummary {
  // ... existing fields ...
  expense_housing_change?: number;
  expense_food_change?: number;
  expense_transport_change?: number;
  expense_utilities_change?: number;
  expense_subscriptions_change?: number;
  expense_insurance_change?: number;
  expense_other_change?: number;
}
```

### Example API Response

```json
{
  "game_state": {
    "monthly_expenses": 1200,
    "expense_housing": 500,
    "expense_food": 300,
    "expense_transport": 100,
    "expense_utilities": 140,
    "expense_subscriptions": 60,
    "expense_insurance": 70,
    "expense_other": 30
  },
  "transaction_summary": {
    "expense_subscriptions_change": -30,
    "motivation_change": -10,
    "energy_change": -5
  }
}
```

---

## Design Considerations

### Visual Hierarchy
- **Primary**: Total monthly expenses (most important number)
- **Secondary**: Individual category breakdown (detailed view)
- **Tertiary**: Changes in transaction log (historical context)

### Color Coding
- Use **green** for reduced expenses (savings)
- Use **red** for increased expenses (costs going up)
- Use **yellow/gold** for neutral display of current values

### Responsive Design
- On mobile: Consider collapsing expense breakdown into expandable section
- On desktop: Show breakdown alongside main dashboard
- Always keep total expenses visible

### User Education
- Add tooltips explaining each category
- Show percentage of total for each category
- Highlight that expense changes have consequences (not "free" savings)

---

## Future Enhancements

1. **Expense Comparison Chart**
   - Compare player's expenses to average for their city/age
   - Show how expenses change over time

2. **Expense Goals**
   - Let players set target expense levels
   - Track progress toward expense reduction goals

3. **Smart Suggestions**
   - AI suggests which expenses to cut based on player's situation
   - Show potential savings vs. consequences

4. **Expense History Graph**
   - Line chart showing how each category changes over time
   - Identify spending patterns

5. **Budget Planner Mode**
   - Let players plan future expense adjustments
   - Simulate consequences before committing

---

## Troubleshooting

### Issue: Expense categories don't sum to monthly_expenses
**Solution:** Check `apply_decision_effects()` in `backend/game_engine.py` - it should recalculate the total from categories.

### Issue: AI not generating expense category changes
**Solution:** Verify `build_consequence_prompt()` in `backend/ai_narrative.py` is passing all 7 expense values to the template.

### Issue: Transaction log not showing expense changes
**Solution:** Check that `TransactionSummary` includes expense category change fields in the API response.

### Issue: Expense breakdown not displaying
**Solution:** Verify `GameStateResponse` includes all expense fields and frontend is accessing them correctly.

---

## Summary

The expense categories feature gives players:
1. **Transparency** - See exactly where their money goes
2. **Control** - Make informed decisions about lifestyle changes
3. **Consequences** - Learn that cutting expenses has trade-offs (energy, motivation, social)
4. **Realism** - Mirrors real-life budgeting decisions

The backend is fully implemented and ready. Follow this guide to build the frontend UI and give players full visibility into their expense breakdown.
