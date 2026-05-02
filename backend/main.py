from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from bs4 import BeautifulSoup

from .models import DiscoverFieldsRequest, DiscoverFieldsResponse, ScrapeRequest, ScrapeResponse, AskRequest, AskResponse
from .scraper import fetch_page, scrape_website, get_repeating_container_selector, answer_question, discover_available_fields


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="AI-Powered Web Scraper", version="1.0.0")

if FRONTEND_DIR.exists():
	app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.get("/")
def read_index() -> FileResponse:
	index_file = FRONTEND_DIR / "index.html"
	if not index_file.exists():
		raise HTTPException(status_code=404, detail="Frontend not found")
	return FileResponse(index_file)


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.post("/discover-fields", response_model=DiscoverFieldsResponse)
def discover_fields(payload: DiscoverFieldsRequest):
	if not payload.url.strip():
		raise HTTPException(status_code=400, detail="URL is required")
	page_bundle = fetch_page(payload.url.strip())
	soup = BeautifulSoup(page_bundle.html, "html.parser")
	container_selector = get_repeating_container_selector(soup)
	detected_fields = discover_available_fields(page_bundle.html)
	sample_data = {field: '' for field in detected_fields}
	return JSONResponse(content={"success": True, "message": "Discovery succeeded", "url": payload.url, "fields": detected_fields, "sample_data": sample_data, "container_selector": container_selector})


@app.post("/scrape", response_model=ScrapeResponse)
def scrape(payload: ScrapeRequest):
	if not payload.url.strip():
		raise HTTPException(status_code=400, detail='URL is required')
	if not payload.query.strip() and not payload.selected_fields:
		raise HTTPException(status_code=400, detail="Either 'query' or 'selected_fields' is required")
	result = scrape_website(payload.url.strip(), payload.query.strip() if payload.query.strip() else None, payload.format, selected_fields=payload.selected_fields or None)
	return JSONResponse(content=result)


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest):
	if not payload.url.strip():
		raise HTTPException(status_code=400, detail='URL is required')
	if not payload.question.strip():
		raise HTTPException(status_code=400, detail='Question is required')
	answer_payload = answer_question(payload.question.strip(), payload.data)
	return JSONResponse(content={"success": True, "answer": answer_payload.get('answer', ''), "scope": payload.scope, "intent": answer_payload.get('intent'), "field": answer_payload.get('field'), "operation": answer_payload.get('operation'), "source": answer_payload.get('source')})