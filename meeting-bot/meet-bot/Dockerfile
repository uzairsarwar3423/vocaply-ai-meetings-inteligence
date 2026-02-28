FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    pulseaudio \
    pulseaudio-utils \
    ffmpeg \
    # Chrome dependencies
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Chromium for Pyppeteer
RUN python -c "from pyppeteer import chromium_downloader; import asyncio; asyncio.get_event_loop().run_until_complete(chromium_downloader.download_chromium())"

# Copy application
COPY . .

# Configure PulseAudio
RUN mkdir -p /etc/pulse && \
    echo "load-module module-native-protocol-unix" > /etc/pulse/system.pa && \
    echo "load-module module-null-sink sink_name=rtp format=s16be channels=2 rate=44100" >> /etc/pulse/system.pa

# Create recordings directory
RUN mkdir -p /tmp/recordings

# Expose port (if needed)
EXPOSE 8003

# Environment variables (must be set at runtime)
ENV BOT_ID=""
ENV MEETING_ID=""
ENV MEETING_URL=""
ENV COMPANY_ID=""
ENV WEBHOOK_URL="http://bot-orchestrator:8001/webhooks/bot-events"
ENV BOT_NAME="Vocaply Bot"

# Start PulseAudio and bot
CMD ["sh", "-c", "pulseaudio --system --daemonize && python -m bot.entrypoint"]