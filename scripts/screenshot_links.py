"""
Automatically capture screenshots for URLs in Excel and save to images/ folder.

Requires:
- Google Chrome installed
- chromedriver available in PATH
"""

import argparse
import hashlib
import os
import time
import ast
import sys

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# Optional Image Enhancement
try:
    from PIL import Image, ImageEnhance
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False


# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.config import IMAGES_DIR


def hash_url(u: str) -> str:
    return hashlib.md5(u.encode()).hexdigest()[:12]


def enhance_image(path: str, brightness: float = 1.12, contrast: float = 1.08):
    if not PIL_AVAILABLE:
        return
    try:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img.save(path, optimize=True, quality=90)
    except Exception:
        pass


def close_popups(driver, wait_short: float = 0.5):
    """General popup closing"""
    try:
        for _ in range(3):
            try:
                driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            except:
                pass
            time.sleep(0.25)
    except:
        pass

    time.sleep(wait_short)

    selectors = [
        'button[aria-label="Close"]',
        'button[title="Close"]',
        'button[class*="close"]',
        'button[class*="dismiss"]',
        'button[class*="cookie"]',
        '.modal .close',
        '.modal button.close',
        '.newsletter-modal button',
        '.cookie-consent button',
        '.cookie-banner button',
        '.overlay button',
    ]

    for sel in selectors:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                try:
                    el.click()
                except:
                    try:
                        driver.execute_script("arguments[0].click();", el)
                    except:
                        pass
                time.sleep(wait_short)
        except:
            pass

    time.sleep(wait_short)


# ----------------------------------------------------------------------
# SPECIAL HANDLING FOR INSTAGRAM
# ----------------------------------------------------------------------
def handle_instagram(driver):
    """
    Remove login popup and force-play reel.
    """
    time.sleep(3)

    # Remove login/signup dialogs aggressively
    js_remove_ig_login = """
        try {
            document.querySelectorAll('[role="dialog"]').forEach(e => e.remove());
            document.querySelectorAll('div[style*="backdrop"]').forEach(e => e.remove());
            document.querySelectorAll('div[style*="position: fixed"]').forEach(e => e.remove());
            document.querySelectorAll('._a9-z').forEach(e => e.remove());  // Login popup container
            document.querySelectorAll('._a9--').forEach(e => e.remove());  // Overlay cover
        } catch(e){}
    """
    try:
        driver.execute_script(js_remove_ig_login)
    except:
        pass

    time.sleep(1)

    # Try clicking "Not Now"
    try:
        for b in driver.find_elements(By.TAG_NAME, "button"):
            try:
                if b.text.lower() in ["not now", "no thanks"]:
                    b.click()
                    time.sleep(1)
            except:
                pass
    except:
        pass

    time.sleep(1)

    # Auto-play reel video
    try:
        video = driver.find_element(By.TAG_NAME, "video")
        driver.execute_script("arguments[0].muted = true;", video)
        driver.execute_script("arguments[0].play();", video)
        driver.execute_script("arguments[0].scrollIntoView(true);", video)
        time.sleep(1.5)
    except:
        pass


# ----------------------------------------------------------------------
# SPECIAL HANDLING FOR YOUTUBE
# ----------------------------------------------------------------------
def handle_youtube(driver):
    time.sleep(3)

    # Close popups: sign-in, cookie, premium
    yt_text_close = [
        "no thanks", "not now", "dismiss", "skip", "close", "i agree"
    ]

    try:
        for b in driver.find_elements(By.XPATH, "//button|//tp-yt-paper-button"):
            try:
                t = b.text.strip().lower()
                if any(x in t for x in yt_text_close):
                    b.click()
                    time.sleep(1)
            except:
                pass
    except:
        pass

    time.sleep(1)

    # Auto-play video
    try:
        driver.execute_script("""
            try {
                document.querySelector('video').muted = true;
                document.querySelector('video').play();
            } catch(e){}
        """)
    except:
        pass

    time.sleep(1)

    # Scroll into the video
    try:
        v = driver.find_element(By.TAG_NAME, "video")
        driver.execute_script("arguments[0].scrollIntoView(true);", v)
    except:
        pass


