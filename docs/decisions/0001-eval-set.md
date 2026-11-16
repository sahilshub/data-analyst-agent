# 0001: Eval set from the 2026 revision of BIRD Mini-Dev

Date: 2026-11-16 · Phase 0

## Decision

- Questions come from the 2026 revision of BIRD Mini-Dev (Hugging Face
  `birdsql/bird_mini_dev`), not the original release.
- Four databases: `formula_1`, `student_club`, `superhero`, `thrombosis_prediction`
  (33 MB in total), committed to the repo under `data/databases/`.
- 100 test and 30 dev questions, sampled evenly across the four databases with a
  fixed seed. The 20 smoke questions are a fixed subset of the test set.

## Why

- The revision corrects reference queries and removes hints that gave away tables
  or answers, so a wrong answer is far more likely to be the agent's fault than
  the benchmark's. That keeps failure analysis honest.
- The four databases are the small ones with enough questions (228 between them).
  The largest BIRD databases are 260 to 600 MB: too big for git and for a 1 GB server.
- Committing the databases means CI and the Docker build need no download step.
- Smoke is drawn from test, not dev, so the PR check previews the full run and the
  dev set stays free for prompt iteration.

## What this changes from the plan

The plan said to balance the test set across difficulty labels. In the 2026
revision 460 of the 500 questions are labelled challenging (94 of our 100), so
that is not possible. The sets are balanced across databases instead, and
difficulty is kept as a recorded field.

## Trade-offs

- Scores will be low. The maintainers' fixed-prompt baselines on the SQLite
  questions range from 21% to 90% depending on the model.
- Numbers are not comparable with papers that used the original Mini-Dev.
- The smoke run touches test questions on every PR. It is used only as a
  regression check, never to tune prompts.

## Checks done

All 228 reference queries for the four databases were run against the committed
SQLite files: none failed and none returned an empty result.
