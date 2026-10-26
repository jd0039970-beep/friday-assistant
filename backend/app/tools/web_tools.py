"""Playwright-based web tools."""
from __future__ import annotations

from .registry import ToolRegistry

_browser = None


def _get_browser(headless: bool = True):
    global _browser
    if _browser is None:
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        _browser = p.chromium.launch(headless=headless)
    return _browser


def register_web_tools(reg: ToolRegistry, headless: bool = True):
    def browse_url(url: str) -> str:
        """Open a URL and return page title + main text content (truncated)."""
        try:
            browser = _get_browser(headless)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            title = page.title()
            # Prefer main / article text
            text = page.inner_text("body")[:6000]
            page.close()
            return f"Title: {title}\n\n{text}"
        except Exception as e:
            return f"ERROR browsing {url}: {e}"

    def search_web(query: str) -> str:
        """Simple web search via DuckDuckGo HTML (no API key)."""
        from urllib.parse import quote_plus
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        return browse_url(url)

    reg.register(
        "browse_url",
        "Open a URL and extract the main text content",
        {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        browse_url,
    )
    reg.register(
        "search_web",
        "Search the web and return results summary",
        {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        search_web,
    )
