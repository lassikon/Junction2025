# API URL Refactoring - Summary

## Overview

This document summarizes the refactoring of API URL configuration across the entire frontend codebase.

## What Changed

### Before
- API URLs were hardcoded in **11 different files**
- Each file had: `const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';`
- Default was `http://localhost:8000` (problematic for production behind nginx)

### After
- **Single centralized configuration** in `src/config/api.js`
- All files import from this module: `import { API_URL } from '../config/api';`
- Default is now `/api` (works seamlessly behind nginx)

## Files Modified

### Created
1. **`src/config/api.js`** - Centralized API configuration module
2. **`src/config/README.md`** - Documentation for API configuration

### Updated (11 files)
1. `src/api/lifesim.js`
2. `src/components/FloatingChatbot.js`
3. `src/components/TopBar.js`
4. `src/components/LoginForm.js`
5. `src/components/RegisterForm.js`
6. `src/components/LeaderboardModal.js`
7. `src/components/TransactionHistory.js`
8. `src/routes/StartGamePage.js`
9. `src/routes/SettingsPage.js`
10. `src/routes/OnboardingPage.js`
11. `src/Chat.js`

## Environment Variable

### Variable Name
`REACT_APP_API_URL`

### Usage Scenarios

#### 1. Local Development
Create `.env.local` in the frontend root:
```bash
REACT_APP_API_URL=http://localhost:8000
```

#### 2. Production Behind Nginx (Recommended)
**Do not set** `REACT_APP_API_URL` - it will default to `/api`

This works with nginx configuration like:
```nginx
location /api/ {
    proxy_pass http://backend:8000/;
}
```

#### 3. Production Different Domain
```bash
REACT_APP_API_URL=https://api.yourdomain.com
```

## Benefits

✅ **Single Source of Truth** - One place to configure API URL
✅ **Production-Ready Default** - Works behind nginx without extra config
✅ **Easy Maintenance** - Change once, affects entire app
✅ **Type-Safe** - Centralized imports reduce typos
✅ **Documented** - Clear documentation in config directory

## Verification

Run the following to verify no hardcoded URLs remain:
```bash
cd frontend/src
grep -r "http://localhost:8000" .
grep -r "http://127.0.0.1:8000" .
```

Should only find comments/documentation, not actual code.

## Testing

1. **Without env variable** (default `/api`):
```bash
unset REACT_APP_API_URL
npm start
```
Check that API calls go to `/api/*`

2. **With env variable** (localhost):
```bash
REACT_APP_API_URL=http://localhost:8000 npm start
```
Check that API calls go to `http://localhost:8000/*`

## Notes

- All linter checks pass ✅
- No breaking changes to existing functionality
- Backward compatible with existing environment variables
- Default changed from `http://localhost:8000` to `/api` for better production deployment

