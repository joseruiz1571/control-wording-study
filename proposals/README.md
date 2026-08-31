Unapplied unified diffs against `mlassure` at `c9cda3a3f8bd87051d7b31f99c7ddf36db7acfcc`.

Do **not** apply until Phase 0 is accepted. From a checkout of that SHA:

```
git apply /workspace/control-wording-study/proposals/01-provider-model-temperature.diff
git apply /workspace/control-wording-study/proposals/02-report-control-intent.diff
git apply /workspace/control-wording-study/proposals/03-cli-flags-report-repeat.diff
# optional, after 01:
git apply /workspace/control-wording-study/proposals/04-capture-api-model-usage.diff
```

Zero diffs were not possible: live stdout is human-only; `--oscal` drops intent, uncited evidence, and LLM identity; `--bundle` `report.json` lacks intent/model/temp; temperature 0 is unreachable from CLI.
