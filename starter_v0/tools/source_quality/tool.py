from __future__ import annotations

from typing import Any

from tools._shared import domain


def _text(value: Any) -> str:
    return str(value or "").strip()


def source_quality(
    items: list[dict[str, Any]] | None = None,
    min_sources: int = 2,
    require_urls: bool = True,
) -> dict[str, Any]:
    items = list(items or [])
    minimum = max(1, int(min_sources or 2))
    sources: set[str] = set()
    warnings: list[str] = []
    scored_items: list[dict[str, Any]] = []

    for index, item in enumerate(items, start=1):
        url = _text(item.get("url"))
        source = _text(item.get("source")) or domain(url) or "unknown"
        sources.add(source)
        item_warnings: list[str] = []
        if require_urls and not url:
            item_warnings.append("missing_url")
        if not _text(item.get("summary")) and not _text(item.get("title")):
            item_warnings.append("missing_description")
        if item_warnings:
            warnings.append(f"item_{index}: {', '.join(item_warnings)}")
        scored_items.append({"index": index, "source": source, "url": url, "warnings": item_warnings})

    if len(sources) < minimum:
        warnings.append(f"source_diversity_below_minimum: {len(sources)} < {minimum}")
    if not items:
        warnings.append("no_items")

    penalty = min(100, len(warnings) * 20)
    score = max(0, 100 - penalty)
    return {
        "tool": "source_quality",
        "score": score,
        "passed": not warnings,
        "source_count": len(sources),
        "min_sources": minimum,
        "require_urls": bool(require_urls),
        "warnings": warnings,
        "items": scored_items,
    }
