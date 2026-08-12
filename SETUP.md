# Module 00 — Professional Setup (Week 0)

Goal: a machine configured the way a Python team in 2026 actually configures it. Budget 2–3 hours.

You have Python 3.10.11 installed. That still works, but the industry baseline is **3.12/3.13**
(pattern matching maturity, better error messages, `TaskGroup`, faster interpreter, and — from
3.13 — an experimental free-threaded build). We'll install a modern interpreter *without*
touching your system Python.

---

## 1. Install `uv`

`uv` is the tool that replaced the old mess of `pip` + `virtualenv` + `pip-tools` + `pyenv` +
`poetry`. It is written in Rust, resolves and installs in milliseconds, and manages interpreters
too. If a JD says "Poetry" they mean this job; if it says "uv" they're current.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen your terminal, then:

```bash
uv --version
```

### Java map

| JVM world | Python world |
| --- | --- |
| SDKMAN / `jenv` | `uv python install` |
| Maven / Gradle | `uv` + `pyproject.toml` |
| `pom.xml` / `build.gradle` | `pyproject.toml` |
| `mvnw` wrapper | `uv run` (bootstraps the env itself) |
| `~/.m2/repository` | `~/.cache/uv` (hardlinked, shared across projects) |
| `mvn dependency:tree` | `uv tree` |
| Maven "effective pom" lock | `uv.lock` |

## 2. Get a modern interpreter

```bash
uv python install 3.13
```

`uv` downloads a standalone CPython build. Your system 3.10 is untouched.

## 3. Create the project environment

From this repo's root:

```bash
uv sync
```

That reads [pyproject.toml](pyproject.toml), creates `.venv/`, installs every dependency, and
writes `uv.lock`. **Commit the lockfile.** Same reasoning as committing a resolved dependency
tree — reproducible builds.

Verify:

```bash
uv run python -c "import sys; print(sys.version)"
```

You should see 3.13.x. Note the pattern: **`uv run <cmd>`** executes inside the venv without you
activating anything. Prefer it over `activate` — it's what CI does.

<details>
<summary>If you do want to activate the venv (PowerShell)</summary>

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks it, that's an execution-policy issue — just use `uv run` instead.
</details>

## 4. Understand what a virtual environment *is*

This is the concept Java devs most often get wrong, because the JVM has no equivalent.

- Python has **no** classpath. `import x` searches `sys.path` at runtime.
- A venv is a directory with its own `python` executable and its own `site-packages`.
- Activating it just prepends its `Scripts/` (or `bin/`) to `PATH`.
- There is **one** version of each package per environment. No shading, no `provided` scope, no
  two versions of the same library coexisting. Dependency conflicts are resolved, not isolated.
- Consequence: one venv per project, always. Never `pip install` into your system Python.

```bash
uv run python -c "import sys; print('\n'.join(sys.path))"
```

Read that output. That *is* your classpath, computed at startup.

## 5. The four tools you will run every day

| Tool | Role | JVM analogue |
| --- | --- | --- |
| `ruff` | Linter **and** formatter, one binary, ~800 rules | Checkstyle + SpotBugs + google-java-format |
| `mypy` | Static type checker | the `javac` type check you took for granted |
| `pytest` | Test runner | JUnit 5 |
| `pre-commit` | Git hooks that run the above | Maven `verify` phase, but before the commit |

```bash
uv run ruff format .          # rewrite files
uv run ruff check . --fix     # lint and autofix
uv run mypy .                 # type check
uv run pytest -q              # run tests
```

### Why `mypy` matters to you specifically

Python is dynamically typed at runtime, but professional Python is **statically typed at review
time**. Type hints are not decoration; `mypy --strict` on a modern codebase catches roughly the
class of bugs `javac` catches for you today. Every serious team runs it in CI. Configure it
strict from day one — retrofitting types onto an untyped codebase is genuinely painful, and you
never have to do that if you never write untyped code.

## 6. Install the git hooks

```bash
uv run pre-commit install
```

Now `git commit` refuses to accept unformatted, unlinted, or badly typed code. You will be
annoyed at this for one week and grateful for it forever.

## 7. Editor

VS Code + these extensions:

- **Python** (Microsoft)
- **Pylance** — set `python.analysis.typeCheckingMode` to `strict`
- **Ruff** (Astral)

Point the interpreter at `.venv` (Command Palette → *Python: Select Interpreter*).

If you're coming from IntelliJ, PyCharm Professional is a legitimate choice and will feel
familiar. But learn the CLI commands above regardless — that's what CI runs, and "works in my
IDE" is not a passing build.

## 8. Verify the whole toolchain

```bash
uv run pytest modules/m01_language_core -q
```

You should see `117 failed, 1 passed, 7 errors` — a wall of `NotImplementedError`. **That is
success.** Those are your week-1 exercises, and turning that wall green is the job.

(The 7 "errors" are tests whose *fixture* calls an unimplemented function, so they blow up during
setup rather than during the assertion. pytest distinguishes the two — a useful signal to
recognize now, because in real work "error" means your harness broke and "failed" means your code
is wrong.)

---

## Checkpoint — you're done with Week 0 when

- [ ] `uv --version` works
- [ ] `uv run python -V` reports 3.13.x
- [ ] `uv run ruff check .` passes
- [ ] `uv run mypy .` passes
- [ ] `uv run pytest -q` runs and reports failures (not errors — failures)
- [ ] `uv run pre-commit install` done
- [ ] You read your `sys.path` output and can explain why there's no classpath

Next: [Module 01 — Language Core](modules/m01_language_core/LESSON.md)
