from __future__ import annotations

import re
from typing import Any


def _plain_markdown(markdown: str) -> str:
    text = markdown.strip()
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    return "\n".join(line.rstrip() for line in text.splitlines()).strip()


def telegram_preview(markdown: str = "", title: str = "", max_chars: int = 3500) -> dict[str, Any]:
    limit = max(200, int(max_chars or 3500))
    body = _plain_markdown(str(markdown or ""))
    header = str(title or "").strip()
    text = f"{header}\n\n{body}".strip() if header else body
    truncated = len(text) > limit
    if truncated:
        text = text[: max(0, limit - 15)].rstrip() + "\n...<truncated>"
    return {
        "tool": "telegram_preview",
        "text": text,
        "char_count": len(text),
        "max_chars": limit,
        "truncated": truncated,
        "status": "preview_only",
    }
