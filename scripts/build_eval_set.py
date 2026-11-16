"""Build the frozen eval sets from BIRD Mini-Dev (2026 revision).

Run once; the output files are committed and never change:

    uv run python scripts/build_eval_set.py

Input:  data/raw/hf/data/mini_dev_sqlite.jsonl (downloaded from Hugging Face, not in git)
Output: evals/data/test.jsonl   100 questions, for reported numbers only
        evals/data/dev.jsonl     30 questions, for prompt iteration and failure analysis
        evals/data/smoke.jsonl   20 questions, a fixed subset of test, for the PR check
        evals/data/manifest.json how the sets were made
"""

import hashlib
import json
import random
from pathlib import Path

SOURCE = Path("data/raw/hf/data/mini_dev_sqlite.jsonl")
# Pinned so a different revision of the benchmark fails loudly instead of
# silently producing different sets.
SOURCE_SHA256 = "926af2a0d1b47e5d0d15a7aa8a34d4721007f4550a881555b6a89496b54a2606"
OUT_DIR = Path("evals/data")
SEED = 42

# Questions per database: (test, dev, smoke). Smoke is drawn from test.
PLAN = {
    "formula_1": (25, 8, 5),
    "student_club": (25, 7, 5),
    "superhero": (25, 7, 5),
    "thrombosis_prediction": (25, 8, 5),
}


def load_source() -> list[dict]:
    raw = SOURCE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise SystemExit(f"{SOURCE} has sha256 {digest}, expected {SOURCE_SHA256}")
    return [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]


def split(rows: list[dict]) -> dict[str, list[dict]]:
    rng = random.Random(SEED)
    sets: dict[str, list[dict]] = {"test": [], "dev": [], "smoke": []}
    for db, (n_test, n_dev, n_smoke) in PLAN.items():
        # Sort first so the result depends only on the seed, not on file order.
        pool = sorted((r for r in rows if r["db_id"] == db), key=lambda r: int(r["question_id"]))
        rng.shuffle(pool)
        test, dev = pool[:n_test], pool[n_test : n_test + n_dev]
        if len(test) + len(dev) != n_test + n_dev:
            raise SystemExit(f"{db}: only {len(pool)} questions, need {n_test + n_dev}")
        sets["test"] += test
        sets["dev"] += dev
        sets["smoke"] += test[:n_smoke]
    return sets


def write(sets: dict[str, list[dict]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, rows in sets.items():
        rows.sort(key=lambda r: int(r["question_id"]))
        lines = [json.dumps(r, ensure_ascii=False) for r in rows]
        (OUT_DIR / f"{name}.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
        )
    manifest = {
        "source": "BIRD Mini-Dev, 2026 revision (Hugging Face birdsql/bird_mini_dev)",
        "source_file": "data/mini_dev_sqlite.jsonl",
        "source_sha256": SOURCE_SHA256,
        "license": "CC BY-SA 4.0",
        "seed": SEED,
        "per_database": {
            db: {"test": n_test, "dev": n_dev, "smoke": n_smoke}
            for db, (n_test, n_dev, n_smoke) in PLAN.items()
        },
        "counts": {name: len(rows) for name, rows in sets.items()},
    }
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    result = split(load_source())
    write(result)
    for set_name, set_rows in result.items():
        print(f"{set_name}: {len(set_rows)} questions")
