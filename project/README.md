# Athena — the incremental project

One system, built across all 24 weeks. Every module adds a stage. By the end it is a real
AI-platform service you can put on your CV and defend line by line in an interview.

**What Athena is:** a document intelligence platform. Point it at a corpus of documents; it
ingests, indexes, searches, summarizes, answers questions with citations, and can run multi-step
research over the corpus with an agent. It knows what it costs, proves it isn't regressing, and
refuses to be prompt-injected.

**Why this project:** it forces you through the exact stack in current AI-engineer job
descriptions — Python, FastAPI, Postgres, async, vector search, LLM orchestration, evals,
observability — without ever being a toy.

## Ground rules

1. **Never rewrite from scratch.** Each stage refactors the last. Feeling the pain of your Stage 1
   dicts is what makes Stage 3's dataclasses land.
2. **Commit at every stage.** `git tag stage-1`, `stage-2`, … Your own diff history is the best
   record of your progress, and reviewing `stage-1..stage-9` at the end is genuinely instructive.
3. **Tests before the next stage.** Athena has no grader — you write the tests. From Module 06
   onward the coverage bar is 80% on `athena/`, enforced in CI.
4. **Only the dependencies the current stage allows.** The constraint is the point.

---

## Stage 1 — CLI indexer (after Module 01)

**Allowed:** stdlib only. Functions, dicts, lists. No classes yet.

Build `athena/index.py` and `athena/cli.py`:

- Walk a directory, read `.txt` and `.md` files (`pathlib`, `encoding="utf-8"`).
- Tokenize each document (reuse your `tokenize` from `ex02_text_stats`).
- Build an inverted index: `dict[str, dict[str, int]]` — token → {doc_path: count}.
- `search(index, query) -> list[tuple[str, int]]` — documents ranked by total match count
  across query tokens, ties broken by path.
- A `python -m athena.cli index <dir>` / `search <query>` entry point using `sys.argv`.
- Persist the index to JSON so `search` doesn't re-index every time.

**Constraints:** no `for i in range(len(...))`; every function annotated and under 20 lines;
`ruff check` clean.

**Done when:** you can index this repo's own `.md` files and search them in under a second.

---

## Stage 2 — Idiomatic refactor (after Module 02)

**Allowed:** stdlib only, plus decorators.

- Replace output-format branching with a dispatch table.
- Make every optional parameter keyword-only.
- `@functools.cache` on the tokenizer; measure the difference on repeated queries.
- Write a `@timed` decorator that records elapsed time per phase into a stats dict; use it to find
  your slowest step and say out loud why it's slowest.
- Audit for mutable defaults: `ruff check --select B006,B008 .`

---

## Stage 3 — Model the domain (after Module 03)

**Allowed:** stdlib only.

- `@dataclass(frozen=True, slots=True)` for `Document`, `Posting`, `SearchHit`.
- A `Corpus` class owning the index, with `__len__`, `__iter__`, `__contains__`, `__repr__`.
- Turn ingestion into a **generator pipeline** — `walk → read → tokenize → post` — so a 10 GB
  corpus streams in constant memory. Prove it by watching RSS while indexing.
- A `@contextmanager` for "open corpus, flush index on exit, even on exception."
- Define `Tokenizer` as a `Protocol`, with two implementations.

---

## Stage 4 — Package it (after Module 04)

- Proper `src/athena/` layout, `__init__.py` exporting the public API.
- Split into `athena.ingest`, `athena.index`, `athena.search`, `athena.cli`.
- Real `logging` with a module-level logger per file. No `print` outside the CLI.
- `argparse` subcommands, `pathlib` everywhere, config from a TOML file.
- Kill any circular import you created, and be able to explain why it happened.

---

## Stage 5 — Types and validation (after Module 05)

- `mypy --strict` clean across `athena/`, zero `# type: ignore` you can't justify.
- Pydantic v2 models for config, search requests, and search results.
- `pydantic-settings` for env-var config (12-factor).
- Generic `Repository[T]` protocol for storage backends.

---

## Stage 6 — Test it properly (after Module 06)

- A real test pyramid: unit tests for tokenizer/ranking, integration for ingest→search.
- `tmp_path` fixtures for corpora; no test touches your real filesystem.
- `@parametrize` your ranking tests across at least 8 corpus shapes.
- One `hypothesis` property test: *indexing then searching any token in a document always returns
  that document.*
- Coverage ≥ 80%, enforced with `--cov-fail-under=80`.

---

## Stage 7 — Make it concurrent (after Module 07)

- Async ingestion with `asyncio` + `anyio.to_thread` for the blocking file reads.
- `TaskGroup` for structured concurrency; a semaphore to bound open file handles.
- Benchmark: sequential vs threaded vs async vs multiprocessing on 1000 files. **Write down the
  numbers and explain them using the GIL.** This is a top-5 Python interview question.

---

## Stage 8 — Ship it (after Module 08)

