from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    limit: int = Field(default=20, ge=1, le=50)


class SearchResponse(BaseModel):
    query: str
    papers: list[dict]
    total: int
    sources: dict[str, str]


class ResearchCreateRequest(BaseModel):
    question: str = Field(..., min_length=10, max_length=1000)


class ResearchCreateResponse(BaseModel):
    research_id: str
    status: str
    result: dict | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str = "1.0.0"
