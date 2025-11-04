# Enhanced Multi-Downloader Video Bot

A powerful Telegram bot that downloads videos using multiple downloader backends for maximum compatibility and reliability.

## 🎯 New Features

### Multi-Downloader Support
- **yt-dlp**: Primary downloader for most platforms
- **youtube-dl**: Alternative fallback for YouTube and other sites  
- **instaloader**: Specialized for Instagram content
- **Enhanced Direct**: Custom headers for better platform compatibility

### Smart Fallback System
The bot automatically tries different downloaders in order:
1. Platform-specific downloader (yt-dlp, youtube-dl, or instaloader)
2. Alternative downloaders if the primary fails
3. Enhanced direct download with custom headers
4. Basic direct download as final fallback

### Platform Support
- **YouTube**: youtube.com, youtu.be (full support)
- **TikTok**: tiktok.com (enhanced support)
- **Instagram**: instagram.com (specialized downloader)
- **Twitter/X**: twitter.com (multiple method support)
- **Facebook**: facebook.com (platform-specific handling)
- **Vimeo**: vimeo.com (standard support)
- **Dailymotion**: dailymotion.com (standard support)
- **Twitch**: twitch.tv (live clip support)
- **Direct URLs**: Any video file URL (.mp4, .avi, .mov, etc.)

## 🚀 Installation

### Quick Setup (with all downloaders)
```bash
# Make setup script executable
chmod +x setup_multi_downloader.sh

# Run complete setup
./setup_multi_downloader.sh
```

### Manual Installation
```bash
# Install core requirements
pip install -r enhanced_requirements.txt

# Install additional downloaders for full functionality
pip install yt-dlp youtube-dl instaloader
```

### Core Requirements Only
The bot works with just the core requirements but has limited platform support:
```bash
pip install python-telegram-bot==20.7 requests==2.31.0
```

## 🔧 Usage

### Start the Bot
```bash
# With full downloader support
./run_enhanced_bot.sh

# Or directly
python enhanced_video_bot.py
```

### Test Downloaders
```bash
python test_multi_downloader.py
```

### Environment Setup
1. Set your bot token:
   ```bash
   export BOT_TOKEN="your_bot_token_here"
   ```
2. Or create a `.env` file:
   ```
   BOT_TOKEN=your_bot_token_here
   ```

## 📥 How It Works

### Download Process
1. **Platform Detection**: Identifies the platform type from the URL
2. **Primary Download**: Uses the best downloader for that platform
3. **Fallback Chain**: Automatically tries alternative downloaders if needed
4. **Enhanced Direct**: Uses custom headers to bypass restrictions
5. **File Processing**: Splits large files, sends to Telegram
6. **Cleanup**: Removes all temporary files

### Downloader Selection Logic
```python
# Platform-specific selection
YouTube → yt-dlp → youtube-dl → enhanced direct
Instagram → instaloader → yt-dlp → enhanced direct  
TikTok → yt-dlp → youtube-dl → enhanced direct
Other platforms → yt-dlp → enhanced direct
Direct URLs → enhanced direct → basic direct
```

