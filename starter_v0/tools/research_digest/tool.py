from __future__ import annotations

from typing import Any

from tools._shared import domain


def _clean(value: Any) -> str:
    return str(value or "").strip().replace("\n", " ")


def _citation(item: dict[str, Any]) -> str:
    url = _clean(item.get("url"))
    source = _clean(item.get("source")) or domain(url) or "source"
    return f"[{source}]({url})" if url else source


def build_research_digest(
    items: list[dict[str, Any]] | None = None,
    headline: str = "Research brief",
    audience: str = "general",
    max_items: int = 5,
) -> dict[str, Any]:
    items = items or []
    try:
        limit = max(1, int(max_items or 5))
    except (TypeError, ValueError):
        limit = 5
    selected = items[:limit]

    lines = [f"# {_clean(headline) or 'Research brief'}", "", f"Audience: {_clean(audience) or 'general'}", ""]
    cited_count = 0

    if not selected:
        lines.append("No evidence items were provided.")
    else:
        lines.append("## Key points")
        for item in selected:
            title = _clean(item.get("title"))
            summary = _clean(item.get("summary"))
            text = summary or title or "Untitled item"
            if len(text) > 240:
                text = text[:237] + "..."
            citation = _citation(item)
            if item.get("url") or item.get("source"):
                cited_count += 1
            lines.append(f"- {text} - {citation}")

    return {
        "tool": "research_digest",
        "markdown": "\n".join(lines),
        "item_count": len(selected),
        "cited_count": cited_count,
    }
