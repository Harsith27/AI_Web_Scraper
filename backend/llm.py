from __future__ import annotations

import json
import os
from typing import Any

import requests

from .models import QueryPlan, SelectorPlan
from .utils import compact_html_snippet, ensure_list, extract_first_json, truncate_text, clean_text


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")


def _has_groq_key() -> bool:
	return bool(os.getenv("GROQ_API_KEY"))


def _call_groq(messages: list[dict[str, str]], temperature: float = 0.1) -> str:
	api_key = os.getenv("GROQ_API_KEY")
	if not api_key:
		raise RuntimeError("GROQ_API_KEY is not set")

	response = requests.post(
		GROQ_API_URL,
		headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
		json={"model": DEFAULT_MODEL, "messages": messages, "temperature": temperature, "max_tokens": 700},
		timeout=60,
	)
	response.raise_for_status()
	payload = response.json()
	return payload["choices"][0]["message"]["content"]


def _fallback_query_plan(query: str) -> QueryPlan:
	lowered = query.lower()
	if any(word in lowered for word in ["job", "career", "salary", "role", "hiring"]):
		return QueryPlan(entity="job", fields=["title", "company", "location", "salary", "url"])
	if any(word in lowered for word in ["product", "price", "rating", "shop", "buy"]):
		return QueryPlan(entity="product", fields=["name", "price", "rating", "url"])
	return QueryPlan(entity="article", fields=["title", "summary", "author", "date", "url"])


def parse_query(query: str) -> dict[str, Any]:
	prompt = f"""
You are a structured data extraction planner.
Classify the user's request into one entity type: product, job, article, or other.
Return only valid JSON with this exact schema:
{{
  "entity": "product|job|article|other",
  "fields": ["field1", "field2", "field3"]
}}

User query:
{query}
""".strip()

	if not _has_groq_key():
		return _fallback_query_plan(query).model_dump()
	raw = _call_groq([
		{"role": "system", "content": "You output strict JSON only."},
		{"role": "user", "content": prompt},
	])
	data = extract_first_json(raw)
	plan = QueryPlan(entity=str(data.get("entity", "other")).strip().lower() or "other", fields=[str(field).strip().lower() for field in ensure_list(data.get("fields")) if str(field).strip()])
	return plan.model_dump()


def _fallback_question_intent(question: str, fields: list[str]) -> dict[str, Any]:
	normalized = question.lower()
	if any(token in normalized for token in ["how many", "number of", "count"]):
		return {"intent": "count", "field": "", "operation": "count"}
	return {"intent": "lookup", "field": fields[0] if fields else "", "operation": "lookup"}


def classify_question_intent(question: str, fields: list[str]) -> dict[str, Any]:
	prompt = f"""
You are an intent classifier for questions about scraped structured data.
Return only valid JSON with this exact schema:
{{
  "intent": "count|max|min|average|sum|lookup|unknown",
  "field": "field_name or empty",
  "operation": "count|max|min|average|sum|lookup|unknown"
}}

Available fields: {json.dumps(fields)}

Question:
{question}
""".strip()

	if not _has_groq_key():
		return _fallback_question_intent(question, fields)
	raw = _call_groq([
		{"role": "system", "content": "You output strict JSON only."},
		{"role": "user", "content": prompt},
	])
	data = extract_first_json(raw)
	return {
		'intent': str(data.get('intent', 'unknown')).strip().lower(),
		'field': str(data.get('field', '')).strip(),
		'operation': str(data.get('operation', 'unknown')).strip().lower(),
	}


def answer_dataset_question(question: str, data: list[dict[str, str]]) -> str:
	prompt = f"""
You are a data assistant. Answer the user's question using only the extracted rows below.
Return exactly one clear sentence.

Extracted rows:
{truncate_text(json.dumps(data, indent=2, ensure_ascii=False), limit=7500)}

Question:
{question}
""".strip()

	if not _has_groq_key():
		if not data:
			return "No data available to answer the question."
		return f"The first row contains {', '.join(list(data[0].keys())[:3])}."

	raw = _call_groq([
		{"role": "system", "content": "You output a concise answer only. Do not hallucinate."},
		{"role": "user", "content": prompt},
	], temperature=0.0)
	return raw.strip()


def generate_selectors(html_snippet: str, fields: list[str]) -> dict[str, Any]:
	prompt = f"""
You are given HTML from a repeating listing page.
Return only valid JSON with this exact schema:
{{
  "container": "css_selector",
  "fields": {{
	"field_name": "css_selector_relative_to_container"
  }}
}}

Fields:
{json.dumps(fields)}

HTML snippet:
{compact_html_snippet(html_snippet)}
""".strip()

	if not _has_groq_key():
		return {"container": "", "fields": {field: "" for field in fields}}
	raw = _call_groq([
		{"role": "system", "content": "You output strict JSON only."},
		{"role": "user", "content": prompt},
	])
	data = extract_first_json(raw)
	return SelectorPlan(container=str(data.get("container", "")).strip(), fields={field: str(data.get("fields", {}).get(field, "")).strip() for field in fields}).model_dump()


def analyze_available_fields(html_snippet: str) -> list[str]:
	if not _has_groq_key():
		if any(x in html_snippet.lower() for x in ["price", "product", "buy", "$"]):
			return ["title", "price", "rating", "url"]
		if any(x in html_snippet.lower() for x in ["job", "career", "apply", "salary"]):
			return ["title", "company", "location", "salary", "url"]
		return ["title", "description", "author", "date", "url"]
	raw = _call_groq([
		{"role": "system", "content": "You output strict JSON only. No explanation."},
		{"role": "user", "content": "Return a JSON array of field names only."},
	])
	data = extract_first_json(raw)
	return [str(f).strip().lower() for f in data if isinstance(f, str)] if isinstance(data, list) else ["title", "description", "url"]


def answer_question_with_context(question: str, context_chunks: list[str], page_title: str = "", url: str = "") -> dict[str, Any]:
	prompt = f"""
You answer questions using only the supplied webpage context.
Return only valid JSON with this exact schema:
{{
  "answer": "short grounded answer",
  "evidence": ["relevant excerpt 1", "relevant excerpt 2"]
}}

Question:
{question}

Context:
{chr(10).join(f"[{index + 1}] {chunk}" for index, chunk in enumerate(context_chunks))}
""".strip()

	if not _has_groq_key():
		return {"answer": context_chunks[0][:700] if context_chunks else "I could not find enough relevant text to answer that question.", "evidence": context_chunks[:3]}
	raw = _call_groq([
		{"role": "system", "content": "You output strict JSON only."},
		{"role": "user", "content": prompt},
	], temperature=0.0)
	data = extract_first_json(raw)
	return {"answer": str(data.get("answer", "")).strip(), "evidence": [str(item).strip() for item in ensure_list(data.get("evidence")) if str(item).strip()][:3]}