### Enhanced Headers
The bot uses sophisticated headers to mimic real browser requests:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Accept': 'video/webm,video/ogg,video/*;q=0.9,...',
    'Sec-Fetch-Dest': 'video',
    'Sec-Fetch-Mode': 'no-cors',
    # ... additional headers for better compatibility
}
```

## 📊 Supported File Formats

### Video Formats
- **Popular**: MP4, AVI, MOV, MKV, WebM
- **Legacy**: FLV, WMV, M4V, 3GP, OGV
- **Streaming**: M3U8, DASH formats (via downloaders)

### File Size Limits
- **Telegram limit**: 50MB per message
- **Bot handling**: Automatically splits files >50MB
- **Maximum file**: Up to 2GB (split into multiple parts)

## 🛡️ Error Handling & Fallbacks

### Graceful Degradation
The bot works even with minimal dependencies:
- No downloaders → Basic direct downloads only
- Some downloaders → Platform-specific support where available
- All downloaders → Full functionality with smart fallbacks

### Error Recovery
- **Platform blocks**: Automatically tries alternative methods
- **Network issues**: Retries with different headers
- **Large files**: Automatic splitting and sequential sending
- **Timeout handling**: 5-minute timeout per download attempt

### Common Issues
- **Platform restrictions**: Some platforms block automated downloads
- **Authentication required**: Bot only handles public content
- **Rate limiting**: Built-in delays between requests

## 🔍 Platform-Specific Features

### YouTube
- **Formats**: mp4, webm, various qualities
- **Features**: Playlist avoidance, quality selection
- **Fallbacks**: yt-dlp → youtube-dl → enhanced direct

### Instagram  
- **Specialized**: instaloader for better compatibility
- **Content**: Posts, reels, stories (public only)
- **Fallbacks**: instaloader → yt-dlp → enhanced direct

### TikTok
- **Enhanced**: Custom handling for TikTok's restrictions
- **Formats**: MP4 with metadata preservation
- **Fallbacks**: yt-dlp → youtube-dl → enhanced direct

### Twitter/X
- **Support**: Tweet videos, GIFs converted to MP4
- **Limitations**: May require enhanced headers
- **Fallbacks**: yt-dlp → enhanced direct

## 📈 Performance

### Download Speed
- **Direct downloads**: Limited by source server speed
- **Platform downloads**: Optimized per platform
- **Large files**: Parallel processing where possible

### Resource Usage
- **Memory**: Efficient streaming for large files
- **Storage**: Automatic cleanup after each download
- **Network**: Intelligent retry with exponential backoff

## 🔧 Advanced Configuration

### Environment Variables
```bash
BOT_TOKEN=your_bot_token                    # Required
TEMP_DIR=/custom/temp/path                  # Optional
MAX_FILE_SIZE=52428800                      # Optional (bytes)
CHUNK_SIZE=1048576                         # Optional (bytes)
```

### Downloader Configuration
```python
# yt-dlp options
'--format': 'best[height<=720]',  # Limit quality
'--output': template,              # Filename template
'--no-playlist': True,             # Avoid playlists

# youtube-dl options  
'-f': 'best[height<=720]',         # Quality limit
'-o': template,                    # Output template
'--no-playlist': True,             # Single video only
```

## 🧪 Testing

### Test Suite
Run comprehensive tests:
```bash
python test_multi_downloader.py
```

### Test Coverage
- ✅ Downloader availability check
- ✅ URL platform detection
- ✅ Enhanced headers functionality
- ✅ File splitting operations
- ✅ Error handling scenarios

### Manual Testing
Test specific URLs:
```python
from enhanced_video_bot import EnhancedVideoDownloader

downloader = EnhancedVideoDownloader()
url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
platform = downloader.get_platform_type(url)
print(f"Platform: {platform}")
```

## 📚 API Reference

### EnhancedVideoDownloader Class
```python
class EnhancedVideoDownloader:
    def download_video(url, filename)      # Main download method
    def get_platform_type(url)             # Platform detection
    def download_with_yt_dlp_fallback()    # Multi-downloader attempt
    def split_large_file(file_path)        # File splitting
    def cleanup_all()                      # Temporary file cleanup
```

### Key Methods
- `is_video_url(url)`: Check if URL contains video
- `get_platform_type(url)`: Detect platform type
- `download_with_yt_dlp_fallback()`: Try multiple downloaders
- `download_direct_with_enhanced_headers()`: Enhanced direct download

## 🚨 Troubleshooting

### Installation Issues
```bash
# Install system dependencies
sudo apt update && sudo apt install python3-pip ffmpeg

# Upgrade pip
pip install --upgrade pip

# Install with specific Python version
python3 -m pip install -r enhanced_requirements.txt
```

### Downloader Issues
```bash
# Test individual downloaders
yt-dlp --version
youtube-dl --version
instaloader --version

# Reinstall specific downloader
pip install --upgrade yt-dlp
```

### Platform-Specific Issues
- **YouTube**: Ensure yt-dlp is updated: `pip install --upgrade yt-dlp`
- **Instagram**: May require instaloader for better compatibility
- **TikTok**: Enhanced headers may be needed for some content
- **Twitter**: Rate limiting may occur with frequent requests

## 📝 Changelog

### v2.0 - Enhanced Multi-Downloader
- ✅ Added youtube-dl as yt-dlp fallback
- ✅ Added instaloader for Instagram
- ✅ Implemented smart fallback system
- ✅ Enhanced direct download with custom headers
- ✅ Improved platform detection
- ✅ Better error handling and recovery
- ✅ Comprehensive test suite
- ✅ Advanced installation scripts

### v1.0 - Basic Platform Support
- Basic yt-dlp integration
- Direct download support
- File splitting for large files
- Telegram bot framework

## 🤝 Contributing

### Adding New Platforms
1. Update `get_platform_type()` method
2. Add platform-specific download logic
3. Include in test suite
4. Update documentation

### Adding New Downloaders
1. Implement download method in `EnhancedVideoDownloader`
2. Add to fallback chain in `download_with_yt_dlp_fallback()`
3. Include availability check in main function
4. Add to test suite

## 📄 License

This project is for educational purposes. Please respect platform terms of service and copyright laws when downloading content.

## 🔗 Links

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Primary downloader
- [youtube-dl](https://github.com/ytdl-org/youtube-dl) - Alternative downloader  
- [instaloader](https://github.com/instaloader/instaloader) - Instagram downloader
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Bot framework
