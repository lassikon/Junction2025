# Account System Implementation Guide

## ✅ What's Been Implemented

We've successfully implemented a complete account system with authentication, test mode, and persistent user profiles!

### Backend Changes

1. **New Database Models** (`backend/models.py`):
   - `Account` - User accounts with hashed passwords
   - `SessionToken` - Session-based authentication tokens
   - Updated `PlayerProfile` - Added `account_id` and `is_test_mode` fields
   - Updated `LeaderboardEntry` - Added `account_id` and `is_test_mode` fields

2. **Authentication Utilities** (`backend/auth_utils.py`):
   - Password hashing with bcrypt
   - Session token generation and validation
   - Auth dependency helpers for FastAPI

3. **New API Endpoints**:
   - `POST /api/auth/register` - Create new account
   - `POST /api/auth/login` - Login to account
   - `POST /api/auth/logout` - Logout and invalidate token
   - `GET /api/account/profile` - Get account profile and defaults
   - `PUT /api/account/onboarding` - Update onboarding defaults

4. **Updated Endpoints**:
   - `POST /api/onboarding` - Now supports optional authentication (links to account or creates guest session)
   - `GET /api/leaderboard` - Now filters out test mode by default

5. **Database Migration** (`backend/alembic/versions/001_add_account_system.py`):
   - Creates accounts and session_tokens tables
   - Adds account_id and is_test_mode columns to existing tables

### Frontend Changes

1. **New Components**:
   - `LandingPage` - New entry point with 3 options (Login, Register, Guest)
   - `RegisterForm` - Account registration form
   - `LoginForm` - Login form
   - Styles: `LandingPage.css`, `AuthForm.css`

2. **Updated Components**:
   - `Onboarding` - Now accepts `defaultData` prop to pre-fill for returning users
   - `OnboardingPage` - Fetches account defaults, supports guest mode
   - `App.js` - Updated routing to use LandingPage

3. **State Management** (`gameStore.js`):
   - Added authentication state (token, accountId, username, displayName, hasCompletedOnboarding)
   - Added `setAuth`, `clearAuth`, `setTestMode`, `clearAll` methods

4. **API Layer** (`api/lifesim.js`):
   - Added `getAuthHeaders()` helper
   - Updated `useOnboarding` to send auth headers

---

## 🚀 How to Use the New System

### Setup & Migration

1. **Install Dependencies**:
```bash
cd backend
pip install bcrypt>=4.0.0
# Or rebuild Docker container: docker-compose build backend
```

2. **Run Database Migration**:
```bash
cd backend
# If using Docker:
docker-compose exec backend alembic upgrade head

# If running locally:
alembic upgrade head
```

### Three User Flows

#### 1. **New User (Create Account)**
1. Start at landing page
2. Click "✨ Create Account"
3. Fill in:
   - Username (3-50 chars)
   - Display Name (optional)
   - Password (min 6 chars)
4. Complete onboarding (7 steps)
5. Onboarding data is saved to account
6. Start playing!

**Benefits:**
- ✅ Onboarding saved (only do it once)
- ✅ Can play multiple games
- ✅ Scores saved to leaderboard
- ✅ Can resume anytime

#### 2. **Returning User (Login)**
1. Start at landing page
2. Click "🔐 Login"
3. Enter username and password
4. If first game: Complete onboarding (pre-filled with saved data)
5. If not first game: Start new game (onboarding pre-filled)
6. Play!

**Benefits:**
- ✅ Onboarding pre-filled (can edit)
- ✅ All scores linked to account
- ✅ Compete on leaderboard

#### 3. **Guest Mode (Test Mode)**
1. Start at landing page
2. Click "👤 Play as Guest (Test Mode)"
3. Complete onboarding (not saved)
4. Play the game
5. See yellow banner: "Playing in Guest Mode"

**Limitations:**
- ⚠️ Onboarding not saved
- ⚠️ Scores NOT saved to leaderboard
- ⚠️ Cannot resume game later

---

## 🧪 Testing Checklist

### Backend API Tests

Test each endpoint using curl or the FastAPI docs at `http://localhost:8000/docs`:

**1. Register Account:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "display_name": "Test User"
  }'
```
Expected: Returns `{token, account_id, username, display_name, has_completed_onboarding: false}`

**2. Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```
Expected: Returns `{token, account_id, username, display_name, has_completed_onboarding}`

**3. Get Account Profile (requires token):**
```bash
curl http://localhost:8000/api/account/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
Expected: Returns account details and defaults

**4. Onboarding (with auth):**
```bash
curl -X POST http://localhost:8000/api/onboarding \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "player_name": "TestPlayer",
    "age": 25,
    "city": "Helsinki",
    "education_path": "university",
    "risk_attitude": "balanced",
    "monthly_income": 2500,
    "monthly_expenses": 1500,
    "starting_savings": 1000,
    "starting_debt": 0,
    "aspirations": {"own_home": true}
  }'
