# Python for Java Engineers → AI Engineering

A 24-week, industry-oriented course that takes you from *"I write Java/Spring Boot"* to
*"I ship production Python and AI systems."*

Built for someone who already knows engineering. There is no "what is a variable" chapter.
Every concept is anchored to what you already know from the JVM, then pushed to what the
Python ecosystem actually expects in 2026 job descriptions.

---

## How this course is different

| Typical Python course | This course |
| --- | --- |
| Teaches syntax in isolation | Teaches Python's **data model** — the thing that makes code Pythonic |
| `print("hello")` exercises | `pytest` suites you must make green, same loop as JUnit |
| Toy scripts | One product (**Athena**) built incrementally over 24 weeks |
| Skips tooling | Week 0 is `uv`, `ruff`, `mypy --strict`, `pytest`, pre-commit, Docker |
| "AI" = one OpenAI call | Retrieval, agents, evals, cost control, prompt injection defense |
| Assumes beginner | Assumes you know DI, transactions, thread pools, and REST |

---

## The pace model

| Slot | Duration | What you do |
| --- | --- | --- |
| Weeknights (Mon–Thu) | 1.5–2h | One lesson section + its examples + exercises |
| Saturday | 3–4h | Project checkpoint — build Athena's next stage |
| Sunday | 2–3h | Review, refactor last week's code, read source of a real library |

That's ~12–15 h/week. **24 weeks ≈ 6 months.** If a week slips, slip it — the modules are
ordered by dependency, not by calendar.

---

## Curriculum

### Phase 0 — Professional setup (Week 0)

| # | Module | Core content |
| --- | --- | --- |
| 00 | Tooling & environment | `uv`, virtual envs, `pyproject.toml`, src-layout, `ruff`, `mypy`, `pytest`, pre-commit, editor config |

> Java map: Maven/Gradle → `uv` + `pyproject.toml`; Checkstyle/SpotBugs → `ruff`; JUnit → `pytest`; SDKMAN → `uv python install`.

### Phase 1 — Language core, rebuilt for a Java brain (Weeks 1–4)

| # | Module | Core content |
| --- | --- | --- |
| 01 | Language core | Objects & names (not variables), mutability, truthiness, sequences, slicing, comprehensions, unpacking, f-strings, EAFP vs LBYL, exceptions |
| 02 | Functions & decorators | First-class functions, `*args`/`**kwargs`, keyword-only params, default-arg trap, closures, `nonlocal`, decorators, parameterized decorators, `functools` |
| 03 | The data model | Dunder methods, `__eq__`/`__hash__` contracts, `dataclasses`, `Protocol` vs ABC, duck typing, iterators, generators, `yield`, context managers, descriptors, properties |
| 04 | Stdlib & project structure | Modules, packages, import system, circular imports, `pathlib`, `collections`, `itertools`, `datetime`, `json`, `logging`, `argparse`, `subprocess`, `contextlib` |

### Phase 2 — Professional Python (Weeks 5–10)

| # | Module | Core content |
| --- | --- | --- |
| 05 | Typing & Pydantic | `mypy --strict`, generics, `TypeVar`, `Protocol`, `Literal`, `TypedDict`, `overload`, variance, `ParamSpec`, Pydantic v2 models/validators/settings |
| 06 | Testing like a pro | pytest fixtures & scopes, `parametrize`, `monkeypatch`, mocking boundaries, fakes vs mocks, coverage, `hypothesis` property tests, `testcontainers` |
| 07 | Concurrency & async | GIL reality, threads vs processes vs async, `asyncio` event loop, `async`/`await`, `TaskGroup`, cancellation, `anyio`, `concurrent.futures`, free-threaded Python |
| 08 | Packaging & delivery | Dependency resolution & lockfiles, versioning, publishing, `typer` CLIs, 12-factor config, structured logging, OpenTelemetry, multi-stage Docker, CI |
| 09 | APIs with FastAPI | Routing, Pydantic request/response, dependency injection, middleware, auth (JWT/OAuth2), background tasks, streaming, error handling, OpenAPI |
| 10 | Data persistence | SQLAlchemy 2.0 ORM & Core, sessions & unit-of-work, Alembic migrations, transactions & isolation, async drivers, Redis, connection pooling |

> Java map: Spring Boot → FastAPI; Bean Validation → Pydantic; Spring DI → FastAPI `Depends`; Hibernate/JPA → SQLAlchemy; Flyway → Alembic; `CompletableFuture` → `asyncio`; virtual threads → free-threaded CPython & async.

### Phase 3 — Numeric & data Python (Weeks 11–13)

