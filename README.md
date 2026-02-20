# AI Dev Assistant

**AI Dev Assistant** is a repository-aware, retrieval-augmented assistant for **understanding, navigating, and reasoning about large Python codebases**.

Instead of treating your code as plain text, it **indexes structure**, **builds semantic representations**, and **answers questions grounded in the actual source tree**, with optional **persistent conversational memory**.

At the moment, the project is **CLI-first** and optimized for **local developer workflows**.
Future iterations are expected to add a Python API and a browser-based / ChatGPT-like UI.

---

## Why this project exists

Large codebases are hard to reason about because:

* Structure is implicit (inheritance, factories, adapters, conventions)
* Relevant context is spread across many files
* Grep and IDE search are insufficient for “why” questions
* LLMs without retrieval hallucinate or miss important details

This project solves that by:

* Parsing code into **structural chunks** (modules, classes, functions, methods)
* Embedding only **meaningful units** (not noise)
* Performing **semantic search** over your repository
* Expanding context using inheritance and overviews
* Passing grounded context into an LLM
* Optionally **remembering past conversation turns**

---

## Current strengths

* ✅ Repository-scoped indexing (multiple repos supported)
* ✅ Deterministic, reproducible data pipeline
* ✅ Semantic search with FAISS
* ✅ Context expansion modes (DEBUGGING, DOCUMENTATION, FULL, …)
* ✅ Persistent conversation memory (SQLite)
* ✅ Dry-run mode for testing (no OpenAI required)
* ✅ Strong separation of concerns (tools / services / rag / infra)
* ✅ Fully testable pipeline with fixtures and golden data

---

## Current limitations (by design)

* CLI-only interface
* OpenAI is the only AI backend today
* Python-centric (no JS/TS yet)
* No live code editing or refactoring
* No browser UI (yet)

---

## High-level architecture

The system is built as a **pipeline + query layer**.

### 1. Indexing pipeline (offline)

This runs once per repository (or when code changes):

```
Repository
  ↓
AST-based chunking
  ↓
chunks.json
  ↓
Embeddings
  ↓
embeddings.json
  ↓
FAISS index
```

Artifacts are stored under:

```
data/<repo_name>/
```

The last indexed repo is tracked via:

```
data/LAST_ACTIVE_REPO
```

---

### 2. Query / interaction layer (online)

When you ask a question:

```
Question
  ↓
Semantic search (FAISS)
  ↓
Context expansion (mode-dependent)
  ↓
LLM reasoning
  ↓
Answer
```

If using conversational mode, memory is appended and optionally summarized.


---

## Conversation modes (how the assistant thinks)

AI Dev Assistant does not have a single “personality”.
Instead, it operates in **explicit conversation modes**.

A **mode is a policy**, not a prompt hack.

It defines:

* what kind of context is retrieved
* how much structure is expanded (inheritance, overviews)
* whether an LLM is used at all
* how answers should be framed
* what the user’s intent is assumed to be

Modes are:

* **explicitly selected by the user**
* **stored per conversation**
* **stable identifiers** (safe for DB, JSON, CLI flags)

This avoids hidden heuristics and makes behavior predictable.

---

### How modes affect the pipeline

Depending on the selected mode, the system changes:

* **retrieval depth** (how much related code is pulled in)
* **context expansion** (inheritance, project overview)
* **prompt directives** (what the LLM is told to focus on)
* **answer style** (locations vs explanations vs guidance)
* **whether an LLM is used at all**

Under the hood, each mode maps to a declarative `ModePolicy`.

---

## Available modes

### `search`

**Purpose:**
Fast code location and discovery.

**Behavior:**

* Semantic search only
* No LLM calls
* Minimal context
* No explanations unless explicitly requested

**Best for:**

* “Where is X defined?”
* “What files mention Y?”
* Quick navigation in large repos

---

### `documentation`

**Purpose:**
Explain *what the code does* and *how it is intended to be used*.

**Behavior:**

* Uses retrieval + LLM
* Injects project overview
* Limited inheritance expansion
* Avoids deep implementation details

**Best for:**

* Understanding APIs
* Onboarding to unfamiliar code
* Generating human-style documentation

---

### `debugging`

**Purpose:**
Explain *runtime behavior* and *failure modes*.

**Behavior:**

* Uses retrieval + LLM
* Prefers full code over summaries
* Deeper inheritance expansion
* Focuses on edge cases and control flow

**Best for:**

* “Why does this crash?”
* “What happens if X is None?”
* Tracing unexpected behavior

---

### `coding`

**Purpose:**
Help write or modify code.

**Behavior:**

* Uses retrieval + LLM
* Prefers full code context
* Concrete, implementation-oriented answers
* Avoids vague advice

**Best for:**

* “How should I implement X here?”
* “What pattern does this codebase use for Y?”
* Guided refactoring

---

### `architecture`

**Purpose:**
Explain system-level structure and design intent.

**Behavior:**

* Uses retrieval + LLM
* Strong inheritance expansion
* Injects project overview
* Focuses on relationships and data flow

**Best for:**

* Understanding how components fit together
* Explaining design decisions
* High-level system reasoning

---

