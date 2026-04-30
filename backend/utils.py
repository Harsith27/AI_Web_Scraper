from __future__ import annotations

import csv
import io
import json
import re
from typing import Any, Sequence
from urllib.parse import urljoin


BLOCKED_HINTS = (
	"access denied",
	"forbidden",
	"robot check",
	"captcha",
	"unusual traffic",
	"temporarily blocked",
)


def clean_text(value: str | None) -> str:
	if not value:
		return ""
	value = re.sub(r"\s+", " ", value)
	return value.strip()


def deduplicate_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
	seen: set[tuple[tuple[str, str], ...]] = set()
	deduped: list[dict[str, Any]] = []
	for row in rows:
		key = tuple(sorted((str(k), clean_text(str(v))) for k, v in row.items() if clean_text(str(v))))
		if key and key not in seen:
			seen.add(key)
			deduped.append(row)
	return deduped


def rows_to_csv(rows: Sequence[dict[str, Any]]) -> str:
	if not rows:
		return ""
	columns: list[str] = []
	for row in rows:
		for key in row.keys():
			if key not in columns:
				columns.append(key)

	buffer = io.StringIO()
	writer = csv.DictWriter(buffer, fieldnames=columns)
	writer.writeheader()
	for row in rows:
		writer.writerow({column: row.get(column, "") for column in columns})
	return buffer.getvalue()


def make_absolute_url(base_url: str, href: str | None) -> str:
	if not href:
		return ""
	return urljoin(base_url, href)


def looks_blocked(status_code: int, html: str) -> bool:
	if status_code in {403, 429}:
		return True
	lowered = html.lower()
	return any(hint in lowered for hint in BLOCKED_HINTS)


def html_is_empty(html: str) -> bool:
	if not html:
		return True
	text = re.sub(r"<[^>]+>", "", html)
	return len(clean_text(text)) < 80 and len(clean_text(html)) < 250


def truncate_text(value: str, limit: int = 10000) -> str:
	if len(value) <= limit:
		return value
	return value[:limit]


def extract_first_json(text: str) -> Any:
	text = text.strip()
	if not text:
		raise ValueError("Empty LLM response")

	if text.startswith("```"):
		text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
		text = re.sub(r"```$", "", text).strip()

	try:
		return json.loads(text)
	except json.JSONDecodeError:
		pass

	start = text.find("{")
	if start == -1:
		raise ValueError("No JSON object found in LLM response")

	in_string = False
	escaped = False
	depth = 0
	end = None
	for index in range(start, len(text)):
		char = text[index]
		if in_string:
			if escaped:
				escaped = False
			elif char == "\\":
				escaped = True
			elif char == '"':
				in_string = False
		else:
			if char == '"':
				in_string = True
			elif char == "{":
				depth += 1
			elif char == "}":
				depth -= 1
				if depth == 0:
					end = index + 1
					break

	if end is None:
		raise ValueError("Could not isolate JSON object in LLM response")
	return json.loads(text[start:end])


def compact_html_snippet(html: str, limit: int = 8000) -> str:
	cleaned = re.sub(r"\s+", " ", html)
	return truncate_text(cleaned, limit)


def ensure_list(value: Any) -> list[Any]:
	if value is None:
		return []
	if isinstance(value, list):
		return value
	return [value]