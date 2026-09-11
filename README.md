# Aura: A Chief of Staff That Shows Its Work

Aura is a personal assistant built on Gemini. It decides for itself whether to answer
from what it already knows, look through your own notes, or search the web, and it
tells you which one it did on every single answer.

Most assistants hide that choice. The whole point of this one is that you can see it.

## Core Capabilities

**Decision Layer**: Every message goes to Gemini with two tools declared. The model
picks between answering directly, calling `search_notes`, or calling `web_search`.
It also has to supply a one sentence reason for the tool it picked, which gets
recorded alongside the choice.

**Note Retrieval**: Your text files in `docs/` are split into chunks, embedded with
`gemini-embedding-001` at 768 dimensions, and stored in a single JSON file. Queries
are embedded the same way and ranked by cosine similarity. No vector database, no
external service, just a file you can open and read.

**Web Search**: Posts the query to DuckDuckGo's lite endpoint and returns the top
four titles, snippets and URLs. The model reads those results and writes the answer
from them. No API key needed.

**Conversation Memory**: The full message history is sent with every request. Once
the conversation crosses the token budget, everything except the last six messages
is replaced by a summary of under 150 words, and the conversation carries on.

**Decision Logging**: Every turn appends one JSON line to `logs/decisions.jsonl`
holding the choice, the reason, the tool query, what came back, how long the tool
took, how long the whole turn took, and the token counts.

## Running the System

**Setup Phase**:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
On macOS or Linux, activate with `source venv/bin/activate` instead. Built and
tested on Python 3.11.

**Configuration**:
```bash
copy .env.example .env
```
Then put your Gemini key in it. Only `GOOGLE_API_KEY` is required. Everything else
falls back to a working default.

| Variable | Default | What it does |
|---|---|---|
| `GOOGLE_API_KEY` | required | Your Gemini API key |
| `AURA_MODEL` | `gemini-2.5-flash` | Chat and routing model |
| `AURA_EMBED_MODEL` | `gemini-embedding-001` | Embedding model for retrieval |
| `AURA_CONTEXT_BUDGET` | `6000` | Token budget before history is summarized |
| `AURA_MAX_TOKENS` | `1024` | Cap on response length |
| `AURA_TEMPERATURE` | `0.7` | Sampling temperature |
| `AURA_TOP_P` | `0.95` | Nucleus sampling |
| `AURA_TOP_K` | `40` | Top k sampling |

**Document Indexing**:
```bash
python -m aura.core.retrieval
```
Reads every `.txt` file in `docs/`, embeds it, and writes `store/index.json`. The
five sample notes produce 20 chunks. You do not have to run this by hand, since the
index rebuilds itself whenever a file in `docs/` is newer than the index, but it is
useful for checking the ingest worked.

**Terminal Chat**:
```bash
python -m aura.cli.chat
```
Type `exit` or `quit` to leave. Tool use shows up as a line like
`[search_notes in 0.4s]` under the answer.

**Web Interface**:
```bash
streamlit run app.py
```
Runs at `http://localhost:8501`. Each answer carries a small badge saying whether
Aura read your notes, searched the web, or answered directly. Hover the badge to
see the reason the model gave for that choice.

**Tests**:
```bash
pytest test
```
Twelve tests covering the token counter, cosine similarity, chunking, and the
search result parser. They make no API calls and need no network.

## Key Design Decisions

Documents are split on blank lines, and any block shorter than nine words is thrown
away, which drops headings and stray fragments before they reach the index. There is
no overlap between chunks yet, so a fact spread across two paragraphs can land half
in each.

Retrieval refuses to return anything scoring below 0.6. That number was tuned rather
than guessed: at 0.45 an unrelated question like "what is the capital of France" was
still pulling back notes at 0.50 and the model was dutifully trying to answer from
them. At 0.6 it correctly says nothing in the notes covers that. The figure is
specific to `gemini-embedding-001` and would need redoing for a different embedding
model.

A turn makes at most one tool call. When a tool fires there are two model calls: the
first decides and calls, the second writes the answer with tools switched off. Turning
them off is what guarantees the second call comes back as text instead of looping into
another tool. The tradeoff is that Aura cannot check your notes and then search the
web inside a single answer.

Logging lives inside `respond()` rather than in the terminal and web entry points.
There is one place a decision can be made, so there is one place it can be recorded,
and neither interface can forget to.

Web search goes through DuckDuckGo rather than Gemini's built in `google_search`
grounding. Grounding was the first choice, but it returns 429 on a free tier key for
every model while normal generation works fine. The cost of the fallback is that it
is a scrape, so it will break if DuckDuckGo changes their markup, and answers are
only as good as the snippets, since Aura never opens the pages themselves.

The token counter approximates four characters to a token. That runs roughly fifteen
percent under the real Gemini count on technical text, which is fine for deciding when
to summarize and not fine for anything to do with billing.

One thing to watch: set `AURA_CONTEXT_BUDGET` too low and summarization starts
thrashing. Six kept messages plus a 150 word summary is around 550 tokens on its own,
so at a budget of 500 it fires every turn and can report the count going up rather
than down. The 6000 default leaves plenty of room.
