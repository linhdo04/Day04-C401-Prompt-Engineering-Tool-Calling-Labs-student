from __future__ import annotations

from datetime import date


def append_runtime_context(system_prompt: str) -> str:
    today = date.today()
    current_year = today.year
    context = (
        "\n\nRuntime context:\n"
        f"- Current date: {today.isoformat()}.\n"
        f"- Interpret relative dates from this date. For example, 'năm nay'/'this year' means {current_year}.\n"
    )
    return system_prompt.rstrip() + context
