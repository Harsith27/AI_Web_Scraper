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


def fetch_html_requests(url: str) -> tuple[str, int]:
	response = requests.get(url, headers=DEFAULT_HEADERS, timeout=25)
	return response.text, response.status_code


def fetch_page(url: str) -> PageBundle:
	html = ''
	status_code = 0
	try:
		html, status_code = fetch_html_requests(url)
	except requests.RequestException:
		html = ''

	if not html or looks_blocked(status_code, html) or html_is_empty(html):
		raise RuntimeError('Page could not be fetched')

	return PageBundle(url=url, html=html, used_playwright=False)