# Zoom Real-Time Media Streams (RTMS) Setup Guide

To use the Vocaply bot as an AI notetaker without violating Zoom's Terms of Service, you need to use the **Zoom Meeting API** and the **Local Recording Token** mechanism to capture audio streams via WebSocket, or integrate with an RTMS provider (like Recall.ai) or build a custom headless client that supports OAuth Server-to-Server and RTMS. 

Follow this step-by-step guide to generate the required `ZOOM_CLIENT_ID` and `ZOOM_CLIENT_SECRET` for a Server-to-Server OAuth App.

---

## Step 1: Log into the Zoom App Marketplace
1. Go to the [Zoom App Marketplace](https://marketplace.zoom.us/).
2. Sign in with your Zoom account (you must be an Admin or have developer privileges to create OAuth apps).

## Step 2: Create a Server-to-Server OAuth App
1. In the top right corner, click **Develop > Build App**.
2. From the list of app types, locate **Server-to-Server OAuth** and click **Create**.
   - *Note: Do NOT choose "Meeting SDK" or "OAuth". You specifically want "Server-to-Server OAuth" for automated bots that run on a backend without human intervention.*
3. Give your app a name (e.g., `Vocaply AI Bot`) and click **Create**.

## Step 3: Configure App Information
1. On the **App Credentials** tab, you will see your **Account ID**, **Client ID**, and **Client Secret**.
   - **Copy the Client ID** (This evaluates to your `ZOOM_CLIENT_ID` variable).
   - **Copy the Client Secret** (This evaluates to your `ZOOM_CLIENT_SECRET` variable).
2. Go to the **Information** tab.
3. Fill out the required fields:
   - **Company Name**: Your company name
   - **Developer Contact Information**: Your Name and Email address.
4. Click **Continue**.

## Step 4: Add Features & Scopes (CRITICAL)
For the bot to access meeting details and the audio streams, you must grant it the correct permissions (scopes).

1. Go to the **Scopes** tab.
2. Click **+ Add Scopes**.
3. You need to add scopes related to Meetings, Recording, and Users. Select the following categories and check these specific scopes:
   - **Meeting**:
     - `meeting:read:admin` (To get meeting details and tokens)
     - `meeting:write:admin` (To join/manage meetings, update statuses)
   - **Recording**:
     - `recording:read:admin` (If you intend to fetch cloud recordings)
   - **User**:
     - `user:read:admin` (To authenticate on behalf of meeting hosts)
4. After selecting the required scopes, click **Done** and then **Continue**.

## Step 5: Activate Your App
1. Go to the **Activation** tab.
2. If all required fields are filled out, you will see a button that says **Activate Your App**. Click it.
3. Your app is now active and the credentials are valid for the backend.

---

## Step 6: Update Your `.env` Files

Now that you have your credentials, update your `.env` files across your ecosystem.

In `/meeting-bot/.env`:
```env
# Zoom App Credentials (Real-time Media Streams)
ZOOM_CLIENT_ID=your_copied_client_id
ZOOM_CLIENT_SECRET=your_copied_client_secret
```

---

## The Request Flow for RTMS (How it works under the hood)

1. **Authentication:** 
   Your backend uses the `ZOOM_CLIENT_ID` and `ZOOM_CLIENT_SECRET` to request a short-lived access token from the Zoom API.
   ```http
   POST https://zoom.us/oauth/token?grant_type=account_credentials
   Authorization: Basic base64(CLIENT_ID:CLIENT_SECRET)
   ```

2. **Fetching the Local Recording Token:** 
   With the access token, your backend calls the Zoom API for the specific meeting to request a recording token. You need this to authorize recording programmatically without triggering a GUI pop-up.
   ```http
   GET https://api.zoom.us/v2/meetings/{meetingId}/local_recording_token
   Authorization: Bearer {Access_Token}
   ```
   *Note: This specific endpoint requires special approval from Zoom for production apps, but usually works in Development for the account that created the App.*

3. **Bot Joins the Meeting (Headless Client):**
   Instead of using the C++ Meeting SDK (which requires UI interaction per ToS), your `bot-service` runs a headless Chromium instance (using Playwright) that joins the meeting via the Web client (`https://app.zoom.us/wc/join/{meetingId}`). 

4. **Triggering Local Recording/RTMS Capture:**
   Using the local recording token from Step 2, the Puppeteer/Playwright headless browser executes JavaScript on the Zoom Web Client page to automatically consent to recording constraints and stream raw Web Audio out to your Media Server via WebSockets.
   ```javascript
   // Web Audio API hooks inside Playwright capture the PCM stream
   const audioCtx = new AudioContext();
   // The PCM data is sent to websocket: MEDIA_SERVER_URL=ws://localhost:8002/audio
   ```

5. **Transcription via Media Server:**
   Your Media Server (Python/WebSocket running at `localhost:8002`) receives the raw PCM audio chunks from the Playwright browser. It buffers the audio and streams it to your transcription provider (Deepgram, AssemblyAI, AWS, OpenAI Realtime API).

---

## Future Scaling Note:
If manually orchestrating Playwright headless browsers becomes too resource-intensive (browsers use 1-2GB RAM each), many AI Notetaker companies transition to using 3rd-party RTMS aggregators like [Recall.ai](https://www.recall.ai/) or build fully headless signaling WebRTC clients, entirely bypassing Chrome and Playwright.
