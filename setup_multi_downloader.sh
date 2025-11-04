#!/bin/bash

echo "🚀 Setting up Enhanced Multi-Downloader Video Bot..."
echo "=================================================="

# Update package manager
echo "📦 Updating package lists..."
sudo apt update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv ffmpeg

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install core requirements
echo "📋 Installing core requirements..."
pip install --upgrade pip
pip install -r enhanced_requirements.txt

# Install additional downloaders for maximum functionality
echo "⬇️ Installing additional downloaders..."
pip install yt-dlp youtube-dl instaloader

# Set up environment
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    echo "BOT_TOKEN=your_bot_token_here" > .env
    echo "⚠️ Please edit .env file and add your actual bot token!"
fi

# Make scripts executable
chmod +x *.sh

echo ""
echo "✅ Setup complete!"
echo "=================="
echo ""
echo "🎯 Installed downloaders:"
echo "• yt-dlp (primary)"
echo "• youtube-dl (fallback)"
echo "• instaloader (Instagram)"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your BOT_TOKEN"
echo "2. Run: ./run_enhanced_bot.sh"
echo ""
echo "🔧 For manual installation of downloaders only:"
echo "pip install yt-dlp youtube-dl instaloader"
echo ""
echo "🤖 Bot will work with just core requirements but has limited platform support."