```
Expected: Links to account, is_test_mode=false, saves defaults

**5. Onboarding (guest mode):**
```bash
curl -X POST http://localhost:8000/api/onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "player_name": "GuestPlayer",
    "age": 25,
    "city": "Helsinki",
    "education_path": "university",
    "risk_attitude": "balanced",
    "monthly_income": 2500,
    "monthly_expenses": 1500,
    "starting_savings": 0,
    "starting_debt": 0,
    "aspirations": {}
  }'
```
Expected: account_id=null, is_test_mode=true

**6. Leaderboard:**
```bash
# Default (no test mode)
curl http://localhost:8000/api/leaderboard

# With test mode
curl http://localhost:8000/api/leaderboard?include_test_mode=true
```
Expected: First call excludes test mode entries, second includes them

### Frontend Tests

**1. Landing Page:**
- [ ] Navigate to `http://localhost:4000`
- [ ] See 3 buttons: Login, Create Account, Play as Guest
- [ ] See features section at bottom

**2. Create Account Flow:**
- [ ] Click "Create Account"
- [ ] Fill out registration form
- [ ] Passwords must match
- [ ] See error if username taken
- [ ] Successfully register → redirect to onboarding
- [ ] Complete onboarding
- [ ] Start game

**3. Login Flow:**
- [ ] Go back to landing page
- [ ] Click "Login"
- [ ] Enter credentials
- [ ] Login → redirect to onboarding
- [ ] Onboarding should be pre-filled with saved data
- [ ] Can edit and start new game

**4. Guest Mode Flow:**
- [ ] Go to landing page
- [ ] Click "Play as Guest"
- [ ] See yellow banner: "Playing in Guest Mode"
- [ ] Complete onboarding
- [ ] Play game
- [ ] Game works normally
- [ ] After completion, score NOT on leaderboard

**5. Persistence Test:**
- [ ] Create account and play game
- [ ] Close browser
- [ ] Open again → should still be logged in (token in localStorage)
- [ ] Start new game → onboarding pre-filled

---

## 🔧 Troubleshooting

### Issue: "alembic: command not found"
**Solution:** Migration is already created manually. Just run migrations inside Docker:
```bash
docker-compose exec backend alembic upgrade head
```

### Issue: "Username already taken"
**Solution:** Either:
- Use a different username
- Or clear the database: `rm backend/lifesim.db` and re-run migrations

### Issue: "Authorization header missing"
**Solution:** This is expected for guest mode. Only affects authenticated endpoints.

### Issue: Onboarding not pre-filling
**Solution:** Make sure:
1. User is logged in (check localStorage for authToken)
2. Has completed onboarding at least once
3. Browser didn't clear localStorage

### Issue: Test mode scores appearing on leaderboard
**Solution:** Check that `is_test_mode=False` in leaderboard query (it's the default)

---

## 📊 Database Schema

### accounts
- id (PK)
- username (unique)
- password_hash
- display_name
- created_at
- last_login
- has_completed_onboarding
- default_* (onboarding defaults)

### session_tokens
- id (PK)
- token (unique)
- account_id (FK → accounts)
- created_at
- expires_at
- is_active

### player_profiles (updated)
- **NEW:** account_id (FK → accounts, nullable)
- **NEW:** is_test_mode (boolean)
- ... (all existing fields)

### leaderboard (updated)
- **NEW:** account_id (FK → accounts, nullable)
- **NEW:** is_test_mode (boolean)
- ... (all existing fields)

---

## 🎯 Key Features Summary

✅ **Account Registration** - Username + password (bcrypt hashed)
✅ **Login/Logout** - Session token-based authentication
✅ **Guest Mode** - Play without account, no leaderboard saves
✅ **Onboarding Persistence** - Save preferences, only do it once
✅ **Pre-filled Onboarding** - Returning users see saved data
✅ **Leaderboard Filtering** - Test mode excluded by default
✅ **Multiple Games** - Users can play multiple games per account
✅ **Secure** - Passwords hashed, tokens expire after 30 days

---

## 🚦 Next Steps (Optional Enhancements)

1. **Add "Continue Game" button** - Show active games for logged-in users
2. **Add email field** - For future password reset feature
3. **Add "Forgot Password"** - Email-based password reset
4. **Add profile editing** - Let users update username/display name
5. **Add game history view** - Show all past games for an account
6. **Add logout button** - In game UI or settings
7. **Add "Delete Account"** - GDPR compliance
8. **Add rate limiting** - Prevent brute force attacks on login

---

## 💡 Tips for Teachers/Educators

### Recommended Setup:
1. **Create a demo account** - username: "demo", password: "demo123"
2. **Use test mode** - For quick demos without cluttering leaderboard
3. **Reset database** - Between teaching sessions if needed
4. **Share credentials** - Students can create accounts or use test mode

### Best Practices:
- **Test Mode** - Perfect for classroom demos
- **Real Accounts** - For student assignments/competitions
- **Leaderboard** - Show only real accounts for competition
- **Privacy** - No email required, minimal data collection

---

Enjoy the new account system! 🎮💰🏆

