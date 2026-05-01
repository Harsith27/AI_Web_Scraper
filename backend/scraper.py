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

def _is_navigation_element(elem) -> bool:
	nav_indicators = ['header', 'nav', 'menu', 'footer', 'breadcrumb', 'search', 'filter', 'sidebar', 'top-bar', 'navbar']
	classes = ' '.join(elem.get('class', [])).lower()
	id_attr = elem.get('id', '').lower()
	data_test = elem.get('data-test', '').lower()
	combined = f"{classes} {id_attr} {data_test}"
	return any(indicator in combined for indicator in nav_indicators)


def _find_repeating_containers(soup: BeautifulSoup) -> list:
	semantic_selectors = ['[data-test*="item"]', '[data-test*="card"]', '[role="listitem"]']
	for selector in semantic_selectors:
		containers = soup.select(selector)
		if len(containers) >= 2:
			filtered = [c for c in containers if not _is_navigation_element(c)]
			if len(filtered) >= 2:
				return filtered
	return soup.find_all(['article', 'li', 'div', 'section'])


def _deduplicate_similar_fields(fields: set) -> set:
	field_groups = {
		'content': ['description', 'summary', 'body', 'content', 'text', 'excerpt'],
		'title': ['title', 'name', 'headline'],
		'tags': ['tags', 'categories', 'labels', 'keywords'],
	}
	deduplicated = set(fields)
	for _, group_fields in field_groups.items():
		group_members = [f for f in group_fields if f in deduplicated]
		if len(group_members) > 1:
			for f in group_members[1:]:
				deduplicated.discard(f)
	return deduplicated


def _infer_fields_from_content(container) -> set[str]:
	detected = set()
	text = container.get_text(' ', strip=True)
	if container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
		detected.add('title')
	if container.find_all('li'):
		detected.add('tags')
	if len(text) > 50:
		detected.add('description')
	return detected


def _analyze_container_for_fields(container) -> set[str]:
	detected = set()
	for elem in container.find_all(True):
		classes = ' '.join(elem.get('class', [])).lower()
		itemprop = elem.get('itemprop', '').lower()
		combined = f"{classes} {itemprop}"
		if 'title' in combined or 'name' in combined:
			detected.add('title')
		if 'author' in combined:
			detected.add('author')
		if 'tag' in combined:
			detected.add('tags')
		if 'price' in combined:
			detected.add('price')
	if not detected:
		detected.update(_infer_fields_from_content(container))
	return detected


def discover_available_fields(html: str) -> list[str]:
	soup = BeautifulSoup(html, 'html.parser')
	containers = _find_repeating_containers(soup)
	detected_fields = set()
	for container in containers[:5]:
		detected_fields.update(_analyze_container_for_fields(container))
	if not detected_fields:
		detected_fields = {'title', 'description'}
	detected_fields = _deduplicate_similar_fields(detected_fields)
	priority_order = ['title', 'description', 'author', 'tags', 'price', 'rating', 'date', 'company', 'location']
	result = [f for f in priority_order if f in detected_fields]
	result.extend(sorted(detected_fields - set(priority_order)))
	return result if result else ['title', 'description']