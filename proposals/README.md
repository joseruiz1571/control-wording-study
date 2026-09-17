Unapplied unified diffs against `mlassure` at `c9cda3a3f8bd87051d7b31f99c7ddf36db7acfcc`.

These patches were never pushed upstream. From a checkout of that SHA, apply relative to this repository:

```
git apply path/to/control-wording-study/proposals/01-provider-model-temperature.diff
git apply path/to/control-wording-study/proposals/02-report-control-intent.diff
git apply path/to/control-wording-study/proposals/03-cli-flags-report-repeat.diff
# optional, after 01:
git apply path/to/control-wording-study/proposals/04-capture-api-model-usage.diff
```

Or, from the mlassure checkout with this repo as a sibling:

```
git apply ../control-wording-study/proposals/01-provider-model-temperature.diff
git apply ../control-wording-study/proposals/02-report-control-intent.diff
git apply ../control-wording-study/proposals/03-cli-flags-report-repeat.diff
git apply ../control-wording-study/proposals/04-capture-api-model-usage.diff
```

Zero diffs were not possible: live stdout is human-only; `--oscal` drops intent, uncited evidence, and LLM identity; `--bundle` `report.json` lacks intent/model/temp; temperature 0 is unreachable from CLI.
