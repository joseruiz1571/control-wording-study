# Control-Wording Variance Study — results (Phases 4 and 5)

**X = 10/40 = 25.0%** (primary, 5-way majority; SI-4 scored on v0,v2,v3,v4 only).

**Y = 70.0%** reduction in flip rate on the 10 treated controls (10/10 flipped before rewrite, 3/10 after).

**X2 = 3/40 = 7.5%**.

Frozen evidence SHA-256 of `evidence/model-stale.json`: `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de` (match vs `evidence/HASH.txt` and the Phase 1 freeze).

## SI-4.v1 exclusion

SI-4.v1 was rewritten after review and is still unmarked (`meaning_preserved` blank). It is **excluded** from SI-4's variant set for X, for the vocab-pattern flip tables, and for paraphrase-vs-v0. SI-4 therefore contributes to primary X using **v0, v2, v3, v4 only (4 variants)**. Those four majority verdicts are all `not-satisfied` (no flip). Sensitivity **X_39** drops SI-4 entirely. SI-4.v1's three replica judgments still sit in the 600-row census and in the noise denominator, because that variant has three successful replicas.

## Verdict census (600 replica judgments)

Last successful jsonl record per `variant_id`+`replica`. Failed credit-crash rows ignored. All 200 variants × 3 replicas present. Model `claude-sonnet-4-6`, temperature `0` on every success.

| status (5-way) | n | share |
| --- | --- | --- |
| not-satisfied | 454 | 75.7% |
| partially-satisfied | 132 | 22.0% |
| satisfied | 10 | 1.7% |
| insufficient-evidence | 4 | 0.7% |
| not-applicable | 0 | 0.0% |
| **total** | **600** | **100.0%** |

jsonl lines read: 1193. Successful keys: 600. Failed credit-crash rows ignored: 593. Raw-report cross-check: 600/600 verdicts match.

## Model noise (5-way)

**32/200 = 16.0%** of variants with 3 successful replicas are not unanimous.

|  | n | share of 200 |
| --- | --- | --- |
| unanimous (3 identical replica verdicts) | 168 | 168/200 = 84.0% |
| not unanimous (model noise) | 32 | 32/200 = 16.0% |
| 2-1 majority (subset of noisy) | 31 | 31/200 = 15.5% |
| 1-1-1 split (subset of noisy) | 1 | 1/200 = 0.5% |

The single 1–1–1 variant is `CM-2.v4` (`partially-satisfied`, `insufficient-evidence`, `not-satisfied`) → majority `split`.

## Primary X (5-way wording variance)

A control **flips** when its scored variant majority verdicts are not all identical.

| metric | value |
| --- | --- |
| X (40 controls; SI-4 uses 4 variants) | 10/40 = 25.0% |
| X_39 (drop SI-4 entirely) | 10/39 = 25.6% |
| SI-4 itself (v0,v2,v3,v4) | no flip (4× not-satisfied) |

## Flipped control IDs (5-way majority verdicts)

10 controls flip. Each cell is the 3-replica majority (or `split`).

| control_id | vocab_pattern | n_scored | v0 | v1 | v2 | v3 | v4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AC-6(9) | specific | 5 | satisfied | partially-satisfied | partially-satisfied | partially-satisfied | partially-satisfied |
| AU-8 | specific | 5 | partially-satisfied | partially-satisfied | satisfied | satisfied | partially-satisfied |
| CM-2 | mixed | 5 | not-satisfied | not-satisfied | partially-satisfied | partially-satisfied | split |
| CM-3 | specific | 5 | partially-satisfied | not-satisfied | partially-satisfied | partially-satisfied | not-satisfied |
| CM-3(1) | specific | 5 | not-satisfied | not-satisfied | partially-satisfied | not-satisfied | not-satisfied |
| CM-3(2) | specific | 5 | not-satisfied | not-satisfied | partially-satisfied | not-satisfied | not-satisfied |
| CM-8(1) | specific | 5 | not-satisfied | not-satisfied | partially-satisfied | not-satisfied | not-satisfied |
| SA-10 | specific | 5 | partially-satisfied | not-satisfied | not-satisfied | not-satisfied | not-satisfied |
| SA-4(8) | mixed | 5 | partially-satisfied | not-satisfied | not-satisfied | partially-satisfied | not-satisfied |
| SI-2 | specific | 5 | not-satisfied | partially-satisfied | not-satisfied | not-satisfied | not-satisfied |

## Flip by vocab_pattern (tagged on v0; 5-way)

| vocab_pattern | n controls | n flipped | flip rate |
| --- | --- | --- | --- |
| vague-qualifier | 4 | 0 | 0/4 = 0.0% |
| specific | 23 | 8 | 8/23 = 34.8% |
| mixed | 13 | 2 | 2/13 = 15.4% |

## Qualifier-present vs specific (hypothesis cut; 5-way)

qualifier-present = vague-qualifier + mixed, vs specific. Jose accepted this cut. The table is complete; it is described below, not treated as a hypothesis test decision.

| cut | n controls | n flipped | flip rate |
| --- | --- | --- | --- |
| qualifier-present (vague-qualifier + mixed) | 17 | 2 | 2/17 = 11.8% |
| specific | 23 | 8 | 8/23 = 34.8% |

qualifier-present flipped **2/17 = 11.8%**; specific flipped **8/23 = 34.8%**. Specific controls flipped more often in this 40-control set. Vague-qualifier alone is 0/4 = 0.0% (AC-6, RA-7, SA-8(32), SI-12; none flipped). Mixed is 2/13 = 15.4% (flips: CM-2, SA-4(8)). The numbers do not show a higher wording-variance rate for qualifier-present wording than for specific wording.

