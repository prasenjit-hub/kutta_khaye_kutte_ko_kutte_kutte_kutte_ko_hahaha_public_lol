"""
Automated YouTube Cookie Generator using Playwright
Logs into Google and extracts YouTube cookies for yt-dlp
Handles various Google login flows
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
    Handles various Google login flows
    """
    if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
        logger.error("❌ GOOGLE_EMAIL or GOOGLE_PASSWORD not set!")
        logger.error(f"   GOOGLE_EMAIL present: {bool(GOOGLE_EMAIL)}")
        logger.error(f"   GOOGLE_PASSWORD present: {bool(GOOGLE_PASSWORD)}")
        return False
    
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        return False
    
    logger.info("🌐 Starting automated browser login...")
    logger.info(f"   Email: {GOOGLE_EMAIL[:3]}***@{GOOGLE_EMAIL.split('@')[-1] if '@' in GOOGLE_EMAIL else '***'}")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            # Go to Google sign-in
            logger.info("📱 Opening Google sign-in page...")
            await page.goto("https://accounts.google.com/signin/v2/identifier?service=youtube&flowName=GlifWebSignIn")
            await page.wait_for_timeout(3000)
            
            # Enter email
            logger.info("📧 Entering email...")
            email_input = await page.wait_for_selector('input[type="email"]', timeout=15000)
            await email_input.fill(GOOGLE_EMAIL)
            await page.wait_for_timeout(1000)
            
            # Click Next
            next_button = await page.query_selector('button:has-text("Next"), #identifierNext')
            if next_button:
                await next_button.click()
            else:
                await page.keyboard.press("Enter")
            
            await page.wait_for_timeout(5000)
            
            # Check for errors
            error_msg = await page.query_selector('[class*="error"], [class*="Error"]')
            if error_msg:
                error_text = await error_msg.text_content()
                logger.error(f"❌ Google error: {error_text}")
                await browser.close()
                return False
            
            # Wait for password field
            logger.info("🔑 Waiting for password field...")
            try:
                password_input = await page.wait_for_selector(
                    'input[type="password"], input[name="Passwd"]', 
                    timeout=20000
                )
            except:
                # Maybe wrong email or verification needed
                current_url = page.url
                page_content = await page.content()
                
                if "challenge" in current_url or "verify" in current_url.lower():
                    logger.error("❌ Google requires verification (phone/email). Use a simple account without 2FA.")
                elif "identifier" in current_url:
                    logger.error("❌ Email not found. Check GOOGLE_EMAIL value.")
                else:
                    logger.error(f"❌ Unexpected page: {current_url}")
                
                await browser.close()
                return False
            
            # Enter password
            logger.info("🔑 Entering password...")
            await password_input.fill(GOOGLE_PASSWORD)
            await page.wait_for_timeout(1000)
            
            # Click Next/Sign in
            sign_in_button = await page.query_selector('button:has-text("Next"), button:has-text("Sign in"), #passwordNext')
            if sign_in_button:
                await sign_in_button.click()
            else:
                await page.keyboard.press("Enter")
            
            await page.wait_for_timeout(8000)
            
            # Check login result
            current_url = page.url
            logger.info(f"   Current URL: {current_url[:50]}...")
            
            if "challenge" in current_url or "signin" in current_url:
                logger.error("❌ Login failed - possibly wrong password or verification needed")
                await browser.close()
                return False
            
            # Navigate to YouTube
            logger.info("📺 Navigating to YouTube...")
            await page.goto("https://www.youtube.com")
            await page.wait_for_timeout(5000)
            
            # Verify we're logged in
            avatar = await page.query_selector('#avatar-btn, [aria-label*="Account"]')
            if avatar:
                logger.info("✅ Successfully logged into YouTube!")
            else:
                logger.warning("⚠️ May not be fully logged in, but continuing...")
            
            # Extract cookies
            cookies = await context.cookies()
            youtube_cookies = [c for c in cookies if "youtube.com" in c.get("domain", "") or "google.com" in c.get("domain", "")]
            
            if not youtube_cookies:
                logger.error("❌ No YouTube cookies found!")
                await browser.close()
                return False
            
            # Convert to Netscape format
            logger.info(f"🍪 Extracted {len(youtube_cookies)} cookies")
            
            with open("youtube_cookies.txt", "w") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
                f.write("# Generated by automated login\n\n")
                
                for cookie in youtube_cookies:
                    domain = cookie.get("domain", "")
                    if not domain.startswith("."):
                        domain = "." + domain
                    
                    flag = "TRUE"
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
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(generate_youtube_cookies())


if __name__ == "__main__":
    success = run_cookie_generator()
    if success:
        print("\n✅ Cookie generation successful!")
    else:
        print("\n❌ Cookie generation failed!")
