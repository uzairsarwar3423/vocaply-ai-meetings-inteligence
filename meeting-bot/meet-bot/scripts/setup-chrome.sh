#!/bin/bash
# Setup Chrome and PulseAudio for Google Meet bot

set -e

echo "🔧 Setting up Chrome and PulseAudio for Meet bot..."

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Install Chrome
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if ! command -v google-chrome &> /dev/null; then
    echo "📦 Installing Google Chrome..."
    
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
    
    apt-get update
    apt-get install -y google-chrome-stable
    
    echo "✅ Chrome installed"
else
    echo "✅ Chrome already installed"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Install PulseAudio
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if ! command -v pulseaudio &> /dev/null; then
    echo "📦 Installing PulseAudio..."
    
    apt-get update
    apt-get install -y pulseaudio pulseaudio-utils
    
    echo "✅ PulseAudio installed"
else
    echo "✅ PulseAudio already installed"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Install FFmpeg
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing FFmpeg..."
    
    apt-get update
    apt-get install -y ffmpeg
    
    echo "✅ FFmpeg installed"
else
    echo "✅ FFmpeg already installed"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configure PulseAudio
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo "⚙️  Configuring PulseAudio..."

# Start PulseAudio in system mode
mkdir -p /etc/pulse
cat > /etc/pulse/system.pa <<EOF
# System-wide PulseAudio configuration for bot

# Load necessary modules
load-module module-native-protocol-unix
load-module module-null-sink sink_name=rtp format=s16be channels=2 rate=44100
load-module module-native-protocol-tcp auth-anonymous=1

# Allow all users
load-module module-native-protocol-unix auth-anonymous=1
EOF

# Create PulseAudio startup script
cat > /usr/local/bin/start-pulseaudio.sh <<EOF
#!/bin/bash
pulseaudio --system --daemonize --disallow-exit --disallow-module-loading=0 -n
EOF

chmod +x /usr/local/bin/start-pulseaudio.sh

echo "✅ PulseAudio configured"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Install Python dependencies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Create recordings directory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

mkdir -p /tmp/recordings
chmod 777 /tmp/recordings

echo "✅ Recordings directory created"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Done
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start PulseAudio:"
echo "  /usr/local/bin/start-pulseaudio.sh"
echo ""
echo "To test audio:"
echo "  pactl list sinks"
echo ""
echo "To run the bot:"
echo "  python -m bot.meet_bot <meeting_url>"
echo ""