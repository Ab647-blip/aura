from __future__ import annotations

import html

import streamlit as st

from aura.core.agent import respond
from aura.core.config import CONTEXT_BUDGET
from aura.core.context_manager import compress_history
from aura.core.tokens import count_tokens, needs_trimming

st.set_page_config(page_title="Aura", layout="centered")

STYLE = """
<style>
:root {
  --paper: #F3EFE7;
  --card:  #FBF9F4;
  --ink:   #201D19;
  --muted: #6F685C;
  --line:  #E2DBCD;
  --notes: #8A6A34;
  --web:   #3D6152;
}

.stApp { background-color: var(--paper); }
header[data-testid="stHeader"] { display: none; }
#MainMenu, footer { visibility: hidden; }

.block-container { max-width: 700px; padding-top: 2.8rem; padding-bottom: 7rem; }

.block-container p, .block-container li {
  color: var(--ink);
  font-size: 1.01rem;
  line-height: 1.72;
}

.masthead {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.6rem;
  margin-bottom: 0.4rem;
}
.masthead .name {
  font-family: "Iowan Old Style", Palatino, Georgia, serif;
  font-size: 1.55rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  color: var(--ink);
}
.masthead .meter {
  font-size: 0.68rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.standfirst {
  font-size: 0.82rem;
  color: var(--muted);
  margin-bottom: 2.2rem;
  line-height: 1.5;
}

.you {
  margin: 2.1rem 0 1.3rem;
  padding-left: 0.95rem;
  border-left: 2px solid var(--notes);
  font-size: 1.01rem;
  line-height: 1.6;
  color: var(--ink);
}

.opener {
  margin: 0.85rem 0;
  padding-left: 0.95rem;
  border-left: 2px solid var(--line);
  font-size: 0.95rem;
  color: var(--muted);
  line-height: 1.55;
}

.who {
  font-size: 0.66rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.15rem;
}

.badge {
  display: inline-block;
  margin: 0.55rem 0 0.2rem;
  padding: 0.14rem 0.55rem;
  font-size: 0.7rem;
  letter-spacing: 0.03em;
  border: 1px solid var(--line);
  border-radius: 2px;
  background: var(--card);
  color: var(--muted);
  cursor: default;
}
.badge.notes { color: var(--notes); border-color: #DFD0B2; }
.badge.web   { color: var(--web);   border-color: #C6D4CC; }
.badge .took { color: var(--muted); font-variant-numeric: tabular-nums; }

.sysnote {
  border-top: 1px solid var(--line);
  text-align: center;
  margin: 2.4rem 0 0.6rem;
  line-height: 0;
}
.sysnote span {
  background: var(--paper);
  padding: 0 0.9rem;
  font-size: 0.68rem;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--muted);
}

[data-testid="stBottomBlockContainer"], [data-testid="stBottom"] { background: var(--paper); }
[data-testid="stChatInput"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 3px;
}
[data-testid="stChatInput"] textarea {
  height: auto !important;
  min-height: 1.6rem !important;
  max-height: 9rem !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #9A9285; }
</style>
"""

LABELS = {
    "search_notes": ("read your notes", "notes"),
    "web_search": ("searched the web", "web"),
}

OPENERS = [
    "What did we decide about the pro tier pricing?",
    "When does my passport expire?",
    "Who is the prime minister of the United Kingdom?",
]

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.shown = []


def badge(turn: dict) -> str:
    label, tone = LABELS.get(turn["tool"], ("answered directly", ""))
    took = f" <span class='took'>{turn['seconds']:.1f}s</span>" if turn["tool"] else ""
    why = html.escape(turn["reason"] or "Answered without looking anything up.", quote=True)

    return f"<div><span class='badge {tone}' title='{why}'>{label}{took}</span></div>"


def draw(turn: dict) -> None:
    if turn["role"] == "note":
        st.markdown(
            f"<div class='sysnote'><span>{turn['text']}</span></div>",
            unsafe_allow_html=True,
        )
        return

    if turn["role"] == "user":
        st.markdown(
            f"<div class='you'>{html.escape(turn['text'])}</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown("<div class='who'>Aura</div>", unsafe_allow_html=True)
    st.markdown(turn["text"])
    st.markdown(badge(turn), unsafe_allow_html=True)


st.markdown(STYLE, unsafe_allow_html=True)

used = count_tokens(st.session_state.history)

st.markdown(
    "<div class='masthead'>"
    "<span class='name'>Aura</span>"
    f"<span class='meter'>context {used} of {CONTEXT_BUDGET}</span>"
    "</div>"
    "<div class='standfirst'>Chief of staff for your notes, meetings and dates. "
    "Every answer says how it was reached.</div>",
    unsafe_allow_html=True,
)

for turn in st.session_state.shown:
    draw(turn)

if not st.session_state.shown:
    st.markdown("<div class='who'>Try asking</div>", unsafe_allow_html=True)
    for opener in OPENERS:
        st.markdown(f"<div class='opener'>{opener}</div>", unsafe_allow_html=True)

question = st.chat_input("Ask Aura something")

if question:
    st.session_state.history.append({"role": "user", "content": question})
    st.session_state.shown.append({"role": "user", "text": question})

    draw(st.session_state.shown[-1])

    with st.spinner(""):
        answer = respond(st.session_state.history)

    st.session_state.history.append({"role": "assistant", "content": answer["text"]})
    st.session_state.shown.append(
        {
            "role": "assistant",
            "text": answer["text"],
            "tool": answer["tool"],
            "reason": answer["reason"],
            "seconds": answer["tool_seconds"],
        }
    )

    if needs_trimming(st.session_state.history):
        before = count_tokens(st.session_state.history)
        st.session_state.history = compress_history(st.session_state.history)
        after = count_tokens(st.session_state.history)
        st.session_state.shown.append(
            {
                "role": "note",
                "text": f"earlier turns summarised, {before} tokens down to {after}",
            }
        )

    st.rerun()
