---
name: telegram_preview
track: bonus
kind: local_formatter
requires_env: []
inputs: [markdown, title, max_chars]
outputs: [text, char_count, truncated]
side_effect: false
---
# telegram_preview

Builds a Telegram-ready text preview from markdown. It never sends messages.
