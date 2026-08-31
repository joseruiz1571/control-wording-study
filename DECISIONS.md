# Phase 0 decisions (orientation only)

Clones (read-only; no edits, no push):

- **mlassure** `/workspace/src/mlassure` @ `c9cda3a3f8bd87051d7b31f99c7ddf36db7acfcc` (2026-08-13 13:47 CDT, "Bump version to 0.3.0")
- **mltrack** `/workspace/src/mltrack` @ `dbf197df24c54eb389cbeb2b06352f69936055fb` (2026-08-24 20:57 CDT, YouTube walkthrough docs)

`gh auth` token for `joseruiz1571` is invalid; public HTTPS clone succeeded. Not a blocker.

## How mlassure loads controls

CLI: `mlassure assess --controls <path> --target <path>` (`src/cli/index.ts` `parseArgs`, `runLive` / `runScaffoldOnly`). No other config file. Input is YAML (`.yaml`/`.yml`) or JSON via `loadControlSet` (`src/loaders/control-loader.ts`): document must have string `version` and `controls[]`; each control requires `id`, `framework`, `pattern` ∈ `AGENT_PATTERNS`, `intent`, optional `collectors[]`, `note`, `tagProvenance`. Fixture: `fixtures/controls/nist-subset.yaml` (8 SP 800-53 controls). There is no NIST catalog prose field; **wording = `ControlItem.intent`**.

## How mlassure retrieves evidence

Not from an mltrack bundle. `runLive` constructs `FixtureProvider(targetPath)` (`src/providers/fixture-provider.ts`) implementing `AwsProvider` (`src/providers/aws-provider.interface.ts`). Collectors named in the control YAML are dispatched by `executeCollector` (`src/tools/executor.ts`) from the agent loop `assessControl` (`src/agent/agent.ts`) or deterministic checks (`src/agent/deterministic-checks.ts`). `FixtureProvider` reads SageMaker-shaped JSON (`registry`, `modelCard`, `endpoint`, `monitors`, `kms`, `network`, `executionRole`, `cloudtrailEvents`) from `--target`. Live AWS provider is documented as M4 / not implemented. mltrack Model Cards (`mltrack.services.card_service.model_to_card`, empty `evidence: []`) are not an input to mlassure.

## Output of a run

Default `--live` stdout is a human table (`src/cli/index.ts` `runLive`, `STATUS_ICON`). Optional files: `--oscal` → OSCAL 1.1.2 Assessment Results (`toOscalAssessmentResults` in `src/output/oscal-ar.ts`); `--narrative` → Markdown (`toNarrativeMarkdown` in `src/output/narrative.ts`); `--bundle <dir>` → custody dir via `writeEvidenceBundle` (`src/output/bundle.ts`): `report.json` (`AssessmentReport`), `evidence/<uuid>.json` (full payloads, cited or not), optional `oscal.json`/`narrative.md`, `manifest.json` (`BUNDLE_FORMAT_VERSION = "1"`). `verify-bundle` checks hashes only. No `--json` / `--report` flag today.

## Three-way verdict?

**No.** `Judgment.status` (`src/types.ts`) is five-valued: `satisfied` | `partially-satisfied` | `not-satisfied` | `not-applicable` | `insufficient-evidence` (`JUDGMENT_STATUSES`; tool enum in `SUBMIT_JUDGMENT_TOOL`, `src/tools/registry.ts`). OSCAL projects fail-closed to binary (`toObjectiveState`: only `satisfied` → OSCAL satisfied; `src/output/oscal-ar.ts`). Do not collapse the enum in source; map in analysis if the study needs three labels.

## Machine-readable run logs vs study fields

| Field | Present today? |
| --- | --- |
| control ID | Yes — `Judgment.controlId` / `ControlResult.controlId` |
| exact control text | **No** — `intent` stays on `ControlItem`; not copied onto `ControlResult`; narrative does not reprint intent |
| evidence retrieved | Yes in memory (`ControlResult.retrievedEvidence`); on disk only with `--bundle` |
| model name and version | **No** — alias `claude-sonnet-4-6` is local to `AnthropicProvider`; API `response.model` / `usage` discarded |
| verdict | Yes, 5-way, not 3-way |
| evidence citations | Yes — `judgment.evidenceCited` + `citedEvidence` |

Stdout-only live runs leave nothing machine-readable.

## How mltrack produces an evidence bundle

