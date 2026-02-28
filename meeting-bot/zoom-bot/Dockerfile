FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    ffmpeg \
    libssl-dev \
    libpulse-dev \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Download and install Zoom Meeting SDK
# Note: In production, you'd download the actual SDK here
# For now, we'll use the mock SDK
ENV USE_MOCK_SDK=true
ENV ZOOM_SDK_PATH=/usr/local/lib/zoom-sdk

# Create recordings directory
RUN mkdir -p /tmp/recordings

# Expose port (if running as service)
EXPOSE 8003

# Default command
CMD ["python", "-m", "bot.zoom_bot"]