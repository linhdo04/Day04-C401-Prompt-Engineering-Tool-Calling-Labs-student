from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import run_model_tool_loop
from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

PROVIDER_LABELS = {
    "openrouter": "OpenRouter",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "gemini": "Gemini",
}


def inject_styles() -> None:
    st.markdown(
        """
<style>
:root {
  --lab-bg: #f6f7fb;
  --lab-surface: #ffffff;
  --lab-ink: #172033;
  --lab-muted: #667085;
  --lab-border: #e3e8ef;
  --lab-accent: #2563eb;
}

.stApp {
  background: var(--lab-bg);
  color: var(--lab-ink);
}

[data-testid="stHeader"] {
  background: rgba(246, 247, 251, 0.82);
  backdrop-filter: blur(10px);
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
  display: none;
}

.block-container {
  max-width: 1280px;
  padding-top: 2rem;
  padding-bottom: 2.5rem;
}

h1 {
  font-size: clamp(2rem, 3vw, 2.7rem);
  letter-spacing: 0;
  margin-bottom: 0.15rem;
}

h2, h3 {
  letter-spacing: 0;
}

[data-testid="stSidebar"] {
  background: var(--lab-surface);
  border-right: 1px solid var(--lab-border);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
.stCaptionContainer {
  color: var(--lab-muted);
}

div[data-testid="stChatMessage"] {
  background: var(--lab-surface);
  border: 1px solid var(--lab-border);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

[data-testid="stChatInput"] > div {
  background: var(--lab-surface);
  border: 1px solid var(--lab-border);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--lab-accent);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] [contenteditable="true"] {
  background: transparent !important;
  box-shadow: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
  color: var(--lab-muted) !important;
}

[data-testid="stChatInput"] textarea::selection,
[data-testid="stChatInput"] [contenteditable="true"]::selection {
  background: transparent;
  color: inherit;
}

[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {
  background: transparent !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
div[data-baseweb="select"] > div {
  border-radius: 8px;
}

.stButton > button,
.stDownloadButton > button {
  border-radius: 8px;
  font-weight: 600;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.35rem;
  border-bottom: 1px solid var(--lab-border);
}

.stTabs [data-baseweb="tab"] {
  border-radius: 8px 8px 0 0;
  padding: 0.55rem 0.8rem;
}

.stTabs [aria-selected="true"] {
  color: var(--lab-accent);
}

.stTabs [data-baseweb="tab-highlight"] {
  background-color: var(--lab-accent);
}

div[data-testid="stExpander"] {
  border-color: var(--lab-border);
  border-radius: 8px;
}

div[data-testid="stAlert"] {
  border-radius: 8px;
}

hr {
  margin: 1.25rem 0;
}
</style>
""",
        unsafe_allow_html=True,
    )


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def trim_history(history: list[dict[str, str]], window: int) -> list[dict[str, str]]:
    return history[-window * 2:] if window > 0 else []


def transcript_path(version: str, provider: str) -> Path:
    if "transcript_path" not in st.session_state:
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version), safe_slug(provider), "streamlit", timestamp])
        st.session_state.transcript_id = transcript_id
        st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    return Path(st.session_state.transcript_path)


