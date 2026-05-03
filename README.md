# Web Scraping AI

This repository contains a working prototype of a web scraping assistant built with Python and JavaScript.

The application is intended to demonstrate a modular scraping architecture, an API-driven extraction workflow, and a conversion-ready documentation style.

---

## Overview

`Web_Scraping_AI` is a sample implementation of a web data discovery and scraping system. It combines:

- a FastAPI backend for serving API endpoints
- a scraping helper module for fetching and analyzing HTML pages
- a lightweight frontend for field discovery and extraction planning
- a document-ready README with detailed architecture and usage guidance

The codebase is structured so that the backend and frontend are separated, making it easier to extend individual components.

---

## Repository Contents

The repository includes the following main components:

- `backend/main.py` — FastAPI application and API route definitions
- `backend/models.py` — request and response models for the API
- `backend/scraper.py` — page fetching, scraping utilities, and container heuristics
- `backend/rag.py` — helper utilities for a future question-answering workflow
- `frontend/index.html` — page layout and interface structure
- `frontend/script.js` — client-side logic for discovery and field rendering
- `frontend/style.css` — styling and theme definitions
- `requirements.txt` — Python dependency specification
- `README.md` — project documentation and usage guide

---

## Technology Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Backend | Python 3.x | Application logic and server runtime |
| API | FastAPI | HTTP routing, request validation and response modeling |
| HTML parsing | BeautifulSoup | Page inspection and selector heuristics |
| HTTP client | requests | Remote page retrieval |
| Frontend | HTML / CSS / JavaScript | User interface and interaction |
| Styling | Tailwind CSS + custom CSS | Layout, theme, and responsive presentation |

---

## Module Summary

| Module | Purpose |
| --- | --- |
| `backend/main.py` | API endpoints and static file serving |
| `backend/models.py` | Request and response schema definitions |
| `backend/scraper.py` | Web page fetching and scraping helper functions |
| `backend/rag.py` | Placeholder text chunking and answer helper functions |
| `frontend/index.html` | Entry page structure and markup |
| `frontend/script.js` | Form handling, API calls, and field rendering |
| `frontend/style.css` | Visual styling and dark theme support |

---

## Project Structure

```text
Web_Scraping_AI/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── rag.py
│   └── scraper.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── .gitignore
├── README.md
├── requirements.txt
```

The separation of backend and frontend code supports clear responsibilities and maintainable evolution.

---

## System Overview

This prototype implements a three-phase workflow:

1. discovery
2. extraction
3. question answering

The frontend is responsible for user interaction and display. The backend handles API routing, request validation, scraping helpers, and placeholder answer logic.

### Discovery phase

The discovery phase analyzes a target URL and returns candidate fields that can be extracted.

### Extraction phase

The extraction phase is designed to convert selected fields into structured results. The current implementation returns sample data to keep the flow demonstrable.

### Question answering phase

The question answering phase is scaffolded for future expansion. It accepts context and a query and currently returns a placeholder response.

---

## Backend Components

### `backend/main.py`

The backend entrypoint defines the following endpoints:

- `GET /` — serves the frontend page
- `GET /health` — returns service health status
- `POST /discover-fields` — accepts a URL and returns candidate scraping fields
- `POST /scrape` — accepts a scrape request and returns structured data
- `POST /ask` — accepts a question request and returns a placeholder answer

The backend uses FastAPI for routing and Pydantic for input validation.

### `backend/models.py`

This module defines the API schema for requests and responses.

Models include:

- `DiscoverFieldsRequest`
- `DiscoverFieldsResponse`
- `ScrapeRequest`
- `ScrapeResponse`
- `AskRequest`
- `AskResponse`

They ensure data consistency between frontend and backend.

### `backend/scraper.py`

This module contains the scraping utility functions.

Key functionality includes:

- `fetch_html_requests()` — fetches raw HTML using a browser-like user agent
- `fetch_page()` — wraps HTML content into a `PageBundle`
- `scrape_website()` — returns a sample structured result payload
- `get_repeating_container_selector()` — attempts to identify a repeating container selector

The module provides a foundation for adding real extraction logic.

### `backend/rag.py`

This module provides helper utilities intended for future retrieval-augmented workflows.

It includes:

- `chunks_from_text()` — splits page text into smaller chunks
- `answer_page_question()` — generates a placeholder page-based answer
- `answer_data_question()` — generates a placeholder answer based on extracted data

This module is designed to be replaced with a true RAG or LLM-based answer engine when the project evolves.

---

