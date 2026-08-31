# Control-Wording Variance Study — Phase 2 report

## What I did

Fetched NIST SP 800-53 Rev 5 OSCAL JSON and the CSRC official control-catalog spreadsheet on 2026-08-29, and copied v0 statements from the spreadsheet (control statement or enhancement statement, whitespace-normalized only). Selected 40 bases the frozen SageMaker fixture can actually inform, using only synthesis, sufficiency, or correlation and the nine existing collectors. Wrote four meaning-preserving paraphrases per base (200 rows), left `meaning_preserved` empty for Jose, and did not modify `evidence/model-stale.json`, spend API money, push, or start Phase 3.

## Artifacts

- `/workspace/control-wording-study/controls/control_set.csv`
- `/workspace/control-wording-study/controls/SELECTION.md`
- `/workspace/control-wording-study/controls/SOURCE.md`
- `/workspace/control-wording-study/DECISIONS.md` (Phase 2 section appended)
- `/workspace/control-wording-study/phase2-report.md` (this file)
- Frozen evidence (unmodified): `/workspace/control-wording-study/evidence/model-stale.json` SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`

## Judgment calls

- Excluded SC-28 and SC-7 (and any attestation control) because those paths never let wording change the verdict; included SC-28(1) and SC-7(5) as sufficiency instead.
- Used official catalog prose, not mlassure `intent`; dropped SI-6(1) (withdrawn) and AU-12(3) (official text is not what the fixture can assess).
- Tagged SA-10 as correlation from registry+CloudTrail, not attestation.
- Kept RA-3/SA-8(32) on getModelCard=null because absence can still flip insufficient-evidence vs not-satisfied; rejected PE/PS/RA-5 and other no-signal families.
- Recorded vocab_pattern as 4 vague-qualifier / 23 specific / 13 mixed rather than forcing 14/14/12.

## Questions

**(i) Accept 4/23/13 vocab mix instead of 14/14/12?**
Recommended answer: **yes.** Rev 5 statements that are fixture-mappable almost never have a qualifier without also naming a frequency, role, or artifact. Forcing 14 pure-vague would mis-tag mixed rows or pull in *-1 policy controls the fixture cannot assess.

**(ii) Keep RA-3 and SA-8(32) even though getModelCard returns null?**
Recommended answer: **yes.** The collector returning null is usable evidence of absence; wording can still move the five-way verdict. Drop them only if Jose wants zero null-card rows.

**(iii) Keep CA-7 (outside the favor-list) and the two SC enhancements?**
Recommended answer: **yes** for CA-7 (monitors/capture map directly). **yes** for SC-28(1) and SC-7(5) as the encryption/network sufficiency counterparts of the excluded deterministic bases. Do not add SC-28 or SC-7.

**(iv) Is official AC-6(9) ("Log the execution of privileged functions") acceptable in place of mlassure's least-privilege rewrite?**
Recommended answer: **yes.** The study hypothesis is about official wording. CloudTrail can assess the official statement. Least privilege is already covered by AC-6 / AC-6(5) / AC-6(10).

## What I will do next if Jose says nothing

Wait. Do not start Phase 3 until he returns the reviewed CSV (`meaning_preserved` filled yes/no). Do not send the CSV to Jose from this phase. Do not spend API budget.
