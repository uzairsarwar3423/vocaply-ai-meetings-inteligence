# Zoom OAuth Integration - Quick Start Guide

## Your Authorization Code
```
code=tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg
```

## What Has Been Implemented

### Backend (Python/FastAPI)
✅ **Zoom OAuth Service** - `/backend/app/services/zoom_oauth.py`
- Exchanges authorization codes for Zoom tokens
- Fetches Zoom user information
- Creates/updates users in your database
- Generates app access and refresh tokens

✅ **Auth Endpoint** - `/backend/app/api/v1/auth.py`
- `POST /api/v1/auth/zoom/callback` - Handle OAuth callback

✅ **Configuration** - `/backend/app/core/config.py`
- Added ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_REDIRECT_URI settings

### Frontend (React/TypeScript)
✅ **Zoom Auth Hook** - `/frontend/hooks/useZoomAuth.ts`
- `initiateZoomLogin()` - Redirect to Zoom OAuth
- `handleZoomCallback(code)` - Exchange code for app tokens
- `getZoomAuthUrl()` - Get authorization URL

✅ **Callback Handler** - `/frontend/app/(auth)/zoom-callback/page.tsx`
- Processes OAuth callback from Zoom
- Exchanges code for app tokens
- Handles errors gracefully

✅ **TypeScript Types** - `/frontend/types/auth.ts`
- `ZoomOAuthTokens` - Zoom token structure
- `ZoomUser` - Zoom user information

✅ **Example Component** - `/frontend/components/auth/ZoomLoginExample.tsx`
- Ready-to-use Zoom login button with proper styling

## Setup Steps

### Step 1: Configure Environment Variables

#### Backend (.env)
```bash
ZOOM_CLIENT_ID=7C4gGx2Qmm_BiItxENBgg
ZOOM_CLIENT_SECRET=your-client-secret-here
ZOOM_REDIRECT_URI=https://vocaply-ai-meetings-inteligence-235.vercel.app/auth/zoom-callback
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_ZOOM_CLIENT_ID=7C4gGx2Qmm_BiItxENBgg
NEXT_PUBLIC_ZOOM_OAUTH_URL=https://zoom.us/oauth/authorize
NEXT_PUBLIC_ZOOM_REDIRECT_URI=https://vocaply-ai-meetings-inteligence-235.vercel.app/auth/zoom-callback
```

### Step 2: Update Zoom App Settings

1. Go to https://marketplace.zoom.us
2. Find your app and go to settings
3. Add **Redirect URI for OAuth**:
   ```
   https://vocaply-ai-meetings-inteligence-235.vercel.app/auth/zoom-callback
   ```
4. Copy your **Client ID** and **Client Secret**
5. Paste them into your `.env` files

### Step 3: Test the Integration

#### Option A: Test with Your Authorization Code
```bash
# Make sure backend is running on http://localhost:8000

curl -X POST http://localhost:8000/api/v1/auth/zoom/callback \
  -H "Content-Type: application/json" \
  -d '{"code": "tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg"}'
```

Expected response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Option B: Full Integration Test
1. Start backend: `make run-backend` or `python -m uvicorn app.main:app --reload`
2. Start frontend: `npm run dev`
3. Go to `http://localhost:3000/login`
4. Click "Sign in with Zoom"
5. Authorize in Zoom
6. You should be redirected to dashboard with stored auth tokens

## File Structure

```
Backend:
├── app/
│   ├── services/
│   │   └── zoom_oauth.py          ← Zoom OAuth service
│   ├── api/v1/
│   │   └── auth.py                ← OAuth callback endpoint
│   ├── schemas/
│   │   └── auth.py                ← Added ZoomOAuthCallback schema
│   └── core/
│       └── config.py              ← Added Zoom config
└── .env                            ← Add Zoom credentials here

Frontend:
├── hooks/
│   └── useZoomAuth.ts             ← Zoom OAuth hook
├── app/(auth)/
│   └── zoom-callback/
│       └── page.tsx               ← Callback handler
├── components/auth/
│   └── ZoomLoginExample.tsx       ← Example component
├── types/
│   └── auth.ts                    ← Added Zoom types
└── .env.local                     ← Add Zoom config here
```

## Usage in Your App

### Add Zoom Login Button
```tsx
import { useZoomAuth } from "@/hooks/useZoomAuth";

export function LoginPage() {
  const { initiateZoomLogin } = useZoomAuth();

  return (
    <button onClick={initiateZoomLogin}>
      Sign in with Zoom
    </button>
  );
}
```

### Get Authorization URL
```tsx
const { getZoomAuthUrl } = useZoomAuth();
const url = getZoomAuthUrl();
// url = "https://zoom.us/oauth/authorize?response_type=code&client_id=...&redirect_uri=..."
```