## Paraphrase-vs-v0 (5-way)

Denominator = meaning-preserved `yes` paraphrases (variant ≠ v0), skipping SI-4.v1. That is 159 rows (160 paraphrases minus the unmarked SI-4.v1).

|  | n |
| --- | --- |
| meaning-preserved paraphrases scored | 159 |
| majority differs from that control's v0 majority | 22 |
| share | 22/159 = 13.8% |

All 22 differing paraphrases sit inside the 10 flipped controls listed above (no control has a paraphrase/v0 majority disagreement without also flipping as a control).

## 3-way sensitivity

Map applied to each replica verdict, then majority and noise recomputed. `satisfied`→`satisfied`; `not-satisfied`→`not-satisfied`; `insufficient-evidence`→`undetermined`; `partially-satisfied`→`not-satisfied` (OSCAL fail-closed); `not-applicable`→`not-satisfied`; `split` stays `split` if the mapped triple is still 1–1–1.

| metric | 5-way (primary) | 3-way (sensitivity) |
| --- | --- | --- |
| model noise | 32/200 = 16.0% | 9/200 = 4.5% |
| X (40; SI-4 uses 4 variants) | 10/40 = 25.0% | 2/40 = 5.0% |
| X_39 (drop SI-4) | 10/39 = 25.6% | 2/39 = 5.1% |
| paraphrase-vs-v0 | 22/159 = 13.8% | 6/159 = 3.8% |

Replica census after the map (same 600 judgments):

| status (3-way) | n | share |
| --- | --- | --- |
| not-satisfied | 586 | 97.7% |
| satisfied | 10 | 1.7% |
| undetermined | 4 | 0.7% |

`partially-satisfied` (132) and `not-applicable` (0) are folded into `not-satisfied`. `insufficient-evidence` (4) becomes `undetermined`.

3-way flip by vocab_pattern:

| vocab_pattern | n controls | n flipped | flip rate |
| --- | --- | --- | --- |
| vague-qualifier | 4 | 0 | 0/4 = 0.0% |
| specific | 23 | 2 | 2/23 = 8.7% |
| mixed | 13 | 0 | 0/13 = 0.0% |

3-way qualifier-present vs specific: qualifier-present 0/17 = 0.0%; specific 2/23 = 8.7%.

3-way flipped controls (majority after the map):

| control_id | vocab_pattern | n_scored | v0 | v1 | v2 | v3 | v4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AC-6(9) | specific | 5 | satisfied | not-satisfied | not-satisfied | not-satisfied | not-satisfied |
| AU-8 | specific | 5 | not-satisfied | not-satisfied | satisfied | satisfied | not-satisfied |

Most 5-way flips are `not-satisfied` ↔ `partially-satisfied` (and one `split`). Those collapse under fail-closed mapping, so 3-way X is **2/40 = 5.0%** on AC-6(9) and AU-8 only — the two controls whose majority moves between `satisfied` and `not-satisfied`.

## What the numbers say

On this frozen stale-model fixture, with temperature 0 and `claude-sonnet-4-6`, **10 of 40 controls change 5-way majority verdict when the official statement is paraphrased** (10/40 = 25.0%). Replica disagreement is material: **32/200 = 16.0%** of variants are not unanimous even at temperature 0. Collapsing to OSCAL's fail-closed 3-way drops wording variance to **2/40 = 5.0%**. The qualifier-present vs specific table is complete: specific wording flipped more (8/23 = 34.8%) than qualifier-present (2/17 = 11.8%). That is a description of these 40 controls, not a confirmation or rejection of the hypothesis beyond the table.

## Phase 5 (rewritten 10; scored from `runs/phase5.jsonl`)

Jose reviewed 50 rewritten rows: 47 `yes`, 3 `unsure` (`AC-6(9).r4`, `AU-8.r4`, `CM-2.r4`). Unsure rows excluded. 47 variants × 3 replicas = **141** assessments, all successful, temperature 0, model `claude-sonnet-4-6`. Frozen hash unchanged.

**Y = 70.0%** reduction in flip rate on the 10 treated controls: 10/10 flipped before rewrite, **3/10 after** (AU-8, CM-2, CM-3).

**X2 = 3/40 = 7.5%** (the 30 untreated controls counted as still non-flipping; the 3 remaining flips are the only wording-variance left on the original 40-control denominator).

| control_id | n scored after review | flipped after? | majorities |
| --- | --- | --- | --- |
| AC-6(9) | 4 | no | 4× partially-satisfied |
| AU-8 | 4 | **yes** | satisfied / partially-satisfied / partially-satisfied / satisfied |
| CM-2 | 4 | **yes** | partially-satisfied / split / partially-satisfied / split |
| CM-3 | 5 | **yes** | not-satisfied / not-satisfied / partially-satisfied / not-satisfied / not-satisfied |
| CM-3(1) | 5 | no | 5× not-satisfied |
| CM-3(2) | 5 | no | 5× not-satisfied |
| CM-8(1) | 5 | no | 5× not-satisfied |
| SA-10 | 5 | no | 5× not-satisfied |
| SA-4(8) | 5 | no | 5× not-satisfied |
| SI-2 | 5 | no | 5× not-satisfied |

Model noise on the rewritten set: **19/47 = 40.4%** of variants not unanimous (including 2 splits, both on CM-2). That is higher than Phase 3 noise (32/200 = 16.0%). Y is still a wording-variance reduction on majority verdicts; the noise rate is reported beside it.

Replica census (141): not-satisfied 90, partially-satisfied 40, satisfied 8, insufficient-evidence 3.

No longer flip: AC-6(9), CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), SI-2.