- `typer` CLI with rich help and shell completion.
- `structlog` JSON logs (the logfmt records from `ex03_log_parser` come full circle).
- Multi-stage Dockerfile, non-root user, image under 200 MB.
- GitHub Actions: ruff + mypy + pytest + coverage gate on every push.
- Publish a wheel to a local index; `uv tool install athena` and run it.

---

## Stage 9 — Serve it (after Module 09)

- FastAPI: `POST /documents`, `GET /search`, `GET /healthz`.
- Pydantic request/response models; auto OpenAPI docs.
- `Depends` for the corpus dependency — compare it to `@Autowired` and note what's different.
- API-key auth middleware, structured error handling, request-id propagation.
- Background ingestion tasks with progress polling.

---

## Stage 10 — Persist it (after Module 10)

- Postgres via SQLAlchemy 2.0 (async engine): `documents`, `tokens`, `postings`.
- Alembic migrations, including one non-trivial data migration.
- Replace the JSON index with SQL, and keep the tests passing throughout.
- Add a Redis cache for hot queries; measure the hit rate.
- Full-text search with Postgres `tsvector` as your keyword baseline — you will compare vector
  search against it in Stage 13, and you need the baseline to be honest.

---

## Stage 11 — Analyze it (after Modules 11–12)

- Corpus analytics with NumPy/Pandas: term distributions, Zipf plot, doc-length histograms,
  duplicate detection via shingling.
- TF-IDF scoring implemented with vectorized NumPy — no Python loops over terms.
- Export to Parquet; compare Pandas vs Polars on the same aggregation.

---

## Stage 12 — Make it fast (after Module 13)

- Profile ingestion with `cProfile` and `py-spy`; find the top 3 hotspots.
- Get a **10× speedup** on the ingest path. Write down what you changed and the before/after
  numbers.
- Add a benchmark to CI that fails on a >20% regression.

---

## Stage 13 — Add the LLM (after Modules 14–15)

- `POST /documents/{id}/summary` — streaming summarization via the Claude API.
- Structured metadata extraction (title, entities, topics) with tool use / structured outputs.
- Prompts live in versioned files, not string literals. Prompt caching where it pays.
- Token accounting and per-request cost, logged on every call.
- Graceful degradation: if the LLM is down, the service still searches.

---

## Stage 14 — Real RAG (after Module 16)

- Chunking with overlap; measure how chunk size changes answer quality.
- Embeddings into pgvector; HNSW index.
- Hybrid retrieval: vector + BM25, fused with reciprocal rank fusion.
- Reranking pass over the top 50.
- `POST /ask` returning an answer **with citations back to chunk IDs**. No citation, no answer.

---

## Stage 15 — Agent (after Module 17)

- A research agent with tools: `search_corpus`, `read_document`, `compare_documents`.
- The agent loop: plan → call tool → observe → repeat, with a hard step budget.
- Expose the tools over MCP so any MCP client can drive your corpus.
- Handle the real failure modes: loops, hallucinated tool names, budget exhaustion.

---

## Stage 16 — Prove it works (after Module 18)

- A golden set of 50 Q&A pairs over a fixed corpus.
- Retrieval metrics (recall@k, MRR) and answer metrics (LLM-judge with a written rubric).
- `pytest -m eval` runs the suite; CI fails on a >5% quality regression.
- OpenTelemetry tracing end-to-end; a dashboard of latency, tokens, and cost per endpoint.

---

## Stage 17 — Harden it (after Module 19)

- Concurrency-limited LLM fan-out with retries, exponential backoff, and jitter.
- Semantic caching keyed by normalized question.
- A per-tenant budget guard that refuses requests over a daily cost cap.
- Prompt-injection defenses: treat retrieved document text as data, never as instructions.
  Write the test that proves a malicious document can't exfiltrate the system prompt.
- PII detection and redaction before anything reaches a log or a model.

---

## Stage 18 — Capstone (Weeks 23–24)

- Deploy it. Load-test it with `locust`; publish p50/p95/p99.
- Write `ARCHITECTURE.md`: the diagram, the trade-offs, the things you'd do differently.
- Write `POSTMORTEM.md` on the worst bug you hit and how you found it. Interviewers ask about
  this exact thing, and having written it down is the difference between a good answer and a
  great one.
- Tag `v1.0.0`.

---

## Interview mapping

When you're done, these are the questions you can now answer from your own code, not from a blog
post you skimmed:

| Question | Your evidence |
| --- | --- |
| "Explain the GIL." | Stage 7 benchmark numbers |
| "How do you make Python fast?" | Stage 12, with a profile |
| "How does RAG work end to end?" | Stage 14 |
| "How do you test something non-deterministic?" | Stage 16 |
| "How do you control LLM cost?" | Stages 13 & 17 |
| "How do you handle prompt injection?" | Stage 17, with the test |
| "Design a document search service." | The whole thing |