| # | Module | Core content |
| --- | --- | --- |
| 11 | NumPy & vectorized thinking | ndarray, dtypes, broadcasting, views vs copies, axis semantics, linear algebra, why loops are the enemy |
| 12 | Pandas & Polars | Series/DataFrame, indexing, joins, groupby-agg, reshaping, missing data, time series, Polars lazy API, Arrow & Parquet |
| 13 | Performance engineering | `cProfile`, `py-spy`, `timeit`, memory profiling, algorithmic vs interpreter overhead, `functools.cache`, `numba`, native extensions, when to reach for Rust |

### Phase 4 — AI Engineering (Weeks 14–22)

| # | Module | Core content |
| --- | --- | --- |
| 14 | LLM fundamentals for engineers | Tokenization, context windows, embeddings, sampling params, latency/cost math, Claude & OpenAI SDKs, streaming, structured outputs, tool use |
| 15 | Prompts as code | Templating, versioning, prompt caching, few-shot construction, system design of prompts, deterministic testing of non-deterministic systems |
| 16 | RAG systems | Loaders, chunking strategies, embedding models, vector stores (pgvector, Qdrant, Chroma), hybrid & BM25 search, reranking, retrieval metrics |
| 17 | Agents & tool use | Agent loops, function/tool schemas, MCP, planning, memory, multi-agent orchestration, LangGraph & the Claude Agent SDK, failure modes |
| 18 | Evals & observability | Golden datasets, LLM-as-judge, rubric design, regression gates in CI, tracing (OTel/Langfuse), token & cost dashboards, drift |
| 19 | Production AI systems | Concurrency for API fan-out, rate limits, retries & backoff, semantic caching, budget guards, prompt injection & output sanitization, PII, deployment topologies |
| 20 | ML foundations for AI engineers | scikit-learn workflow, train/val/test discipline, metrics, PyTorch tensors & autograd, Hugging Face `transformers`, local inference, when fine-tuning beats prompting |

### Phase 5 — Capstone (Weeks 23–24)

| # | Module | Core content |
| --- | --- | --- |
| 21 | Capstone | Ship Athena: containerized, typed, tested, traced, evaluated, cost-capped, load-tested. Write the architecture doc and the postmortem. |

---

## The incremental project: **Athena**

One system, grown every single week. By week 24 it is a portfolio piece that maps to a real
AI-platform JD, and you will have written every line.

| Weeks | Athena becomes |
| --- | --- |
| 1–4 | A stdlib-only CLI that ingests a folder of documents, tokenizes, indexes, and searches them |
| 5–6 | Fully typed (`mypy --strict`) and tested, with Pydantic models and a real test pyramid |
| 7–8 | Concurrent ingestion, packaged & installable, `typer` CLI, structured logs, Dockerized |
| 9–10 | A FastAPI service backed by Postgres + Alembic, with auth and background jobs |
| 11–13 | Corpus analytics with NumPy/Pandas, and a profiled 10× faster ingest path |
| 14–15 | LLM-powered summarization and metadata extraction with versioned prompts |
| 16 | Real RAG: pgvector store, hybrid retrieval, reranking, cited answers |
| 17 | An agent that plans multi-step research over your corpus using tools |
| 18 | An eval harness with golden Q&A, LLM-judge scoring, and CI regression gates |
| 19–22 | Hardened: rate-limited, cached, budgeted, injection-resistant, traced, deployed |
| 23–24 | Load-tested, documented, released v1.0.0 |

---

## Repository layout

```text
.
├── README.md                     <- you are here (the syllabus)
├── SETUP.md                      <- Week 0: do this first
├── ROADMAP.html                  <- interactive progress tracker
├── pyproject.toml                <- single source of truth for deps & tool config
├── reference/
│   └── java_to_python.md         <- the translation cheatsheet you'll reread often
├── modules/
│   └── mNN_topic/
│       ├── LESSON.md             <- read this first
│       ├── examples/             <- runnable, annotated. Run them, break them.
│       ├── exercises/            <- functions with `raise NotImplementedError`
│       └── tests/                <- pytest suite that grades your exercises
└── project/
    └── README.md                 <- Athena: the stage-by-stage spec
```

## The loop, every session

```bash
uv run pytest modules/m01_language_core -x -q
```

1. Read the relevant section of `LESSON.md`.
2. Run the matching file in `examples/` — then **edit it and break it** to see the error.
3. Open the `exercises/` file, implement the functions.
4. Run the tests above until green.
5. Run `uv run ruff check . && uv run mypy .` — green means idiomatic and type-safe, not just correct.

Rule: **never read the test file before attempting the exercise.** The docstring is the spec,
exactly like a JD ticket.

## Built so far

- ✅ Module 00 — `SETUP.md`
- ✅ Module 01 — Language core
- ✅ Module 02 — Functions & decorators
- ⏳ Modules 03–21 — generated as you reach them, so the tooling and model advice stays current

Ask for the next module when you finish the current one (or ask for a whole phase ahead of time).
# python-a2z
