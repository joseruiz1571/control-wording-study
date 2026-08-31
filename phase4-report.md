# Control-Wording Variance Study — Phase 4 report

## What I did

Scored the completed Phase 3 jsonl (last successful record per variant_id+replica; 593 credit-crash rows ignored) against `controls/control_set.reviewed.csv`, and re-verified frozen evidence SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`. Asserted 600 unique successful keys, temperature 0, model `claude-sonnet-4-6`, and three replicas on every variant. Computed 5-way majority, model noise, primary X with SI-4.v1 excluded (SI-4 uses v0,v2,v3,v4 only), X_39, vocab-pattern and qualifier-present tables, paraphrase-vs-v0, and the 3-way OSCAL fail-closed sensitivity. Wrote `analysis/score.py`, `RESULTS.md`, and `analysis/tables.json`; appended a Phase 4 section to `DECISIONS.md`. Did not modify the frozen evidence file, spend API money, push, or start Phase 5.

## Artifacts

- `/workspace/control-wording-study/analysis/score.py` (re-runnable: `python3 analysis/score.py` from the study root)
- `/workspace/control-wording-study/RESULTS.md`
- `/workspace/control-wording-study/analysis/tables.json`
- `/workspace/control-wording-study/DECISIONS.md` (Phase 4 section appended)
- `/workspace/control-wording-study/phase4-report.md` (this file)
- Inputs (unmodified): `runs/phase3.jsonl`, `controls/control_set.reviewed.csv`, `evidence/model-stale.json` + `evidence/HASH.txt`

## Judgment calls

- Last-successful jsonl record wins; credit-crash failures are ignored, not treated as verdicts.
- SI-4.v1 is excluded from X / vocab flip / paraphrase-vs-v0 (unmarked rewrite); it remains in the 600-row census and the 200-variant noise denominator.
- Majority is unique status with count ≥2; the one 1-1-1 (`CM-2.v4`) is labeled `split`.
- 5-way is the headline; 3-way maps replica verdicts first, then recomputes majority and X (so `CM-2.v4` ceases to be split).
- Qualifier-present vs specific is a completed table, not a confirm/reject claim; specific flipped more (8/23 vs 2/17).
- Y is a placeholder; Phase 5 rewriting is not started.

## Questions (batched)

**(i) Accept X = 10/40 = 25.0% as the primary wording-variance rate?**
Recommended answer: **yes**, with X_39 = 10/39 = 25.6% and 3-way X = 2/40 = 5.0% reported beside it. SI-4.v1 exclusion does not change X (SI-4 does not flip on the four scored variants).

**(ii) Keep 5-way as the study claim, or switch the headline to 3-way fail-closed (2/40)?**
Recommended answer: **keep 5-way primary.** The runs logged five-way on purpose. Eight of the ten flips stay inside `not-satisfied` / `partially-satisfied` / `split`; only AC-6(9) and AU-8 move `satisfied`. That is wording variance even if OSCAL collapses the first group. 3-way remains the labeled sensitivity.

**(iii) Proceed to Phase 5 given that specific flipped more than qualifier-present (8/23 vs 2/17)?**
Recommended answer: **proceed only to rewrite the 10 flipped controls if Jose wants Phase 5**, and do not claim the qualifier hypothesis was supported. Vague-qualifier is 0/4. Target AC-6(9), AU-8, CM-2, CM-3, CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), SI-2 — not the qualifier-tagged set.

**(iv) SI-4.v1 is still unmarked. Mark it, leave it excluded, or drop SI-4?**
Recommended answer: **leave it excluded** until Jose marks the row. Its three replicas are unanimous `not-satisfied`, matching v0/v2/v3/v4, so marking `yes` would not change X. Dropping SI-4 is X_39 = 10/39 = 25.6%.

**(v) Model noise is 16.0% at temperature 0. Add replicas, or keep majority-of-3?**
Recommended answer: **keep majority-of-3.** The protocol is locked. Report the 32/200 noise; do not rerun or spend more API money.

## What I will do next if Jose says nothing

Wait. Do not start Phase 5 rewriting until he accepts X or asks to proceed.