# ----------------------------------------------------------------------
# MAIN CAPTURE FUNCTION
# ----------------------------------------------------------------------
def capture_screenshots(url: str, out_prefix: str, shots: int = 3, delay: float = 1.0):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,2200")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)

    # Special IG handling
    if "instagram.com" in url:
        handle_instagram(driver)

    # Special YT handling
    if "youtube.com" in url or "youtu.be" in url:
        handle_youtube(driver)

    # GENERAL popup cleaning (after special handlers)
    try:
        close_popups(driver)
    except:
        pass

    out_files = []
    for i in range(shots):
        out_path = os.path.join(IMAGES_DIR, f"{out_prefix}_{i}.png")

        # Refresh removal each shot
        try:
            close_popups(driver)
        except:
            pass

        # Inject CSS reset to remove backdrop-filter/filter effects and dark translucent overlays
        css_reset = '''
try {
    const css = document.createElement('style');
    css.type = 'text/css';
    css.id = 'screenshot-helper-reset';
    css.appendChild(document.createTextNode(`
        * { background: transparent !important; background-color: transparent !important; filter: none !important; -webkit-filter: none !important; backdrop-filter: none !important; -webkit-backdrop-filter: none !important; opacity: 1 !important; mix-blend-mode: normal !important; }
        html, body { background: transparent !important; }
        ::backdrop { background: transparent !important; }
    `));
    const prev = document.getElementById('screenshot-helper-reset');
    if (prev) prev.remove();
    document.head.appendChild(css);
} catch(e){}
'''
        try:
            driver.execute_script(css_reset)
        except Exception:
            pass

        driver.save_screenshot(out_path)

        try:
            enhance_image(out_path)
        except:
            pass

        out_files.append(out_path)
        time.sleep(delay)
    driver.quit()
    return out_files


# ----------------------------------------------------------------------
# URL SHOT COUNT DECISION
# ----------------------------------------------------------------------
def determine_shots_for_url(url: str, default: int = 1) -> int:
    if not url:
        return default
    u = url.lower()

    if "instagram.com/reel" in u or "/reel/" in u or "/reels/" in u:
        return 3

    if "youtube.com" in u or "youtu.be" in u:
        return 3

    return default


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Capture screenshots from links listed in an Excel file')
    parser.add_argument('--excel', required=True, help='Path to the Excel file containing a `links` column')
    parser.add_argument('--shots', type=int, default=0, help='Override number of shots per URL (0 = use per-URL logic)')
    parser.add_argument('--limit', type=int, default=10, help='Maximum number of rows to process')
    parser.add_argument('--start', type=int, default=0, help='Row index to start from (0-based)')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between shots')
    parser.add_argument('--skip-logins', action='store_true', help='Skip URLs that look like login pages based on URL tokens')

    args = parser.parse_args()

    df = pd.read_excel(args.excel)
    processed = 0
    end = min(len(df), args.start + args.limit)
    for idx in range(args.start, end):
        row = df.iloc[idx]
        raw = row.get('links', '')
        try:
            parsed = ast.literal_eval(raw)
            url = parsed[0] if parsed else None
        except Exception:
            url = raw
        if not url or str(url).strip() == '':
            continue

        # optional skip-login based on URL heuristics
        if args.skip_logins:
            lurl = str(url).lower()
            login_tokens = ['login', 'signin', 'sign-in', 'auth', 'accounts', 'challenge']
            if any(t in lurl for t in login_tokens):
                print(f'Skipped (login-like URL): {url}')
                continue

        # decide shots: use explicit override if provided, otherwise per-URL logic
        if args.shots and args.shots > 0:
            shots = args.shots
        else:
            shots = determine_shots_for_url(url, default=1)

        print(f'[{processed+1}/{end - args.start}] Capturing: {url} (shots={shots})')
        try:
            out = capture_screenshots(url, hash_url(url), shots=shots, delay=args.delay)
            print('   Saved:', out)
        except Exception as e:
            print('   Failed:', repr(e))

        processed += 1

    print('DONE - processed', processed, 'rows')
