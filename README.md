# Data Analyst Agent

An agent that answers plain-English questions over a SQL database: it explores
the schema, writes and runs SQL, fixes its own errors, and returns the answer
with the query behind it.

Status: Phase 0 (walking skeleton). The full plan is in [docs/plan.md](docs/plan.md).

## Results

No numbers yet. The baseline lands in Phase 1.

## Eval set

Questions come from the 2026 revision of BIRD Mini-Dev, over four of its SQLite
databases (`data/databases/`). The sets in `evals/data/` are frozen:

| File | Questions | Used for |
| --- | --- | --- |
| `test.jsonl` | 100 | Reported numbers only |
| `dev.jsonl` | 30 | Prompt iteration and failure analysis |
| `smoke.jsonl` | 20 (subset of test) | Regression check on every PR |

How and why they were chosen: [docs/decisions/0001-eval-set.md](docs/decisions/0001-eval-set.md).

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync            # create .venv and install dependencies
uv run pytest      # run tests
uv run ruff check .
```

Start the API and check it:

```
uv run uvicorn app.main:app --reload
curl http://localhost:8000/health
```

Or run it in Docker, the same way production does:

```
docker compose up --build
```

## Credits

Evaluation data: [BIRD Mini-Dev](https://github.com/bird-bench/mini_dev), CC BY-SA 4.0.
