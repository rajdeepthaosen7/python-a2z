"""The full parameter grammar, and why keyword-only params are a habit worth building.

Run me:  uv run python modules/m02_functions/examples/02_args_kwargs.py
"""

from typing import Any


def main() -> None:
    # ---- 1. The whole grammar in one signature ---------------------------
    def demo(pos_only: int, /, standard: int, *args: int, kw_only: str, **kwargs: Any) -> str:
        return f"{pos_only=} {standard=} {args=} {kw_only=} {kwargs=}"

    print("1)", demo(1, 2, 3, 4, kw_only="x", extra=True))
    print("2)", demo(1, standard=2, kw_only="x"))
    try:
        demo(pos_only=1, standard=2, kw_only="x")  # type: ignore[call-arg]
    except TypeError as exc:
        print("3)", exc)

    # ---- 2. *args collects positionals into a TUPLE ---------------------
    def total(*values: float) -> float:
        return sum(values)

    print("4)", total(), total(1), total(1, 2, 3.5))

    # ---- 3. **kwargs collects keywords into a DICT ----------------------
    def tag(name: str, **attrs: str) -> str:
        rendered = "".join(f' {k.rstrip("_")}="{v}"' for k, v in attrs.items())
        return f"<{name}{rendered}>"

    print("5)", tag("a", href="/x", class_="btn"))
    # note class_ -> class: the trailing-underscore convention for keywords

    # ---- 4. The bare `*`: keyword-only parameters ------------------------
    def connect(host: str, port: int, *, timeout: float = 5.0, retries: int = 3) -> str:
        return f"{host}:{port} timeout={timeout} retries={retries}"

    print("6)", connect("db", 5432, timeout=1.0))
    try:
        connect("db", 5432, 1.0)  # type: ignore[call-arg]
    except TypeError as exc:
        print("7)", exc)

    # THIS is the habit. Compare the two call sites:
    def render_bad(data: str, sort: bool, header: bool, ascii_only: bool) -> str:
        return f"{data} {sort} {header} {ascii_only}"

    def render_good(data: str, *, sort: bool = False, header: bool = True) -> str:
        return f"{data} {sort} {header}"

    print("8)", render_bad("x", True, False, True))  # what do these mean?
    print("9)", render_good("x", sort=True, header=False))  # self-documenting

    # Boolean positional args are a known code smell — ruff's FBT rules flag
    # them. Keyword-only params are Python's answer to the Builder pattern.

    # ---- 5. Spreading at the call site ----------------------------------
    args = ("db", 5432)
    kwargs: dict[str, Any] = {"timeout": 2.0}
    print("10)", connect(*args, **kwargs))

    # Collect-then-spread is the mechanism behind every decorator:
    def forwarding_wrapper(*args: Any, **kwargs: Any) -> str:
        print("11) intercepted", args, kwargs)
        return connect(*args, **kwargs)

    print("12)", forwarding_wrapper("cache", 6379, retries=1))

    # ---- 6. Unpacking a dict into a typed call --------------------------
    config = {"host": "prod-db", "port": 5432, "timeout": 0.5}
    print("13)", connect(**config))  # type: ignore[arg-type]
    # Convenient, but mypy can't verify it. In real code, parse the dict into a
    # Pydantic model first (Module 05) and pass the model's fields explicitly.

    # ---- 7. Introspection -----------------------------------------------
    import inspect

    sig = inspect.signature(connect)
    print("14)", sig)
    for name, param in sig.parameters.items():
        print(f"15) {name}: kind={param.kind.name} default={param.default!r}")
    # This is how pytest fixtures, FastAPI Depends, and typer CLIs all work:
    # they read your signature and supply arguments to match it.


if __name__ == "__main__":
    main()
