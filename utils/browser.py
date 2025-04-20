# import os, random
# from playwright.sync_api import sync_playwright
# import requests

# TOKEN = os.getenv('BROWSERLESS_TOKEN')

# # 1) Local Playwright fetch
# def get_html_playwright(url, headless=True, timeout=60000):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=headless)
#         page = browser.new_page()
#         page.goto(url, timeout=timeout)
#         html = page.content()
#         browser.close()
#     return html

# # 2) Browserless fetch via HTTP API (rotates proxies, residential)
# def get_html_browserless(url, timeout=60000):
#     api = f"https://chrome.browserless.io/content?token={TOKEN}"
#     payload = {"url": url, "timeout": timeout}
#     r = requests.post(api, json=payload)
#     r.raise_for_status()
#     return r.text

# # 3) Unified helper -- choose strategy
# def get_html(url, js_render=False):
#     if js_render:
#         return get_html_playwright(url)
#     # for static pages, simple requests
#     from requests import get
#     return get(url, timeout=60000).text

# file: utils/browser.py
from playwright.sync_api import sync_playwright
import random

def get_html(url, proxy_list=None, headless=True, timeout=60000):
    """
    Opens a browser context with Playwright, optionally using a proxy (rotated from the given list),
    navigates to the URL, and returns the rendered HTML content.
    """
    selected_proxy = None
    if proxy_list:
        # Choose a random proxy from the list
        selected_proxy = random.choice(proxy_list)
    
    with sync_playwright() as p:
        launch_options = {"headless": headless}
        # Launch browser
        browser = p.chromium.launch(**launch_options)
        
        # Create a new context with proxy option if available
        context_args = {}
        if selected_proxy:
            # Example: "http://username:password@proxyserver:port"
            context_args["proxy"] = {"server": selected_proxy}
        
        context = browser.new_context(**context_args)
        page = context.new_page()
        # Go to the URL and wait for full render
        page.goto(url, timeout=timeout)
        # Optionally, wait for network idle or for a selector:
        # page.wait_for_load_state("networkidle")
        content = page.content()
        context.close()
        browser.close()
    return content
