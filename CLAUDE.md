# Working in this repo

This is a **self-study course**, not an application. The reader is an experienced Java/Spring Boot
engineer learning professional Python, aiming at AI engineering. Full syllabus: [README.md](README.md).

Do not explain programming fundamentals. Anchor Python concepts to their JVM counterpart, and name
the Java habit each idiom replaces.

## Layout

```
modules/mNN_topic/
  LESSON.md      four weeknight sections + a weekend project checkpoint
  examples/      runnable, annotated scripts. Deliberately contain anti-patterns.
  exercises/     stubs that `raise NotImplementedError`. The docstring is the spec.
  tests/         pytest suite that grades the exercises
  solutions/     verified reference implementations (+ a README telling the reader not to peek)
project/         Athena — one system refactored forward across all 24 weeks
reference/       java_to_python.md cheatsheet
```

## Adding a module — required procedure

1. Write `LESSON.md`, `examples/`, `exercises/` (stubs only), and `tests/`.
2. Write a full reference implementation into `solutions/`.
3. **Verify the graders**: temporarily copy `solutions/*.py` over `exercises/*.py`, run
   `uv run pytest modules/mNN_topic -q`, and confirm **everything passes**. A grader that
   disagrees with its own spec is worse than no grader.
4. **Restore the stubs** and confirm the suite goes red again.
5. Run every example script and confirm it exits 0.
6. `uv run ruff format . && uv run ruff check . && uv run mypy .` must all be clean.
7. Copy the `solutions/README.md` warning file into the new module.
8. Update the "Built so far" list in `README.md` and the module row in `ROADMAP.html`.

Never skip step 3. It has already caught spec/test mismatches.

## Conventions

- Every function gets full type annotations, including in exercise stubs.
- Exercise docstrings are written as tickets: behaviour, examples, edge cases, `Raises:`.
  Include a hint only where a stdlib tool is the point of the exercise.
- Tests use plain `assert`, `@pytest.mark.parametrize`, and `pytest.raises`. Group them in
  `Test*` classes by function. Test names state the behaviour, not the mechanics.
- Examples number their output (`print("1)", ...)`) so the reader can match output to source.
- Exceptions end in `Error` (ruff N818). Give each package one base exception class.
- Deliberate anti-patterns live **only** in `examples/`, and are kept lint-clean via the
  `per-file-ignores` block in `pyproject.toml` — extend that list rather than deleting a lesson.
- `UP047` is globally disabled: the course teaches `TypeVar` first because that's what existing
  code uses, and introduces PEP 695 syntax in Module 05.

## Athena

One system, refactored forward, **never rewritten** — feeling the pain of an earlier stage is the
teaching mechanism. Stage specs: [project/README.md](project/README.md). Each `LESSON.md` ends
with the matching weekend checkpoint.

## Commands

```bash
uv sync                                          # set up
uv run pytest modules/m01_language_core -x -q    # grade one module
uv run pytest -q                                 # everything
uv run ruff format . && uv run ruff check .
uv run mypy .
```

## Pace

~12–15 h/week: 1.5–2h weeknights, longer weekend blocks. 24 weeks total. Size modules to that —
four weeknight sections plus one weekend project checkpoint.
