# Arithmetic Ledger

A desktop calculator that remembers what you asked it.

## Overview

Most built-in OS calculators throw your last result away the moment you close
the window, and most "calculator tutorial" Tkinter projects skip session
history entirely because it complicates the click handler. This project
keeps a running, selectable log of every calculation performed in the
session, sitting behind a single collapsible panel so it doesn't clutter the
primary interface when you don't need it. It's aimed at anyone who wants a
desktop scratchpad calculator with an audit trail, or anyone studying how far
a single evaluation call and a plain Tkinter grid can carry a functional GUI
before you need a real parsing layer or a UI framework.

## Under the Hood / How It Works

The application is a single `ExtendedCalculator` class wrapping one `tk.Tk`
root window. There is no background thread and no async event loop — Tkinter
already owns the event loop via `root.mainloop()`, and every operation here
is synchronous and fast enough to run directly inside a button callback.

**Expression state:** the current expression is held as one mutable string
(`self.expression`) on the instance. Every digit, operator, or function press
appends to or truncates that string, and the `Entry` widget is fully cleared
and re-rendered from it after each mutation. There's no tokenizer and no
operator-precedence stack — string concatenation plus Python's own parser at
evaluation time does that work.

**Evaluation:** on `=`, the expression is sanitized (`%` is rewritten to
`/100`) and passed to `eval()` with an explicit `{"__builtins__": None}`
globals dict and an empty locals dict. This blocks access to `__import__`,
`open`, and the rest of the builtin namespace, restricting the callable
surface to arithmetic syntax and literals. It is not a sandbox in the strict
security sense, but for a single-string arithmetic buffer, it closes off the
obvious escape hatches.

**Unary math (`√`, `x²`):** these don't append to the expression — they
evaluate the current buffer immediately, apply a lambda (`x ** 2` or
`math.sqrt(x)`), log the operation to history, and reseed `self.expression`
with the formatted result so subsequent input chains off it.

**History:** a plain in-memory `list[str]`, appended to on every successful
evaluation. It's mirrored into a `tk.Listbox` via a full delete-and-reinsert
pass (`_sync_history_ui`) rather than incremental diffing — simple, and fast
enough for a list that resets on process exit and rarely grows past a few
hundred entries in one sitting.

**Input:** keyboard support is a single `root.bind("<Key>", ...)` handler
that maps digits, operators, `Enter`, `Backspace`, and `Escape` onto the same
`_handle_click` method the on-screen buttons call — one code path regardless
of whether input came from a click or a keystroke.

## Key Features

- Four standard arithmetic operators plus `%`, `√`, `x²`, and `x^y`
  (exponentiation via `**`)
- Sandboxed `eval()` evaluation with builtins explicitly disabled
- Collapsible side panel with full calculation history, resizing the window
  rather than overlaying it
- Click-to-recall: selecting a past entry reloads its result into the active
  expression
- Full keyboard parity with the on-screen button grid
- Zero third-party runtime dependencies

## Tech Stack & Core Dependencies

- **Python:** 3.9+ (uses `dict`/`list` built-ins and f-strings only; no
  version-specific syntax beyond widely-supported modern Python)
- **`tkinter`** (standard library) — window, `Entry`, `Button`, `Listbox`,
  `Frame` widgets and the grid geometry manager
- **`math`** (standard library) — `math.sqrt` for the `√` operator
- No third-party runtime packages. Dev-only tooling (`ruff`, `mypy`,
  `pytest`, `black`) is listed separately below and is not required to run
  the application.

## Environment & Web-Based Quick Start

### Option A — GitHub Codespaces (no local install)

1. On the repository page, click **Code → Codespaces → Create codespace on
   main**.
2. Codespaces ships Python preinstalled. Once the container finishes
   building, open a terminal inside the Codespace and run:
```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-dev.txt
```
3. Tkinter GUIs need a display. Codespaces' default container is headless,
   so either use the **Codespaces desktop/browser forwarding** feature
   (Ports tab → enable a virtual desktop) or run the app under `xvfb`:
```bash
   sudo apt-get update && sudo apt-get install -y xvfb python3-tk
   xvfb-run -a python main.py
```

### Option B — Local virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt   # only needed for lint/type/test tooling
python main.py
```

### Environment variables

The application has no required environment variables — it runs with
`python main.py` out of the box. A `.env.example` is included as a
placeholder for optional future configuration (such as a default color
theme); copy it to `.env` only if you're extending the project to read one.

## Repository Structure
```text
arithmetic-ledger/
├── main.py # Entry point; ExtendedCalculator app + Tk mainloop
├── tests/
│     └── test_main.py # Unit tests for expression handling & evaluation
├── .github/
│     └── workflows/
│     └── ci.yml # Lint, format-check, type-check, and test pipeline
├── .env.example # Placeholder for optional future config
├── requirements-dev.txt # ruff, mypy, pytest, black (dev-only)
├── pyproject.toml # ruff/black/mypy configuration
├── .gitignore # Python/venv/IDE ignore rules
├── LICENSE # MIT
└── README.md
```


## Roadmap

1. **Replace `eval()` with an `ast`-based evaluator** — parse the expression
   into an AST and walk only whitelisted node types (`BinOp`, `Num`,
   `UnaryOp`) instead of calling `eval()` at all, closing the remaining
   attack surface even in a sandboxed builtins dict.
2. **Add type stubs and full `mypy --strict` compliance** — the current
   codebase has no type annotations; adding them clarifies the
   `str | int | float` boundary between `self.expression` and evaluated
   results.
3. **Persist history across sessions** — swap the in-memory `list[str]` for
   a small SQLite-backed or JSON-file history log, with an optional
   `--no-history` CLI flag for users who want the current ephemeral
   behavior.
