# Summary Project: Day 04 Lab v2 - Research Agent Tool Eval

## 1. Tong quan project

Day 04 Lab v2 la mot bai lab ve **prompt engineering** va **tool calling**. Nhiem vu la build mot research agent nho co the:

- Nhan request tu user.
- Tu chon tool phu hop.
- Truyen dung arguments cho tool.
- Chay tool that qua API hoac local tool.
- Luu full JSON log.
- Doc log de toi uu `system_prompt.md` va `tools.yaml` qua nhieu version.

Trong lab nay, muc tieu chinh khong phai la lam chatbot tra loi hay, ma la hoc vong lap **evidence-driven optimization**:

1. Chay baseline bang provider that.
2. Doc run JSON de tim loi sai tool, sai args, thieu hoi lai, hoac goi tool thua.
3. Sua `artifacts/system_prompt.md` hoac `artifacts/tools.yaml`.
4. Chay lai eval va so sanh metric.
5. Ghi lai versioning.
6. Tu viet them eval case.
7. Viet report dua tren log that.

## 2. Cau truc thu muc quan trong

```text
starter_v0/
  agent.py                    # one-shot model -> tool calls -> tool execution
  chat.py                     # interactive chat, multi-round tools, transcript JSON
  run_eval.py                 # chay eval, ghi runs/*.json
  versioning.py               # tao prompt_hash va tools_hash

  artifacts/
    system_prompt.md          # file prompt can sua
    tools.yaml                # khai bao tool can sua
    version_log.csv           # ghi lai cac version v0, v1, v2, v3
    REPORT.md                 # report cuoi

  data/
    eval_base.json            # eval co dinh, khong sua noi dung case
    eval_group.json           # team tu them eval case
    eval_research_extension.json

  tools/
    README.md
    __init__.py               # registry tool
    clarify/
    timeline/
    social_search/
    lookup/
    fetch/
    format/
    send/
    policy/
    papers/
    paper_text/

  company_policy/             # local markdown KB cho policy tool
  providers/                  # OpenRouter/OpenAI/Anthropic/Gemini adapters
  scripts/
  samples/
```

## 3. Cac file can chu y

- `starter_v0/artifacts/system_prompt.md`: prompt he thong. Ban starter hien dang co tinh sai, vi du bao agent doan bua, khong hoi lai, chi goi mot tool, va tu gui Telegram khong can xac nhan.
- `starter_v0/artifacts/tools.yaml`: khai bao cac tool cho model. Ban starter con mo ho, can sua description va argument convention de agent route dung.
- `starter_v0/data/eval_base.json`: bo eval co dinh. Khong sua noi dung case, tru khi doi ten tool thi phai dong bo.
- `starter_v0/data/eval_group.json`: noi team tu them eval case. Hien dang rong.
- `starter_v0/run_eval.py`: script chay eval va tao log trong `runs/*.json`.
- `starter_v0/chat.py`: script chat live va tao transcript trong `transcripts/*.transcript.json`.
- `starter_v0/artifacts/version_log.csv`: noi ghi lai ly do sua, hypothesis, metric truoc/sau, run file.
- `starter_v0/artifacts/REPORT.md`: template bao cao cuoi.

## 4. Cac tool hien co

### Core tools

- `clarify`: gui mot cau hoi cho user khi thieu thong tin.
- `timeline`: lay bai dang gan day cua mot account, vi du tweet moi nhat cua Sam Altman.
- `social_search`: tim bai dang tren mang xa hoi theo tu khoa/chu de.
- `lookup`: tra cuu thong tin tren web, co ho tro `topic=general/news` va `timeframe=day/week/month/year`.
- `fetch`: doc noi dung tu mot URL cu the.
- `format`: trinh bay cac item da co thanh markdown digest.

### Bonus tools

- `send`: gui text len Telegram channel. Day la action tool, can confirmation truoc khi gui.
- `policy`: tim trong company policy markdown noi bo.
- `papers`: tim paper tren arXiv.
- `paper_text`: tai PDF arXiv va trich text cuc bo.

## 5. Setup moi truong

Chay tu thu muc `starter_v0/`:

```bash
cd starter_v0
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Dien API keys vao `.env`.

Toi thieu nen co:

```bash
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
```

Chay preflight:

```bash
python scripts/preflight_provider.py --provider openrouter
```

## 6. Task bat buoc can lam

### Task 1: Chay baseline `v0`

```bash
python run_eval.py \
  --provider openrouter \
  --version v0 \
  --suite base \
  --eval-cases data/eval_base.json
