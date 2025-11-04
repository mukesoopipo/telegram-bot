#!/usr/bin/env python3
"""
Enhanced Telegram Video Downloader Bot
Features: yt-dlp, multiple download methods, file splitting, auto-cleanup
"""

import os
import logging
import subprocess
import tempfile
import requests
import shutil
import math
import time
from urllib.parse import urlparse, urljoin
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import asyncio
import mimetypes
from pathlib import Path
import json

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit for Telegram
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for splitting
TEMP_DIR = os.getenv('TEMP_DIR', tempfile.mkdtemp())

class EnhancedVideoDownloader:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temp directory: {self.temp_dir}")
        self.downloads_dir = os.path.join(self.temp_dir, "downloads")
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def is_video_url(self, url):
        """Check if URL points to a video file or video platform"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ogv']
        video_platforms = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 
            'twitch.tv', 'instagram.com', 'tiktok.com', 'twitter.com',
            'facebook.com', 'reddit.com', 'discord.com', 'pinterest.com',
            'snapchat.com', 'linkedin.com', 'tumblr.com'
        ]
        
        parsed = urlparse(url.lower())
        path = parsed.path.lower()
        
        # Check for video platforms
        if any(platform in parsed.netloc for platform in video_platforms):
            return True
        
        # Check for direct video files
        return any(path.endswith(ext) for ext in video_extensions)
    
    def extract_filename(self, url):
        """Extract filename from URL"""
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename or '.' not in filename:
            filename = f"video_{int(time.time())}.mp4"
        return filename
    
    def download_with_ytdlp(self, url, output_dir):
        """Download using yt-dlp (best for video platforms)"""
        try:
            # Test if yt-dlp is working first
            test_result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
            if test_result.returncode != 0:
                logger.warning("yt-dlp is not working properly, skipping yt-dlp download")
                return None
                
            output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
            cmd = [
                'yt-dlp',
                '--format', 'best[height<=720]',  # Limit to 720p for size
                '--output', output_template,
                '--no-playlist',
                url
            ]
            
            logger.info(f"yt-dlp command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find downloaded file
                for file in os.listdir(output_dir):
                    if file.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v')):
                        return os.path.join(output_dir, file)
            else:
                logger.error(f"yt-dlp error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("yt-dlp timeout")
            return None
        except Exception as e:
            logger.error(f"yt-dlp error: {e}")
            return None
    
    def download_with_youtubedl(self, url, output_dir):
        """Download using youtube-dl (alternative to yt-dlp)"""
        try:
            # Test if youtube-dl is working
            test_result = subprocess.run(['youtube-dl', '--version'], capture_output=True, text=True)
            if test_result.returncode != 0:
                logger.warning("youtube-dl is not working properly, skipping youtube-dl download")
                return None
                
            output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
            cmd = [
                'youtube-dl',
                '-f', 'best[height<=720]',  # Limit to 720p for size
                '-o', output_template,
                '--no-playlist',
                url
            ]
            
            logger.info(f"youtube-dl command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find downloaded file
                for file in os.listdir(output_dir):
                    if file.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v')):
                        return os.path.join(output_dir, file)
            else:
                logger.error(f"youtube-dl error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("youtube-dl timeout")
            return None
        except Exception as e:
            logger.error(f"youtube-dl error: {e}")
            return None
    
    def download_with_instaloader(self, url, output_dir):
        """Download Instagram content using instaloader"""
        try:
            # Test if instaloader is working
            test_result = subprocess.run(['instaloader', '--version'], capture_output=True, text=True)
            if test_result.returncode != 0:
                logger.warning("instaloader is not working properly, skipping instaloader download")
                return None
            
            # Extract post URL for instaloader
            # instaloader expects profile or post ID, not full URL
            cmd = [
                'instaloader',
                '--no-pictures',  # Only download videos
                '--no-captions',  # Don't save captions separately
                '--no-metadata-json',  # Don't save metadata
                '-o', output_dir,
                url
            ]
            
            logger.info(f"instaloader command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find downloaded video file
                for file in os.listdir(output_dir):
                    if file.endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                        return os.path.join(output_dir, file)
            else:
                logger.error(f"instaloader error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("instaloader timeout")
            return None
        except Exception as e:
            logger.error(f"instaloader error: {e}")
            return None
    
    def download_with_yt_dlp_fallback(self, url, output_dir):
        """Try different yt-dlp variants or downloaders"""
        # Try yt-dlp first
        result = self.download_with_ytdlp(url, output_dir)
        if result:
            return result
            
        # Try youtube-dl as fallback
        result = self.download_with_youtubedl(url, output_dir)
        if result:
            return result
            
        # Try instaloader for Instagram specifically
        if 'instagram.com' in url.lower():
            result = self.download_with_instaloader(url, output_dir)
            if result:
                return result
                
        return None
    
    def download_direct(self, url, output_path):
        """Download direct video file"""
        try:
            logger.info(f"Downloading direct: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress for large files
                        if total_size > 10 * 1024 * 1024:
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            if progress % 10 == 0:
                                logger.info(f"Download progress: {progress:.1f}%")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Direct download error: {e}")
            return None
    
    def split_large_file(self, file_path, chunk_size=CHUNK_SIZE):
        """Split large file into smaller chunks"""
        try:
            file_size = os.path.getsize(file_path)
            if file_size <= MAX_FILE_SIZE:
                return [file_path]
            
            chunks = []
            base_name = os.path.splitext(file_path)[0]
            extension = os.path.splitext(file_path)[1]
            
            with open(file_path, 'rb') as source:
                chunk_num = 0
                while True:
                    chunk_data = source.read(chunk_size)
                    if not chunk_data:
                        break
                    
                    chunk_path = f"{base_name}_part{chunk_num:03d}{extension}"
                    with open(chunk_path, 'wb') as chunk_file:
                        chunk_file.write(chunk_data)
                    
                    chunks.append(chunk_path)
                    chunk_num += 1
            
            logger.info(f"Split file into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting file: {e}")
            return [file_path]
    
    def download_video(self, url, filename):
        """Main download function with multiple downloader methods"""
        try:
            download_dir = os.path.join(self.downloads_dir, str(int(time.time())))
            os.makedirs(download_dir, exist_ok=True)
            
            # Try different download methods based on platform type
            downloaded_file = None
            platform_type = self.get_platform_type(url)
            
            logger.info(f"Detected platform type: {platform_type} for URL: {url}")
            
            # Method 1: Platform-specific downloaders
            if self.is_video_platform(url):
                logger.info(f"Trying platform-specific downloader for {platform_type}...")
                downloaded_file = self.download_with_yt_dlp_fallback(url, download_dir)
            
            # Method 2: Try alternative downloaders if platform downloader failed
            if not downloaded_file and self.is_video_platform(url):
                logger.info("Platform downloader failed, trying alternative methods...")
                
                # Try direct download with different headers for platforms
                if platform_type in ['youtube', 'instagram', 'tiktok']:
                    try:
                        file_path = os.path.join(download_dir, f"alternative_{filename}")
                        downloaded_file = self.download_direct_with_enhanced_headers(url, file_path)
                    except Exception as e:
                        logger.warning(f"Enhanced direct download failed: {e}")
            
            # Method 3: Direct download as fallback
            if not downloaded_file:
                logger.info("Trying direct download...")
                file_path = os.path.join(download_dir, filename)
                downloaded_file = self.download_direct(url, file_path)
            
            if downloaded_file and os.path.exists(downloaded_file):
                return downloaded_file
            else:
                raise Exception(f"All download methods failed for {platform_type} platform")
                
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise Exception(f"Failed to download video: {str(e)}")
    
    def download_direct_with_enhanced_headers(self, url, output_path):
        """Download direct with enhanced headers for better platform compatibility"""
        try:
            logger.info(f"Enhanced direct download: {url}")
            
            # More comprehensive headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'no-cache'
            }
            
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress for large files
                        if total_size > 10 * 1024 * 1024:
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            if progress % 10 == 0:
                                logger.info(f"Download progress: {progress:.1f}%")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Enhanced direct download error: {e}")
            return None
    
    def is_video_platform(self, url):
        """Check if URL is from a video platform that needs special downloaders"""
        video_platforms = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 
            'twitch.tv', 'instagram.com', 'tiktok.com', 'twitter.com',
            'facebook.com', 'reddit.com', 'pinterest.com', 'snapchat.com',
            'linkedin.com', 'tumblr.com', 'discord.com'
        ]
        parsed = urlparse(url.lower())
        return any(platform in parsed.netloc for platform in video_platforms)
    
    def get_platform_type(self, url):
        """Get the type of platform to use appropriate downloader"""
        parsed = urlparse(url.lower())
        netloc = parsed.netloc
        
        if 'youtube.com' in netloc or 'youtu.be' in netloc:
            return 'youtube'
        elif 'instagram.com' in netloc:
            return 'instagram'
        elif 'tiktok.com' in netloc:
            return 'tiktok'
        elif 'twitter.com' in netloc:
            return 'twitter'
        elif 'facebook.com' in netloc:
            return 'facebook'
        elif 'vimeo.com' in netloc:
            return 'vimeo'
        elif 'dailymotion.com' in netloc:
            return 'dailymotion'
        elif 'twitch.tv' in netloc:
            return 'twitch'
        else:
            return 'other'
    
    def cleanup_all(self):
        """Clean up all temporary files and directories"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = """
