import asyncio
import os
import tempfile
import time
from typing import Dict, Any
from tools.base_tool import BaseTool

class WebNavigatorAgentTool(BaseTool):
    """Autonomous Web Agent tool powered by Playwright for site navigation and data extraction."""

    name = "web_navigator"
    description = "Navigates websites, searches web pages, extracts text content, and captures web page screenshots using Playwright."

    def execute(self, action: str, url: str = None, query: str = None, headless: bool = True) -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return ("⚠️ Playwright library is not installed.\n"
                    "Install it using: `pip install playwright` then `playwright install chromium`.")

        action = (action or "").lower().strip()
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(viewport={"width": 1280, "height": 800})
                page = context.new_page()

                if action in ["navigate", "visit", "open"] and url:
                    if not url.startswith(("http://", "https://")):
                        url = "https://" + url
                    page.goto(url, timeout=25000, wait_until="domcontentloaded")
                    title = page.title()
                    text_content = page.evaluate("document.body.innerText")[:1500]
                    browser.close()
                    return f"🌐 **Navigated to**: [{title}]({url})\n\n**Page Snippet**:\n{text_content}..."

                elif action in ["search", "search_web"] and query:
                    search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
                    page.goto(search_url, timeout=25000, wait_until="domcontentloaded")
                    links = page.query_selector_all(".result__title .result__url")
                    snippets = page.query_selector_all(".result__snippet")

                    results = []
                    for i in range(min(5, len(links))):
                        href = links[i].get_attribute("href") or ""
                        snippet_text = snippets[i].inner_text() if i < len(snippets) else ""
                        results.append(f"{i+1}. {snippet_text} ({href})")

                    browser.close()
                    res_str = "\n".join(results) if results else "No search results found."
                    return f"🔍 **Web Search Results for**: *{query}*\n\n{res_str}"

                elif action in ["screenshot", "capture"] and url:
                    if not url.startswith(("http://", "https://")):
                        url = "https://" + url
                    page.goto(url, timeout=25000, wait_until="domcontentloaded")
                    temp_dir = tempfile.gettempdir()
                    filepath = os.path.join(temp_dir, f"web_capture_{int(time.time())}.png")
                    page.screenshot(path=filepath, full_page=False)
                    browser.close()
                    return f"📸 Web page screenshot captured and saved to: `{filepath}`"

                else:
                    browser.close()
                    return f"⚠️ Unsupported web action '{action}'. Options: 'navigate' (with url), 'search' (with query), 'screenshot' (with url)."

        except Exception as e:
            return f"Web Navigator Agent Error: {e}"
