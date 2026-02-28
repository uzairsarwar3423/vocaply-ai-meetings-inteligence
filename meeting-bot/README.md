# 🤖 Vocaply Meeting Bot Service

Playwright-based bot service for automated meeting joining and recording.

## Architecture

```
Bot Service (FastAPI)
├── Bot Manager     — High-level orchestration
├── Instance Pool   — Pre-warmed bot instances
├── Health Monitor  — System health & metrics
└── Redis State     — Distributed state management
```

## Features

- **Pre-warmed Pool**: Maintains 5-10 ready bots for instant assignment
- **Platform Support**: Zoom, Google Meet, Microsoft Teams, Webex
- **Auto-scaling**: Dynamically creates/destroys bots based on demand
- **Health Monitoring**: Detects stuck bots, alone bots, max duration
- **Webhook Delivery**: Real-time events to platform backend
- **Recording**: Captures audio/video with Playwright

## Quick Start

```bash
# Build and run
docker-compose -f docker-compose.bots.yml up --build

# Or run locally
cd bot-service
pip install -r requirements.txt
playwright install chromium
python -m app.main
```

## Configuration

The service uses environment variables for configuration. A template is provided in `.env.example`.

```bash
# Set up environment files
cp .env.example .env
cp .env.example bot-service/.env
cp .env.example zoom-bot/.env
```

Key variables to configure:
- `ZOOM_CLIENT_ID` / `ZOOM_CLIENT_SECRET`: From Zoom Marketplace (OAuth app for Server-to-Server / RTMS)
- `BACKEND_API_URL`: URL of the main platform backend
- `USE_MOCK_SDK`: Set to `true` for development without the actual Zoom C++ SDK

## API Endpoints

```
POST   /bots/create          Create bot for meeting
POST   /bots/{id}/stop       Stop bot
GET    /bots/{id}/status     Get bot status
GET    /bots/active          List active bots
GET    /bots/pool/status     Pool metrics
GET    /health               Health check
```

## Environment Variables

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Backend API
BACKEND_API_URL=http://localhost:8000
BACKEND_API_KEY=your-internal-api-key

# Pool Configuration
POOL_MIN_SIZE=5
POOL_MAX_SIZE=20
POOL_PRE_WARM=10

# Bot Behavior
BOT_DISPLAY_NAME="Vocaply Bot"
BOT_JOIN_TIMEOUT=60
BOT_ALONE_TIMEOUT=300
BOT_MAX_DURATION=10800

# Recording
RECORDING_PATH=/tmp/recordings
RECORDING_FORMAT=webm

# Playwright
BROWSER_HEADLESS=true
```

## Redis Schema

```
bot:{bot_id}                      → Bot instance data (JSON, TTL 1h)
bot:pool:available                → Set of available bot IDs
bot:pool:in_use                   → Set of in-use bot IDs
company:{company_id}:active_bots  → Set of company's active bots
bot:{bot_id}:heartbeat            → Last heartbeat timestamp (TTL 60s)
```

## Bot Lifecycle

```
INITIALIZING → AVAILABLE → ASSIGNED → JOINING → IN_MEETING → RECORDING → LEAVING → COMPLETED
                                                      ↓
                                                   FAILED
```

## Platform-Specific Notes

### Zoom
- Uses public join URL (no auth required)
- Bot auto-mutes on join
- Detects participants via `[aria-label*="participant"]`

### Google Meet
- Turns off camera/mic before joining
- Clicks "Join now" after permissions
- Detects participants via `[data-participant-id]`

### Microsoft Teams
- Uses web version (no app install)
- Enters bot name on join screen
- Detects participants via `[role="list"]`

## Monitoring

Health check returns:
```json
{
  "status": "healthy",
  "redis": {"connected": true},
  "pool": {"available": 8, "in_use": 2, "total": 10},
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.3,
    "disk_percent": 62.1
  }
}
```

## Production Deployment

- Run multiple bot-service instances behind load balancer
- Use Redis Sentinel/Cluster for HA
- Mount shared volume for recordings (or stream directly to S3)
- Set `BROWSER_HEADLESS=true` in production
- Monitor pool size with Prometheus/Grafana
- Set up alerts for stuck bots, pool exhaustion

## Troubleshooting

**Bot stuck joining**
- Check meeting URL validity
- Verify platform credentials if needed
- Increase BOT_JOIN_TIMEOUT

**Pool exhausted**
- Increase POOL_MAX_SIZE
- Check for leaked bots (not properly released)
- Review BOT_ALONE_TIMEOUT (bots leaving too slowly)

**High CPU usage**
- Reduce POOL_PRE_WARM
- Enable BROWSER_HEADLESS=true
- Limit concurrent bots per instance