"""In-memory research cache for serverless (state does not persist across all instances)."""

from __future__ import annotations

_cache: dict[str, dict] = {}


def cache_research(research_id: str, data: dict) -> None:
    _cache[research_id] = data


def get_cached_research(research_id: str) -> dict | None:
    return _cache.get(research_id)
