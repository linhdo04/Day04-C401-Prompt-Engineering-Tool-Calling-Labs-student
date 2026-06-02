from __future__ import annotations

from typing import Any

from tools._shared import terms


def _item_terms(items: list[dict[str, Any]]) -> set[str]:
    text = " ".join(
        " ".join(str(item.get(key) or "") for key in ("title", "summary", "source"))
        for item in items
    )
    return terms(text)


def trend_compare(
    web_items: list[dict[str, Any]] | None = None,
    social_items: list[dict[str, Any]] | None = None,
    topic: str = "",
    top_k: int = 5,
) -> dict[str, Any]:
    web_items = list(web_items or [])
    social_items = list(social_items or [])
    limit = max(1, int(top_k or 5))
    web_terms = _item_terms(web_items)
    social_terms = _item_terms(social_items)

    shared = sorted(web_terms & social_terms)[:limit]
    web_only = sorted(web_terms - social_terms)[:limit]
    social_only = sorted(social_terms - web_terms)[:limit]

    label = topic or "topic"
    summary = (
        f"Compared {len(web_items)} web item(s) and {len(social_items)} social item(s) for {label}. "
        f"Shared themes: {', '.join(shared) if shared else 'none detected'}."
    )
    return {
        "tool": "trend_compare",
        "topic": label,
        "web_count": len(web_items),
        "social_count": len(social_items),
        "shared_terms": shared,
        "web_only_terms": web_only,
        "social_only_terms": social_only,
        "summary": summary,
    }