def write_transcript(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = now_iso()
    path.write_text(json_text(payload), encoding="utf-8")


def init_state() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("last_preview", "")
    st.session_state.setdefault("last_send_status", None)


def build_transcript(version: str, provider_name: str, model: str | None, prompt_path: Path, tools_path: Path) -> dict[str, Any]:
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    return {
        "transcript_id": st.session_state.transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": st.session_state.get("history_window", 5),
        "max_tool_rounds": st.session_state.get("max_tool_rounds", 4),
        "created_at": st.session_state.get("created_at", now_iso()),
        "updated_at": now_iso(),
        "ui": "streamlit",
        "turns": st.session_state.turns,
    }


def render_tool_events(events: list[dict[str, Any]]) -> None:
    if not events:
        st.caption("No tool calls in the latest turn.")
        return
    for event in events:
        name = event.get("tool", "tool")
        with st.expander(f"{name} call", expanded=False):
            st.json(event)


def extract_latest_preview(events: list[dict[str, Any]]) -> str:
    for event in reversed(events):
        result = event.get("result", {})
        if event.get("tool") == "telegram_preview" and isinstance(result, dict):
            text = result.get("text")
            if text:
                return str(text)
        if event.get("tool") == "research_digest" and isinstance(result, dict):
            markdown = result.get("markdown")
            if markdown:
                return str(markdown)
        if event.get("tool") == "format" and isinstance(result, dict):
            markdown = result.get("markdown")
            if markdown:
                return str(markdown)
    return ""


st.set_page_config(page_title="Research Agent Lab", page_icon=None, layout="wide")
init_state()
inject_styles()

st.title("Research Agent Lab")
st.caption("Run tool-calling experiments, inspect the latest trace, and save transcript evidence.")

with st.sidebar:
    st.header("Setup")
    provider_name = st.selectbox(
        "Provider",
        list(PROVIDER_LABELS.keys()),
        index=0,
        format_func=lambda value: PROVIDER_LABELS[value],
    )
    version = st.text_input("Version label", value="v3")

    with st.expander("Advanced", expanded=False):
        model_text = st.text_input("Model override", value="", placeholder="Use provider default")
        prompt_path = st.text_input("System prompt", value=str(ARTIFACTS_DIR / "system_prompt.md"))
        tools_path = st.text_input("Tools YAML", value=str(ARTIFACTS_DIR / "tools.yaml"))
        st.session_state.history_window = st.number_input("History turns", min_value=0, max_value=20, value=5)
        st.session_state.max_tool_rounds = st.number_input("Tool rounds", min_value=1, max_value=8, value=4)

    prompt_exists = Path(prompt_path).exists()
    tools_exists = Path(tools_path).exists()
    if prompt_exists and tools_exists:
        st.success("Artifacts ready.")
    else:
        st.warning("Check artifact paths in Advanced.")

    if st.button("Reset Chat", use_container_width=True):
        for key in ("history", "turns", "last_preview", "last_send_status", "transcript_path", "transcript_id", "created_at"):
            st.session_state.pop(key, None)
        init_state()
        st.rerun()

prompt_file = Path(prompt_path)
tools_file = Path(tools_path)
model = model_text.strip() or None

left, right = st.columns([0.62, 0.38], gap="large")

with left:
    st.subheader("Conversation")
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input("Ask for research, formatting, preview, or a guarded Telegram send")
    if user_text:
        st.session_state.setdefault("created_at", now_iso())
        path = transcript_path(version, provider_name)
        try:
            with st.spinner("Running agent and tools..."):
                system_prompt = prompt_file.read_text(encoding="utf-8")
                tool_declarations = load_tool_declarations(tools_file)
                openai_tools = to_openai_tools(tool_declarations)
                provider = make_provider(provider_name)
                messages = [
                    {"role": "system", "content": system_prompt},
                    *trim_history(st.session_state.history, int(st.session_state.history_window)),
                    {"role": "user", "content": user_text},
                ]
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=int(st.session_state.max_tool_rounds),
                )
            assistant_text = result.get("assistant_text", "")
            turn_record = {
                "turn_index": len(st.session_state.turns) + 1,
                "started_at": now_iso(),
                "ended_at": now_iso(),
                "user": user_text,
                **result,
            }
            st.session_state.history.append({"role": "user", "content": user_text})
            st.session_state.history.append({"role": "assistant", "content": assistant_text})
            st.session_state.turns.append(turn_record)
            preview = extract_latest_preview(result.get("tool_events", []))
            if preview:
                st.session_state.last_preview = preview
            write_transcript(path, build_transcript(version, provider_name, model, prompt_file, tools_file))
            st.rerun()
        except Exception as exc:
            st.error(f"{type(exc).__name__}: {exc}")

with right:
    trace_tab, telegram_tab, transcript_tab = st.tabs(["Trace", "Telegram", "Transcript"])

    with trace_tab:
        st.subheader("Latest trace")
        latest_events: list[dict[str, Any]] = []
        if st.session_state.turns:
            latest_events = st.session_state.turns[-1].get("tool_events", [])
        render_tool_events(latest_events)

    with telegram_tab:
        st.subheader("Telegram draft")
        preview_text = st.text_area(
            "Preview text",
            value=st.session_state.last_preview,
            height=260,
            placeholder="Use telegram_preview, research_digest, or format to populate this area.",
        )
        if preview_text != st.session_state.last_preview:
            st.session_state.last_preview = preview_text

        confirm = st.checkbox("I confirm this exact text should be sent to Telegram")
        send_clicked = st.button(
            "Send To Telegram",
            type="primary",
            disabled=not (confirm and preview_text.strip()),
            use_container_width=True,
        )
        if send_clicked:
            result = TOOL_FUNCTIONS["send"](text=preview_text, confirmed=True)
            st.session_state.last_send_status = result
            send_event = {
                "turn_index": len(st.session_state.turns) + 1,
                "started_at": now_iso(),
                "ended_at": now_iso(),
                "user": "[ui_send_to_telegram]",
                "status": "ui_action",
                "assistant_text": "Telegram send requested from UI after explicit confirmation.",
                "rounds": [],
                "tool_events": [{"tool": "send", "args": {"confirmed": True}, "result": result}],
            }
            st.session_state.turns.append(send_event)
            path = transcript_path(version, provider_name)
            write_transcript(path, build_transcript(version, provider_name, model, prompt_file, tools_file))
            st.rerun()

        if st.session_state.last_send_status:
            st.json(st.session_state.last_send_status)

    with transcript_tab:
        st.subheader("Transcript file")
        if "transcript_path" in st.session_state:
            st.code(str(st.session_state.transcript_path))
            st.download_button(
                "Download Transcript JSON",
                data=Path(st.session_state.transcript_path).read_text(encoding="utf-8") if Path(st.session_state.transcript_path).exists() else "{}",
                file_name=Path(st.session_state.transcript_path).name,
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.caption("A transcript file will be created after the first turn.")