## OAuth Flow Diagram

```
┌─────────────┐
│   Frontend  │
│   (User)    │
└──────┬──────┘
       │
       │ 1. Click "Sign in with Zoom"
       ▼
┌─────────────────────────────────────┐
│   useZoomAuth Hook                  │
│   .initiateZoomLogin()              │
│   Redirects to Zoom                 │
└──────┬──────────────────────────────┘
       │
       │ 2. User authorizes in Zoom
       ▼
┌─────────────────────────────────────┐
│   Zoom OAuth                        │
│   https://zoom.us/oauth/authorize   │
└──────┬──────────────────────────────┘
       │
       │ 3. Zoom redirects with code
       ▼
┌─────────────────────────────────────┐
│   Frontend Callback                 │
│   /auth/zoom-callback?code=...      │
│   Extracts code from URL            │
└──────┬──────────────────────────────┘
       │
       │ 4. POST code to backend
       ▼
┌─────────────────────────────────────┐
│   Backend API                       │
│   POST /api/v1/auth/zoom/callback   │
│   exchange_code_for_tokens()        │
│   get_zoom_user_info()              │
│   create_or_update_user()           │
└──────┬──────────────────────────────┘
       │
       │ 5. Return app tokens
       ▼
┌─────────────────────────────────────┐
│   Frontend                          │
│   Store tokens in localStorage      │
│   Redirect to /dashboard            │
│   User authenticated!               │
└─────────────────────────────────────┘
```

## API Documentation

### POST /api/v1/auth/zoom/callback
Exchange Zoom authorization code for app tokens.

**Request:**
```json
{
  "code": "tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg",
  "state": "optional-state-value"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Failed to process Zoom OAuth: [error details]"
}
```

## Debugging

### Check if environment variables are set
```bash
# Backend
echo $ZOOM_CLIENT_ID
echo $ZOOM_CLIENT_SECRET
echo $ZOOM_REDIRECT_URI

# Frontend (if using Next.js with public vars)
echo $NEXT_PUBLIC_ZOOM_CLIENT_ID
```

### Test Zoom API connectivity
```bash
# Test Zoom token endpoint
curl -X POST https://zoom.us/oauth/token \
  -u "your-client-id:your-client-secret" \
  -d "grant_type=authorization_code&code=test-code&redirect_uri=your-redirect-uri"
```

### Check backend logs
```bash
# Monitor backend for Zoom-related errors
grep -i "zoom" backend/logs/*
```

### Check frontend console
```javascript
// In browser console
console.log("Checking Zoom config...");
console.log("ZOOM_CLIENT_ID:", process.env.NEXT_PUBLIC_ZOOM_CLIENT_ID);
console.log("ZOOM_REDIRECT_URI:", process.env.NEXT_PUBLIC_ZOOM_REDIRECT_URI);
```

## Security Notes

1. ⚠️ **Never commit** `.env` files with credentials
2. ⚠️ **Never expose** `ZOOM_CLIENT_SECRET` in frontend code
3. ✅ Use `NEXT_PUBLIC_` prefix only for public variables
4. ✅ Store sensitive tokens securely (HttpOnly cookies in production)
5. ✅ Always use HTTPS in production for OAuth redirects

## Next Steps

1. **Store Zoom Integration Tokens** - Create a `user_zoom_integration` table to store and refresh Zoom tokens
2. **List Zoom Meetings** - Use Zoom API to list user's upcoming meetings
3. **Real-Time Integration** - Connect Zoom webhooks for live meeting events
4. **RTMS Setup** - Implement Real-Time Meeting Service for meeting transcription
5. **Join Zoom Meetings** - Allow users to join Zoom meetings directly from app

## Support

For issues or questions:
1. Check the [ZOOM_OAUTH_INTEGRATION.md](./ZOOM_OAUTH_INTEGRATION.md) for detailed documentation
2. Review backend logs: `backend/logs/`
3. Check Zoom Developer Console for API errors
4. Verify all environment variables are correctly set

## Related Files

- Backend OAuth Service: [zoom_oauth.py](./backend/app/services/zoom_oauth.py)
- Backend Auth Endpoint: [auth.py](./backend/app/api/v1/auth.py)
- Backend Config: [config.py](./backend/app/core/config.py)
- Frontend Hook: [useZoomAuth.ts](./frontend/hooks/useZoomAuth.ts)
- Frontend Callback: [zoom-callback/page.tsx](./frontend/app/(auth)/zoom-callback/page.tsx)
- Example Component: [ZoomLoginExample.tsx](./frontend/components/auth/ZoomLoginExample.tsx)
