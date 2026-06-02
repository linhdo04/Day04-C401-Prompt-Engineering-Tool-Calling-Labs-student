---
name: papers
track: bonus
kind: live_api
provider: arXiv API
requires_env: [ARXIV_USER_AGENT]
inputs: [query, max_results, sort_by, year, published_after, published_before]
outputs: [items, total_results]
side_effect: false
---
# papers

Searches arXiv via the official Atom API. Rate-limited (waits ~3s between
in-process requests).

Use `year` for requests like "this year" / "năm nay". Use
`published_after` and `published_before` in `YYYY-MM-DD` format for explicit
date windows.
