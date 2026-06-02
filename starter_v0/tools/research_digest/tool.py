from __future__ import annotations

from typing import Any

from tools._shared import domain


def _clean(text: Any, fallback: str = "") -> str:
    value = str(text or fallback).strip().replace("\n", " ")
    return " ".join(value.split())


def _source(item: dict[str, Any]) -> str:
    url = _clean(item.get("url"))
    source = _clean(item.get("source")) or domain(url) or "unknown source"
    return f"[{source}]({url})" if url else source


def research_digest(
    items: list[dict[str, Any]] | None = None,
    headline: str = "Research brief",
    audience: str = "general",
    max_items: int = 5,
) -> dict[str, Any]:
    items = list(items or [])
    limit = max(1, int(max_items or 5))
    selected = items[:limit]

    caveats: list[str] = []
    if not selected:
        caveats.append("No evidence items were provided.")
    if len(items) > len(selected):
        caveats.append(f"Trimmed {len(items) - len(selected)} extra item(s).")

    sources = {_clean(item.get("source")) or domain(_clean(item.get("url"))) for item in selected}
    sources.discard("")
    if len(sources) < 2 and len(selected) > 1:
        caveats.append("Source diversity is limited.")

    title = _clean(headline, "Research brief")
    parts = [f"# {title}", "", f"Audience: {audience or 'general'}", "", "## Key findings"]
    for index, item in enumerate(selected, start=1):
        summary = _clean(item.get("summary")) or _clean(item.get("title"), "Untitled item")
        if len(summary) > 260:
            summary = summary[:257] + "..."
        parts.append(f"{index}. {summary} - {_source(item)}")

    parts += ["", "## Caveats"]
    parts.extend(f"- {caveat}" for caveat in (caveats or ["No major caveats detected from supplied metadata."]))

    return {
        "tool": "research_digest",
        "headline": title,
        "audience": audience or "general",
        "markdown": "\n".join(parts).strip(),
        "item_count": len(selected),
        "source_count": len(sources),
        "caveats": caveats,
    }
