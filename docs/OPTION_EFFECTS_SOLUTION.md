# Option Mismatch Fix: Frontend-Provided Effects

## The Problem (Original)

When a player made a decision, the backend was **regenerating options with AI** to try to match the player's choice. This caused mismatches because:

1. AI is non-deterministic (generates different values each time)
2. Backend tried to match OLD options (from previous generation) with NEW options (regenerated)
3. Player saw "Invest €500" but backend applied "-€1000" from regenerated option

## Previous Attempted Solution (Didn't Work Well)

We tried creating a separate `/api/start` endpoint to avoid regeneration on the first question. This was overly complex and didn't solve the root problem.

## The Real Solution: Trust the Frontend

**Key Insight:** The frontend already has the full option data (including all effects) from when options were generated. Just send that data back!

### How It Works Now

1. **Backend generates options ONCE** (during onboarding or previous `/api/step`)
   - Options include ALL data: text, money_change, energy_change, etc.
   - Returns full option objects: `[{text: "...", money_change: -500, ...}, ...]`

2. **Frontend stores full option data** in Zustand state
   - Not just the text, but the complete option object with effects

3. **Player makes decision** → Frontend sends FULL option data back
   ```javascript
   {
     session_id: "abc123",
     chosen_option: "Invest €500 in a startup",
     option_index: 2,
     option_effects: {  // ← The full option data
       text: "Invest €500...",
       money_change: -500,
       investment_change: 500,
       energy_change: -5,
       ...
     }
   }
   ```

4. **Backend trusts frontend data** and applies effects directly
   - No AI regeneration needed
   - No matching logic needed
   - Just parse the option_effects dict and apply changes

### Benefits

✅ **No more mismatches** - Effects always match what player saw
✅ **Simpler code** - No complex matching logic
✅ **Faster** - One less AI call per decision
✅ **More reliable** - No AI non-determinism issues

## Code Changes

### Backend

**models.py:**
```python
class DecisionRequest(SQLModel):
    session_id: str
    chosen_option: str
    option_effects: Optional[Dict] = None  # ← NEW: Full option data
    option_index: Optional[int] = None

class OnboardingResponse(SQLModel):
    game_state: GameStateResponse
    initial_narrative: str
    initial_options: List[Dict] = []  # ← Changed from List[str]

class DecisionResponse(SQLModel):
    ...
    next_options: List[Dict] = []  # ← Changed from List[str]
```

**main.py `/api/step`:**
```python
# OLD: Regenerate and try to match
available_options = generate_dynamic_options(...)
chosen_option_data = available_options[request.option_index]

# NEW: Trust frontend data
if not request.option_effects:
    raise HTTPException(400, "option_effects is required")
chosen_option_data = request.option_effects
```

### Frontend

**OnboardingPage.js:**
```javascript
// Store full option data (not just text)
setNarrativeAndOptions(result.initial_narrative, result.initial_options);
```

**GamePage.js:**
```javascript
const handleChooseOption = async (chosenOption, optionIndex) => {
  const optionEffects = currentOptions[optionIndex];  // ← Get full option object
  
  const result = await decisionMutation.mutateAsync({
    sessionId,
    chosenOption,
    optionIndex,
    optionEffects,  // ← Send it back
  });
```

**ChoiceList.js:**
```javascript
// Handle options as objects with .text field
const optionText = typeof option === 'string' ? option : option.text;
```

**lifesim.js:**
```javascript
mutationFn: async ({ sessionId, chosenOption, optionIndex, optionEffects }) => {
  const response = await axios.post(`${API_URL}/api/step`, {
    session_id: sessionId,
    chosen_option: chosenOption,
    option_index: optionIndex,
    option_effects: optionEffects,  // ← Send full data
  });
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Onboarding / Previous Decision                          │
│    Backend generates options with AI                        │
│    Returns: [{text: "...", money_change: -500, ...}, ...]  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Frontend stores in Zustand                               │
│    currentOptions = full option objects                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Player sees options                                      │
│    Display: option.text for each option                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Player clicks option (index 2)                          │
│    Get: currentOptions[2]                                   │
│    Send to backend: full option object                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Backend receives option_effects                         │
│    Parse: option_effects.money_change = -500               │
│    Apply: state.money -= 500                               │
│    Generate: NEXT options with AI                          │
│    Return: next_options (full objects)                     │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
                   (cycle repeats)
```

## Why This Is Better

### Before (Problematic)
1. Backend generates options → sends text only
2. Player chooses → frontend sends text + index
3. **Backend regenerates options** (different values!)
4. Backend tries to match by index → **MISMATCH**
5. Player sees €500 but loses €1000

### After (Clean)
1. Backend generates options → sends **FULL objects**
2. Player chooses → frontend sends **SAME object back**
3. Backend applies effects from **PROVIDED object**
4. No regeneration, no matching, no mismatch!

## Edge Cases Handled

**Q: What if frontend sends malicious data?**
A: We can add validation (max/min checks) if needed. For now, we trust the frontend since it's a single-player game.

**Q: What about backward compatibility?**
A: ChoiceList handles both string and object formats. Store version bumped to 5 to clear old caches.

**Q: What if AI changes option format?**
A: We control the AI prompt. Options always have the same fields. Frontend only sends back what backend generated.

## Testing

Test scenarios:
1. ✅ Start new game → first question shows correct options
2. ✅ Choose option → effects match displayed text
3. ✅ Second question → effects still match
4. ✅ Check logs → no "option mismatch" errors
5. ✅ Investment amounts → verify €1000 stays €1000

## Migration

Store version bumped from 4 → 5. Users will see:
- Old localStorage cleared automatically
- Must start new game or continue from clean state
- No manual intervention needed

## Summary

**Before:** Backend regenerated options, causing mismatches
**After:** Frontend sends back the exact option data it received
**Result:** Perfect match between displayed text and applied effects

This is the correct, simple solution. Trust the data flow!
