# Day 04 Lab v2 Report - Research Agent

## Team

- Team: 4 zone 1
- Members:
  - Đào Xuân Bách - 2A202600640
  - Đỗ Thiện Lĩnh - 2A202600775
  - Dương Quang Minh - 2A202600686
- Provider/model: OpenRouter, target model `openai/gpt-4o-mini`

## Final Metrics

- Final version: `v3`
- Final artifact_version: `v3+p487b1fac43cd+t74517821ae3d`
- Final prompt_hash: `487b1fac43cd94d7822def23e32052fc0c462133f21f5a050b50c994042acd55`
- Final tools_hash: `74517821ae3d932ce70d3e89d16275d0cbb81181d2d06e41a7b5e56e1408ffd9`
- Best base run: `runs/v3_B_base_openrouter_20260602T154433057497.json`
- Base result: 20/20 passed, case_accuracy 1.00, routing 1.00, argument 1.00, multiturn 1.00, provider errors 0
- Final group run: `runs/v3_B_group_openrouter_20260602T155049032867.json`
- Group result: 10/10 passed, case_accuracy 1.00, routing 1.00, argument 1.00, multiturn 1.00, provider errors 0
- Note: the final artifact hash above matches the current prompt/tools and the final group run. The best base run was recorded earlier in v3 before the final group-specific refinements.

## Version Evidence

| Version | Suite | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---|---|---|---|
| v0 | base | baseline | Starter artifacts should expose routing and argument weaknesses before targeted changes. | N/A | 14/20 passed, accuracy 0.70, routing 0.75, argument 0.70 | `runs/v0_B_base_openrouter_20260602T150904214592.json` |
| v1 | base | `system_prompt.md` | Explicit scope, routing, clarification, confirmation, and multi-turn rules should reduce unsafe guessing and wrong tools. | v0 base accuracy 0.70 | 18/20 passed, accuracy 0.90, routing 0.95, argument 0.90 | `runs/v1_B_base_openrouter_20260602T152420568529.json` |
| v2 | base | `tools.yaml` | More precise tool descriptions and required args should remove remaining base failures. | v1 base accuracy 0.90 | 20/20 passed, accuracy 1.00, routing 1.00, argument 1.00 | `runs/v2_B_base_openrouter_20260602T154019970526.json` |
| v2 | group | `data/eval_group.json` | Group cases should test transfer to policy, papers, local analyzers, Telegram preview, and multi-turn corrections. | v2 base accuracy 1.00 | 9/10 passed, accuracy 0.90, multiturn 0.80 | `runs/v2_B_group_openrouter_20260602T154759214854.json` |
| v3 | base | `system_prompt.md`, `tools.yaml` | Group/local-tool refinements should preserve perfect base performance. | v2 base accuracy 1.00 | 20/20 passed, accuracy 1.00, routing 1.00, argument 1.00 | `runs/v3_B_base_openrouter_20260602T154433057497.json` |
| v3 | group | `system_prompt.md`, `tools.yaml`, `data/eval_group.json`, `tools/research_digest` | Stronger local-tool boundaries should fix the remaining group miss. | v2 group accuracy 0.90 | 10/10 passed, accuracy 1.00, routing 1.00, argument 1.00 | `runs/v3_B_group_openrouter_20260602T155049032867.json` |

## Failure Analysis

