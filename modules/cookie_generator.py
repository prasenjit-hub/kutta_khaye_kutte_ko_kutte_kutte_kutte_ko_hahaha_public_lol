"""
Automated YouTube Cookie Generator using Playwright
Logs into Google and extracts YouTube cookies for yt-dlp
"""
import os
import json
import logging
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get credentials from environment
GOOGLE_EMAIL = os.environ.get("GOOGLE_EMAIL", "")
GOOGLE_PASSWORD = os.environ.get("GOOGLE_PASSWORD", "")


async def generate_youtube_cookies():
    """
    Automate Google login and extract YouTube cookies
    """
    if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
        logger.error("❌ GOOGLE_EMAIL or GOOGLE_PASSWORD not set!")
        return False
    
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        return False
    
    logger.info("🌐 Starting automated browser login...")
    
    async with async_playwright() as p:
        # Launch browser (headless for server)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Go to YouTube (will redirect to Google login)
            logger.info("📱 Opening YouTube...")
            await page.goto("https://accounts.google.com/signin/v2/identifier?service=youtube")
            await page.wait_for_timeout(3000)
            
            # Enter email
            logger.info("📧 Entering email...")
            await page.fill('input[type="email"]', GOOGLE_EMAIL)
            await page.click('button:has-text("Next")')
            await page.wait_for_timeout(3000)
            
            # Enter password
            logger.info("🔑 Entering password...")
            await page.wait_for_selector('input[type="password"]', timeout=10000)
            await page.fill('input[type="password"]', GOOGLE_PASSWORD)
            await page.click('button:has-text("Next")')
            await page.wait_for_timeout(5000)
            
            # Check if login successful
            current_url = page.url
            if "myaccount.google.com" in current_url or "youtube.com" in current_url:
                logger.info("✅ Login successful!")
            else:
                # Maybe verification needed
                logger.warning(f"⚠️ Login might need verification. Current URL: {current_url}")
            
            # Navigate to YouTube to ensure cookies are set
            logger.info("📺 Navigating to YouTube...")
            await page.goto("https://www.youtube.com")
            await page.wait_for_timeout(5000)
            
            # Extract cookies
            cookies = await context.cookies()
            youtube_cookies = [c for c in cookies if "youtube.com" in c.get("domain", "") or "google.com" in c.get("domain", "")]
            
            if not youtube_cookies:
                logger.error("❌ No YouTube cookies found!")
                await browser.close()
                return False
            
            # Convert to Netscape format for yt-dlp
            logger.info(f"🍪 Extracted {len(youtube_cookies)} cookies")
            
            with open("youtube_cookies.txt", "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
                f.write("# This is a generated file! Do not edit.\n\n")
                
                for cookie in youtube_cookies:
                    domain = cookie.get("domain", "")
                    if not domain.startswith("."):
                        domain = "." + domain
                    
                    flag = "TRUE" if domain.startswith(".") else "FALSE"
                    path = cookie.get("path", "/")
                    secure = "TRUE" if cookie.get("secure", False) else "FALSE"
                    expires = str(int(cookie.get("expires", 0)))
                    name = cookie.get("name", "")
                    value = cookie.get("value", "")
                    
                    f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
            
            logger.info("✅ Cookies saved to youtube_cookies.txt")
            
            await browser.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            await browser.close()
            return False


def run_cookie_generator():
    """Synchronous wrapper for async function"""
    return asyncio.get_event_loop().run_until_complete(generate_youtube_cookies())


if __name__ == "__main__":
    success = run_cookie_generator()
    if success:
        print("\n✅ Cookie generation successful!")
    else:
        print("\n❌ Cookie generation failed!")
