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

# Repository link for secrets
REPO_SECRETS_URL = "https://github.com/prasenjit-hub/kutta_khaye_kutte_ko_kutte_kutte_kutte_ko_hahaha_public_lol/settings/secrets/actions"


def send_telegram_message(message: str) -> bool:
    """Send a message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️ Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
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
    message = f"""🍪 <b>COOKIES REFRESH NEEDED!</b>

YouTube automation ko fresh cookies chahiye.

<b>Steps:</b>
1. YouTube open karo browser mein (logged in)
2. Cookies export karo
3. Base64 encode karo
4. YOUTUBE_COOKIES secret update karo

🔗 <b>Direct Link:</b>
{REPO_SECRETS_URL}

⏰ Please 24 hours mein refresh karo!"""
    
    return send_telegram_message(message)


def notify_all_videos_complete():
    """Send notification that all videos are processed"""
    message = """🎉 <b>ALL VIDEOS COMPLETE!</b>

Sab video parts YouTube Shorts pe upload ho gaye!

<b>What to do:</b>
1. YouTube channel check karo
2. Naye videos ke liye cookies refresh karo

✅ Great work! Channel growing! 📈"""
    
    return send_telegram_message(message)


def notify_video_uploaded(video_title: str, part_num: int, total_parts: int, video_url: str = None):
    """Send notification when a part is uploaded"""
    complete_emoji = "🎉 Video complete!" if part_num == total_parts else f"⏳ {total_parts - part_num} parts remaining"
    
    url_line = f"\n🔗 <a href='{video_url}'>Watch on YouTube</a>" if video_url else ""
    
    message = f"""✅ <b>Part Uploaded!</b>

📹 <b>{video_title[:50]}</b>
📊 Part {part_num}/{total_parts}
{url_line}

{complete_emoji}"""
    
    return send_telegram_message(message)


def notify_download_failed(video_title: str, reason: str = ""):
    """Send notification when download fails"""
    message = f"""⚠️ <b>DOWNLOAD FAILED!</b>

📹 Video: <b>{video_title[:50]}</b>
❌ Reason: {reason or 'Hindi audio not available or cookies expired'}

<b>Action needed:</b>
1. Check if video has Hindi audio
2. Refresh cookies if expired

🔗 <b>Secrets Link:</b>
{REPO_SECRETS_URL}"""
    
    return send_telegram_message(message)


def notify_error(error_message: str):
    """Send error notification"""
    message = f"""⚠️ <b>AUTOMATION ERROR!</b>

{error_message}

🔗 <b>Check Logs:</b>
https://github.com/prasenjit-hub/kutta_khaye_kutte_ko_kutte_kutte_kutte_ko_hahaha_public_lol/actions"""
    
    return send_telegram_message(message)


if __name__ == "__main__":
    print("Testing Telegram notification...")
    result = send_telegram_message("🧪 Test: MrBeast Shorts Bot is working!")
    print("Success!" if result else "Failed - check credentials")