### `exploration`

**Purpose:**
Balanced, general-purpose exploration.

**Behavior:**

* Uses retrieval + LLM
* Moderate context expansion
* Mix of overview and detail
* Less opinionated than other modes

**Best for:**

* Open-ended questions
* Initial exploration of a new area
* “Tell me about this part of the code”

---

### `full`

**Purpose:**
Maximum context, maximum detail.

**Behavior:**

* Uses retrieval + LLM
* Full code preferred
* Deep inheritance expansion
* Project overview injected
* Minimal filtering

**Best for:**

* Deep dives
* Complex reasoning
* When you explicitly want “everything”

---

## Why explicit modes matter

Most AI tools try to **infer intent**.

This project intentionally does **not**.

Reasons:

* Inference is brittle
* Hidden behavior is hard to debug
* Developers prefer control
* Different tasks require different reasoning strategies

By making modes explicit:

* Behavior is predictable
* Answers are more consistent
* The system is easier to extend
* UIs can present clear choices

In the future, UIs *may* suggest modes —
but the mode will always remain visible and overridable.


---

## 1. How the memory system works (conceptual explanation)

At a high level, your memory system is:

> **A bounded, summarizing conversation state that persists across runs and stays small enough to remain useful.**

### Core idea

The assistant does **not** replay the full chat history to the LLM.

Instead, it maintains **two layers of memory**:

1. **A compact summary** of older conversation
2. **A short window of recent turns**

This gives you:

* continuity
* relevance
* bounded token usage
* long-running conversations without degradation

---

### Memory data model (what is stored)

A conversation state consists of:

```text
ConversationState
├── summary        # Optional[str]
└── recent_turns   # List[ConversationTurn]
```

Each turn is:

```text
ConversationTurn
├── role: "user" | "assistant"
└── content: str
```

---

### Lifecycle of a conversation

#### 1. Conversation starts

When a new conversation is created:

* `summary = None`
* `recent_turns = []`

No memory exists yet.

---

#### 2. Turns are appended

Each user query and assistant answer is appended via:

```python
append_turn(state, role, content)
```

This is **pure domain logic**:

* no persistence
* no LLM calls
* no side effects

---

#### 3. Summarization threshold is reached

After a configurable number of turns (default: `max_turns = 6`):

```python
needs_summarization(state) == True
```

This triggers summarization **outside** the memory module.

Important design decision:

> `rag.memory` only decides *when* summarization is needed — it does not perform it.

---

#### 4. Summarization happens (LLM-assisted, elsewhere)

Another layer (service / app):

1. Builds a **summarization prompt** using:

   * existing summary (if any)
   * recent dialogue
2. Calls the LLM
3. Produces a new, compact summary

The prompt is constructed by:

```python
build_summarization_prompt(summary, turns)
```

This ensures:

* technical tone
* factual preservation
* removal of redundancy

---

#### 5. Memory is compacted

After summarization:

```python
apply_summary(state, new_summary)
```

This:

* replaces the old summary
* truncates `recent_turns` to the last N turns (default: 2)

Result:

* long-term context is preserved
* short-term context stays sharp
* memory size stays bounded

---

#### 6. Memory is injected into the next prompt

Before answering a new question, memory is rendered as text via:

```python
build_memory_context(state)
```

Output looks like:

```text
Conversation summary:
<compact technical summary>

Recent conversation:
User: ...
Assistant: ...
```

This text is prepended to the LLM prompt.

---

### Persistence (SQLite)

Persistence is handled **outside** `rag.memory`, in:

```
infra/memory_sqlite.py
```

Key properties:

* One row per `conversation_id`
* State stored as JSON
* Fully replace-on-update (simple & robust)
* No schema coupling to domain logic

This cleanly separates:

| Concern           | Module                    |
| ----------------- | ------------------------- |
| Memory semantics  | `rag.memory`              |
| Storage           | `infra.memory_sqlite`     |
| LLM summarization | `services.memory_summary` |
| Orchestration     | `app.ask_with_memory`     |

---

### Why this design is strong

✅ Bounded memory (no runaway prompts)

✅ Explicit summarization policy

✅ Testable without OpenAI

✅ Persistent across CLI runs

✅ Easy to swap storage backend

✅ Easy to add alternative summarizers


---

## Repository layout (what is what)

### `data/`

**Generated workspace** (not source code).

```
data/
├── <repo_name>/
│   ├── chunks.json           # structural code chunks
│   ├── embeddings.json       # vector embeddings
│   ├── faiss.index           # FAISS index
│   ├── faiss_meta.json
│   ├── memory.sqlite.db      # conversation memory
│   └── chunks.preview.yaml   # human-readable preview
└── LAST_ACTIVE_REPO
```

Safe to delete and regenerate via the pipeline.

---

### `src/ai_dev_assistant/`

#### `cli/` — user-facing commands

Thin wrappers around the core logic.

* `index_repo.py` — chunk a repository
* `rebuild_embeddings.py` — compute embeddings
* `build_vector_store.py` — build FAISS index
* `export_yaml_preview.py` — readable chunk preview
* `init_data.py` — run the full pipeline
* `ask.py` — one-shot question answering
* `inspect_repo.py` — search / inspect without LLM
* `chat.py` — interactive conversational CLI with memory