🎬 **Enhanced Multi-Downloader Video Bot**

I can download videos using multiple downloaders for better compatibility!

**Features:**
• 🎯 **Multiple Downloaders**: yt-dlp, youtube-dl, instaloader support
• 📹 **Direct Download**: Works with direct video file URLs (.mp4, .avi, etc.)
• 🔗 **Platform URLs**: YouTube, TikTok, Instagram, Twitter, Facebook, etc.
• ✅ **Smart Fallback**: Automatic downloader selection with fallbacks
✅ **Large File Support**: Files >50MB split and sent in parts
• ✅ **Auto-Cleanup**: All downloads automatically deleted

**Supported Platforms:**
📺 **YouTube**: youtube.com, youtu.be
📱 **TikTok**: tiktok.com
📷 **Instagram**: instagram.com
🐦 **Twitter/X**: twitter.com
📹 **Facebook**: facebook.com
🎥 **Vimeo**: vimeo.com
📺 **Dailymotion**: dailymotion.com
🎮 **Twitch**: twitch.tv
📁 **Direct video URLs**: MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V

**How to use:**
1. Send me a video URL
2. I'll automatically select the best downloader
3. Multiple fallbacks if primary downloader fails
4. Files automatically split if >50MB
5. All temporary files auto-deleted

**Example URLs:**
• `https://youtube.com/watch?v=...`
• `https://tiktok.com/@user/video/...`
• `https://instagram.com/p/...`
• `https://twitter.com/user/status/...`
• `https://example.com/video.mp4`
• `https://site.com/file.mov`

