# Zoom OAuth Integration Setup Guide

## Overview
This guide walks you through integrating Zoom OAuth2 authentication into your Vocaply AI application. With this integration, users can sign up and log in using their Zoom accounts.

## Prerequisites
1. Zoom Developer Account (https://marketplace.zoom.us)
2. Zoom OAuth App credentials:
   - Client ID
   - Client Secret
   - Redirect URI

## Step 1: Get Your Zoom OAuth Credentials

### 1. Create a Zoom OAuth App
- Go to [Zoom App Marketplace](https://marketplace.zoom.us)
- Click "Build an App"
- Select "OAuth" as the app type
- Fill in the app details

### 2. Add OAuth Redirect URI
In your Zoom app settings, add your redirect URI:
- **For Local Development**: `http://localhost:3000/auth/zoom-callback`
- **For Production**: `https://vocaply-ai-meetings-inteligence-235.vercel.app/auth/zoom-callback`

### 3. Copy Your Credentials
From your Zoom app dashboard, copy:
- Client ID
- Client Secret

## Step 2: Environment Configuration

### Backend (.env)
Add the following to your backend `.env` file:

```env
# Zoom OAuth
ZOOM_CLIENT_ID=<your-zoom-client-id>
ZOOM_CLIENT_SECRET=<your-zoom-client-secret>
ZOOM_REDIRECT_URI=https://vocaply-ai-meetings-inteligence-235.vercel.app/auth/zoom-callback
```

### Frontend (.env.local)
Add the following to your frontend `.env.local` file:

```env
NEXT_PUBLIC_ZOOM_CLIENT_ID=<your-zoom-client-id>
NEXT_PUBLIC_ZOOM_OAUTH_URL=https://zoom.us/oauth/authorize
NEXT_PUBLIC_ZOOM_REDIRECT_URI=https://vocaply-ai-meetings-inteligence-235.vercel.app/auth/zoom-callback
```

## Step 3: Using the Authorization Code

You already have an authorization code:
```
code=tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg
```

### Option 1: Automatic Exchange via Frontend
The frontend callback handler will automatically exchange this code when you redirect to:
```
https://your-frontend/auth/zoom-callback?code=tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg
```

### Option 2: Manual Exchange via API
Send a POST request to your backend:

```bash
curl -X POST http://localhost:8000/api/v1/auth/zoom/callback \
  -H "Content-Type: application/json" \
  -d '{
    "code": "tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg",
    "state": "optional-state-value"
  }'
```

Response:
```json
{
  "access_token": "app-access-token",
  "refresh_token": "app-refresh-token",
  "token_type": "bearer"
}
```

## Step 4: Frontend Integration

### Add Zoom Login Button
In your login component, import and use the `useZoomAuth` hook:

```typescript
import { useZoomAuth } from "@/hooks/useZoomAuth";

export function LoginPage() {
  const { initiateZoomLogin } = useZoomAuth();

  return (
    <div>
      <button onClick={initiateZoomLogin} className="btn btn-primary">
        Sign in with Zoom
      </button>
    </div>
  );
}
```

### Get Authorization URL
If you need to generate the authorization URL manually:

```typescript
const { getZoomAuthUrl } = useZoomAuth();
const authUrl = getZoomAuthUrl();
// authUrl will be: https://zoom.us/oauth/authorize?response_type=code&client_id=...&redirect_uri=...
```

## Step 5: Flow Overview

```
1. User clicks "Sign in with Zoom"
   ↓
2. Frontend redirects to: https://zoom.us/oauth/authorize?...
   ↓
3. User authorizes in Zoom
   ↓
4. Zoom redirects to: https://your-frontend/auth/zoom-callback?code=...
   ↓
5. Frontend extracts code and sends to backend: POST /api/v1/auth/zoom/callback
   ↓
6. Backend:
   - Exchanges code for Zoom tokens
   - Fetches Zoom user info
   - Creates or updates user in database
   - Returns app access/refresh tokens
   ↓
7. Frontend stores app tokens and redirects to dashboard
```

## Backend Implementation Details

### Key Files
- **[/backend/app/services/zoom_oauth.py](/backend/app/services/zoom_oauth.py)** - Zoom OAuth service handling token exchange and user info fetching
- **[/backend/app/api/v1/auth.py](/backend/app/api/v1/auth.py)** - OAuth callback endpoint (`POST /api/v1/auth/zoom/callback`)
- **[/backend/app/core/config.py](/backend/app/core/config.py)** - Configuration for Zoom credentials

### Zoom OAuth Service
The `ZoomOAuthService` class handles:
- **exchange_code_for_tokens()** - Exchange authorization code for Zoom tokens
- **get_zoom_user_info()** - Fetch user information from Zoom API
- **handle_zoom_oauth_callback()** - Complete OAuth flow (code → tokens → user → app tokens)
- **refresh_zoom_token()** - Refresh expired Zoom access tokens

## Frontend Implementation Details

### Key Files
- **[/frontend/hooks/useZoomAuth.ts](/frontend/hooks/useZoomAuth.ts)** - React hook for Zoom OAuth flow
- **[/frontend/app/(auth)/zoom-callback/page.tsx](/frontend/app/(auth)/zoom-callback/page.tsx)** - Callback handler page
- **[/frontend/types/auth.ts](/frontend/types/auth.ts)** - TypeScript types for Zoom OAuth

### useZoomAuth Hook
Provides:
- **initiateZoomLogin()** - Redirect to Zoom authorization URL
- **handleZoomCallback(code)** - Exchange code for app tokens
- **getZoomAuthUrl()** - Get the authorization URL manually

## API Endpoints

### Exchange Authorization Code
```
POST /api/v1/auth/zoom/callback
Content-Type: application/json

{
  "code": "authorization-code-from-zoom",
  "state": "optional-state-value"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## Testing

### 1. Test Authorization URL Generation
```typescript
import { useZoomAuth } from "@/hooks/useZoomAuth";

const { getZoomAuthUrl } = useZoomAuth();
console.log(getZoomAuthUrl());
```

### 2. Test with Your Authorization Code
```bash
# Backend must be running with ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_REDIRECT_URI set

curl -X POST http://localhost:8000/api/v1/auth/zoom/callback \
  -H "Content-Type: application/json" \
  -d '{"code": "tl0phWarTYWdVqTu-EpTo6cxu7gCDVYmg"}'
```

### 3. Test Complete Flow
1. Navigate to login page
2. Click "Sign in with Zoom"
3. You should be redirected to Zoom OAuth consent screen
4. After authorizing, you'll be redirected to callback page
5. Callback page processes the code and redirects to dashboard

## Troubleshooting

### "Client ID is missing"
- Check that `NEXT_PUBLIC_ZOOM_CLIENT_ID` is set in frontend `.env.local`
- Check that `ZOOM_CLIENT_ID` is set in backend `.env`

### "Invalid redirect URI"
- Ensure the redirect URI in your Zoom app settings matches exactly what's in your config
- Common mistake: http vs https mismatch

### "Authorization code not found in callback URL"
- Check that the redirect URI is correctly configured in both Zoom app and your `.env`
- Verify the authorization flow is completing properly

### "User authentication failed at backend"
- Verify `ZOOM_CLIENT_SECRET` is correct
- Check that Zoom API is accessible from your backend environment
- Review backend logs for detailed error messages

## Security Considerations

1. **Never expose ZOOM_CLIENT_SECRET** - This should only be in backend `.env`
2. **Validate state parameter** - Use to prevent CSRF attacks (optional enhancement)
3. **HTTPS in production** - OAuth requires HTTPS for redirect URIs in production
4. **Token storage** - Store tokens securely (localStorage for now, consider HttpOnly cookies)
5. **Token expiration** - Implement token refresh before access_token expires

## Next Steps

1. Add Zoom meeting integration (list user's Zoom meetings, join meetings via API)
2. Store Zoom tokens securely for later API access
3. Implement automatic Zoom token refresh
4. Add Zoom meeting webhook handling
5. Implement RTMS (Real-Time Meeting Service) for live meeting data

## References

- [Zoom OAuth Documentation](https://developers.zoom.us/docs/integration-development/oauth/)
- [Zoom API Documentation](https://developers.zoom.us/docs/api/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