---

#### `tools/` — pipeline steps (pure, non-interactive)

These are **building blocks**, not UI.

* `index_repo.py`
* `rebuild_embeddings.py`
* `build_vector_store.py`
* `export_yaml_preview.py`
* `init_data.py`
* `defaults.py` — workspace + repo resolution
* `utils.py`

---

#### `rag/` — retrieval & reasoning logic

Core “intelligence” layer.

* `chunking.py` — AST → structural chunks
* `schema.py` — `CodeChunk` definition
* `semantic_search.py` — FAISS querying
* `embedding_pipeline.py` — filtering + embedding logic
* `embedding_policy.py` — what gets embedded (and why)
* `context.py` — context expansion
* `modes.py` — DEBUGGING / DOCUMENTATION / FULL
* `memory.py` — in-memory conversation state
* `overviews.py` — high-level repo summaries
* `cost.py` — token & cost estimation

---

#### `services/` — orchestration layer

High-level, testable services.

* `search.py` — semantic search service
* `context.py` — context assembly
* `explain.py` — LLM explanation
* `memory_summary.py` — memory summarization

---

#### `app/` — application entrypoints

* `ask.py` — stateless Q&A
* `ask_with_memory.py` — conversational Q&A

---

#### `infra/` — external integrations

* `openai_client.py` — OpenAI client creation
* `ai_client.py` — abstraction for future providers
* `embeddings.py` — low-level embedding calls
* `llm_reasoning.py` — chat completions
* `memory_sqlite.py` — persistent memory
* `config.py` — env flags (DRY_RUN, models, etc.)

---

## Typical usage

### 1. Install (development)

```bash
pip install -e .
```

---

### 2. Index a repository

```bash
python -m ai_dev_assistant.cli.init_data --repo /path/to/repo
```

This runs:

1. Chunking
2. Embeddings
3. FAISS index
4. YAML preview

---

### 3. Ask a question (one-shot)

```bash
python -m ai_dev_assistant.cli.ask "How does FmriprepAdapterFactory work?"
```

---

### 4. Interactive chat with memory

```bash
python -m ai_dev_assistant.cli.chat
```

Features:

* Persistent memory per conversation
* Context-aware follow-up questions
* Automatic summarization

---

### 5. Inspect without LLM

```bash
python -m ai_dev_assistant.cli.inspect_repo "adapter factory"
```

Useful when you want **zero AI calls**.


---

## OpenAI usage and approximate costs

This project uses OpenAI models for:

- **Embeddings** (semantic search over your repository)
- **LLM reasoning** (explanations, debugging, documentation, summaries)

You must provide your own OpenAI API key to enable these features.

### Setting your OpenAI API key

Export your key as an environment variable:

```bash
export OPENAI_API_KEY=sk-...
````

To make this permanent, add it to your shell config (`~/.bashrc`, `~/.zshrc`, etc.).

The assistant will fail fast with a clear error message if the key is missing and an AI call is required.

---

### Approximate costs (guidelines, not guarantees)

Costs depend on:

* repository size
* number of chunks embedded
* how often you query
* selected conversation mode

Typical ballpark numbers:

#### Embeddings (one-time per repo version)

* Small repo (few thousand lines): **fractions of a cent**
* Medium repo (tens of thousands of lines): **a few cents**
* Large repo: still typically **well under $1**

Embeddings are **cached on disk** and only need to be regenerated when the code changes.

#### LLM queries (per question)

* Most questions cost **a few cents or less**
* DEBUGGING / FULL modes are more expensive than SEARCH
* Conversational memory adds minimal overhead due to summarization

The project estimates token usage before embedding and prints the expected cost.

---

### Dry-run mode (no OpenAI required)

For testing, development, or CI, you can disable **all OpenAI calls**:

```bash
export AI_DEV_ASSISTANT_DRY_RUN=1
```

In dry-run mode:

* No embeddings are generated
* No LLM calls are made
* Pipelines still run end-to-end
* Tests use precomputed golden data

This makes the project safe and cheap to develop and test locally.

---

### Important note

This project:

* **does not proxy or store your API key**
* **does not send code unless explicitly embedding or querying**
* **never makes silent API calls**

All AI usage is explicit, inspectable, and opt-in.

---

## Testing philosophy

* No OpenAI required for tests
* `AI_DEV_ASSISTANT_DRY_RUN=1` disables all AI calls
* Tests use:

  * isolated temp data workspaces
  * mini repositories
  * precomputed golden artifacts

This makes CI reliable and cheap.

---

## Future directions

* 🔌 Multiple AI backends (local / hosted)
* 🌐 Browser-based UI (ChatGPT-like)
* 🧠 Better cross-file reasoning
* 🧪 Smarter chunking for non-Python languages
* ✍️ Code navigation + refactoring suggestions

---

## Philosophy

This project is intentionally:

* **Explicit** over magical
* **Composable** over monolithic
* **Testable** over clever
* **Grounded** over hallucinated

It treats LLMs as **reasoning engines**, not oracles.
