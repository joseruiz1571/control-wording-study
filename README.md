# Control-Wording Variance Study

When an LLM assesses whether an AI system meets a NIST SP 800-53 control, does the *wording* of the control change the verdict? This archive measures that on one frozen evidence fixture, one model (`claude-sonnet-4-6`, temperature 0), and 40 official Rev 5 statements each with four meaning-preserving paraphrases.

Primary result: **X = 10/40 = 25.0%** of controls change 5-way majority verdict when only vocabulary and sentence structure change. The study expected qualifier-present controls to flip more than specific controls; they did not (qualifier-present 2/17 = 11.8%; specific 8/23 = 34.8%; vague-qualifier 0/4). The qualifier hypothesis is **not supported**. A vocabulary-control rewrite of the ten controls that had flipped cut their flip rate from 10/10 to 3/10 (**Y = 70%** reduction). Secondary **X2 = 3/40 = 7.5%**.

This copy is a **private study archive**, not a journal submission. Nothing has been published. Do not treat it as a public dataset until the owner says so.

Frozen evidence: `evidence/model-stale.json`, SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`. Copied mlassure SageMaker-shaped fixture (`churn-predictor-v1`), not an mltrack bundle. Hash unchanged through Phase 5.

## Reproduce tables (frozen logs)

From the repository root, Python 3.10+, standard library only:

```
python3 analysis/score.py
```

That command (a) re-verifies the evidence SHA-256, (b) recomputes Phase 4 X and noise from `runs/phase3.jsonl` + `controls/control_set.reviewed.csv`, (c) recomputes Phase 5 Y/X2 from `runs/phase5.jsonl` + `controls/control_set_rewritten.reviewed.csv`, and (d) rewrites `RESULTS.md` and `analysis/tables.json`. It does **not** call an LLM API, does **not** run mlassure, and does **not** re-assess the 741 successful replicas.

Live re-runs need patched mlassure and an Anthropic API key. They are out of scope for the one-command table rebuild.

## How live assessments were produced

Recorded runners (not something a stranger can run without a key and a patched clone): `runs/run_phase3.py` and `runs/run_phase5.py`.

- Tool: mlassure (`github.com/joseruiz1571/mlassure`) with local logging patches 01–05 on branch `study/logging-patches`, base SHA `c9cda3a`. Patches were not pushed.
- Command shape: `mlassure assess --controls <yaml> --target evidence/model-stale.json --live --temperature 0 --model claude-sonnet-4-6 --report <raw.json>`.
- YAML: `controls/yaml/` (Phase 3, 200 variants) and `controls/yaml_rewritten/` (Phase 5, rewritten 10).
- Wording = `ControlItem.intent`. Verdicts are 5-way.

mlassure patches live in the local mlassure clone and are also stored as `proposals/*.diff` in this repo.

## Layout

```
analysis/          score.py, tables.json
controls/          official v0, paraphrases, reviewed CSVs, YAML
controls/yaml/     Phase 3 one-control YAML
controls/yaml_rewritten/  Phase 5 rewritten YAML
evidence/          frozen model-stale.json, HASH.txt
paper/             draft.md
phase5/            RULES.md
proposals/         mlassure logging patches 01–05 (.diff)
runs/              phase3.jsonl, phase5.jsonl, runners, raw reports
RESULTS.md         scored tables (X, Y, X2, noise)
DECISIONS.md       protocol log
LICENSE            CC-BY-4.0 for study artifacts; NIST text is US government work
```

## License

`LICENSE` in this repository is **CC-BY-4.0** for the paper, variants, logs, and scoring scripts. NIST SP 800-53 control text reproduced under `controls/` is a United States government work and is not subject to copyright in the United States.

## Private-repo note

This copy is the study archive. Do not open a public GitHub repository from this tree as part of packaging. mlassure patches remain local except for the diffs under `proposals/`.
