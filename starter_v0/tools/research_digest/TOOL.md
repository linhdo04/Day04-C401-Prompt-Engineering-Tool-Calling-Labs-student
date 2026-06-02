---
name: research_digest
track: team
kind: local_formatter
requires_env: []
inputs: [items, headline, audience, max_items]
outputs: [markdown, item_count, cited_count]
side_effect: false
---
# research_digest

Creates a concise cited research brief from already collected evidence items.

This tool does not fetch live data or verify facts. Use `lookup`, `social_search`,
or `fetch` first when fresh evidence is required.
