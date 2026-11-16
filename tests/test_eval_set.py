"""Guards the frozen eval sets: sizes, no leakage between dev and test, databases present."""

import json
from pathlib import Path

DATA = Path("evals/data")
DATABASES = Path("data/databases")


def load(name: str) -> list[dict]:
    lines = (DATA / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


def ids(rows: list[dict]) -> set[str]:
    return {r["question_id"] for r in rows}


def test_set_sizes():
    assert len(ids(load("test"))) == 100
    assert len(ids(load("dev"))) == 30
    assert len(ids(load("smoke"))) == 20


def test_dev_and_test_do_not_overlap():
    assert ids(load("dev")).isdisjoint(ids(load("test")))


def test_smoke_is_a_subset_of_test():
    assert ids(load("smoke")) <= ids(load("test"))


def test_every_question_is_complete_and_has_its_database():
    for row in load("test") + load("dev"):
        assert row["question"].strip()
        assert row["SQL"].strip()
        db = row["db_id"]
        assert (DATABASES / db / f"{db}.sqlite").is_file()
