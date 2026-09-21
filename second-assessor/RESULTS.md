# Second assessor: Jev on the same strings, matched evidence (2026-09-21)

Sequel to the Phases 0 to 6 study. Nothing in those phases was changed. (Not to be confused with `phase2-report.md`, which is Phase 2 of the original study.)

## What ran

- Assessor: TypeSafe Jev, `jev-latest` resolved to `jev-1.13.0` on all 1000 calls, TypeSafe direct.
- Same 40 controls x 5 variants as Phase 1 (`controls/control_set.accepted.csv`), 5 replicas each, 1000/1000 ok (one socket error, retried). Estimated spend $0.145.
- Evidence per control equals Phase-1 `retrievedEvidence` for that control (constant across all 600 Sonnet runs). Check: 0 payload mismatches across 1000 logged request bodies. RA-3 and SA-8(32) carry one item with `payload: null`, because `getModelCard` returned null to Sonnet too.
- Question: one typed `choice` over the five mlassure statuses, wording fixed (`second-assessor/run_jev.ts`). A second self-rated confidence question is sent for parity with the first run and ignored in analysis.
- This is a different assessor architecture (typed question, no agent loop), not "one more model in mlassure."
- Scoring matches Phase 1: 5-way majority, SI-4.v1 out of the flip denominator. `second-assessor/score_jev.ts` reproduces the first run's 5/40 and 14/200 exactly.

## The first run is invalid

`runs-v1-invalid/full.jsonl` attached the same two CloudTrail events to every call regardless of declared collectors. Input size there is explained by control-text length alone (R2 0.98). 35 of 40 controls were judged on missing evidence. Its 12.5% is not comparable to anything.

## Numbers

| | Jev (this run) | Sonnet (Phase 1) |
| --- | --- | --- |
| X, controls that flip | 6/40 = 15.0% | 10/40 = 25.0% |
| Noisy variants | 14/200 = 7.0% (5 replicas) | 32/200 = 16.0% (3 replicas) |
| insufficient-evidence share | 277/1000 = 27.7% | 4/600 = 0.7% |
| Controls abstaining on all variants | 8 | 0 |

- 6 vs 10 of 40 is not a distinguishable difference (Fisher exact p is about 0.4). Do not rank the models on it.
- Cell agreement, majority vs majority: 126/199 = 63.3%. On v0 alone: 24/40. Of 73 disagreeing cells, 56 are Sonnet giving a verdict where Jev abstains.
- Flip overlap: AC-6(9) and SA-4(8). Union is 14 controls.
- Jev flips: AC-6(5), AC-6(9), AU-6, AU-12(1), SA-4(8), SI-12. Five of the six are commit vs abstain. Only AC-6(9) moves between two substantive verdicts. Sonnet's flips are almost all not-satisfied vs partially-satisfied. Each assessor has its own fragile boundary.
- Vocab cut (Jev): specific 3/23, mixed 2/13, vague-qualifier 1/4. No pattern.

## The result that is new

Jev returns a probability per status. Take the gap between its top two statuses on the original wording only (v0, 5 calls per control) and rank the 40 controls from smallest gap up. The six controls that flip sit at ranks 1, 2, 3, 5, 6, 7. AUC 0.985. The same holds when "flip" is defined on the paraphrases alone (v1 to v4), so v0 is not predicting itself.

Plainly: on this fixture, about $0.03 of calls on the official wording pointed at the controls whose verdict would move under paraphrase.

Limits: six positives, one fixture, one model version, no held-out set, and it predicts Jev's own flips, not Sonnet's.

It does not transfer. The same Jev v0 gap ranks Sonnet's 10 flipped controls at 3, 6, 13, 14, 16, 32, 36, 37, 38, 40 (AUC 0.40, no better than chance). The signal tells you where Jev is fragile, not where the control text is fragile for any assessor.

## Open

- Does the ranking hold on the Phase-5 rewritten controls?
- Would Sonnet's own token-level uncertainty predict Sonnet's flips the same way? Not testable from the Phase-1 logs.
