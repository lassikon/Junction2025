# AI Effect Timing Refactor - Complete

## Problem Identified

The game was applying financial effects BEFORE the AI generated the consequence narrative. This created a logical impossibility:

**Example of the bug:**
1. Player chooses: "Invest €500 in trending meme stock"
2. ✅ Game immediately applies: `+€500 investments`
3. ❌ AI generates: "Stock crashed, you lost €350 of your investment"
4. 💥 MISMATCH: Game state shows +€500, but narrative says -€350

## Root Cause

Options had predetermined effects that were applied before consequence generation:
```python
OLD_OPTION = {
    "text": "Invest €500 in meme stock",
    "money_change": -500,      # ← Predetermined
    "investment_change": 500,  # ← Applied immediately
    "explanation": "..."       # ← AI describes later
}
```

## Solution Architecture

### Two-Stage AI Prompting

**Stage 1: Option Generation (Action Descriptions Only)**
- AI generates potential ACTIONS
- NO predetermined effects
- Format: `{text, risk_level, category}`

**Stage 2: Consequence Generation (AI Determines Effects)**
- AI generates BOTH narrative AND effects
- Effects determined based on risk level and context
- Format: `{narrative: string, effects: {...}}`

### New Flow

```
1. Generate Options
   ↓
   [{text: "Invest €500...", risk_level: "high", category: "investment"}]
   
2. Player Chooses Option
   ↓
   
3. AI Generates Consequence + Effects
   ↓
   {
     narrative: "Stock crashed, lost €350...",
     effects: {
       money_change: 150,          # ← AI determined
       investment_change: -500,     # ← Based on risk
       motivation_change: -20,
       knowledge_change: 15
     }
   }
   
4. Apply Those Effects to Game State
```

## Files Changed

### 1. Prompt Files (Replaced)

**`backend/prompts/dynamic_options_prompt.json`** (NEW)
- System: "Generate potential ACTIONS, not outcomes"
- Format: `{text, risk_level, category}`
- NO effect fields (money_change, investment_change, etc.)

**`backend/prompts/consequence_prompt.json`** (NEW)
- System: "Determine what ACTUALLY happens"
- Format: `{narrative, effects: {...}}`
- Includes full effect schema with examples
- High risk actions can fail (realistic outcomes)

### 2. Backend Core (`backend/ai_narrative.py`)

**`generate_consequence_narrative()` - REFACTORED**
```python
# OLD: Returns string narrative only
async def generate_consequence_narrative(...) -> str

# NEW: Returns dict with narrative AND effects
async def generate_consequence_narrative(
    chosen_option: str,
    option_data: Dict,  # Now includes risk_level, category
    state: GameState,
    profile: PlayerProfile,
    event_narrative: str,
    state_before: Dict,  # NEW: State snapshot before effects
    db_session = None,
    client = None
) -> Dict:  # Returns {'narrative': str, 'effects': {...}}
```

**`build_consequence_prompt()` - UPDATED**
```python
# NEW: Includes risk_level, category in template
prompt_content = prompts['template'].format(
    # ... player context ...
    chosen_option=chosen_option,
    risk_level=option_data.get('risk_level', 'medium'),  # NEW
    category=option_data.get('category', 'financial'),    # NEW
    event_narrative=event_narrative                       # NEW
)
```

### 3. API Layer (`backend/main.py`)

**`/api/step` endpoint - REFACTORED**

```python
# OLD FLOW
chosen_option_data = request.option_effects
effect = setup_dynamic_option_effect(chosen_option_data)
apply_decision_effects(game_state, effect)  # ← Applied FIRST
consequence = await generate_consequence_narrative(...)  # ← Generated AFTER

# NEW FLOW
# 1. Store state BEFORE any changes
state_before = {
    'money': game_state.money,
    'investments': game_state.investments,
    # ... all metrics ...
}

# 2. Generate consequence AND effects from AI
consequence_result = await generate_consequence_narrative(
    chosen_option=request.chosen_option,
    option_data=chosen_option_data,  # {text, risk_level, category}
    state=game_state,
    profile=profile,
    event_narrative=current_narrative,
    state_before=state_before,  # ← Snapshot before effects
    db_session=db_session,
    client=client
)

consequence = consequence_result['narrative']
effects_dict = consequence_result['effects']  # ← AI determined

# 3. NOW apply the effects that AI determined
effect = setup_dynamic_option_effect(effects_dict)
apply_decision_effects(game_state, effect)

# 4. Record in history using state_before dict
decision_record = DecisionHistory(
    profile_id=profile.id,
    # ...
    money_before=state_before['money'],  # ← From dict
    fi_score_before=state_before['fi_score'],
    # ...
    money_after=game_state.money,
    # ...
    consequence_narrative=consequence,
    learning_moment=learning
)
```

### 4. Utility Functions (`backend/game_engine.py`)

**`setup_dynamic_option_effect()` - NO CHANGES NEEDED**
```python
# Already handles dict format correctly
def setup_dynamic_option_effect(option: Dict) -> DecisionEffect:
    effect = DecisionEffect()
    effect.money_change = option.get("money_change", 0)
    effect.investment_change = option.get("investment_change", 0)
    # ... etc
    return effect
```

