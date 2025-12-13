"""
Telegram Notification Module
Sends notifications when cookies need refresh or all videos are done
"""
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_telegram_message(message: str) -> bool:
    """Send a message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Telegram notification sent!")
            return True
        else:
            logger.error(f"❌ Telegram error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")
        return False


def notify_cookies_needed():
    """Send notification that cookies need refresh"""
    message = """🍪 <b>COOKIES REFRESH NEEDED!</b>

Your YouTube automation needs fresh cookies.

<b>Steps:</b>
1. Open YouTube in browser (logged in)
2. Export cookies using browser extension
3. Encode and update YOUTUBE_COOKIES secret in GitHub

⏰ Please refresh within 24 hours!"""
    
    return send_telegram_message(message)


def notify_all_videos_complete():
    """Send notification that all videos are processed"""
    message = """🎉 <b>ALL VIDEOS COMPLETE!</b>

All video parts have been uploaded to YouTube Shorts!

<b>What to do:</b>
1. Check your YouTube channel
2. Update cookies if you want to process new videos

✅ Great work! Channel growing! 📈"""
    
    return send_telegram_message(message)


def notify_video_uploaded(video_title: str, part_num: int, total_parts: int):
    """Send notification when a part is uploaded"""
    complete_emoji = "🎉 Video complete!" if part_num == total_parts else f"⏳ {total_parts - part_num} parts remaining"
    
    message = f"""✅ <b>Part Uploaded!</b>

📹 <b>{video_title}</b>
📊 Part {part_num}/{total_parts}

{complete_emoji}"""
    
    return send_telegram_message(message)


def notify_error(error_message: str):
    """Send error notification"""
    message = f"""⚠️ <b>AUTOMATION ERROR!</b>

{error_message}

Please check the GitHub Actions logs for details."""
    
    return send_telegram_message(message)


if __name__ == "__main__":
    print("Testing Telegram notification...")
    result = send_telegram_message("🧪 Test: MrBeast Shorts Bot is working!")
    print("Success!" if result else "Failed - check credentials")
