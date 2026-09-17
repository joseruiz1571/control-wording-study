# Same Control, Different Verdict: Measuring How Control Wording Changes Automated AI Compliance Assessments

Jose Ruiz-Vazquez  
August 2026

*Methods-preprint style study draft. Public study archive. Not a journal article.*

## Abstract

Organizations are starting to use large language models to check whether their AI systems meet security and governance controls, such as those in NIST SP 800-53. These controls are written in plain English, and plain English is imprecise. Two auditors reading the same control can disagree about what it requires. This paper asks a simple question: when an LLM does the reading, how much does the wording of a control change the verdict?

We took 40 controls from NIST SP 800-53 that apply to machine learning systems. For each control, we wrote five versions that a reasonable reviewer would accept as saying the same thing, changing only vocabulary and sentence structure, not meaning. We then ran every version against the same frozen set of evidence — a SageMaker-shaped model-inventory fixture with mixed outcomes — using an automated assessment tool, and recorded the five-way verdict: satisfied, partially-satisfied, not-satisfied, not-applicable, or insufficient-evidence.

Across 200 control–evidence pairs, the 5-way majority verdict changed with the wording in 25.0% of cases (10 of 40 controls). The study had expected controls that contain vague qualifiers to flip more often than controls that name a specific artifact, frequency, or role. The opposite pattern appeared. Qualifier-present controls (vague-qualifier plus mixed) flipped in 2/17 = 11.8% of cases; specific controls flipped in 8/23 = 34.8%; vague-qualifier controls alone flipped in 0/4. A vocabulary-control rewrite of the ten controls that had flipped, using seven editing rules drawn from thesaurus and authority-control practice, reduced the flip rate on those ten from 10/10 to 3/10 (Y = 70% reduction). On the original 40-control denominator the remaining wording variance is X2 = 3/40 = 7.5%.

Control wording is a security-relevant attribute of an automated assessment. That claim does not depend on the qualifier hypothesis, which this dataset does not support. Vocabulary control belongs in control design. The variants, frozen evidence, run logs, and scoring scripts are released with this draft.

## 1. The question

NIST SP 800-53 Revision 5 states security and privacy requirements in English. Those statements are the objects that auditors, GRC tools, and now large language models read. A control that says “log the execution of privileged functions” and a paraphrase that says “record privileged-function execution” will both pass a human meaning-preservation check, yet they are not the same string. If an automated assessor changes its verdict when only the string changes, the wording of the control is doing security-relevant work.

This study measures how often that happens on a frozen evidence target, with a single model, temperature 0, and a human-reviewed set of meaning-preserving paraphrases. A secondary question, posed before the data were scored, was whether controls that contain vague qualifiers — adequate, appropriate, periodically, as needed, and close relatives — would flip more often than controls that name a specific artifact, frequency, or role. That hypothesis is reported as a completed table. It was not supported.

A third question, asked only of the controls that did flip, is whether a rewrite that applies vocabulary-control editing rules reduces flip rate without adding, removing, or weakening requirements.

## 2. Method

### 2.1 Controls

Forty NIST SP 800-53 Rev 5 controls were selected because they apply to a machine-learning system that an automated assessor can actually inspect. Families: AC (8), AU (7), CM (8), RA (2), SA (5), SI (7), SC (2), CA (1). See `controls/SELECTION.md`. Deterministic and attestation controls were excluded; their verdicts are not produced by reading `intent`, so wording cannot change them.

Official v0 wording is the CSRC spreadsheet Control Text (NIST SP 800-53 Rev 5), not mlassure’s adapted fixture intents and not reconstructed OSCAL parameter inserts. `[Assignment:]` and `[Selection:]` blocks are copied verbatim (`controls/SOURCE.md`).

