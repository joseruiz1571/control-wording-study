# Second assessor, same strings

Same 200 control strings. Same frozen evidence. A different kind of assessor. The verdicts moved again, in a different place.

My first lab note covered forty official NIST SP 800-53 Rev 5 statements, four meaning-preserving paraphrases each, one frozen evidence fixture, and a 5-way majority verdict that moved on ten of the forty when only the wording moved. I closed it by saying the results were not a claim about a second model. This is the second model. It is a methods note, not a ranking.

## What I ran

The second assessor is Jev, from TypeSafe. It is not a chat model. You send it a state and a typed question, and it returns a choice with a probability for every option. It writes no rationale. I asked it one question per call: which of the five mlassure statuses fits this control statement against this evidence.

Same 40 controls, same 5 variants, same SI-4.v1 exclusion, same flip definition, same evidence hash, SHA-256 `bded936e...12de`. Five replicas per variant instead of three. 1,000 calls, 1,000 successful, every one resolved to `jev-1.13.0`.

This is a different assessor architecture. Sonnet ran inside mlassure's agent loop and called collectors. Jev got the collector output serialized into the question. So the comparison is between two ways of assessing, not between two models in one pipeline.

## The first run was wrong, and the number looked fine

The first run of this sequel attached the same two CloudTrail events to every call, whatever collectors the control declared. Thirty-five of forty controls were judged on evidence that was missing. It returned a flip rate of 12.5% and looked like a result.

Two things gave it away. Jev said insufficient-evidence on 51% of calls where Sonnet had said it on 0.7%. And the input size of every call tracked the length of the control text and nothing else, which cannot happen if the evidence varies by control.

I rebuilt the serializer so each control carries exactly what Sonnet retrieved for it in Phase 1, and logged the full request body on every row. Zero payload mismatches across 1,000 requests. The numbers below are from that run only. My first lab note said the log can verify a verdict on a string plus a hash. The hash was right on every call of the bad run. The hash was of the file, not of what was sent.

## Findings

**1. X = 6/40 = 15.0%.** Six controls change 5-way majority under paraphrase: AC-6(5), AC-6(9), AU-6, AU-12(1), SA-4(8), SI-12. Sonnet's X was 10/40 = 25.0%. Six against ten out of forty is not a distinguishable difference (Fisher exact, p = 0.40). I am not going to write the sentence that says one assessor is more stable.

**2. The two assessors flip different controls.** Only AC-6(9) and SA-4(8) flip under both. The union is fourteen. Whatever is fragile here is not simply a property of the control text. It belongs to the pair: this string, this assessor.

**3. Each assessor has its own fragile boundary.** Sonnet's flips were almost all not-satisfied against partially-satisfied. Five of Jev's six are a verdict against insufficient-evidence: the wording decides whether it commits or abstains. Jev abstained on 27.7% of calls with the same evidence in hand, and on eight controls it abstained under every wording. In 56 of the 73 cells where the two majorities disagree, Sonnet gives a verdict and Jev declines to.

That changes the sensitivity table. Under the fail-closed 3-way map from the first note, Sonnet's X fell from 25.0% to 5.0%, because its movement collapsed into not-satisfied. Jev's X stays at 6/40 under the same map, because undetermined survives it. Under a strict binary, where only satisfied counts, Jev is 1/40 and Sonnet 2/40. The enum you persist still decides how much movement lands in the artifact. It decides it differently for each assessor.

**4. The probabilities pointed at the fragile controls in advance.** Take only the official wording, five calls per control. Measure the gap between Jev's top two status probabilities and rank the forty controls from smallest gap up. The six that flip sit at ranks 1, 2, 3, 5, 6, and 7. AUC 0.985. It holds when a flip is defined on the paraphrases alone, so the official wording is not predicting itself.

**5. That signal does not transfer.** The same ranking puts Sonnet's ten flipped controls at 3, 6, 13, 14, 16, 32, 36, 37, 38, and 40. AUC 0.40. Jev's uncertainty tells you where Jev is fragile. It does not tell you which control statements are fragile for another assessor. I could not run the mirror test, because the Phase 1 logs carry no probabilities for Sonnet.

Noise: 14/200 = 7.0% of variants were not unanimous across five replicas.

## Limitations

One fixture. Forty controls. One version of each assessor. Six positives behind finding 4, no held-out set, and the ranking was measured on the same run that defined the flips. No human gold label, so nothing here says which assessor was right on the 73 cells where they disagree, including whether abstaining was the better answer. The question wording I gave Jev is itself a string, fixed once and not varied. Runner, scorer, and all 1,000 logged requests are in the study repo under `second-assessor/`, with the invalid first run kept beside them.

What I will keep doing: log the request that was actually sent, next to the hash of the file it was built from. And when an assessor can return a probability, keep it. On this fixture it was the cheapest check I ran.

## Files

- `RESULTS.md`: the numbers on one page.
- `run_jev.ts`, `score_jev.ts`: runner and scorer (bun). The runner needs `TYPESAFE_API_KEY` in the environment. The scorer reproduces the invalid first run's 5/40 and 14/200 exactly.
- `runs/full.jsonl`: 1,000 rows, each with the full request body that was sent. `runs/full_score.json`: scored and paired against Phase 1.
- `runs/smoke.jsonl`, `runs/probe.jsonl`: the checks run before the full matrix.
- `runs-v1-invalid/full.jsonl`: the first run, kept as the record of the serializer bug.

This folder is a sequel. `phase2-report.md` at the repo root is Phase 2 of the original study and is unrelated.
