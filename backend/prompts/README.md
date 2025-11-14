# LifeSim Prompts Directory

This directory contains all LLM prompt templates used by the AI narrative generation system. Separating prompts into JSON files makes them easier to maintain, version, and customize without touching the code.

## Files

### narrative_prompt.json
Templates for generating event narratives (the story presented to the player).

**Structure:**
- `system_context`: Base system message for AI
- `tone_guidance`: Tone adjustments based on player risk attitude
  - `risk_averse`: Reassuring and supportive
  - `balanced`: Practical and straightforward
  - `risk_seeking`: Exciting and opportunity-focused
- `event_descriptions`: Context for each event type
- `curveball_instruction`: Template for unexpected events
- `regular_event_instruction`: Template for regular events
- `format_instruction`: Output format guidelines

**Used by:** `generate_event_narrative()` and `build_narrative_prompt()`

---

### consequence_prompt.json
Templates for generating consequence narratives (feedback after a decision).

**Structure:**
- `system_context`: System role for consequence generation
- `instruction`: What the AI should do
- `template`: Information template with player state

**Used by:** `generate_consequence_narrative()` and `build_consequence_prompt()`

---

### learning_moment_prompt.json
Templates for generating educational insights (financial literacy tips).

**Structure:**
- `system_context`: Educational coach persona
- `instruction`: Guidelines for creating tips
- `template`: Information template with financial metrics

**Used by:** `generate_learning_moment()`

**Note:** Learning moments appear ~30% of the time to avoid overwhelming the player.

---

### fallback_narratives.json
Pre-written narratives used when AI is unavailable.

**Structure:**
- Event-specific narrative templates with placeholders
- Supports formatting with state variables:
  - `{monthly_income}`: Player's monthly income
  - `{monthly_expenses}`: Player's monthly expenses
  - `{target}`: Calculated target (e.g., 3 months expenses)
  - `{money}`: Current cash/savings
  - `{debts}`: Current debt amount

**Used by:** `get_fallback_narrative()`

**Included events:**
- first_paycheck
- budget_decision
- emergency_fund
- investment_opportunity
- career_opportunity
- lifestyle_choice
- debt_management
- social_event
- education_opportunity
- default (catch-all)

---

## Usage Example

```python
from ai_narrative import (
    generate_event_narrative,
    generate_consequence_narrative,
    generate_learning_moment
)

# Generate event narrative
narrative = generate_event_narrative(
    event_type="first_paycheck",
    state=game_state,
    profile=player_profile,
    client=gemini_client
)

# Generate consequence after decision
consequence = generate_consequence_narrative(
    chosen_option="Save 50% for emergency fund",
    option_effect={"explanation": "Building emergency fund"},
    state=updated_game_state,
    profile=player_profile,
    client=gemini_client
)

# Maybe get a learning moment
learning = generate_learning_moment(
    chosen_option="Save 50% for emergency fund",
    state=updated_game_state,
    profile=player_profile,
    client=gemini_client
)
```

---

## Customization Guide

### Adding a New Event Type

1. **Update `narrative_prompt.json`:**
   ```json
   "event_descriptions": {
     "your_new_event": "Description for the AI to understand the context"
   }
   ```

2. **Update `fallback_narratives.json`:**
   ```json
   {
     "your_new_event": "Fallback narrative text with {placeholders}"
   }
   ```

3. No code changes needed! The system automatically loads and uses the new templates.

### Adjusting AI Tone

Edit `tone_guidance` in `narrative_prompt.json`:
```json
"tone_guidance": {
  "risk_averse": "Your custom tone guidance",
  "balanced": "Your custom tone guidance",
  "risk_seeking": "Your custom tone guidance"
}
```

### Modifying Learning Moment Style

Edit `instruction` in `learning_moment_prompt.json` to change how educational tips are generated.

---

## Template Variable Reference

### State Variables (used in fallbacks)
- `monthly_income`: €2700.0
- `monthly_expenses`: €1400.0
- `money`: €5000.0
- `debts`: €0.0
- `target`: Calculated value (e.g., monthly_expenses * 3)

### Formatting
All monetary values should use `€` symbol and `.0f` formatting for whole euros:
```json
"example": "You have €{money:.0f} in your account"
```

---

## Benefits of JSON Prompts

✅ **Easy to edit** - No need to dive into Python code
✅ **Version control** - Track prompt changes separately from logic
✅ **A/B testing** - Easy to swap different prompt sets
✅ **Localization** - Simpler to create translations
✅ **Non-technical editing** - Game designers can modify without coding
✅ **Consistency** - Centralized prompt management

---

## Testing

After modifying prompts, test with:
```bash
python test_game_flow.py
```

Or test individual functions:
```python
from ai_narrative import load_prompt_template

prompts = load_prompt_template("narrative_prompt.json")
print(prompts['event_descriptions']['first_paycheck'])
```
