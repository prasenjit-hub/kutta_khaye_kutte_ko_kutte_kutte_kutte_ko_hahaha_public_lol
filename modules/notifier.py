"""
Notification Module - Telegram + Pushover
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

# Pushover credentials
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY", "")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API_TOKEN", "")


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


def send_pushover_message(title: str, message: str, priority: int = 0) -> bool:
    """Send a message via Pushover"""
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        logger.warning("⚠️ Pushover credentials not configured")
        return False
    
    url = "https://api.pushover.net/1/messages.json"
    
    payload = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "title": title,
        "message": message,
        "priority": priority
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Pushover notification sent!")
            return True
        else:
            logger.error(f"❌ Pushover error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Pushover error: {e}")
        return False


def notify(title: str, message: str, telegram_msg: str = None):
    """Send notification via all available channels"""
    # Try Telegram
    telegram_sent = send_telegram_message(telegram_msg or f"<b>{title}</b>\n\n{message}")
    
    # Try Pushover
    pushover_sent = send_pushover_message(title, message)
    
    return telegram_sent or pushover_sent


def notify_cookies_needed():
    """Send notification that cookies need refresh"""
    title = "🍪 COOKIES REFRESH NEEDED!"
    message = """Your YouTube automation needs fresh cookies.

Steps:
1. Open YouTube in browser (logged in)
2. Export cookies using browser extension
3. Encode and update YOUTUBE_COOKIES secret in GitHub

Please refresh within 24 hours!"""
    
    telegram_msg = """🍪 <b>COOKIES REFRESH NEEDED!</b>

Your YouTube automation needs fresh cookies.

<b>Steps:</b>
1. Open YouTube in browser (logged in)
2. Export cookies using browser extension
3. Update YOUTUBE_COOKIES secret in GitHub

⏰ Please refresh within 24 hours!"""
    
    return notify(title, message, telegram_msg)


def notify_all_videos_complete():
    """Send notification that all videos are processed"""
    title = "🎉 ALL VIDEOS COMPLETE!"
    message = """All video parts have been uploaded to YouTube Shorts!

What to do:
1. Check your YouTube channel
2. Update cookies if you want to process new videos
3. The automation will pick up new videos automatically

Great work! Channel growing!"""
    
    telegram_msg = """🎉 <b>ALL VIDEOS COMPLETE!</b>

All video parts have been uploaded to YouTube Shorts!

<b>What to do:</b>
1. Check your YouTube channel
2. Update cookies if you want to process new videos

✅ Great work! Channel growing! 📈"""
    
    return notify(title, message, telegram_msg)


def notify_video_uploaded(video_title: str, part_num: int, total_parts: int):
    """Send notification when a part is uploaded"""
    title = "✅ Part Uploaded!"
    message = f"{video_title}\nPart {part_num}/{total_parts}"
    
    complete_emoji = "🎉 Video complete!" if part_num == total_parts else f"⏳ {total_parts - part_num} parts remaining"
    
    telegram_msg = f"""✅ <b>Part Uploaded!</b>

� <b>{video_title}</b>
📊 Part {part_num}/{total_parts}

{complete_emoji}"""
    
    return notify(title, message, telegram_msg)


def notify_error(error_message: str):
    """Send error notification"""
    title = "⚠️ AUTOMATION ERROR!"
    message = f"{error_message}\n\nPlease check GitHub Actions logs."
    
    telegram_msg = f"""⚠️ <b>AUTOMATION ERROR!</b>

{error_message}

Please check the GitHub Actions logs for details."""
    
    return notify(title, message, telegram_msg)


if __name__ == "__main__":
    print("Testing notifications...")
    result = notify("🧪 Test Notification", "MrBeast Shorts Bot is working!")
    print("Success!" if result else "No notification channels configured")
