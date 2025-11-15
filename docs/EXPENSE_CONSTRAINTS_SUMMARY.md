# Expense Constraints & Health Impact System

## Overview

This system ensures realistic expense management by enforcing minimum living standards and applying health consequences when players cut expenses too low.

## Key Features

### 1. Minimum Expense Constraints

Players **cannot** reduce expenses below these minimums (automatically enforced):

| Category | Minimum | Helsinki Min | Notes |
|----------|---------|--------------|-------|
| Housing | €300 | €400 | Shared room, poor conditions |
| Food | €150 | €150 | ⚠️ Bare minimum nutrition (dangerous) |
| Transport | €30 | €30 | Basic public transport |
| Utilities | €50 | €50 | Cannot turn off electricity/water |
| Insurance | €20 | €20 | Minimum health coverage |
| Other | €20 | €20 | Basic hygiene, personal care |
| Subscriptions | €0 | €0 | Fully optional |

### 2. Health Impact Thresholds

When expenses are reduced, players experience **real consequences**:

#### Food (Most Critical)
- **€150 or below**: -3 energy, -1 motivation per month (malnutrition)
- **€150-200**: -1 energy per month (poor diet)
- **€200-250**: Adequate (neutral)
- **€250+**: Good nutrition (potential +1 energy)

#### Housing
- **€300-350**: -2 energy, -1 social per month (poor conditions)
- **€350-500**: -1 energy per month (uncomfortable)
- **€500+**: Comfortable (neutral)

#### Transport
- **Below €50**: -1 social per month (limited mobility)
- **€50+**: Adequate (neutral)

### 3. Automatic Validation

The `validate_expense_change()` function:
- Checks if proposed reduction would go below minimum
- Caps the reduction at the minimum level
- Returns a warning message if minimum is hit
- Adjusts minimums based on city (Helsinki more expensive)

### 4. Health Impact Calculation

The `calculate_health_impact()` function:
- Evaluates new expense level against thresholds
- Returns metric changes (energy, motivation, social)
- Applied immediately when expense changes occur
- Cumulative effects over time compound consequences

## Implementation Files

### Backend Core
1. **`backend/expense_constraints.py`** (NEW)
   - `EXPENSE_MINIMUMS` - Minimum values per category
   - `EXPENSE_HEALTH_THRESHOLDS` - Health impact breakpoints
   - `validate_expense_change()` - Validates and caps expense changes
   - `calculate_health_impact()` - Calculates immediate health effects
   - `calculate_monthly_health_impact()` - Ongoing monthly effects
   - `get_expense_warning()` - Warning messages for low expenses
   - `format_expense_constraints_info()` - Info for AI prompts

2. **`backend/game_engine.py`** (UPDATED)
   - Imports constraint validation functions
   - `apply_decision_effects()` validates each expense change
   - Applies health impacts automatically
   - Prints warnings to console when minimums hit

3. **`backend/prompts/consequence_prompt.json`** (UPDATED)
   - Added expense constraint section
   - Listed all minimums with clear warnings
   - Added health impact threshold documentation
   - Updated examples to show severe malnutrition scenario
   - Instructs AI to respect minimums and apply health impacts

## Usage Example

### Scenario: Player tries to cut food budget by €150

**Current state**: `expense_food = 250`

**Requested change**: `-150` (trying to go to €100)

**System response**:
1. Validates: `validate_expense_change("food", 250, -150)`
2. Detects violation: €100 < €150 minimum
3. Caps reduction: `allowed_change = -100` (can only cut to €150)
4. Warning: "Cannot reduce food below €150/month (minimum living standard)"
5. Calculates health impact: `-3 energy, -1 motivation` (at minimum threshold)
6. Applies capped change: `expense_food = 150`
7. Applies health penalty: `energy -= 3, motivation -= 1`
8. Returns transaction summary with actual change

### AI Behavior

When AI generates expense reduction options:
- Checks current expense values
- Respects minimums (cannot suggest €100 food budget)
- Includes appropriate health impacts in narrative
- Warns player about severe consequences of minimum spending

Example AI response:
```json
{
  "narrative": "You slashed your food budget to the bare minimum of €150/month. You're eating the cheapest foods - ramen, rice, canned goods. While saving money, you're constantly hungry and lack energy. This is not sustainable.",
  "effects": {
    "expense_food_change": -100,
    "energy_change": -12,
    "motivation_change": -8,
    "social_change": -5,
    "knowledge_change": 8
  }
}
```

## Testing Checklist

- [ ] Try to reduce food budget below €150 → Should be capped
- [ ] Try to reduce housing below €300 → Should be capped  
- [ ] Try to reduce housing below €400 in Helsinki → Should be capped
- [ ] Reduce food to €150 → Should get -3 energy, -1 motivation
- [ ] Reduce food to €180 → Should get -1 energy
- [ ] Reduce housing to €320 → Should get -2 energy, -1 social
- [ ] Check console for warning messages when hitting minimums
- [ ] Verify AI respects minimums in generated options
- [ ] Check transaction log includes actual changes (not requested)

## Future Enhancements

1. **Monthly Health Checks**
   - Add `calculate_monthly_health_impact()` call at start of each month
   - Apply ongoing penalties for sustained low spending
   - Compound effects over time

2. **Recovery System**
   - When expenses increase above thresholds, gradually restore health
   - Not instant recovery - takes time to rebuild

3. **Dynamic Minimums**
   - Adjust based on player's assets (car ownership = higher transport minimum)
   - Consider family status, health conditions, etc.

4. **Warning Notifications**
   - Popup warnings before accepting dangerous expense cuts
   - "Are you sure? This will severely impact your health!"

5. **Educational Content**
   - Link warnings to learning moments about nutrition, housing quality
   - Real-world data about minimum living costs

## Related Documentation

- **Frontend Guide**: `docs/EXPENSE_CATEGORIES_FRONTEND_GUIDE.md`
- **API Documentation**: `docs/API_DOCUMENTATION.md`
- **Database Schema**: `docs/DATABASE.md`

---

**Key Takeaway**: Cutting expenses saves money but has **real consequences**. The game teaches that financial decisions involve trade-offs, and some expenses cannot be eliminated without harming wellbeing.