## Frontend Components

### `frontend/index.html`

The frontend page contains the UI layout for the discovery workflow.

It provides:

- a URL input field
- a submit button for discovery
- a message area for status updates
- a field list area for discovered data fields

Tailwind CSS is used via CDN to provide simple styling and layout.

### `frontend/script.js`

The frontend logic implements the basic interaction flow.

It performs the following tasks:

- validates the URL input
- sends the discovery request to the backend
- updates the state with discovered fields
- renders fields as checkbox options
- updates a query helper string based on selections

The frontend is intentionally minimal and can be extended with actual scrape and ask submission paths.

### `frontend/style.css`

The stylesheet adds the visual theme for the page.

It includes:

- page background and text color rules
- spacing and typography settings
- form control styling for buttons and inputs
- basic card styling for field results

---

## User Interface Flow

The application is designed for direct interaction through the frontend interface.

### Page load and landing state

When the page loads, the interface displays a single input card with the following elements:

- a URL entry field labeled clearly for the target website
- a primary action button labeled `Check Available Fields`
- a status area for feedback messages
- an empty results panel for discovered fields

The landing state is minimal so the user can focus immediately on entering a target URL.

### URL entry and validation

The first interaction is entering the target URL.

- the input field should accept standard web addresses
- the button remains enabled once text is present
- validation is performed before the request is sent
- if the URL is empty, the status message should explain the requirement

This step ensures that the user does not make a request until a URL is provided.

### Discovery interaction

After the user clicks `Check Available Fields`:

- the button transitions into a loading state or remains visually active
- the status area updates to show that discovery is in progress
- the frontend submits the URL to the backend discovery endpoint
- the backend returns a candidate field list and a container selector heuristic
- the frontend renders the candidate fields in the results panel

The discovery result should present each field as a checkbox item with a short label.

### Review and refinement

Once candidate fields are displayed, the user can review them:

- each discovered field is shown with an interactive checkbox
- all fields are selected by default to simplify the initial experience
- uncheck fields that are irrelevant or noisy
- as checkboxes change, the query helper updates automatically
- the status area should reflect the current number of selected fields

This refinement step gives the user control over the extraction intent without requiring custom syntax.

### Query helper and extraction intent

A query helper area summarizes the selected fields in a human-readable form.

- the helper text appears below the field list
- it should read like a natural instruction, such as `Extract title, url, description`
- the helper is updated whenever field selection changes
- it provides immediate confirmation of what will be extracted

This design reduces uncertainty and helps the user understand the extraction request.

### Scrape request submission

After reviewing field selection, the user can initiate the scrape.

- the UI should expose a scrape action button once fields are discovered
- clicking the button submits the extracted intent to the backend
- the frontend switches into a running state for the scrape operation
- the results area is reserved for the returned structured output

The scrape response is displayed in the UI rather than requiring the user to inspect raw API responses.

### Structured output presentation

The scraped result area is built to show structured data clearly.

- each returned item can be displayed as a card or table row
- the selected extraction fields should appear as labels
- sample values can be displayed in a compact format
- a JSON preview is acceptable for prototype output

The presentation should make it easy to verify that the scraped fields were captured correctly.

### Question workflow

The UI includes an optional question workflow for future development.

- a question input field is presented after discovery
- the user can type a natural language question about the page or extracted data
- a submit button triggers the question endpoint in the backend
- the returned answer is shown as readable text in the interface

This workflow demonstrates how a question-answering layer would be integrated with the extraction experience.

### Error and empty state handling

The frontend must provide clear feedback in the following cases:

- invalid or empty URL input
- backend discovery failure
- no fields discovered on the target page
- scrape request failure
- ask question failure

Each error state should be displayed in the status area with a short explanation and suggested next step.

### Example UI sequence

A typical UI flow is described below:

1. the user visits the page and sees the URL input and action button
2. the user enters `https://example.com/products`
3. the user clicks `Check Available Fields`
4. the interface displays `Discovering fields...`
5. the interface returns options such as `title`, `url`, and `description`
6. the user deselects `description` and confirms the query helper text
7. the user clicks the scrape button
8. the interface shows structured sample data for the selected fields
9. the user optionally enters a question and clicks submit
10. the interface displays the answer text below the question input

### Detailed interface behavior

The UX is designed to minimize friction and make each phase explicit.

- the field discovery card should remain visible while the results panel populates
- input fields should preserve the entered URL when results appear
- the selected field count should be visible above the field list
- the scrape action should only be available after discovery succeeds
- the question input should be disabled until extraction data is available