It does not. Entry point: `mltrack` → `mltrack.cli.main:app` (`pyproject.toml`). Closest artifacts: `mltrack sample-data` (synthetic inventory into `~/.mltrack/mltrack.db`, `src/mltrack/cli/sample_data_command.py`); `mltrack card export` (Governance Model Card JSON, `evidence: []` reserved for mlassure, `card_service.model_to_card`); `mltrack report compliance -f oscal`; `mltrack export` CSV/JSON inventory. README “Examination Evidence Package” (`mltrack package …`) is **future, not implemented**. No checked-in sample bundle. **`sample_bundle_path`: null.** mlassure’s own demo evidence is `fixtures/targets/model-clean.json` and `model-stale.json` (SageMaker fixture JSON, not an mltrack bundle).

## Default model, temperature, pinning

- Model: `AnthropicProvider` default `"claude-sonnet-4-6"` (`src/llm/anthropic-provider.ts`). README: “Claude Sonnet 4”. `.env.example` documents `MLASSURE_MODEL` — **unread**.
- Temperature: `params.temperature ?? 0.1` in `complete()`. `assessControl` does not pass `temperature` → always 0.1. `0` would work if passed (`??` not `||`).
- Pinning: alias, not a dated snapshot. `@anthropic-ai/sdk` `^0.104.1` (lockfile 0.104.1). `max_tokens` default 4096; `MAX_ITERATIONS = 10` (`src/agent/agent.ts`). No cost/usage logging.

## Judgment calls

1. **Wording = `intent`.** No other control-text field exists in `ControlItem`.
2. **Do not invent an mltrack→mlassure bundle path.** Code has `FixtureProvider` only; card `evidence: []` is a documented empty slot.
3. **Keep the 5-way enum.** Collapsing it would be a feature change, not logging.
4. **Map 3-way in analysis, not in mlassure:** `satisfied`→satisfied; `not-satisfied`→not satisfied; `insufficient-evidence`→undetermined; keep `partially-satisfied` / `not-applicable` native (OSCAL already fail-closes them).
5. **Extend `AssessmentReport` rather than invent JSONL.** `--bundle` already serializes that object.
6. **mltrack sample-data is not an evidence dataset** for this study; mlassure fixtures are.
7. **`--repeat` is optional** given a shell loop; **`--temperature 0` is not**.
8. **No live LLM runs in Phase 0** (brief).

## 2026-08-27 — Patches 01–04 applied locally

Jose approved applying 01–03 and optional 04. Applied on branch `study/logging-patches` at SHA base `c9cda3a`. Working tree modified, not committed (no git identity on this machine; I did not set `git config`). Not pushed.

Verification: `bun install`, `bun run typecheck` (clean), `bun test` (180 pass, 4 skip: 2 cosign, 2 live API).

Patch 04 records `response.model` and token `usage` on `LlmCompletionResult` only. The agent still does not copy those onto `AssessmentReport`. A follow-up would be needed if we want the dated snapshot id in `report.json`. I am not writing that follow-up unless asked.

## 2026-08-29 — API cap and Phase 1 freeze

Jose set the assessment API cap at **$50**. Stop and report at 80% (**$40**). Model remains `claude-sonnet-4-6`. No live runs yet.

