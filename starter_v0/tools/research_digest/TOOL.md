---
name: research_digest
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, headline, audience, max_items]
outputs: [markdown, item_count, source_count, caveats]
side_effect: false
---
# research_digest

Creates a concise cited research brief from already collected items. It does not
fetch, verify, or create new evidence.