### UI expectations for prototype output

The current prototype expects the following output behavior:

- discovery produces simple field suggestions
- extraction returns sample data items rather than full production scraping
- questions return a placeholder answer text

The UI is intentionally scaffolded to support these prototype behaviors while leaving room for real output in future versions.

---

## UI Flow Summary

| Step | Interface action | Result |
| --- | --- | --- |
| Discovery | Enter URL and click `Check Available Fields` | Candidate fields are displayed in the UI |
| Selection | Toggle checkboxes for desired fields | Extraction intent is updated and displayed |
| Extraction | Submit the scrape request | Structured sample data is shown in the interface |
| Question | Enter a question and submit | Answer text is displayed in the interface |

---

## UI Test Case

| Scenario | UI action | Expected UI result |
| --- | --- | --- |
| Discover fields | Enter `https://example.com/products` and click `Check Available Fields` | A list of fields appears with checkboxes and a status message indicates success |
| Scrape data | Select fields and submit the scrape action | A structured result area displays sample item data and field names |

---

## API Reference

The backend API supports the frontend interface and provides the underlying data responses.

This section documents the available API endpoints and their request/response contracts.

### `GET /`

Returns the frontend page.

### `GET /health`

Returns a service health response.

Example response:

```json
{
  "status": "ok"
}
```

### `POST /discover-fields`

Discovers candidate fields for a target URL.

Request body:

```json
{
  "url": "https://example.com/products"
}
```

Response body:

```json
{
  "success": true,
  "message": "Discovery succeeded",
  "url": "https://example.com/products",
  "fields": ["title", "url", "description"],
  "sample_data": {
    "title": "",
    "url": "https://example.com/products",
    "description": ""
  },
  "container_selector": "article.some-class"
}
```

### `POST /scrape`

Extracts data based on the selected fields and query.

Request body:

```json
{
  "url": "https://example.com/products",
  "query": "Extract title, url, description",
  "selected_fields": ["title", "url", "description"],
  "format": "json"
}
```

Response body:

```json
{
  "success": true,
  "message": "Scraped sample data",
  "data": [
    {"title": "Sample title", "url": "Sample url", "description": "Sample description"}
  ],
  "fields": ["title", "url", "description"],
  "csv": null
}
```

### `POST /ask`

Accepts a question and returns a placeholder answer.

Request body:

```json
{
  "url": "https://example.com/products",
  "question": "What are the top product names?",
  "scope": "data",
  "data": []
}
```

Response body:

```json
{
  "success": true,
  "answer": "This is a placeholder answer.",
  "scope": "data"
}
```

---

## Installation

The following steps describe how to set up the repository locally.

### Clone the repository

```bash
git clone <repo-url>
cd Web_Scraping_AI
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

- macOS / Linux:

  ```bash
  source .venv/bin/activate
  ```

- Windows PowerShell:

  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- Windows CMD:

  ```cmd
  .\.venv\Scriptsctivate.bat
  ```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
uvicorn backend.main:app --reload
```

### View the application

Open the browser at:

```text
http://127.0.0.1:8000
```

---

## Edge Cases and Resilience

The current implementation covers basic validation and prototype behavior.

### Current protections

- requests without a URL are rejected
- scraping requests require either a query or selected fields
- ask requests require a non-empty question

### Additional cases to address

- invalid or malformed URLs
- network failures and HTTP errors
- unsupported content types
- pages without repeatable containers
- websites that require JavaScript rendering
- large pages and pagination

The code is structured so that these cases can be added without major refactoring.

---

## Future Enhancements

Potential future improvements include:

- replacing the sample scraper with actual extraction logic
- adding support for CSV and Excel export
- adding a real question-answering engine
- improving field discovery for dynamic page layouts
- adding loading indicators and richer frontend feedback
- adding retry logic and robust error handling
- introducing authentication and deployment configuration

These enhancements would move the prototype toward a production-ready architecture.

---

## Conversion Guidance

The README is formatted for easy conversion to DOCX or other document formats.

The document structure includes:

- clear headings and subheadings
- numbered and bulleted lists
- code examples in fenced blocks
- concise, descriptive sections

This format should convert cleanly with most Markdown-to-DOCX tools.

---

## Conclusion

`Web_Scraping_AI` is a prototype that demonstrates a modular scraping workflow.

It combines a backend API, a minimal frontend, and documentation that supports both development and review.

The current implementation is intended to provide a strong foundation for further improvements rather than to serve as a finished production system.
