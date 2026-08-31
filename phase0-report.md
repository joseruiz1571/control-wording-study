# Control-Wording Variance Study — Phase 0 report

## What I did

Cloned `joseruiz1571/mltrack` and `joseruiz1571/mlassure` into `/workspace/src` over public HTTPS (`gh` token for joseruiz1571 is invalid; clones still succeeded). Read READMEs, CLIs, control loader, fixture provider, agent/runner, LLM provider, and mltrack card/sample-data/export paths; did not run live assessments or spend API budget. Recorded SHAs, wrote orientation notes, and drafted the smallest unapplied mlassure diffs so a run can log control ID, intent text, retrieved evidence, model, temperature (including 0), 5-way verdict, citations, and optional repeats. Did not modify either clone, did not push, did not create a GitHub repo.

## Artifacts

- `/workspace/control-wording-study/phase0-report.md` (this file)
- `/workspace/control-wording-study/DECISIONS.md`
- `/workspace/control-wording-study/phase0-facts.json`
- `/workspace/control-wording-study/proposals/README.md`
- `/workspace/control-wording-study/proposals/01-provider-model-temperature.diff` (+ `.note.md`) — required
- `/workspace/control-wording-study/proposals/02-report-control-intent.diff` (+ `.note.md`) — required
- `/workspace/control-wording-study/proposals/03-cli-flags-report-repeat.diff` (+ `.note.md`) — required (flags/`--report`; `--repeat` is convenience)
- `/workspace/control-wording-study/proposals/04-capture-api-model-usage.diff` (+ `.note.md`) — optional, stacked on 01
- Clones (untouched): `/workspace/src/mlassure` @ `c9cda3a3f8bd87051d7b31f99c7ddf36db7acfcc`; `/workspace/src/mltrack` @ `dbf197df24c54eb389cbeb2b06352f69936055fb`

## Judgment calls

- Wording for the study is `ControlItem.intent` — there is no NIST catalog prose field on the control type.
- mlassure does not consume mltrack bundles or Model Cards; evidence is `FixtureProvider` over `--target` JSON (AWS provider is M4 / absent).
- Do not collapse mlassure’s 5-way `Judgment.status` in source; map to three labels only in later analysis.
- Recommended 3-way map: `satisfied` → satisfied; `not-satisfied` → not satisfied; `insufficient-evidence` → undetermined; leave `partially-satisfied` and `not-applicable` native (OSCAL already fail-closes them to not-satisfied).
- Extend existing `AssessmentReport` / `report.json` rather than invent a JSONL schema.
- mltrack `sample-data` is inventory into `~/.mltrack/mltrack.db`, not an evidence bundle; mlassure `fixtures/targets/*.json` is the demo evidence that already exists.
- `--repeat` can be a shell loop; `--temperature 0` cannot, because the agent never passes temperature and the provider defaults to 0.1.
- `.env.example`’s `MLASSURE_MODEL` is documentation only until patch 01.

## Questions (batched)

**(i) Are mlassure source changes actually needed?**
Recommended answer: **yes, patches 01–03.** Today a live run’s stdout is human-only; `--oscal` drops intent, uncited evidence, and LLM identity and projects verdicts to binary; `--bundle` `report.json` has ID/verdict/evidence/citations but not intent, model, or temperature; temperature 0 is unreachable from the CLI. Patch 04 (API snapshot id + token usage) is optional.

**(ii) Which model/version to freeze?**
Recommended answer: **the code default `claude-sonnet-4-6`**, and pin `@anthropic-ai/sdk` to lockfile **0.104.1** (package.json currently uses `^`). That alias is not a dated snapshot; `response.model` is discarded unless patch 04 lands. If Anthropic publishes a dated id for this alias, freeze that string via `--model` / `MLASSURE_MODEL` once 01 is applied. README’s “Claude Sonnet 4” is marketing text, not the API id.

**(iii) Does a demo evidence dataset exist, or must we propose a synthetic one in Phase 1?**
Recommended answer: **use mlassure’s existing fixtures; do not invent a synthetic dataset yet.** Paths: `/workspace/src/mlassure/fixtures/targets/model-clean.json` (fraud-detection-v2, clean monitoring) and `model-stale.json` (churn-predictor-v1, stale/missing controls), plus `/workspace/src/mlassure/fixtures/controls/nist-subset.yaml` (8 controls). mltrack has **no** checked-in evidence bundle (`sample_bundle_path: null`); `mltrack sample-data` generates inventory, not collector payloads, and `mltrack package` is README-future only.

**(iv) Estimated API cost shape (from code; no dollar cap invented)?**
Per assessment of `nist-subset.yaml`: **5 LLM controls** (SI-6(1), AC-6(9), AU-12(3), RA-3, CA-7) each up to `MAX_ITERATIONS=10` `messages.create` calls (`assessControl`); SC-28/SC-7 deterministic and SA-10 attestation make **zero** LLM calls. Typical path is ~2 calls/LLM control (collect then `submit_judgment`) → **~10 calls/run**. Each call `max_tokens` default **4096**, temperature default **0.1**. A wording study with 3 replicas × 2 fixture targets × V variants is **~60×V** API calls. Token `usage` is not recorded unless patch 04. No price table or dollar cap exists in the repo.

## What I will do next if Jose says nothing

Wait. Do not apply diffs. Do not start Phase 1 until Phase 0 is accepted — even though a sample fixture exists, the brief says report at end of phase before starting the next. If diffs are later approved, apply 01→02→03 (then optional 04) on a branch of mlassure and only then design Phase 1 runs against the fixtures.
