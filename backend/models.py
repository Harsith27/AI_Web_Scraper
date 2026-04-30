from pydantic import BaseModel
from typing import List, Optional


class QueryPlan(BaseModel):
	entity: str
	fields: list[str]


class SelectorPlan(BaseModel):
	container: str
	fields: dict[str, str]


class DiscoverFieldsRequest(BaseModel):
	url: str


class DiscoverFieldsResponse(BaseModel):
	success: bool
	message: str
	url: str
	fields: List[str]
	sample_data: dict[str, str]
	container_selector: Optional[str] = None


class ScrapeRequest(BaseModel):
	url: str
	query: str
	selected_fields: list[str] = []
	format: str = 'json'


class ScrapeResponse(BaseModel):
	success: bool
	message: str
	data: list[dict[str, str]]
	fields: list[str]
	csv: str | None = None


class AskRequest(BaseModel):
	url: str
	question: str
	scope: str = 'data'
	data: list[dict[str, str]] = []


class AskResponse(BaseModel):
	success: bool
	answer: str
	scope: str
	intent: Optional[str] = None
	field: Optional[str] = None
	operation: Optional[str] = None
	source: Optional[str] = None