```

Sau khi chay, doc file trong `runs/*.json`, chu y:

- `summary.case_accuracy`
- `summary.tool_routing_accuracy`
- `summary.argument_accuracy`
- `summary.multiturn_accuracy`
- `results[*].result.failures`
- `results[*].result.observed_mismatch`
- `actual_tool_calls`
- `actual_tool_results`

### Task 2: Toi uu prompt/tool declaration qua 3 version

Chi sua hai file:

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`

Chay it nhat 3 version sau baseline:

```bash
python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v2 --suite base --eval-cases data/eval_base.json
python run_eval.py --provider openrouter --version v3 --suite base --eval-cases data/eval_base.json
```

Sau moi lan chay, dien vao:

```text
artifacts/version_log.csv
```

Can ghi:

- version
- author
- changed_artifact
- artifact_version
- prompt_hash
- tools_hash
- reason
- hypothesis
- metric_before
- metric_after
- run_file

### Task 3: Sua cac hanh vi agent dang bi eval kiem tra

Agent can hoc cac routing/behavior sau:

- Tweet cua mot nguoi cu the -> dung `timeline`.
- Tweet theo chu de -> dung `social_search`.
- Tin tuc web/hom nay/tuan nay -> dung `lookup` voi `topic=news`, `timeframe` dung.
- Co URL cu the -> dung `fetch`, khong search web.
- Thieu handle/account -> dung `clarify`, khong doan bua.
- Thieu URL khi user noi "bai nay" -> dung `clarify`, xin URL.
- Request gui/dang Telegram -> hoi xac nhan truoc bang `clarify` voi `response_type=yes_no`.
- Cau hoi ngoai pham vi research, vi du math/coding -> khong goi tool.
- Cau hoi meta ve agent -> tra loi truc tiep, khong goi tool.
- Request can nhieu nguon -> co the goi nhieu tool, vi du `lookup` va `social_search`.
- Multi-turn -> carry context dung, sua context khi user correction.

### Task 4: Them it nhat 1 tool moi

Tao folder moi:

```text
starter_v0/tools/<tool_name>/
  TOOL.md
  tool.py
```

Sau do dang ky tool trong:

- `starter_v0/tools/__init__.py`
- `starter_v0/artifacts/tools.yaml`

Neu doi ten tool co san, phai dong bo o ca:

- `artifacts/tools.yaml`
- `tools/__init__.py`
- `data/eval_base.json`
- `data/eval_research_extension.json`

Khuyen nghi khong doi ten tool co san neu khong can thiet.

### Task 5: Viet them 10 eval case cho team

Them vao:

```text
starter_v0/data/eval_group.json
```

Yeu cau:

- It nhat 10 case.
- 5 single-turn.
- 5 multi-turn.
- Moi case can co:
  - `id`
  - `phase`: `"B"`
  - `query` hoac `turns`
  - `failure_type`
  - `expect`
  - `metadata.what_it_tests`

Allowed `failure_type`:

- `wrong_tool`
- `wrong_arg_value`
- `wrong_boundary`
- `unnecessary_tool`
- `out_of_scope`
- `missing_info`

Chay group eval:

```bash
python run_eval.py \
  --provider openrouter \
  --version v3 \
  --suite group \
  --eval-cases data/eval_group.json
```

### Task 6: Chay live chat

```bash
python chat.py --provider openrouter --version v3
```

Can thu it nhat 3 tinh huong:

- Mot request research binh thuong.
- Mot request thieu thong tin, sau do user bo sung.
- Mot request gui/dang Telegram de xem agent co hoi confirmation truoc khong.

Transcript se duoc luu trong:

```text
transcripts/*.transcript.json
```

### Task 7: Viet report cuoi

Dien vao:

```text
starter_v0/artifacts/REPORT.md
```

Report can dua tren log that, gom:

- Team info.
- Provider/model.
- Final metrics.
- Best base run file.
- Group eval run file.
- Chat transcript file.
- Version evidence tu `version_log.csv`.
- Failure analysis tu `runs/*.json`.
- Team eval cases.
- Live chat evidence.
- Bonus evidence neu co.
- Reflection.

## 7. Bonus

Bonus co the lam:

- `send` Telegram: dam bao co confirmation truoc khi gui.
- Extra tools: `policy`, `papers`, `paper_text`.
- UI: Streamlit hoac Vercel.

Diem thuong neu lam ca hai:

- Dung duoc UI.
- Tu viet them hon 3 tool moi ngoai cac tool co san, moi tool co `TOOL.md`, dang ky trong `tools/__init__.py` va `tools.yaml`.

## 8. Artifact can nop

Can chuan bi cac artifact sau:

- `runs/*.json`
- `transcripts/*.transcript.json`
- `starter_v0/artifacts/version_log.csv`
- `starter_v0/artifacts/REPORT.md`
- Tool moi trong `starter_v0/tools/<tool_name>/`
- `TOOL.md` cua tool moi
- `starter_v0/data/eval_group.json`
- `starter_v0/artifacts/system_prompt.md`
- `starter_v0/artifacts/tools.yaml`

## 9. Hien trang repo hien tai

Theo trang thai hien tai:

- `starter_v0/data/eval_group.json` dang rong.
- `starter_v0/artifacts/system_prompt.md` van la prompt starter co tinh sai.
- `starter_v0/artifacts/tools.yaml` van la declaration starter con mo ho.
- Chua thay folder `runs/` va `transcripts/` that trong `starter_v0/`, chi co sample transcript trong `samples/`.
- Can chay baseline va toi uu truoc khi nop.

## 10. Checklist ngan gon

- [ ] Setup `.venv` va cai dependencies.
- [ ] Dien `.env`.
- [ ] Chay preflight provider.
- [ ] Chay baseline `v0`.
- [ ] Doc run JSON va phan tich loi.
- [ ] Sua `system_prompt.md` hoac `tools.yaml` cho `v1`.
- [ ] Chay eval `v1`, ghi `version_log.csv`.
- [ ] Sua tiep cho `v2`.
- [ ] Chay eval `v2`, ghi `version_log.csv`.
- [ ] Sua tiep cho `v3`.
- [ ] Chay eval `v3`, ghi `version_log.csv`.
- [ ] Them it nhat 1 tool moi.
- [ ] Them 10 eval case vao `eval_group.json`.
- [ ] Chay group eval.
- [ ] Chay live chat va lay transcript.
- [ ] Dien `REPORT.md`.
- [ ] Kiem tra lai artifact can nop.