Phase 1 freeze: copied mlassure fixture `fixtures/targets/model-stale.json` to `evidence/model-stale.json` (read-only). SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`. Source mlassure SHA `c9cda3a3f8bd87051d7b31f99c7ddf36db7acfcc`. Chose the stale fixture because it has mixed satisfied / not-satisfied conditions, so wording has room to flip. One target, not two. This is not an mltrack bundle; mlassure cannot consume one. Do not modify `evidence/model-stale.json` after this point.

## Phase 2 — control set (2026-08-29)

Frozen evidence was not modified. SHA-256 still `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`. No GitHub repo, no push, no API spend, Phase 3 not started.

### Judgment calls

1. **No deterministic or attestation controls in the 40.** mlassure keys deterministic checks by control ID for `SC-28` and `SC-7` only; attestation never calls the LLM. Including those IDs (or tagging any study control `deterministic`/`attestation`) would make wording unable to change the verdict. SC-28 and SC-7 bases are out. SC-28(1) and SC-7(5) are in, tagged `sufficiency`, because those IDs have no code bypass.
2. **Official v0, not mlassure intent.** mlassure's `nist-subset.yaml` rewrites AC-6(9) as least-privilege on the execution role and AU-12(3) as approval-before-deploy. Official AC-6(9) is "Log the execution of privileged functions." Official AU-12(3) is about changing logging configuration; it is **not** in the 40 because the fixture does not speak to selectable logging criteria. SI-6(1) is withdrawn in Rev 5; the study uses SI-6.
3. **SA-10 is correlation, not attestation.** Official SA-10 is developer configuration management (approved, documented, integrity-controlled changes). Registry + CloudTrail can speak to that. mlassure tagged SA-10 attestation for a named-reviewer rewrite; we do not use that rewrite or that pattern.
4. **RA-3 and SA-8(32) keep getModelCard even though the fixture returns null.** Null is a collector result the LLM can use (absence vs gap). Wording can still flip `insufficient-evidence` vs `not-satisfied`. Controls that the fixture cannot speak to at all (PE, PS, IA identity, vuln scanners, PE physical) were rejected.
5. **RA family is thin (2).** Most RA controls need a risk/vuln document the collectors cannot return. RA-3 (card) and RA-7 (failed monitor + unmanaged hotfix as unaddressed findings) are the honest mappings. Do not pretend data-quality monitors are CVE scanning (RA-5).
6. **One CA control (CA-7) despite the favor-list of AC/AU/CM/RA/SA/SI.** The frozen monitors/capture fields map directly to continuous monitoring; mlassure's own subset already used CA-7. SC does not dominate (2 enhancements, not the deterministic bases).
7. **vocab_pattern mix is 4 vague-qualifier / 23 specific / 13 mixed**, not 14/14/12. NIST Rev 5 statements rarely use appropriate/adequate/sufficient/periodically/as needed/timely without also naming an assignment (role, frequency, or artifact). Forcing 14 pure-vague would mean mis-tagging mixed controls or admitting *-1 policy controls the fixture cannot assess. Actual counts are recorded. Close undefined qualifiers counted: necessary, unnecessary, applicable, sufficient, adequate, as needed, appropriate, if necessary, risk tolerance, consistent with operational requirements, when required.
8. **Tagging rule for vocab_pattern** (applied to v0 only, copied onto variants): vague-qualifier = list/close qualifier and no named frequency, numeric threshold, or role/personnel assignment; specific = names an artifact, number, frequency, or role and has no such qualifier; mixed = both. `[Assignment: organization-defined frequency]` and `[Assignment: organization-defined personnel or roles]` count as naming frequency/role.
9. **Paraphrases keep every `[Assignment:]` / `[Selection:]` block verbatim** and do not add SHALL/MUST/numbers/roles absent from v0. `meaning_preserved` is left empty for Jose. No paraphrase is marked `unsure` after that check.
10. **Collectors are a subset of the nine mlassure names.** No invented collectors. Pattern is never deterministic or attestation.

### Not selected (examples)

- SC-28, SC-7 (deterministic). SA-10 as attestation. SI-6(1), AU-2(3), and other withdrawn.
- PE, PS, and other families with no fixture signal.
- AU-12(3) official text (logging-change capability / selectable event criteria) — fixture cannot speak to it; mlassure's adapted approval-before-deploy intent was discarded.
- RA-5 vulnerability scanning — no scanner collector.

## 2026-08-30 — Phase 2 accepted; Phase 3 start

Jose: "Go with your recommendations and continue." Locked: 4/23/13 vocab mix, hypothesis cut is qualifier-present (17) vs specific (23); keep RA-3 and SA-8(32); keep CA-7, SC-28(1), SC-7(5); keep official AC-6(9). He did not return a marked CSV. I treated the 200-row set as meaning-preserved as-shipped (neither of us had marked unsure), wrote `controls/control_set.accepted.csv`, and generated 200 one-control YAML files. Original `control_set.csv` still has a blank `meaning_preserved` column.

Phase 3 runner: `runs/run_phase3.py`, 3 replicas, temperature 0, model `claude-sonnet-4-6`, frozen target `evidence/model-stale.json`. Cap $50, stop at $40. Blocked on `ANTHROPIC_API_KEY` in `/workspace/src/mlassure/.env` (not present). No live calls yet.

## 2026-08-30 — Patch 05: anthropic-workspace-id from env

Jose approved a local mlassure patch so identity-linked keys can send `anthropic-workspace-id` from `ANTHROPIC_WORKSPACE_ID`. Applied on `study/logging-patches`. Not pushed. Admin API list-workspaces returned 403 with this key, so the workspace id still has to come from Console → Settings → Workspaces.

## 2026-08-30 — Jose reviewed CSV; Phase 3 stalled on credits

Jose returned `control_set.reviewed.csv`: 199 `yes`, 0 `no`, 1 `unsure` (`SI-4.v1`, identical to v0). I rewrote SI-4.v1 as a real paraphrase and left that row's `meaning_preserved` blank for him. Do not score SI-4.v1 until he marks yes.

Phase 3 ran to completion of the queue: 7 succeeded (AC-2(7).v0–v2 replicas), 593 failed. Every failure was Anthropic `credit balance is too low`. Failures were logged, not dropped. Runner now aborts on that error instead of walking the rest of the queue. Resume when the Anthropic account has credits. Frozen hash unchanged.

## 2026-08-30 — Phase 4 scoring (no Phase 5)

Frozen evidence SHA-256 re-verified: `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de` matches `evidence/HASH.txt` and `evidence/model-stale.json`. File still read-only. No API spend. No push. Phase 5 not started.

Phase 3 jsonl had 1193 lines: 600 successes and 593 credit-crash failures. Scoring uses the **last successful** record per `variant_id`+`replica` and ignores failed rows. Asserted 600 unique successful keys, all temperature 0, all model `claude-sonnet-4-6`, every variant has replicas 1/2/3. Raw reports match jsonl verdicts 600/600.

### Scoring rules applied (Jose-accepted)

- Replica verdict = mlassure 5-way `Judgment.status` as logged.
- Majority = unique status with count ≥2 among 3 replicas; 1-1-1 → `split`.
- Model noise = share of variants with 3 successful replicas whose three verdicts are not unanimous (denominator 200, including SI-4.v1).
- A control flips when its scored variant majority verdicts are not all identical. Primary **X = flipped_controls / 40**.
- **SI-4.v1 excluded** from that control's variant set (rewritten, still unmarked). SI-4 contributes to X using v0,v2,v3,v4 only (4 variants). Those four majorities are all `not-satisfied` (no flip). **X_39** drops SI-4 entirely.
- Paraphrase-vs-v0: meaning-preserved `yes` paraphrases only; skip SI-4.v1 (159 rows).
- Vocab_pattern from CSV v0 tags. Hypothesis cut = qualifier-present (vague-qualifier + mixed) vs specific. Report both 3-way pattern table and 2-way cut; do not declare the hypothesis confirmed or rejected.
- 5-way is PRIMARY. 3-way sensitivity maps replica verdicts (`satisfied`→satisfied; `not-satisfied`→not-satisfied; `insufficient-evidence`→undetermined; `partially-satisfied`→not-satisfied fail-closed; `not-applicable`→not-satisfied), then recomputes majority/noise/X. `split` stays `split` if the mapped triple is still 1-1-1.

### Computed (from logs; see RESULTS.md)

- Verdict census (600): not-satisfied 454, partially-satisfied 132, satisfied 10, insufficient-evidence 4, not-applicable 0.
- Noise 32/200 = 16.0% (31 two-one; 1 split = CM-2.v4).
- **X = 10/40 = 25.0%**. X_39 = 10/39 = 25.6%.
- Flipped: AC-6(9), AU-8, CM-2, CM-3, CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), SI-2.
- Vocab flip rates: vague-qualifier 0/4, specific 8/23 = 34.8%, mixed 2/13 = 15.4%. Qualifier-present 2/17 = 11.8% vs specific 8/23 = 34.8%.
- Paraphrase-vs-v0: 22/159 = 13.8%.
- 3-way sensitivity: noise 9/200 = 4.5%; X 2/40 = 5.0% (AC-6(9), AU-8 only).

### Judgment calls

1. SI-4.v1 stays out of X even though it has three successful replicas (unanimous `not-satisfied`, same as the other SI-4 variants).
2. Noise keeps SI-4.v1 in the 200 because the definition is variants with 3 successful replicas, not meaning-preserved.
3. 3-way map is applied to replica verdicts before majority, so CM-2.v4's 5-way `split` becomes 3-way `not-satisfied`.
4. The qualifier-present table is reported as numbers only; specific flipped more in this set.
5. Y is a placeholder. Do not start Phase 5 until Jose accepts X or asks to proceed.

## Phase 5 proposal (2026-08-30)

Jose accepted primary X = 10/40 = 25.0% (5-way) and scoped Phase 5 to the **10 flipped controls only** (not all 40): AC-6(9), AU-8, CM-2, CM-3, CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), SI-2. The qualifier-present vs specific hypothesis was **not** supported (specific flipped more). Phase 5 rules therefore de-ambiguate those 10; they are not written as if vague-qualifier wording caused the flips.

Frozen evidence was not modified. SHA-256 still `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`. No GitHub push, no API spend, mlassure not rerun, Phase 6 not started.

### Outcomes defined for later (not computed now)

- **Y (primary for the rewrite test):** reduction in flip rate **on these 10** after Jose reviews `meaning_preserved` on `controls/control_set_rewritten.csv` and a later rerun. Y is not run in this phase.
- **X2 (secondary, whole-set):** `(flips remaining in the 10 + 0 from the other 30) / 40`. The other 30 are treated as contributing 0 additional flips because they did not flip on the Phase 3/4 run and were not rewritten.

### Judgment calls

1. **Seven rules (R1–R7), not a qualifier-fix.** Preferred-term lock; name the implied evidence object; factor compound actions; scope the class with the control’s own words; closed selection for OR; name both ends of an associative hedge; discrete authorised headings plus locked `[Assignment:]`/`[Selection:]`. Citations from sources actually retrieved: ANSI/NISO Z39.19-2005 (R2010), ISO 25964-1:2011, IFLA GARR 2nd ed. 2001, IFLA ICP 2016 (RDA-aligned authority control; RDA Toolkit not retrieved).
2. **Rewrites only of official v0.** Traceable to CSRC spreadsheet text in `control_set.reviewed.csv` variant 0. No requirements added, removed, or weakened. No fixture artifact names injected into control text. No SHALL/MUST/new numbers/roles.
3. **Paraphrases r1–r4** use the same Phase 2 rules (vocab/structure only; Assignment/Selection verbatim; mark unsure rather than weaken). IDs are `{control_id}.r0`–`.r4` so they never collide with `.v0`–`.v4`. `meaning_preserved` left empty for Jose. None marked unsure.
4. **vocab_pattern retagged on rewritten r0** with the Phase 2 tagging rule. Result: 8 specific / 2 mixed (CM-2, SA-4(8) stay mixed because R6 keeps “consistent with” / circumstances-require rather than deleting them). Copied onto r1–r4.
5. **Do not rerun until Jose returns the rewritten CSV with `meaning_preserved` filled.** YAML in `controls/yaml_rewritten/` is ready for a later mlassure run; this phase does not start it.

### Artifacts

- `phase5/RULES.md`
- `controls/control_set_rewritten.csv` (50 rows)
- `controls/yaml_rewritten/` (50 YAML files)
- `phase5-report.md`

## 2026-08-30 — Phase 5 review returned; rerun started

Jose marked control_set_rewritten.reviewed.csv: 47 yes, 3 unsure (AC-6(9).r4, AU-8.r4, CM-2.r4). Unsure rows excluded from the rerun and from Y. 47 variants x 3 replicas started against frozen evidence. No push.

## 2026-08-30 — Phase 5 rerun scored

141/141 successful. Y = 70% reduction (10/10 flipped before, 3/10 after: AU-8, CM-2, CM-3). X2 = 3/40 = 7.5%. Noise on rewritten variants 19/47 = 40.4%. Unsure rows excluded. Frozen hash unchanged. Phase 6 not started.


## 2026-08-30 — Phase 6 packaging

Paper written (`paper/draft.md`). The hypothesis claim in the target abstract (qualifier controls flip most; specific flip least) was not supported, so the paper reports the reverse table and does not claim the qualifier hypothesis was confirmed. Private-repo packaging: `README.md`, `LICENSE` (CC-BY-4.0 for study artifacts; NIST control text is US government work), `.gitignore`, and `analysis/score.py` extended to recompute Phase 5 Y/X2 from frozen logs. No public push in this step.

## 2026-08-30 — Phase 6 private repo

Jose approved a private archive. Created https://github.com/joseruiz1571/control-wording-study (visibility PRIVATE) and pushed `main`. Not public. Paper 2496 words. Reproduce: `python3 analysis/score.py`. mlassure patches still unpushed on the mlassure clone.