| Run | Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|---|
| v0 base | R08_out_of_scope | out_of_scope | `send` | Math answer was treated as a send action instead of no tool. | Added scope boundary: out-of-domain math/coding should answer without tools. |
| v0 base | R10_missing_handle | missing_info | `timeline(sama)` | Agent guessed a handle when the user did not provide an account. | Added clarify rule for missing account/handle. |
| v0 base | R11_missing_url | missing_info | `fetch(example.com/article)` | Agent guessed a URL for "this article". | Added clarify rule for missing URL. |
| v0 base | R12_confirm_before_send | wrong_boundary | `send` | Telegram send happened without explicit confirmation. | Added `clarify` yes/no confirmation boundary before `send`. |
| v0 base | R13_parallel_web_and_tweets | wrong_arg_value | `lookup`, `social_search` | Web/news args used `query=AI news` and missed `topic=news`. | Added argument conventions for news topic/timeframe and multi-tool requests. |
| v0 base | R14_out_of_scope_coding | out_of_scope | `send` | Coding answer was routed through send. | Added no-tool boundary for coding/meta/out-of-scope tasks. |
| v1 base | R10_missing_handle | missing_info | `social_search(query="")` | Missing account still caused an empty social search. | Updated prompt/tool descriptions: latest tweets without account/topic requires `clarify`. |
| v1 base | R12_confirm_before_send | wrong_boundary | `clarify(response_type=text)` | Agent asked for content instead of yes/no send confirmation. | Made `response_type=yes_no` explicit for send/post/publish. |
| v2 group | G09_multiturn_compare_topic_carryover | wrong_arg_value | `lookup`, `social_search` | Existing `web_items/social_items` comparison fetched fresh data instead of using `trend_compare`. | Added rules for existing items, `web_items`, `social_items`, and `trend_compare` with carried `topic/top_k`. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Final Result |
|---|---|---|---|
| G01_policy_data_privacy | Internal company policy questions should use local policy search. | `policy` | PASS |
| G02_papers_discovery | Paper discovery should use arXiv search with count and recency sorting. | `papers` | PASS |
| G03_paper_text_specific_id | Specific arXiv ID should read/extract paper text, not search papers. | `paper_text` | PASS |
| G04_research_digest_existing_items | Already collected evidence should be formatted into a digest, not fetched again. | `research_digest` | PASS |
| G05_telegram_preview_not_send | Telegram preview/draft should not call the side-effecting send tool. | `telegram_preview` | PASS |
| G06_multiturn_policy_area_correction | Later correction should switch policy area while keeping context. | `policy` | PASS |
| G07_multiturn_switch_social_to_web | Latest-turn switch should use web news, not social search. | `lookup` | PASS |
| G08_multiturn_source_quality_constraints | Source-quality constraints should carry across turns. | `source_quality` | PASS |
| G09_multiturn_compare_topic_carryover | Existing web/social items should be compared with carried topic/top_k. | `trend_compare` | PASS |
| G10_multiturn_confirm_before_send | Send action should ask yes/no confirmation before sending. | `clarify(response_type=yes_no)` | PASS |

## Tool And Bonus Evidence

| Item | Evidence | Status |
|---|---|---|
| Tool declarations | `artifacts/tools.yaml` declares 14 tools. | PASS |
| Tool registry | `tools/__init__.py` registers all 14 declared tools; no missing registry entries. | PASS |
| Team-added tools | `research_digest`, `source_quality`, `trend_compare`, `telegram_preview` each include `tool.py` and `TOOL.md`. | PASS |
| Bonus: more than 3 new tools | Four team-added tools are present and registered. | PASS |
| Bonus: UI | `ui_streamlit.py` exists and `streamlit` is listed in `requirements.txt`. | PASS |
| Bonus: guarded Telegram send | `send` refuses unconfirmed sends; prompt and tool declarations require confirmation first. | PASS |

## Live Chat Evidence

| Requirement | Evidence | Status |
|---|---|---|
| Live transcript JSON | `transcripts/v3_openrouter_streamlit_20260602T161451876447.transcript.json` exists with 1 Streamlit turn. | PASS |
| Streamlit transcript support | The recorded turn used OpenRouter v3 and called `lookup` for a live AI-news request. | PASS |

## Reflection

- Baseline v0 exposed the intended weak spots: guessing missing handles/URLs, unsafe send behavior, out-of-scope tool calls, and loose news arguments.
- v1 improved behavior mainly through system-level policy: clarification, no-tool boundaries, confirmation, and multi-turn correction rules.
- v2 made the tool declarations precise enough for perfect base eval accuracy.
- Group eval surfaced one remaining boundary issue: existing `web_items/social_items` should be analyzed locally rather than refetched.
- v3 fixed that local-tool boundary and reached 100% measured accuracy on both the recorded base and final group suites.

## Remaining Work

- If artifacts change again after this report, rerun base and group evals so hashes and metrics stay aligned.
