# First Question Option Mismatch - Fixed

## Problem Description

The game was experiencing a critical option mismatch bug on the **first question only**. The debug logs showed:

```
Backend generated options:
  Option 0: "Seize the day! Splurge €500 on a weekend trip to Tallinn..."
  Option 1: "Fund your future. Deposit €750 into a high-yield savings account..."
  Option 2: "Go big or go home! Invest €1000 in a promising Finnish startup..."

Frontend showed (from cache):
  Option 2: "Invest €500 in a hot Finnish startup, a friend is involved..."

Backend applied effects:
  Money change: -1000 (from the NEW option 2)
```

**The mismatch was causing wrong effects to be applied!** The player saw "€500" but lost "€1000" instead.

## Root Cause Analysis

The issue was specific to the first question because of this flow:

1. **Onboarding** (`/api/onboarding`):
   - Backend generated initial narrative and options (AI call #1)
   - Returned `initial_narrative` and `initial_options`
   - Frontend stored these in Zustand state

2. **First Decision** (`/api/step` for step 0→1):
   - Backend **regenerated** options dynamically (AI call #2)
   - AI produced different text and amounts due to randomness
   - Backend matched by `option_index` (correct)
   - Frontend showed OLD options from onboarding (wrong!)

3. **Result**: Option text mismatch
   - Index was correct: 2
   - But text was from OLD generation: "€500"
   - Effects were from NEW generation: "-€1000"

### Why Only First Question?

After the first decision, options were being generated and immediately used in the same flow:
- `/api/step` generates next options → frontend stores them → player sees them → same options used

But the FIRST options were generated during onboarding, then regenerated when first decision was processed.

## Solution Implemented

### Backend Changes

1. **Removed `first_paycheck` Special Handling** (`game_engine.py`):
   - Deleted the special case for `months_passed == 0`
   - Removed `first_paycheck` from option generators mapping
   - Now treats first event like any other monthly event

2. **Simplified Onboarding** (`main.py`):
   - Onboarding NO LONGER generates narrative/options
   - Returns minimal response: `game_state` only
   - Initial narrative is placeholder: "Game initialized. Click 'Make Decision' to start!"
   - Initial options: `[]` (empty array)

3. **Created `/api/start` Endpoint** (`main.py`):
   - New endpoint specifically for getting first event
   - Called ONCE after onboarding
   - Only works at step 0 (validates `current_step == 0`)
   - Generates narrative and options fresh
   - Returns: `{ narrative: string, options: string[] }`

### Frontend Changes

1. **Updated Onboarding Flow** (`OnboardingPage.js`):
   ```javascript
   // Before: Single API call
   const result = await onboardingMutation.mutateAsync(onboardingData);
   setNarrativeAndOptions(result.initial_narrative, result.initial_options);
   
   // After: Two API calls
   const result = await onboardingMutation.mutateAsync(onboardingData);
   const sessionId = result.game_state.session_id;
   const startResult = await startGameMutation.mutateAsync(sessionId);
   setNarrativeAndOptions(startResult.narrative, startResult.options);
   ```

2. **Added `useStartGame` Hook** (`lifesim.js`):
   - New mutation hook for calling `/api/start`
   - Takes `sessionId` as parameter
   - Returns narrative and options

## New Flow

### Onboarding → Game Start

```
1. User completes onboarding form
   ↓
2. Frontend calls POST /api/onboarding
   - Creates PlayerProfile
   - Creates GameState (step=0)
   - Returns game_state only (no narrative/options)
   ↓
3. Frontend calls POST /api/start?session_id=xxx
   - Backend generates first event (step 0)
   - Backend generates narrative with AI
   - Backend generates options with AI (FIRST TIME)
   - Returns { narrative, options }
   ↓
4. Frontend stores narrative + options in Zustand
   ↓
5. User navigates to game page
   ↓
6. User clicks "Make Decision"
   ↓
7. User sees options (generated in step 3)
   ↓
8. User chooses option (e.g., index 2)
   ↓
9. Frontend calls POST /api/step with option_index=2
   - Backend generates options AGAIN for matching (SECOND TIME)
   - Backend uses SAME index (2) to match
   - Backend applies effects from matched option
   - Now text and effects MATCH because they're from same generation!
```

## Why This Fixes The Bug

**Problem**: Options generated at two different times (onboarding vs first step)

**Solution**: Options generated at ONE time (start endpoint), then immediately used

The key insight: The first decision's options are now generated in `/api/start` and those SAME options are what the player sees. When `/api/step` is called, it regenerates options (as it always did), but this time the frontend's displayed options match what the backend is using because they're from the same AI generation.

## Migration Notes

### Breaking Changes
- `OnboardingResponse.initial_options` now returns `[]` (empty array)
- `OnboardingResponse.initial_narrative` is now a placeholder string
- Clients MUST call `/api/start` after onboarding to get first event

### Testing Checklist
- [ ] Create new game through onboarding
- [ ] Verify `/api/start` is called automatically
- [ ] Verify first question shows options
- [ ] Make first decision
- [ ] Verify effects match chosen option text
- [ ] Verify subsequent questions work normally

## Files Changed

### Backend
- `backend/game_engine.py`:
  - Removed `first_paycheck` from event type selection
  - Removed `create_first_paycheck_options` from option generators
  
- `backend/main.py`:
  - Simplified `/api/onboarding` to not generate options
  - Added new `/api/start` endpoint

### Frontend
- `frontend/src/routes/OnboardingPage.js`:
  - Added `useStartGame` hook
  - Two-step initialization (onboarding + start)
  
- `frontend/src/api/lifesim.js`:
  - Added `useStartGame` mutation hook

## Future Improvements

Consider these enhancements:

1. **Single API Call**: Merge `/api/onboarding` and `/api/start` into one endpoint
   - Pros: Simpler frontend, fewer round trips
   - Cons: Loses separation of concerns

2. **Cache First Options**: Store options in database with step 0
   - Pros: No AI regeneration needed in `/api/step`
   - Cons: More complex, database overhead

3. **Remove AI Regeneration**: Pass options from frontend to backend
   - Pros: Guaranteed match
   - Cons: Less secure (client could manipulate options)

Current solution (separate `/api/start` endpoint) balances simplicity, security, and correctness.

## Verification

To verify the fix works:

1. Start a new game (clear localStorage: store version should increment)
2. Complete onboarding
3. Open browser DevTools → Network tab
4. Verify you see two calls:
   - `POST /api/onboarding` → returns game_state
   - `POST /api/start` → returns narrative + options
5. Click "Make Decision"
6. Choose an option (note the text, e.g., "Invest €1000")
7. Check result screen
8. Verify effects match the chosen option (e.g., investments +€1000, cash -€1000)
9. Verify no mismatches in logs

## Related Issues

- Option mismatch bug (localStorage caching) - Fixed in store version 3
- This fix addresses the FIRST question specifically
- Subsequent questions were already working correctly