Each of the 40 has five versions (v0 plus four paraphrases). Paraphrases change vocabulary and sentence structure only. They do not add SHALL/MUST, numbers, or roles absent from v0. Review of `controls/control_set.reviewed.csv`: 199 rows marked meaning-preserved `yes`. SI-4.v1 was rewritten after review and remains unmarked, so it is excluded from that control’s variant set for X. Vocab tags on v0: 4 vague-qualifier, 23 specific, 13 mixed. The hypothesis cut is qualifier-present (vague-qualifier + mixed = 17) versus specific (23).

### 2.2 Frozen evidence

Every assessment used one frozen target: `evidence/model-stale.json`, SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`. The file is a copied mlassure SageMaker-shaped fixture (`churn-predictor-v1`) chosen because it has mixed satisfied and not-satisfied conditions, so wording has room to flip. It is not an mltrack bundle; mlassure cannot consume mltrack bundles. One target. The hash was re-verified at scoring and is unchanged through Phase 5.

### 2.3 Assessor, replicas, scoring

Assessments were produced by mlassure (github.com/joseruiz1571/mlassure) with local logging patches 01–05 on branch `study/logging-patches`, base SHA `c9cda3a`. The patches are not pushed; diffs sit in `proposals/`. Wording is `ControlItem.intent`. Verdicts are five-way: satisfied, partially-satisfied, not-satisfied, not-applicable, insufficient-evidence. The model is `claude-sonnet-4-6`. Temperature is 0 on every successful replica.

A 3-way OSCAL fail-closed map is a labeled sensitivity, not the primary outcome: satisfied stays satisfied; not-satisfied stays not-satisfied; insufficient-evidence becomes undetermined; partially-satisfied and not-applicable become not-satisfied.

Each variant was assessed three times. Scoring uses the last successful jsonl record per `variant_id`+`replica`. Failed credit-crash rows are ignored. Majority is the unique status with count ≥ 2 among three replicas; a 1-1-1 triple is labeled `split`. A control flips when its scored variant majority verdicts are not all identical. Primary X is flipped controls / 40. SI-4 contributes using v0, v2, v3, v4 only.

Phase 3 produced 600 unique successful replicas (200 variants × 3). An earlier 593 jsonl rows were credit-crash failures, retried, and ignored for scoring. Tables are rebuilt from those frozen logs by `analysis/score.py`, not from a live 741-run re-assessment.

### 2.4 Rewrite test

Seven editing rules (R1–R7), documented in `phase5/RULES.md`, were applied only to the ten controls that flipped — not to all 40. The rules do not add, remove, or weaken requirements and do not inject fixture artifact names into control text. Sources actually retrieved: ANSI/NISO Z39.19-2005 (R2010), ISO 25964-1:2011, IFLA GARR 2nd ed. 2001, and IFLA ICP 2016. Review of 50 rewritten rows: 47 `yes`, 3 `unsure` (`AC-6(9).r4`, `AU-8.r4`, `CM-2.r4`). Unsure rows are excluded from Y. The remaining 47 variants × 3 replicas produced 141 successful assessments and 0 failures.

Y is the reduction in flip rate on the ten treated controls: (10 − n_flipped_after) / 10. Before rewrite, all ten flipped. X2 is n_flipped_after / 40, counting the 30 untreated controls as still non-flipping.

## 3. Results

### 3.1 Census, noise, and primary X

Of 600 replica judgments: 454 not-satisfied, 132 partially-satisfied, 10 satisfied, 4 insufficient-evidence, 0 not-applicable. Model noise: 32/200 = 16.0% of variants were not unanimous (31 two-one; 1 split, `CM-2.v4`). Temperature was 0 on every success.

X = 10/40 = 25.0%. Dropping SI-4 entirely (X_39) is 10/39 = 25.6%. SI-4 itself does not flip: the four scored variants are all not-satisfied. The ten flipped controls: AC-6(9), AU-8, CM-2, CM-3, CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), SI-2. Paraphrase-versus-v0: 22 of 159 meaning-preserved paraphrases (13.8%) differ from that control’s v0 majority. All 22 sit inside the ten flipped controls.

### 3.2 Hypothesis table

The brief expected qualifier-present controls to flip most and specific controls to flip least. The table goes the other way.

| vocab_pattern | n controls | n flipped | flip rate |
| --- | --- | --- | --- |
| vague-qualifier | 4 | 0 | 0/4 = 0.0% |
| mixed | 13 | 2 | 2/13 = 15.4% |
| specific | 23 | 8 | 8/23 = 34.8% |
| qualifier-present (vague-qualifier + mixed) | 17 | 2 | 2/17 = 11.8% |

Vague-qualifier alone is 0/4 (AC-6, RA-7, SA-8(32), SI-12). Mixed flips are CM-2 and SA-4(8). Specific flipped more often than qualifier-present in this 40-control set. The qualifier hypothesis is not supported. This paper does not claim it was confirmed, qualified, or directionally right. The reverse table is the result.

### 3.3 Three-way sensitivity

After the fail-closed map, X = 2/40 = 5.0%. Only AC-6(9) and AU-8 move satisfied ↔ not-satisfied. Most 5-way flips are not-satisfied ↔ partially-satisfied, plus one split. Those collapse under OSCAL fail-closed mapping. 3-way noise is 9/200 = 4.5%. 3-way paraphrase-versus-v0 is 6/159 = 3.8%. If a downstream program treats partially-satisfied as “the control is not met,” eight of the ten 5-way flips are operationally silent. Primary X keeps the five-way enum the tool actually emits.

### 3.4 Y and X2

Before rewrite, all ten treated controls flipped. After rewrite, three still flip: AU-8, CM-2, and CM-3. Seven no longer flip: AC-6(9), CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), and SI-2.

| control_id | n scored after review | flipped after? | majorities |
| --- | --- | --- | --- |
| AC-6(9) | 4 | no | 4× partially-satisfied |
| AU-8 | 4 | yes | satisfied / partially-satisfied / partially-satisfied / satisfied |
| CM-2 | 4 | yes | partially-satisfied / split / partially-satisfied / split |
| CM-3 | 5 | yes | not-satisfied / not-satisfied / partially-satisfied / not-satisfied / not-satisfied |
| CM-3(1) | 5 | no | 5× not-satisfied |
| CM-3(2) | 5 | no | 5× not-satisfied |
| CM-8(1) | 5 | no | 5× not-satisfied |
| SA-10 | 5 | no | 5× not-satisfied |
| SA-4(8) | 5 | no | 5× not-satisfied |
| SI-2 | 5 | no | 5× not-satisfied |

Y = 70.0% reduction (10/10 before, 3/10 after). X2 = 3/40 = 7.5%. Phase 5 replica census (141): 90 not-satisfied, 40 partially-satisfied, 8 satisfied, 3 insufficient-evidence. Model noise on the rewritten set is 19/47 = 40.4% (2 splits, both on CM-2). That is higher than Phase 3 noise (16.0%). Y is a reduction in majority-verdict wording variance; the noise rate is reported beside it, not folded into it.

## 4. Rewriting rules

The seven rules are a librarian’s toolkit, not a claim that vague qualifiers caused the flips. R1 locks a preferred term so near-synonyms (log / record / capture) are not substituted in the rewritten base. R2 names the implied evidence object as a count noun already present in the control. R3 factors compound actions into separately assessable clauses. R4 scopes a class term with the control’s own words. R5 states OR-alternatives as a closed one-or-more selection. R6 names both ends of an associative hedge such as “consistent with,” keeping the relation rather than deleting it. R7 treats lettered clauses as discrete authorised headings and copies every `[Assignment:]` and `[Selection:]` block verbatim.

Citations are to sources actually retrieved: ANSI/NISO Z39.19-2005 (R2010) on preferred terms, count nouns, and associative relationships; ISO 25964-1:2011 on concepts and splitting compound terms; IFLA GARR (2nd ed., 2001) on authorised headings; IFLA ICP (2016) on consistent authorized access points. The rules do not add completeness words, fixture names, SHALL/MUST, or new numbers and roles. Before/after examples are in `phase5/RULES.md`. This section does not reprint the seven rules in full.

## 5. Discussion

Control wording moved the 5-way majority on a quarter of this set. That is enough to treat wording as a security-relevant attribute of a control. The mechanism is not the one the study expected. Specific controls flipped more than qualifier-present controls; vague-qualifier controls did not flip at all. A plausible reading, not a confirmed finding, is that specific statements give the model more surface to synonymize. Reporting the reverse table honestly is the result.

The 5-way versus 3-way gap matters for anyone who will consume OSCAL. Eight of ten flips live in not-satisfied ↔ partially-satisfied. Fail-closed mapping hides them. Primary X keeps the native enum. The sensitivity is reported so a reader who must fail-close can see the 2/40 figure.

The rewrite reduced majority flips on the treated ten from ten to three. Noise rose: 40.4% of rewritten variants were not unanimous, versus 16.0% in Phase 3. Possible causes include a harder set, longer factored sentences, and the three unsure paraphrases. The study cannot separate those. Y is not “the model became more stable”: majority votes aligned across paraphrases, while replica noise rose. Remaining flips are AU-8, CM-2, and CM-3.

Limitations are binding. One fixture, one model, forty controls. SI-4.v1 is a hole in that control’s paraphrase set; it does not change X, because the four scored SI-4 variants already agree. Three rewritten paraphrases were excluded as unsure, so AC-6(9), AU-8, and CM-2 are scored on four variants rather than five. mlassure patches are local and unpushed. Temperature 0 does not imply determinism; 16.0% Phase 3 noise is the measurement. Results are not a ranking of NIST families, not a claim about other assessors, and not a catalog rewrite. They are a measurement on one frozen target.

## 6. Recommendations

1. Treat control wording as a testable attribute when an LLM is the reader. Pin the official statement. Do not silently substitute a vendor’s adapted intent for the catalog text.
2. Prefer vocabulary control in control design: one preferred term per required action or object; named count-noun artifacts; factored compound actions; closed selections; explicit associative links. That is thesaurus practice, not a substitute for a testable requirement.
3. Do not assume that stripping vague qualifiers will stabilize automated verdicts. It did not in this set, because the qualifier-tagged controls were not the ones that flipped.
4. Report 5-way and 3-way side by side if the downstream consumer is OSCAL. Do not collapse partial into fail before measuring wording variance.
5. Keep meaning-preservation review as a human gate. Unsure rows are excluded, not recoded as yes.

## Data availability

Variants, YAML, frozen evidence, jsonl logs, scoring scripts, and this draft live in this repository. Tables are rebuilt from the frozen logs with `python3 analysis/score.py` from the repository root (Python 3.10+, standard library only). That command re-verifies the evidence hash and recomputes X, Y, X2, and noise; it does not call an LLM and does not run mlassure. Live re-assessment needs a patched mlassure clone and an Anthropic API key; it is out of scope for the table rebuild. Official NIST control text is a U.S. government work. Other study artifacts are offered under CC-BY-4.0. This repository is a public study archive in methods-preprint style; it is not a journal article.

## References

ANSI/NISO. 2010. *Guidelines for the Construction, Format, and Management of Monolingual Controlled Vocabularies.* ANSI/NISO Z39.19-2005 (R2010). Baltimore: National Information Standards Organization.

IFLA. 2001. *Guidelines for Authority Records and References* (GARR). 2nd ed. UBCIM Publications New Series Vol. 23.

IFLA. 2016. *Statement of International Cataloguing Principles* (ICP). 2016 edition with minor revisions 2017.

ISO. 2011. *Information and documentation — Thesauri and interoperability with other vocabularies — Part 1: Thesauri for information retrieval.* ISO 25964-1:2011.

National Institute of Standards and Technology. *Security and Privacy Controls for Information Systems and Organizations.* NIST SP 800-53 Revision 5. Official v0 wording from the CSRC control-catalog spreadsheet.

Ruiz-Vazquez, Jose. mlassure. https://github.com/joseruiz1571/mlassure.
