# API Configuration

This directory contains the centralized API configuration for the frontend application.

## Files

- `api.js` - Main configuration module for API base URL

## Usage

### Importing the API URL

```javascript
import { API_URL } from '../config/api';

// Use in your API calls
const response = await axios.get(`${API_URL}/api/game/${sessionId}`);
```

### Environment Variables

The API URL is controlled by the `REACT_APP_API_URL` environment variable:

#### Local Development

Create a `.env.local` file in the frontend root directory:

```bash
REACT_APP_API_URL=http://localhost:8000
```

#### Production (behind nginx)

When deployed behind nginx with same-origin API routing, **do not set** `REACT_APP_API_URL`. It will automatically default to `/api`, allowing requests like:

- `/api/game/123`
- `/api/auth/login`
- etc.

#### Production (different domain)

If your API is on a different domain:

```bash
REACT_APP_API_URL=https://api.yourdomain.com
```

### Helper Functions

The module also exports helper functions:

```javascript
import { buildApiUrl, getApiUrl } from '../config/api';

// Build a complete API URL
const url = buildApiUrl('/game/123');
// Returns: "/api/game/123" or "http://localhost:8000/game/123"

// Get the base API URL
const base = getApiUrl();
// Returns: "/api" or "http://localhost:8000"
```

## Migration Notes

All files in the frontend have been updated to use this centralized configuration. Previously, each file had its own:

```javascript
// OLD - Don't do this anymore
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

Now all files import from this module:

```javascript
// NEW - Correct approach
import { API_URL } from '../config/api';
```

This ensures:
- ✅ Single source of truth
- ✅ Consistent default behavior
- ✅ Easy to maintain
- ✅ Works behind nginx without configuration

