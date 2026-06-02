# Day 04 Lab v2 Report — Research Agent

## Team

- Team: bachbach
- Members: bachbach
- Provider/model: OpenRouter target `openai/gpt-4o-mini`; Gemini fallback `gemini-3.5-flash`

## Final Metrics

- Final version: v3
- Final artifact_version: `v3+pf51dc1465fce+t333c9c9a7ed7`
- Best base run file: `runs/v3_B_base_gemini_20260602T142804115713.json`
- Base case accuracy: 1.0 on measured cases; 3 measured, 17 provider errors
- Base tool routing accuracy: 1.0 on measured cases
- Base argument accuracy: 1.0 on measured cases
- Group eval run file: `runs/v3_B_group_gemini_20260602T142759056407.json`
- Group eval accuracy: 1.0 on measured cases; 3 measured, 7 provider errors
- OpenRouter base run file: `runs/v3_B_base_openrouter_20260602T143012008850.json` recorded provider errors because `OPENROUTER_API_KEY` is missing
- OpenRouter group run file: `runs/v3_B_group_openrouter_20260602T142721094642.json` recorded provider errors because `OPENROUTER_API_KEY` is missing
- Chat transcript file: created by `ui_streamlit.py` after the first UI turn; no completed live transcript exists yet

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline attempt | OpenRouter baseline should establish starter behavior. Blocked because `.env` lacks `OPENROUTER_API_KEY`. | N/A | N/A | N/A |
| v1 | `system_prompt.md` | Explicit routing, clarification, send confirmation, and multi-turn correction rules should improve tool choice and safety. | N/A | Gemini base measured cases 3/3 passed | `runs/v3_B_base_gemini_20260602T142804115713.json` |
| v2 | `tools.yaml` | Clearer descriptions and argument conventions should reduce wrong-tool and wrong-arg failures. | N/A | 14 declared tools all implemented; group measured cases 3/3 passed | `runs/v3_B_group_gemini_20260602T142759056407.json` |
| v3 | new tools, group eval, UI | Bonus workflow tools and guarded UI should satisfy bonus scope without automated send side effects. | N/A | Direct tool tests and compile checks passed | local validation |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| OpenRouter all attempted cases | provider_error | none | `OPENROUTER_API_KEY` is absent from `.env`, so provider completion cannot start. | Add `OPENROUTER_API_KEY` and rerun v0-v3 evals. |
| Gemini unmeasured base/group cases | provider_error | none | Gemini free-tier quota/high-demand errors: 429 `RESOURCE_EXHAUSTED` and 503 `UNAVAILABLE`. | Rerun after quota reset or use OpenRouter/OpenAI with a valid key. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01 | Research digest from already collected evidence | `research_digest` | PASS on Gemini |
| G02 | Source-diversity/citation readiness | `source_quality` | Provider error on Gemini |
| G03 | Web/social trend comparison | `trend_compare` | Provider error on Gemini |
| G04 | Telegram preview without sending | `telegram_preview` | PASS on Gemini |
| G05 | Send boundary requires confirmation | `clarify` yes/no | Provider error on Gemini |
| G06 | Missing digest items in multi-turn context | `clarify` text | PASS on Gemini |
| G07 | Correction from send to preview | `telegram_preview` | Provider error on Gemini |
| G08 | Carry topic/top_k into comparison | `trend_compare` | Provider error on Gemini |
| G09 | Carry source-quality constraints | `source_quality` | Provider error on Gemini |
| G10 | Confirmation before send | `clarify` yes/no | Provider error on Gemini |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| UI pending | Run `python3 -m streamlit run ui_streamlit.py` and submit a first turn | Logged in `transcripts/*.transcript.json` | v3 artifact hashes | Not run yet because OpenRouter key is missing and Gemini quota was exhausted during eval. |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Four new tools | `tools/research_digest`, `tools/source_quality`, `tools/trend_compare`, `tools/telegram_preview` | Direct local tool tests passed; all tools registered in `tools.yaml` and `tools/__init__.py`. | Tools are local analyzers/formatters only and do not fetch new evidence. |
| send (Telegram) | `tools/send/tool.py`, `ui_streamlit.py` | Existing `send` refuses unconfirmed sends; UI requires a checked confirmation before calling `send(..., confirmed=True)`. | Automated eval cases expect `clarify` or `telegram_preview`, not `send`. |
| UI | `ui_streamlit.py` | Streamlit operator surface supports provider/model/version selection, chat, tool traces, Telegram preview/send, and transcript JSON. | Needs a working provider key/quota for live chat. |

## Reflection

- `system_prompt.md` fixes the agent policy: when to clarify, when not to use tools, how to handle send confirmation, and how to interpret multi-turn corrections.
- `tools.yaml` fixes model-facing affordances: exact routing descriptions, handle mappings, timeframe conventions, and local-tool boundaries.
- Provider failures need manual review because they are not routing failures.
- Next improvement: add `OPENROUTER_API_KEY`, rerun true v0-v3 OpenRouter evals, then update metrics with full measured runs.
