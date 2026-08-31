# Control-Wording Variance Study — Phase 5 report

## What I did

Jose accepted X = 10/40 = 25.0% and scoped Phase 5 to the 10 flipped controls (not all 40). The qualifier-present vs specific hypothesis was not supported, so I did not write rules as if vague-qualifier wording caused flips. I retrieved ANSI/NISO Z39.19-2005 (R2010), ISO 25964-1:2011 (SIST preview identical to the 2011 edition), IFLA GARR 2nd ed. 2001, and IFLA ICP 2016, and proposed seven editing rules (R1–R7) that reduce hedge-room on the 10 official v0 statements (undefined class, compound unseparated actions, unnamed evidence objects, unspecified associative links) without adding, removing, or weakening requirements. I applied those rules only to the 10 bases, wrote four Phase-2-style paraphrases of each rewritten base (IDs `.r0`–`.r4`), left `meaning_preserved` empty for Jose, retagged `vocab_pattern` on rewritten r0, and did not modify frozen evidence, spend API money, push, rerun mlassure, or start Phase 6.

## Artifacts

- `/workspace/control-wording-study/phase5/RULES.md`
- `/workspace/control-wording-study/controls/control_set_rewritten.csv` (50 rows: 10 bases × 5 variants)
- `/workspace/control-wording-study/controls/yaml_rewritten/` (50 YAML files, same schema as `controls/yaml`)
- `/workspace/control-wording-study/DECISIONS.md` (Phase 5 proposal section appended)
- `/workspace/control-wording-study/phase5-report.md` (this file)
- Inputs (unmodified): `controls/control_set.reviewed.csv`, `RESULTS.md`, `analysis/tables.json`, `evidence/model-stale.json` SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`

## Judgment calls

- Rules target the 10 that flipped, not the qualifier-tagged set. Specific flipped more (8/23 vs 2/17); vague-qualifier was 0/4.
- Prefer tightening reference (preferred term, named object already in the control, split of an existing AND) over new obligations. No CloudTrail/registry/monitor names in control text.
- Most flips were `not-satisfied` ↔ `partially-satisfied`; R3 (factor compound actions) and R5 (closed OR) are aimed at that hedge, not at manufacturing `satisfied`.
- vocab_pattern on rewritten r0: 8 specific / 2 mixed (CM-2, SA-4(8)). Mixed stays mixed because “consistent with” and circumstances-require were kept.
- Paraphrases follow Phase 2 (vocab/structure; Assignment/Selection verbatim; no SHALL/MUST). None marked `unsure`. `meaning_preserved` blank.
- Y and X2 are defined, not computed. No rerun in this phase.

## Questions (batched)

**(i) Accept the seven rules (R1–R7) as the Phase 5 editing set?**
Recommended answer: **yes.** They are grounded in Z39.19 / ISO 25964 / GARR / ICP citations actually retrieved, and each has a before/after from one of the 10 official v0 statements. They do not claim the qualifier hypothesis was supported.

**(ii) Accept rewriting only these 10, not the other 30?**
Recommended answer: **yes.** That is Jose’s scope. The other 30 did not flip; rewriting them would confound Y.

**(iii) Accept Y = reduction in flip rate on these 10 after review+rerun, and X2 = (flips remaining in the 10 + 0 from the other 30)/40 as secondary?**
Recommended answer: **yes.** Y is the rewrite test. X2 puts the rewrite back on the original 40-control denominator without pretending the untouched 30 were re-tested.

**(iv) Leave `meaning_preserved` empty and wait for Jose to mark the rewritten CSV before any mlassure rerun?**
Recommended answer: **yes.** Same gate as Phase 2. Do not spend API budget on unmarked paraphrases.

**(v) Accept the vocab_pattern retags (8 specific / 2 mixed) on rewritten r0?**
Recommended answer: **yes.** Same tagging rule as Phase 2. CM-2 and SA-4(8) remain mixed because R6 names both ends of an existing hedge rather than deleting it.

## What I will do next if Jose says nothing

WAIT. Do not rerun mlassure until he returns `controls/control_set_rewritten.csv` with `meaning_preserved` filled. Do not start Phase 6. Do not spend API budget. Do not push.
