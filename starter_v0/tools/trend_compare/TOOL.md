---
name: trend_compare
track: bonus
kind: local_formatter
requires_env: []
inputs: [web_items, social_items, topic, top_k]
outputs: [topic, shared_terms, web_only_terms, social_only_terms, summary]
side_effect: false
---
# trend_compare

Compares already collected web/news and social items for one topic. It does not
fetch live data.