## Benefits of New Architecture

### 1. Logical Consistency
- Narrative always matches actual game state changes
- No more "lost money" when balance went up

### 2. Dynamic Outcomes
- High risk actions can succeed OR fail
- AI determines outcomes based on:
  - Risk level
  - Player's financial situation
  - Market realities
  - Realistic probabilities

### 3. Educational Value
- Players learn about real risk/reward
- Failure teaches valuable lessons
- Success feels earned, not predetermined

### 4. Gameplay Variety
- Same action can have different outcomes
- Replayability increased
- Each playthrough feels unique

## Example Scenarios

### High Risk Action - SUCCESS
```json
{
  "option": {
    "text": "Invest €500 in trending meme stock",
    "risk_level": "high",
    "category": "investment"
  },
  "consequence": {
    "narrative": "The meme stock surged 200%! Your €500 is now worth €1,000. You're thrilled but also aware this could have easily gone the other way.",
    "effects": {
      "money_change": 0,
      "investment_change": 1000,
      "motivation_change": 25,
      "knowledge_change": 10
    }
  }
}
```

### High Risk Action - FAILURE
```json
{
  "option": {
    "text": "Invest €500 in trending meme stock",
    "risk_level": "high",
    "category": "investment"
  },
  "consequence": {
    "narrative": "The stock crashed within days. You lost €350 of your investment, with only €150 remaining. A painful but valuable lesson in speculative investing.",
    "effects": {
      "money_change": 150,
      "investment_change": -500,
      "motivation_change": -20,
      "knowledge_change": 15
    }
  }
}
```

### Low Risk Action - PREDICTABLE
```json
{
  "option": {
    "text": "Put €500 into diversified index fund",
    "risk_level": "low",
    "category": "investment"
  },
  "consequence": {
    "narrative": "You opened an index fund account and invested €500. The fund is performing steadily, earning modest but reliable returns. You feel good about this smart choice.",
    "effects": {
      "money_change": -500,
      "investment_change": 500,
      "passive_income_change": 2.5,
      "motivation_change": 10,
      "knowledge_change": 10
    }
  }
}
```

## Testing Checklist

### Backend Tests
- [ ] Options generated have only {text, risk_level, category}
- [ ] Consequence generation returns {narrative, effects}
- [ ] High risk actions produce variable outcomes
- [ ] Low risk actions produce consistent outcomes
- [ ] Effects are applied AFTER consequence generation
- [ ] DecisionHistory records state_before correctly
- [ ] TransactionLog tracks changes accurately

### Frontend Tests (Pending Updates)
- [ ] Frontend handles new option format
- [ ] No errors when options lack predetermined effects
- [ ] Consequence display works correctly
- [ ] Metrics update after consequence shown

### Integration Tests
- [ ] Complete flow: option → choice → consequence → effects
- [ ] Multiple high-risk choices show different outcomes
- [ ] Game state stays consistent with narratives
- [ ] Database records are accurate

## Known Issues

### Frontend Compatibility
⚠️ **Frontend still expects old option format**
- Currently expects: `{text, money_change, investment_change, ...}`
- Now receives: `{text, risk_level, category}`
- **Action Required**: Update frontend to handle new format

### Potential Areas
- Verify all references to old effect fields removed
- Check for any caching of option data
- Ensure error handling covers new format

## Migration Steps

1. ✅ Create new prompt files
2. ✅ Update `ai_narrative.py` consequence generation
3. ✅ Update `main.py` effect application flow
4. ✅ Fix DecisionHistory to use state_before dict
5. ⏳ Restart backend server
6. ⏳ Update frontend option handling
7. ⏳ Test complete flow end-to-end
8. ⏳ Verify AI generates realistic outcomes

## Performance Considerations

### AI Call Timing
- **Before**: 2 AI calls (options + consequences)
- **After**: Still 2 AI calls, no performance impact
- **Benefit**: Better quality outcomes

### Database Impact
- No schema changes required
- DecisionHistory already has before/after fields
- TransactionLog already tracks all changes

## Future Enhancements

### Contextual Risk
- AI could adjust risk based on player's financial stability
- "High risk when you have €100" vs "High risk when you have €10,000"

### Learning from Outcomes
- Track player's risk-taking patterns
- Adjust future option generation based on history
- "Player lost 3 times on high risk, offer more guidance"

### Dynamic Risk Levels
- Market conditions affect outcomes
- Time-based factors (bull vs bear market)
- Player's financial knowledge affects success rate

## Conclusion

This refactor fixes the fundamental timing issue where effects were applied before consequences were generated. The new two-stage AI architecture ensures:

1. **Consistency**: Narratives always match state changes
2. **Realism**: High risk actions can fail
3. **Education**: Players learn from variable outcomes
4. **Engagement**: Uncertainty makes game more interesting

The game now properly simulates financial decision-making with realistic risk/reward dynamics.
