---
name: source_quality
track: bonus
kind: local_formatter
requires_env: []
inputs: [items, min_sources, require_urls]
outputs: [score, passed, warnings, source_count]
side_effect: false
---
# source_quality

Checks source diversity, URL presence, and citation readiness for already
collected items. It does not fetch or verify facts.
