import os, random
from playwright.sync_api import sync_playwright
import requests

TOKEN = os.getenv('BROWSERLESS_TOKEN')

# 1) Local Playwright fetch
def get_html_playwright(url, headless=True, timeout=60000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url, timeout=timeout)
        html = page.content()
        browser.close()
    return html

# 2) Browserless fetch via HTTP API (rotates proxies, residential)
def get_html_browserless(url, timeout=60000):
    api = f"https://chrome.browserless.io/content?token={TOKEN}"
    payload = {"url": url, "timeout": timeout}
    r = requests.post(api, json=payload)
    r.raise_for_status()
    return r.text

# 3) Unified helper -- choose strategy
def get_html(url, js_render=False):
    if js_render:
        return get_html_playwright(url)
    # for static pages, simple requests
    from requests import get
    return get(url, timeout=60000).text