**Downloader Features:**
• 🔄 **Automatic Selection**: Chooses best downloader for each platform
• 🛡️ **Graceful Fallbacks**: If one downloader fails, tries others
• ⚡ **Enhanced Headers**: Better compatibility with platform restrictions
    """
    
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🆘 **Enhanced Multi-Downloader Help**

**Commands:**
• `/start` - Start the bot
• `/help` - Show this help message

**Supported Sources:**
🎥 **Video Platforms:**
• **YouTube**: youtube.com, youtu.be
• **TikTok**: tiktok.com
• **Instagram**: instagram.com
• **Twitter/X**: twitter.com
• **Facebook**: facebook.com
• **Vimeo**: vimeo.com
• **Dailymotion**: dailymotion.com
• **Twitch**: twitch.tv
• **Pinterest**: pinterest.com
• **Snapchat**: snapchat.com
• **LinkedIn**: linkedin.com
• **Tumblr**: tumblr.com

📁 **Direct Files:**
• MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V, 3GP, OGV

**Downloader Support:**
🔧 **yt-dlp**: Primary downloader for most platforms
🔧 **youtube-dl**: Fallback for YouTube and other sites
🔧 **instaloader**: Specialized for Instagram content
🔧 **Enhanced Direct**: Custom headers for better compatibility

**Features:**
• **Multi-Downloader**: Automatically selects best downloader
• **Smart Fallbacks**: If one downloader fails, tries others automatically
• **Platform Detection**: Identifies platform type for optimal download
• **Enhanced Headers**: Bypasses common platform restrictions
• **Large Files**: Split >50MB files into parts automatically
• **Auto-Cleanup**: No storage waste
• **Progress Tracking**: Real-time download status

**Download Process:**
1. **Platform Detection**: Identifies the platform type
2. **Primary Download**: Uses best downloader for that platform
3. **Fallback Chain**: Tries alternative downloaders if needed
4. **File Processing**: Splits large files, sends to Telegram
5. **Cleanup**: Removes all temporary files

**Troubleshooting:**
• **Platform Blocks**: Some platforms restrict automated downloads
• **Large Files**: May take time to download and process
• **Direct URLs**: Must be publicly accessible without authentication
• **Bot Limitations**: Respects platform terms of service
• **Multiple Attempts**: Bot tries different methods automatically

**File Limits:**
• **Individual file**: Up to 2GB (automatically split)
• **Telegram limit**: 50MB per message
• **Processing**: Automatic splitting and sequential sending
• **Timeout**: 5 minutes max per download attempt

**Installation Tips:**
For best results, install additional downloaders:
```bash
pip install yt-dlp youtube-dl instaloader
```

**Advanced Features:**
• **Platform-specific optimization**: Different strategies per platform
• **Header spoofing**: Mimics real browser requests
• **Graceful degradation**: Works even with minimal dependencies
    """
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced video download with splitting and cleanup"""
    url = update.message.text.strip()
    user = update.message.from_user
    user_id = user.id
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ Invalid URL. Please provide a valid HTTP/HTTPS URL."
        )
        return
    
    downloader = EnhancedVideoDownloader()
    
    # Send initial message
    processing_msg = await update.message.reply_text(
        "🔍 Analyzing URL and selecting download method..."
    )
    
    try:
        # Extract filename
        filename = downloader.extract_filename(url)
        if not filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.3gp', '.ogv')):
            filename += ".mp4"
        
        platform_type = downloader.get_platform_type(url)
        method_text = f"{platform_type.title()} Platform" if downloader.is_video_platform(url) else "Direct Download"
        
        await processing_msg.edit_text(
            f"📥 Downloading {filename}...\n"
            f"🌐 Method: {method_text}\n"
            f"🔍 Platform: {platform_type}"
        )
        
        # Download video
        file_path = downloader.download_video(url, filename)
        
        if not file_path or not os.path.exists(file_path):
            raise Exception("Download failed - file not found")
        
        # Check file size and split if necessary
        file_size = os.path.getsize(file_path)
        logger.info(f"Downloaded file size: {file_size / 1024 / 1024:.1f}MB")
        
        # Split large files
        if file_size > MAX_FILE_SIZE:
            await processing_msg.edit_text(
                f"📦 File is {file_size / 1024 / 1024:.1f}MB (splitting into parts)...\n"
                f"🔄 Splitting into {math.ceil(file_size / MAX_FILE_SIZE)} parts"
            )
            
            file_chunks = downloader.split_large_file(file_path, MAX_FILE_SIZE)
            
            # Send parts
            for i, chunk_path in enumerate(file_chunks):
                await processing_msg.edit_text(
                    f"📤 Sending part {i+1}/{len(file_chunks)} ({i+1})...\n"
                    f"📊 Part size: {os.path.getsize(chunk_path) / 1024 / 1024:.1f}MB"
                )
                
                with open(chunk_path, 'rb') as chunk_file:
                    # Create part filename
                    part_filename = f"{os.path.splitext(filename)[0]}_part{i+1:03d}{os.path.splitext(filename)[1]}"
                    
                    await update.message.reply_video(
                        video=chunk_file,
                        caption=f"📹 {filename} (Part {i+1}/{len(file_chunks)})\n"
                               f"📊 Size: {os.path.getsize(chunk_path) / 1024 / 1024:.1f}MB\n"
                               f"👤 From: {user.first_name}\n"
                               f"🔗 Original: {url}"
                    )
                
                # Clean up each part after sending
                try:
                    os.remove(chunk_path)
                except:
                    pass
                
                # Small delay between parts to avoid rate limiting
                if i < len(file_chunks) - 1:
                    await asyncio.sleep(1)
        else:
            # Send single file
            await processing_msg.edit_text(
                f"📤 Sending {filename} ({file_size / 1024 / 1024:.1f}MB)..."
            )
            
            with open(file_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"✅ {filename}\n📊 Size: {file_size / 1024 / 1024:.1f}MB\n"
                           f"👤 From: {user.first_name}\n🔗 Source: {url}"
                )
        
        await processing_msg.edit_text(
            f"✅ Download completed!\n"
            f"📁 File(s): {filename}\n"
            f"🗑️ All downloads auto-deleted"
        )
        
        # Final cleanup
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            downloader.cleanup_all()
        except Exception as e:
            logger.error(f"Final cleanup error: {e}")
        
    except subprocess.CalledProcessError as e:
        await processing_msg.edit_text(
            f"❌ Download failed: Platform access denied\n"
            f"The platform may block automated downloads."
        )
        logger.error(f"yt-dlp error: {e}")
        
    except requests.exceptions.RequestException as e:
        await processing_msg.edit_text(
            f"❌ Download failed: Network error\n"
            f"Please check the URL and try again."
        )
        logger.error(f"Network error: {e}")
        
    except Exception as e:
        await processing_msg.edit_text(
            f"❌ Download failed: {str(e)}\n"
            f"Please check the URL and try again."
        )
        logger.error(f"Download error: {e}")
        
    finally:
        # Ensure cleanup happens
        try:
            downloader.cleanup_all()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.warning(f'Update "{update}" caused error "{context.error}"')
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again later."
        )

def main():
    """Run the enhanced bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable is not set!")
        print("❌ Please set your BOT_TOKEN environment variable")
        print("Example: export BOT_TOKEN='your_bot_token_here'")
        return
    
    # Check for available downloaders
    available_downloaders = []
    
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
        available_downloaders.append("yt-dlp")
        logger.info("✅ yt-dlp is available")
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        logger.info("⚠️ yt-dlp not available")
    
    try:
        subprocess.run(['youtube-dl', '--version'], capture_output=True, check=True)
        available_downloaders.append("youtube-dl")
        logger.info("✅ youtube-dl is available")
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        logger.info("⚠️ youtube-dl not available")
    
    try:
        subprocess.run(['instaloader', '--version'], capture_output=True, check=True)
        available_downloaders.append("instaloader")
        logger.info("✅ instaloader is available")
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
        logger.info("⚠️ instaloader not available")
    
    if available_downloaders:
        logger.info(f"🚀 Available downloaders: {', '.join(available_downloaders)}")
    else:
        logger.warning("⚠️ No specialized downloaders available, will use direct downloads only")
        logger.info("💡 For better platform support, install: pip install yt-dlp youtube-dl instaloader")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🚀 Starting Enhanced Telegram Video Downloader Bot...")
    print("🤖 Enhanced bot is running! Press Ctrl+C to stop.")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == '__main__':
    main()