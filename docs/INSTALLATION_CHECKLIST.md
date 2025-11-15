# 🎯 Installation & Testing Checklist

## ✅ Step-by-Step Guide

### 1️⃣ Install Dependencies

```bash
cd /home/jberay/Junction2025/frontend
```

**If you have permission issues:**

```bash
# Option A: Fix ownership
sudo chown -R $USER:$USER node_modules package-lock.json

# Option B: Clean install
rm -rf node_modules package-lock.json
```

**Then install:**

```bash
npm install @tanstack/react-query @tanstack/react-query-devtools zustand
```

**Verify installation:**

```bash
npm list @tanstack/react-query zustand
```

Should show:

```
├── @tanstack/react-query@x.x.x
├── @tanstack/react-query-devtools@x.x.x
└── zustand@x.x.x
```

---

### 2️⃣ Start Backend

```bash
cd /home/jberay/Junction2025/backend
python start_server.py
```

**Expected output:**

```
🚀 Starting up LifeSim API...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test backend:**

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

### 3️⃣ Start Frontend

```bash
cd /home/jberay/Junction2025/frontend
npm start
```

**Expected output:**

```
Compiled successfully!
Local: http://localhost:4000
```

---

### 4️⃣ Test the Application

#### Test 1: API Status ✅

- Open http://localhost:4000
- Top bar should show: **"API: connected"** (green)
- If red, check backend is running

#### Test 2: Onboarding ✅

- Should see onboarding screen
- Fill in your details:
  - Name: [Your name]
  - Age: 25
  - City: Helsinki
  - Education: Any option
  - Risk attitude: Balanced
  - Aspirations: Select a few
- Click "Start Journey"
- Should load game dashboard

#### Test 3: React Query DevTools ✅

- Look for **React Query icon** in bottom-left corner
- Click to open DevTools panel
- Should see queries:
  - `['health']` - API health check
  - `['playerState', sessionId]` - Player data
- Queries should show as "success" (green)

#### Test 4: Game Dashboard ✅

- Should see:
  - FI Score (0-10%)
  - Money (€0-500)
  - Life metrics (Energy, Motivation, etc.)
- All values should be numbers, not undefined

#### Test 5: Make a Decision ✅

- Click "Make Decision" button
- Should see modal with:
  - Narrative text
  - 3-5 decision options
- Click an option
- Modal closes, shows consequence modal
- Click "Continue"
- Dashboard metrics should update
- **Open React Query DevTools** - See cache update!

#### Test 6: localStorage Persistence ✅

- Open browser DevTools (F12)
- Go to: Application → Local Storage → http://localhost:4000
- Should see key: `lifesim-game-storage`
- Value should contain `sessionId`
- Refresh page (F5)
- Game should still be there (no onboarding)

#### Test 7: New Game ✅

- Click "New Game" button
- Page should reload
- Should see onboarding again
- localStorage should be cleared

---

### 5️⃣ Inspect the Code

#### Check Zustand Store

```javascript
// In browser console:
window.useGameStore = require("./store/gameStore").useGameStore;
console.log(window.useGameStore.getState());

// Should show:
// { sessionId: "...", showDecisionModal: false, ... }
```

#### Check TanStack Query Cache

- Open React Query DevTools
- Click on `['playerState', sessionId]`
- Should see full player state data
- Click "Refetch" to manually trigger API call

---

## 🐛 Troubleshooting

### Problem: "Cannot find module 'zustand'"

**Solution:**

```bash
cd /home/jberay/Junction2025/frontend
npm install zustand @tanstack/react-query @tanstack/react-query-devtools
```

### Problem: "API: disconnected" (red)

**Solution:**

1. Check backend is running:
   ```bash
   curl http://localhost:8000/health
   ```
2. If not, start it:
   ```bash
   cd /home/jberay/Junction2025/backend
   python start_server.py
   ```
3. Check CORS settings in backend

### Problem: Page is blank

**Solution:**

1. Open browser console (F12)
2. Check for errors
3. Common issues:
   - Missing `QueryClientProvider` in index.js
   - Import errors for Zustand/TanStack Query
   - Backend not running

### Problem: "undefined" values everywhere

**Solution:**

1. Open React Query DevTools
2. Check if `playerState` query is successful
3. If error, check:
   - Backend is running
   - Session ID is valid
   - API endpoint returns correct data structure

### Problem: Modals don't open

**Solution:**

1. Check browser console for errors
2. Verify Zustand store:
   ```javascript
   console.log(useGameStore.getState());
   ```
3. Check `currentNarrative` and `currentOptions` are populated

### Problem: Changes not persisting

**Solution:**

1. Check localStorage:
   - DevTools → Application → Local Storage
   - Should see `lifesim-game-storage`
2. Verify Zustand persist config in `gameStore.js`

---

## 📊 Success Criteria

### ✅ Installation Success

- [ ] All 3 packages installed
- [ ] No npm errors
- [ ] `npm list` shows packages

### ✅ Backend Success

- [ ] Backend starts without errors
- [ ] `/health` endpoint returns `{"status":"healthy"}`
- [ ] No Python errors in console

### ✅ Frontend Success

- [ ] Frontend starts without errors
- [ ] No console errors in browser
- [ ] "API: connected" shows green
- [ ] React Query DevTools visible

### ✅ Functionality Success

- [ ] Onboarding completes successfully
- [ ] Game dashboard displays
- [ ] Can make decisions
- [ ] Consequences display
- [ ] Metrics update correctly
- [ ] New game works

### ✅ Architecture Success

- [ ] No `useState` for API data in App.js
- [ ] React Query DevTools shows queries
- [ ] localStorage contains `lifesim-game-storage`
- [ ] No prop drilling for gameState
- [ ] Automatic loading states work

---

## 🎉 When Everything Works

You should see:

1. ✅ **Green "API: connected"** status
2. ✅ **React Query DevTools** in bottom-left
3. ✅ **Smooth onboarding** flow
4. ✅ **Game dashboard** with metrics
5. ✅ **Decision modals** working
6. ✅ **Consequence narratives** displaying
7. ✅ **Metrics updating** after decisions
8. ✅ **localStorage persistence** working
9. ✅ **Page refresh** maintains session
10. ✅ **New game** resets everything

---

## 📚 Next Steps

Once everything works:

1. **Explore React Query DevTools** - See queries in action
2. **Inspect localStorage** - See Zustand persistence
3. **Read MIGRATION_GUIDE.md** - Understand architecture
4. **Check BEFORE_AFTER_COMPARISON.md** - See code improvements
5. **Review QUICK_REFERENCE.js** - Learn common patterns

---

## 🆘 Still Having Issues?

1. Check all error messages carefully
2. Review browser console for errors
3. Check React Query DevTools for failed queries
4. Verify backend logs for API errors
5. Compare your code with the reference files

**Common gotchas:**

- Forgot to install packages
- Backend not running
- CORS issues
- Wrong API_URL in environment

---

**Good luck! 🚀**
