from __future__ import annotations

from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

from .utils import clean_text, html_is_empty, looks_blocked


DEFAULT_HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
	'Accept-Language': 'en-US,en;q=0.9',
}


@dataclass
class PageBundle:
	url: str
	html: str
	used_playwright: bool = False

def _render_html_with_playwright(url: str) -> tuple[str, int]:
	from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
	from playwright.sync_api import sync_playwright

	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=True)
		context = browser.new_context(viewport={'width': 1440, 'height': 2200})
		page = context.new_page()
		try:
			response = page.goto(url, wait_until='domcontentloaded', timeout=20000)
			page.wait_for_timeout(800)
			for _ in range(4):
				page.mouse.wheel(0, 2400)
				page.wait_for_timeout(300)
			try:
				page.wait_for_load_state('networkidle', timeout=5000)
			except PlaywrightTimeoutError:
				pass
			html = page.content()
			status_code = response.status if response is not None else 200
			return html, status_code
		finally:
			context.close()
			browser.close()


def _looks_like_js_shell(html: str) -> bool:
	lowered = html.lower()
	markers = ('id="root"', 'id="app"', 'data-reactroot', '__next_data__', 'window.__', 'vite/client')
	text_length = len(clean_text(re.sub(r'<[^>]+>', ' ', html)))
	return text_length < 250 and any(marker in lowered for marker in markers)


def fetch_page(url: str) -> PageBundle:
	html = ''
	status_code = 0
	used_playwright = False

	try:
		html, status_code = fetch_html_requests(url)
	except requests.RequestException:
		html = ''

	if not html or looks_blocked(status_code, html) or html_is_empty(html) or _looks_like_js_shell(html):
		html, status_code = _render_html_with_playwright(url)
		used_playwright = True

	return PageBundle(url=url, html=html, used_playwright=used_playwright)

