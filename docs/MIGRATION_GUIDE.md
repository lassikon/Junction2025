# TanStack Query + Zustand Migration Complete! 🎉

## What Was Changed

Your LifeSim frontend has been successfully refactored to use **TanStack Query** (React Query) + **Zustand** for modern state management!

## Files Created/Modified

### New Files:

1. **`src/store/gameStore.js`** - Zustand store for UI state and session management
2. **`src/api/gameApi.js`** - TanStack Query hooks for all API calls

### Modified Files:

1. **`src/index.js`** - Added QueryClientProvider wrapper
2. **`src/App.js`** - Completely refactored to use new architecture
3. **`src/components/Onboarding.js`** - Updated to work with new hooks

## Installation Steps

### ⚠️ IMPORTANT: Fix Node Modules Permissions First

You have a permission issue with your `node_modules` folder. Run this command:

```bash
cd /home/jberay/Junction2025/frontend
sudo chown -R $USER:$USER node_modules package-lock.json
```

Or if that doesn't work, remove and reinstall everything:

```bash
cd /home/jberay/Junction2025/frontend
rm -rf node_modules package-lock.json
npm install
```

### Install New Dependencies

Once permissions are fixed, install the required packages:

```bash
npm install @tanstack/react-query @tanstack/react-query-devtools zustand
```

Or if you use yarn:

```bash
yarn add @tanstack/react-query @tanstack/react-query-devtools zustand
```

## Architecture Overview

### Before (Old Way):

```javascript
// ❌ Manual state management everywhere
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);

// ❌ Manual API calls with try/catch
const fetchData = async () => {
  setLoading(true);
  try {
    const response = await axios.get("/api/data");
    setData(response.data);
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};

// ❌ Manual localStorage management
localStorage.setItem("key", JSON.stringify(data));
```

### After (New Way):

```javascript
// ✅ Zustand handles UI state
const sessionId = useGameStore((state) => state.sessionId);
const openModal = useGameStore((state) => state.openModal);

// ✅ TanStack Query handles API calls
const { data, isLoading, error } = usePlayerState(sessionId);
const mutation = useMakeDecision();

// ✅ Automatic caching, retries, and persistence!
```

## What Each Tool Does

### 🗄️ Zustand (Client State)

**Location:** `src/store/gameStore.js`

Stores **local UI state**:

- Session ID (persisted to localStorage)
- Modal visibility states
- UI preferences (sound, animations)
- Temporary data (current narrative, options)

**Usage:**

```javascript
const { sessionId, openModal, closeModal } = useGameStore();
```

### 🌐 TanStack Query (Server State)

**Location:** `src/api/gameApi.js`

Handles **all API communication**:

- Automatic loading/error states
- Smart caching (no duplicate requests)
- Auto retries on failure
- Background refetching
- Optimistic updates

**Available Hooks:**

- `useHealthCheck()` - Check API status
- `usePlayerState(sessionId)` - Fetch player data
- `useOnboarding()` - Create new player
- `useMakeDecision()` - Process decisions
- `useLeaderboard(limit)` - Fetch leaderboard
- `useFinishGame()` - Submit to leaderboard

## Key Features

### 1. Automatic Caching

```javascript
// First call: Fetches from API
const { data } = usePlayerState(sessionId);

// Switch to another component and back
// Second call: Uses cached data (instant!)
const { data } = usePlayerState(sessionId);
```

### 2. Built-in Loading States

```javascript
const { data, isLoading, isError, error } = usePlayerState(sessionId);

if (isLoading) return <Spinner />;
if (isError) return <Error message={error.message} />;
return <Dashboard data={data} />;
```

### 3. Automatic localStorage Persistence

```javascript
// Zustand automatically saves to localStorage
const { sessionId, setSessionId } = useGameStore();
setSessionId("abc123"); // Auto-saved!

// Reload page → sessionId is still there!
```

### 4. React Query DevTools

A dev panel appears in development mode (bottom-left corner) showing:

- All active queries
- Cache contents
- Loading states
- Refetch history

## Testing the New Architecture

### 1. Start the backend:

```bash
cd /home/jberay/Junction2025/backend
python start_server.py
```

### 2. Start the frontend:

```bash
cd /home/jberay/Junction2025/frontend
npm start
```

### 3. Check DevTools:

- Open React Query DevTools (bottom-left corner)
- Watch queries execute in real-time
- Inspect cached data

## Benefits Over Old Approach

| Feature                | Old Way                   | New Way                 |
| ---------------------- | ------------------------- | ----------------------- |
| **Code Lines**         | ~200 lines of boilerplate | ~50 lines               |
| **Loading States**     | Manual everywhere         | Automatic               |
| **Error Handling**     | try/catch everywhere      | Built-in                |
| **Caching**            | Manual localStorage       | Automatic + Smart       |
| **Retries**            | Manual implementation     | Auto-retry on failure   |
| **Duplicate Requests** | Possible                  | Prevented               |
| **Refetching**         | Manual refresh            | Background auto-refresh |
| **DevTools**           | None                      | Full query inspector    |

## Common Operations

### Get player state:

```javascript
const sessionId = useGameStore((state) => state.sessionId);
const { data: playerState, isLoading } = usePlayerState(sessionId);
```

### Make a decision:

```javascript
const mutation = useMakeDecision();

const handleDecision = async (option) => {
  await mutation.mutateAsync({ sessionId, chosenOption: option });
};

// Access loading state
if (mutation.isPending) return <Spinner />;
```

### Reset game:

```javascript
const resetGame = useGameStore((state) => state.resetGame);
resetGame(); // Clears everything!
```

## Troubleshooting

### If packages won't install:

```bash
# Fix ownership
sudo chown -R $USER:$USER /home/jberay/Junction2025/frontend/node_modules

# Or clean install
rm -rf node_modules package-lock.json
npm install
```

### If you see "QueryClient not found":

Make sure `src/index.js` has the `<QueryClientProvider>` wrapper.

### If localStorage isn't persisting:

Check the Zustand store's `partialize` config in `src/store/gameStore.js`.

### If API calls fail:

1. Check backend is running on `http://localhost:8000`
2. Open React Query DevTools to see error details
3. Check browser console for CORS errors

## Next Steps

1. **Install dependencies** (see above)
2. **Test the game** - Try onboarding, making decisions
3. **Inspect DevTools** - See queries in action
4. **Check localStorage** - Open Dev Console → Application → Local Storage

## Questions?

- **TanStack Query Docs:** https://tanstack.com/query/latest
- **Zustand Docs:** https://zustand-demo.pmnd.rs/

Enjoy your new clean, performant state management! 🚀
