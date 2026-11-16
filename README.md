# Data Analyst Agent

An agent that answers plain-English questions over a SQL database: it explores
the schema, writes and runs SQL, fixes its own errors, and returns the answer
with the query behind it.

Status: Phase 0 (walking skeleton). The full plan is in [docs/plan.md](docs/plan.md).

## Results

No numbers yet. The baseline lands in Phase 1.

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync            # create .venv and install dependencies
uv run pytest      # run tests
uv run ruff check .
```

## Credits

Evaluation data: [BIRD Mini-Dev](https://github.com/bird-bench/mini_dev), CC BY-SA 4.0.
