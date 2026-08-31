#!/usr/bin/env python3
"""Phase 4 + Phase 5 scorer for the Control-Wording Variance Study.

Headless, argparse-free. From the study root:

    python3 analysis/score.py

(a) re-verifies evidence SHA-256,
(b) recomputes Phase 4 X and noise from runs/phase3.jsonl +
    controls/control_set.reviewed.csv,
(c) recomputes Phase 5 Y/X2 from runs/phase5.jsonl +
    controls/control_set_rewritten.reviewed.csv,
(d) rewrites RESULTS.md and analysis/tables.json including Phase 5.

Does not modify evidence/model-stale.json. Does not call any API.
Does not re-run mlassure. Unsure rewritten rows are excluded from Y.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EXPECTED_HASH = "bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de"
EXCLUDE_VARIANT = "SI-4.v1"
MODEL = "claude-sonnet-4-6"
TEMPERATURE = 0
N_REPLICAS = 3
N_CONTROLS = 40
N_SUCCESS = 600

MAP_3WAY = {
    "satisfied": "satisfied",
    "not-satisfied": "not-satisfied",
    "insufficient-evidence": "undetermined",
    "partially-satisfied": "not-satisfied",  # OSCAL fail-closed
    "not-applicable": "not-satisfied",
}

FIVE_WAY = (
    "satisfied",
    "partially-satisfied",
    "not-satisfied",
    "not-applicable",
    "insufficient-evidence",
    "split",
)


def study_root() -> Path:
    return Path(__file__).resolve().parent.parent


def pct(n: int, d: int) -> str:
    if d == 0:
        raise SystemExit("percentage denominator is 0")
    return f"{n}/{d} = {100.0 * n / d:.1f}%"


def pct_num(n: int, d: int) -> float:
    return round(100.0 * n / d, 1)


def majority(verdicts: list[str]) -> str:
    """Unique status with count >= 2 among 3 replicas; 1-1-1 → split."""
    if len(verdicts) != N_REPLICAS:
        raise SystemExit(f"majority() expected {N_REPLICAS} verdicts, got {verdicts}")
    c = Counter(verdicts)
    if len(c) == 3 and all(v == 1 for v in c.values()):
        return "split"
    ge2 = [status for status, n in c.items() if n >= 2]
    if len(ge2) != 1:
        raise SystemExit(f"could not resolve unique majority from {c}")
    return ge2[0]


def map3(status: str) -> str:
    if status == "split":
        return "split"
    if status not in MAP_3WAY:
        raise SystemExit(f"unknown 5-way status {status!r}")
    return MAP_3WAY[status]


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def load_successes(jsonl_path: Path) -> dict[tuple[str, int], dict]:
    """Last successful record per variant_id+replica. Ignore failed rows."""
    by_key: dict[tuple[str, int], dict] = {}
    n_lines = 0
    n_fail = 0
    n_credit = 0
    for line in jsonl_path.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        n_lines += 1
        rec = json.loads(line)
        vid = rec.get("variant_id")
        replica = rec.get("replica")
        if not vid or replica not in (1, 2, 3):
            raise SystemExit(f"malformed jsonl record: variant_id={vid!r} replica={replica!r}")
        ok = rec.get("returncode") == 0 and rec.get("verdict")
        if not ok:
            n_fail += 1
            blob = (rec.get("stderr_tail") or "") + (rec.get("stdout_tail") or "")
            if "credit balance is too low" in blob:
                n_credit += 1
            continue
        by_key[(vid, int(replica))] = rec
    return by_key, {"n_lines": n_lines, "n_fail": n_fail, "n_credit": n_credit}


def cross_check_raw(successes: dict[tuple[str, int], dict], raw_dir: Path) -> int:
    """Optional: jsonl verdict must match the raw report when the file exists."""
    n_checked = 0
    for (vid, replica), rec in successes.items():
        report_path = rec.get("report_path")
        if not report_path:
            path = raw_dir / f"{vid}-r{replica:02d}.json"
        else:
            path = Path(report_path)
        if not path.is_file() and report_path:
            path = raw_dir / Path(str(report_path)).name
        if not path.is_file():
            alt = raw_dir / f"{vid}-r{replica:02d}.json"
            if alt.is_file():
                path = alt
        if not path.is_file():
            raise SystemExit(f"raw report missing for {vid} replica {replica}: {path}")
        report = json.loads(path.read_text(encoding="utf-8"))
        results = report.get("results") or []
        if len(results) != 1:
            raise SystemExit(f"{path} has {len(results)} results, expected 1")
        status = (results[0].get("judgment") or {}).get("status")
        if status != rec.get("verdict"):
            raise SystemExit(
                f"jsonl/raw mismatch {vid} r{replica}: jsonl={rec.get('verdict')!r} raw={status!r}"
            )
        n_checked += 1
    return n_checked


def verify_hash(root: Path) -> str:
    evidence = root / "evidence" / "model-stale.json"
    hash_file = root / "evidence" / "HASH.txt"
    if not evidence.is_file():
        raise SystemExit(f"missing frozen evidence file: {evidence}")
    computed = hashlib.sha256(evidence.read_bytes()).hexdigest()
    recorded = hash_file.read_text(encoding="utf-8").strip().split()[0]
    if computed != EXPECTED_HASH:
        raise SystemExit(
            f"HASH MISMATCH on evidence/model-stale.json\n"
            f"  computed: {computed}\n"
            f"  expected: {EXPECTED_HASH}\n"
            f"ABORT."
        )
    if recorded != EXPECTED_HASH:
        raise SystemExit(
            f"HASH MISMATCH vs evidence/HASH.txt\n"
            f"  HASH.txt: {recorded}\n"
            f"  expected: {EXPECTED_HASH}\n"
            f"ABORT."
        )
    return computed


def load_csv_n(path: Path, expected_n: int) -> tuple[list[dict], dict[str, dict]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    if len(rows) != expected_n:
        raise SystemExit(f"expected {expected_n} CSV rows in {path}, got {len(rows)}")
    meta = {}
    for r in rows:
        vid = r["variant_id"]
        if vid in meta:
            raise SystemExit(f"duplicate variant_id in CSV: {vid}")
        meta[vid] = r
    return rows, meta


def load_csv(path: Path) -> tuple[list[dict], dict[str, dict]]:
    return load_csv_n(path, 200)


def meaning_unsure(s: str) -> bool:
    return "unsure" in (s or "").strip().lower()


def meaning_yes(s: str) -> bool:
    return (s or "").strip().lower() == "yes"


def variant_sort_key(vid: str) -> tuple[str, int]:
    tag = vid.split(".")[-1]
    letter = tag[0]
    try:
        n = int(tag[1:])
    except ValueError:
        n = 0
    return letter, n


def fmt_maj_cell(majs: list[str]) -> str:
    if majs and len(set(majs)) == 1:
        return f"{len(majs)}× {majs[0]}"
    return " / ".join(majs)


def control_order(rows: list[dict]) -> list[str]:
    order = []
    seen = set()
    for r in rows:
        cid = r["control_id"]
        if cid not in seen:
            seen.add(cid)
            order.append(cid)
    return order


def variant_ids_for(cid: str, rows: list[dict], exclude: bool = True) -> list[str]:
    vids = []
    for r in rows:
        if r["control_id"] != cid:
            continue
        if exclude and r["variant_id"] == EXCLUDE_VARIANT:
            continue
        vids.append(r["variant_id"])
    return vids


def score_phase5(root: Path, treated_ids: list[str]) -> dict:
    """Recompute Y/X2 from frozen phase5.jsonl + rewritten reviewed CSV.

    Unsure rows (meaning_preserved containing 'unsure') are excluded from Y.
    Last successful jsonl record per variant_id+replica. Majority of 3;
    1-1-1 = split. A control flips when scored variant majorities are not
    all identical. Y = (n_treated - n_flipped_after) / n_treated.
    X2 = n_flipped_after / 40 (untreated 30 counted as still non-flipping).
    """
    jsonl_path = root / "runs" / "phase5.jsonl"
    csv_path = root / "controls" / "control_set_rewritten.reviewed.csv"
    raw_dir = root / "runs" / "raw"
    if not jsonl_path.is_file():
        raise SystemExit(f"missing {jsonl_path}")
    if not csv_path.is_file():
        raise SystemExit(f"missing {csv_path}")

    rows, meta = load_csv_n(csv_path, 50)
    treated_order = control_order(rows)
    if set(treated_order) != set(treated_ids):
        raise SystemExit(
            f"Phase 5 control set mismatch: csv={treated_order} treated={treated_ids}"
        )
    if len(treated_ids) != 10:
        raise SystemExit(f"expected 10 treated controls, got {len(treated_ids)}")

    unsure_ids = [r["variant_id"] for r in rows if meaning_unsure(r["meaning_preserved"])]
    yes_rows = [r for r in rows if meaning_yes(r["meaning_preserved"])]
    yes_ids = [r["variant_id"] for r in yes_rows]
    if len(yes_ids) != 47:
        raise SystemExit(f"expected 47 meaning_preserved=yes rewritten rows, got {len(yes_ids)}")

    successes, jsonl_meta = load_successes(jsonl_path)
    extra = sorted({vid for vid, _ in successes} - set(yes_ids))
    missing = sorted(set(yes_ids) - {vid for vid, _ in successes})
    if extra:
        raise SystemExit(f"phase5.jsonl has variants not marked yes: {extra}")
    if missing:
        raise SystemExit(f"phase5.jsonl missing yes variants: {missing}")
    if len(successes) != 141:
        raise SystemExit(
            f"expected 141 unique successful Phase 5 keys, got {len(successes)}"
        )
    if jsonl_meta["n_fail"] != 0:
        raise SystemExit(f"expected 0 Phase 5 failures, got {jsonl_meta['n_fail']}")

    by_var: dict[str, dict[int, str]] = defaultdict(dict)
    for (vid, replica), rec in successes.items():
        if rec.get("model") != MODEL:
            raise SystemExit(f"{vid} r{replica} model={rec.get('model')!r} expected {MODEL}")
        if rec.get("temperature") != TEMPERATURE:
            raise SystemExit(
                f"{vid} r{replica} temperature={rec.get('temperature')!r} expected {TEMPERATURE}"
            )
        verdict = rec["verdict"]
        if verdict not in FIVE_WAY:
            raise SystemExit(f"{vid} r{replica} unknown verdict {verdict!r}")
        by_var[vid][replica] = verdict

    missing_rep = []
    for vid in yes_ids:
        have = set(by_var[vid])
        if have != {1, 2, 3}:
            missing_rep.append(f"{vid} has replicas {sorted(have)}")
    if missing_rep:
        raise SystemExit("Phase 5 missing replica(s):\n  " + "\n  ".join(missing_rep))

    n_raw = cross_check_raw(successes, raw_dir)
    jsonl_meta["n_raw_checked"] = n_raw

    var_verdicts = {vid: [by_var[vid][1], by_var[vid][2], by_var[vid][3]] for vid in yes_ids}
    var_majority = {vid: majority(vs) for vid, vs in var_verdicts.items()}
    var_unanimous = {vid: len(set(vs)) == 1 for vid, vs in var_verdicts.items()}
    n_unanimous = sum(1 for u in var_unanimous.values() if u)
    n_noisy = 47 - n_unanimous
    n_split = sum(1 for m in var_majority.values() if m == "split")
    n_two_one = n_noisy - n_split
    split_ids = sorted(vid for vid, m in var_majority.items() if m == "split")

    census = Counter(rec["verdict"] for rec in successes.values())
    for status in FIVE_WAY:
        if status != "split":
            census.setdefault(status, 0)
    if sum(census.values()) != 141:
        raise SystemExit("Phase 5 census does not sum to 141")

    per_control = []
    flipped_after = []
    for cid in treated_order:
        vids = sorted(
            (r["variant_id"] for r in yes_rows if r["control_id"] == cid),
            key=variant_sort_key,
        )
        majs = [var_majority[v] for v in vids]
        is_flip = len(set(majs)) > 1
        rec = {
            "control_id": cid,
            "n_variants_scored": len(vids),
            "variant_ids": vids,
            "majority_verdicts": majs,
            "majority_by_variant": {v.split(".")[-1]: var_majority[v] for v in vids},
            "majority_cell": fmt_maj_cell(majs),
            "flips": is_flip,
        }
        per_control.append(rec)
        if is_flip:
            flipped_after.append(cid)

    n_flipped_after = len(flipped_after)
    n_treated = 10
    n_reduced = n_treated - n_flipped_after
    no_longer = [cid for cid in treated_order if cid not in flipped_after]

    noisy_variants = []
    for vid in yes_ids:
        if not var_unanimous[vid]:
            noisy_variants.append(
                {
                    "variant_id": vid,
                    "replicas": var_verdicts[vid],
                    "majority": var_majority[vid],
                }
            )

    return {
        "jsonl": jsonl_meta,
        "unsure_excluded": unsure_ids,
        "n_yes_variants": 47,
        "n_success": 141,
        "y": {
            "status": "run",
            "n_treated": n_treated,
            "n_flipped_before": n_treated,
            "n_flipped_after": n_flipped_after,
            "n_reduced": n_reduced,
            "rate_reduction": n_reduced / n_treated,
            "percent": pct_num(n_reduced, n_treated),
            "flipped_after_ids": flipped_after,
            "no_longer_flip_ids": no_longer,
            "unsure_excluded": unsure_ids,
            "note": "Y = (10 - n_flipped_after)/10 on the 10 treated controls; unsure rows excluded",
        },
        "x2": {
            "n_flipped": n_flipped_after,
            "n_controls": 40,
            "rate": n_flipped_after / 40,
            "percent": pct_num(n_flipped_after, 40),
            "note": "n_flipped_after / 40; 30 untreated counted as still non-flipping",
        },
        "noise": {
            "n_variants": 47,
            "n_unanimous": n_unanimous,
            "n_noisy": n_noisy,
            "n_two_one": n_two_one,
            "n_split": n_split,
            "rate": n_noisy / 47,
            "percent": pct_num(n_noisy, 47),
            "split_ids": split_ids,
            "noisy_variants": noisy_variants,
        },
        "verdict_census": {
            "n": 141,
            "counts": dict(census),
        },
        "per_control": per_control,
        "treated_ids": treated_order,
    }


def build_results_md(d: dict) -> str:
    x = d["x"]
    x39 = d["x_39"]
    noise = d["noise"]
    census = d["verdict_census"]
    para = d["paraphrase_vs_v0"]
    vocab = d["flip_by_vocab_pattern"]
    cut = d["qualifier_present_vs_specific"]
    sens = d["sensitivity_3way"]
    flipped = d["flipped_controls"]
    hash_hex = d["hash"]
    y = d["y"]
    x2 = d.get("x2") or {}
    p5 = d.get("phase5") or {}

    census_rows = []
    for status in (
        "not-satisfied",
        "partially-satisfied",
        "satisfied",
        "insufficient-evidence",
        "not-applicable",
    ):
        n = census["counts"].get(status, 0)
        census_rows.append([status, str(n), f"{pct_num(n, 600):.1f}%"])
    census_rows.append(["**total**", "**600**", "**100.0%**"])

    vocab_rows = []
    for pat in ("vague-qualifier", "specific", "mixed"):
        cell = vocab[pat]
        vocab_rows.append(
            [pat, str(cell["n_controls"]), str(cell["n_flipped"]), pct(cell["n_flipped"], cell["n_controls"])]
        )

    cut_rows = [
        [
            "qualifier-present (vague-qualifier + mixed)",
            str(cut["qualifier_present"]["n_controls"]),
            str(cut["qualifier_present"]["n_flipped"]),
            pct(cut["qualifier_present"]["n_flipped"], cut["qualifier_present"]["n_controls"]),
        ],
        [
            "specific",
            str(cut["specific"]["n_controls"]),
            str(cut["specific"]["n_flipped"]),
            pct(cut["specific"]["n_flipped"], cut["specific"]["n_controls"]),
        ],
    ]

    flip_rows = []
    for rec in flipped:
        cells = [rec["control_id"], rec["vocab_pattern"], str(rec["n_variants_scored"])]
        maj = rec["majority_by_variant"]
        for tag in ("v0", "v1", "v2", "v3", "v4"):
            vid = f"{rec['control_id']}.{tag}"
            if vid == EXCLUDE_VARIANT and vid not in maj:
                cells.append("— (excluded)")
            else:
                cells.append(maj.get(tag, "—"))
        flip_rows.append(cells)

    sens_vocab_rows = []
    for pat in ("vague-qualifier", "specific", "mixed"):
        cell = sens["flip_by_vocab_pattern"][pat]
        sens_vocab_rows.append(
            [pat, str(cell["n_controls"]), str(cell["n_flipped"]), pct(cell["n_flipped"], cell["n_controls"])]
        )

    sens_flip_rows = []
    for rec in sens["flipped_controls"]:
        cells = [rec["control_id"], rec["vocab_pattern"], str(rec["n_variants_scored"])]
        maj = rec["majority_by_variant"]
        for tag in ("v0", "v1", "v2", "v3", "v4"):
            cells.append(maj.get(tag, "—"))
        sens_flip_rows.append(cells)

    sens_census_rows = []
    for status in ("not-satisfied", "satisfied", "undetermined"):
        n = sens["replica_census"]["counts"].get(status, 0)
        sens_census_rows.append([status, str(n), f"{pct_num(n, 600):.1f}%"])
    n_na_mapped = census["counts"].get("not-applicable", 0)
    n_ps_mapped = census["counts"].get("partially-satisfied", 0)

    if y.get("status") == "not_run":
        y_block = ["**Y = not run.** Phase 5 rewriting has not started.", ""]
    else:
        y_block = [
            f"**Y = {y['percent']:.1f}%** reduction in flip rate on the {y['n_treated']} treated controls "
            f"({y['n_flipped_before']}/{y['n_treated']} flipped before rewrite, "
            f"{y['n_flipped_after']}/{y['n_treated']} after).",
            "",
        ]
        if x2:
            y_block += [f"**X2 = {pct(x2['n_flipped'], x2['n_controls'])}**.", ""]

    lines = [
        "# Control-Wording Variance Study — results (Phases 4 and 5)",
        "",
        f"**X = {pct(x['n_flipped'], x['n_controls'])}** (primary, 5-way majority; SI-4 scored on v0,v2,v3,v4 only).",
        "",
        *y_block,
        f"Frozen evidence SHA-256 of `evidence/model-stale.json`: `{hash_hex}` (match vs `evidence/HASH.txt` and the Phase 1 freeze).",
        "",
        "## SI-4.v1 exclusion",
        "",
        "SI-4.v1 was rewritten after review and is still unmarked (`meaning_preserved` blank). It is **excluded** from SI-4's variant set for X, for the vocab-pattern flip tables, and for paraphrase-vs-v0. SI-4 therefore contributes to primary X using **v0, v2, v3, v4 only (4 variants)**. Those four majority verdicts are all `not-satisfied` (no flip). Sensitivity **X_39** drops SI-4 entirely. SI-4.v1's three replica judgments still sit in the 600-row census and in the noise denominator, because that variant has three successful replicas.",
        "",
        "## Verdict census (600 replica judgments)",
        "",
        "Last successful jsonl record per `variant_id`+`replica`. Failed credit-crash rows ignored. All 200 variants × 3 replicas present. Model `claude-sonnet-4-6`, temperature `0` on every success.",
        "",
        md_table(["status (5-way)", "n", "share"], census_rows),
        "",
        f"jsonl lines read: {d['jsonl']['n_lines']}. Successful keys: 600. Failed credit-crash rows ignored: {d['jsonl']['n_credit']}. Raw-report cross-check: {d['jsonl']['n_raw_checked']}/600 verdicts match.",
        "",
        "## Model noise (5-way)",
        "",
        f"**{pct(noise['n_noisy'], noise['n_variants'])}** of variants with 3 successful replicas are not unanimous.",
        "",
        md_table(
            ["", "n", "share of 200"],
            [
                ["unanimous (3 identical replica verdicts)", str(noise["n_unanimous"]), pct(noise["n_unanimous"], 200)],
                ["not unanimous (model noise)", str(noise["n_noisy"]), pct(noise["n_noisy"], 200)],
                ["2-1 majority (subset of noisy)", str(noise["n_two_one"]), pct(noise["n_two_one"], 200)],
                ["1-1-1 split (subset of noisy)", str(noise["n_split"]), pct(noise["n_split"], 200)],
            ],
        ),
        "",
        "The single 1–1–1 variant is `CM-2.v4` (`partially-satisfied`, `insufficient-evidence`, `not-satisfied`) → majority `split`.",
        "",
        "## Primary X (5-way wording variance)",
        "",
        "A control **flips** when its scored variant majority verdicts are not all identical.",
        "",
        md_table(
            ["metric", "value"],
            [
                ["X (40 controls; SI-4 uses 4 variants)", pct(x["n_flipped"], x["n_controls"])],
                ["X_39 (drop SI-4 entirely)", pct(x39["n_flipped"], x39["n_controls"])],
                ["SI-4 itself (v0,v2,v3,v4)", "no flip (4× not-satisfied)"],
            ],
        ),
        "",
        "## Flipped control IDs (5-way majority verdicts)",
        "",
        f"{x['n_flipped']} controls flip. Each cell is the 3-replica majority (or `split`).",
        "",
        md_table(["control_id", "vocab_pattern", "n_scored", "v0", "v1", "v2", "v3", "v4"], flip_rows),
        "",
        "## Flip by vocab_pattern (tagged on v0; 5-way)",
        "",
        md_table(["vocab_pattern", "n controls", "n flipped", "flip rate"], vocab_rows),
        "",
        "## Qualifier-present vs specific (hypothesis cut; 5-way)",
        "",
        "qualifier-present = vague-qualifier + mixed, vs specific. Jose accepted this cut. The table is complete; it is described below, not treated as a hypothesis test decision.",
        "",
        md_table(["cut", "n controls", "n flipped", "flip rate"], cut_rows),
        "",
        f"qualifier-present flipped **{pct(cut['qualifier_present']['n_flipped'], cut['qualifier_present']['n_controls'])}**; specific flipped **{pct(cut['specific']['n_flipped'], cut['specific']['n_controls'])}**. Specific controls flipped more often in this 40-control set. Vague-qualifier alone is {pct(vocab['vague-qualifier']['n_flipped'], vocab['vague-qualifier']['n_controls'])} (AC-6, RA-7, SA-8(32), SI-12; none flipped). Mixed is {pct(vocab['mixed']['n_flipped'], vocab['mixed']['n_controls'])} (flips: CM-2, SA-4(8)). The numbers do not show a higher wording-variance rate for qualifier-present wording than for specific wording.",
        "",
        "## Paraphrase-vs-v0 (5-way)",
        "",
        "Denominator = meaning-preserved `yes` paraphrases (variant ≠ v0), skipping SI-4.v1. That is 159 rows (160 paraphrases minus the unmarked SI-4.v1).",
        "",
        md_table(
            ["", "n"],
            [
                ["meaning-preserved paraphrases scored", str(para["n_paraphrases"])],
                ["majority differs from that control's v0 majority", str(para["n_differ"])],
                ["share", pct(para["n_differ"], para["n_paraphrases"])],
            ],
        ),
        "",
        "All 22 differing paraphrases sit inside the 10 flipped controls listed above (no control has a paraphrase/v0 majority disagreement without also flipping as a control).",
        "",
        "## 3-way sensitivity",
        "",
        "Map applied to each replica verdict, then majority and noise recomputed. `satisfied`→`satisfied`; `not-satisfied`→`not-satisfied`; `insufficient-evidence`→`undetermined`; `partially-satisfied`→`not-satisfied` (OSCAL fail-closed); `not-applicable`→`not-satisfied`; `split` stays `split` if the mapped triple is still 1–1–1.",
        "",
        md_table(
            ["metric", "5-way (primary)", "3-way (sensitivity)"],
            [
                [
                    "model noise",
                    pct(noise["n_noisy"], noise["n_variants"]),
                    pct(sens["noise"]["n_noisy"], sens["noise"]["n_variants"]),
                ],
                [
                    "X (40; SI-4 uses 4 variants)",
                    pct(x["n_flipped"], x["n_controls"]),
                    pct(sens["x"]["n_flipped"], sens["x"]["n_controls"]),
                ],
                [
                    "X_39 (drop SI-4)",
                    pct(x39["n_flipped"], x39["n_controls"]),
                    pct(sens["x_39"]["n_flipped"], sens["x_39"]["n_controls"]),
                ],
                [
                    "paraphrase-vs-v0",
                    pct(para["n_differ"], para["n_paraphrases"]),
                    pct(sens["paraphrase_vs_v0"]["n_differ"], sens["paraphrase_vs_v0"]["n_paraphrases"]),
                ],
            ],
        ),
        "",
        "Replica census after the map (same 600 judgments):",
        "",
        md_table(["status (3-way)", "n", "share"], sens_census_rows),
        "",
        f"`partially-satisfied` ({n_ps_mapped}) and `not-applicable` ({n_na_mapped}) are folded into `not-satisfied`. `insufficient-evidence` ({census['counts'].get('insufficient-evidence', 0)}) becomes `undetermined`.",
        "",
        "3-way flip by vocab_pattern:",
        "",
        md_table(["vocab_pattern", "n controls", "n flipped", "flip rate"], sens_vocab_rows),
        "",
        "3-way qualifier-present vs specific: "
        f"qualifier-present {pct(sens['qualifier_present_vs_specific']['qualifier_present']['n_flipped'], sens['qualifier_present_vs_specific']['qualifier_present']['n_controls'])}; "
        f"specific {pct(sens['qualifier_present_vs_specific']['specific']['n_flipped'], sens['qualifier_present_vs_specific']['specific']['n_controls'])}.",
        "",
        "3-way flipped controls (majority after the map):",
        "",
        md_table(["control_id", "vocab_pattern", "n_scored", "v0", "v1", "v2", "v3", "v4"], sens_flip_rows)
        if sens_flip_rows
        else "_none_",
        "",
        "Most 5-way flips are `not-satisfied` ↔ `partially-satisfied` (and one `split`). Those collapse under fail-closed mapping, so 3-way X is **"
        + pct(sens["x"]["n_flipped"], sens["x"]["n_controls"])
        + "** on AC-6(9) and AU-8 only — the two controls whose majority moves between `satisfied` and `not-satisfied`.",
        "",
        "## What the numbers say",
        "",
        f"On this frozen stale-model fixture, with temperature 0 and `claude-sonnet-4-6`, **{x['n_flipped']} of {x['n_controls']} controls change 5-way majority verdict when the official statement is paraphrased** ({pct(x['n_flipped'], x['n_controls'])}). Replica disagreement is material: **{pct(noise['n_noisy'], 200)}** of variants are not unanimous even at temperature 0. Collapsing to OSCAL's fail-closed 3-way drops wording variance to **{pct(sens['x']['n_flipped'], 40)}**. The qualifier-present vs specific table is complete: specific wording flipped more ({pct(cut['specific']['n_flipped'], cut['specific']['n_controls'])}) than qualifier-present ({pct(cut['qualifier_present']['n_flipped'], cut['qualifier_present']['n_controls'])}). That is a description of these 40 controls, not a confirmation or rejection of the hypothesis beyond the table.",
        "",
        "## Phase 5 (rewritten 10; scored from `runs/phase5.jsonl`)",
        "",
    ]

    if y.get("status") == "not_run" or not p5:
        lines += [
            "Not started. **Y** is a placeholder until Jose accepts X (or asks to proceed).",
            "",
        ]
        return "\n".join(lines)

    unsure = p5.get("unsure_excluded") or y.get("unsure_excluded") or []
    unsure_fmt = ", ".join(f"`{u}`" for u in unsure)
    noise5 = p5["noise"]
    census5 = p5["verdict_census"]["counts"]
    p5_rows = []
    for rec in p5["per_control"]:
        flag = "**yes**" if rec["flips"] else "no"
        p5_rows.append(
            [
                rec["control_id"],
                str(rec["n_variants_scored"]),
                flag,
                rec["majority_cell"],
            ]
        )
    census5_bits = []
    for status in (
        "not-satisfied",
        "partially-satisfied",
        "satisfied",
        "insufficient-evidence",
        "not-applicable",
    ):
        n = census5.get(status, 0)
        if n or status != "not-applicable":
            census5_bits.append(f"{status} {n}")
    split_note = ""
    if noise5.get("split_ids"):
        hosts = sorted({vid.rsplit(".", 1)[0] for vid in noise5["split_ids"]})
        if len(hosts) == 1:
            split_note = f" (including {noise5['n_split']} splits, both on {hosts[0]})" if noise5["n_split"] == 2 else f" (including {noise5['n_split']} splits on {hosts[0]}: {', '.join(noise5['split_ids'])})"
        else:
            split_note = f" (including {noise5['n_split']} splits: {', '.join(noise5['split_ids'])})"
    remaining = ", ".join(y["flipped_after_ids"])
    stable = ", ".join(y["no_longer_flip_ids"])
    n_yes = p5.get("n_yes_variants", 47)
    n_succ = p5.get("n_success", 141)

    lines += [
        f"Jose reviewed 50 rewritten rows: {n_yes} `yes`, {len(unsure)} `unsure` ({unsure_fmt}). Unsure rows excluded. {n_yes} variants × 3 replicas = **{n_succ}** assessments, all successful, temperature 0, model `claude-sonnet-4-6`. Frozen hash unchanged.",
        "",
        f"**Y = {y['percent']:.1f}%** reduction in flip rate on the 10 treated controls: 10/10 flipped before rewrite, **{y['n_flipped_after']}/10 after** ({remaining}).",
        "",
        f"**X2 = {pct(x2['n_flipped'], x2['n_controls'])}** (the 30 untreated controls counted as still non-flipping; the {y['n_flipped_after']} remaining flips are the only wording-variance left on the original 40-control denominator).",
        "",
        md_table(["control_id", "n scored after review", "flipped after?", "majorities"], p5_rows),
        "",
        f"Model noise on the rewritten set: **{pct(noise5['n_noisy'], noise5['n_variants'])}** of variants not unanimous{split_note}. That is higher than Phase 3 noise ({pct(noise['n_noisy'], noise['n_variants'])}). Y is still a wording-variance reduction on majority verdicts; the noise rate is reported beside it.",
        "",
        f"Replica census ({n_succ}): {', '.join(census5_bits)}.",
        "",
        f"No longer flip: {stable}.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    root = study_root()
    jsonl_path = root / "runs" / "phase3.jsonl"
    csv_path = root / "controls" / "control_set.reviewed.csv"
    raw_dir = root / "runs" / "raw"
    results_path = root / "RESULTS.md"
    tables_path = root / "analysis" / "tables.json"

    computed_hash = verify_hash(root)
    print(f"HASH ok {computed_hash}", flush=True)

    if not jsonl_path.is_file():
        raise SystemExit(f"missing {jsonl_path}")
    successes, jsonl_meta = load_successes(jsonl_path)

    if len(successes) != N_SUCCESS:
        raise SystemExit(
            f"expected {N_SUCCESS} unique successful variant+replica keys, got {len(successes)}"
        )

    keys = set(successes)
    variants = sorted({vid for vid, _ in keys})
    if len(variants) != 200:
        raise SystemExit(f"expected 200 variants with successes, got {len(variants)}")

    missing = []
    by_var: dict[str, dict[int, str]] = defaultdict(dict)
    for (vid, replica), rec in successes.items():
        if rec.get("model") != MODEL:
            raise SystemExit(f"{vid} r{replica} model={rec.get('model')!r} expected {MODEL}")
        if rec.get("temperature") != TEMPERATURE:
            raise SystemExit(
                f"{vid} r{replica} temperature={rec.get('temperature')!r} expected {TEMPERATURE}"
            )
        llm_model = rec.get("llm_model")
        if llm_model not in (None, MODEL):
            raise SystemExit(f"{vid} r{replica} llm_model={llm_model!r}")
        llm_temp = rec.get("llm_temperature")
        if llm_temp not in (None, TEMPERATURE):
            raise SystemExit(f"{vid} r{replica} llm_temperature={llm_temp!r}")
        verdict = rec["verdict"]
        if verdict not in FIVE_WAY:
            raise SystemExit(f"{vid} r{replica} unknown verdict {verdict!r}")
        by_var[vid][replica] = verdict

    for vid in variants:
        have = set(by_var[vid])
        if have != {1, 2, 3}:
            missing.append(f"{vid} has replicas {sorted(have)}")
    if missing:
        raise SystemExit("missing replica(s):\n  " + "\n  ".join(missing))

    n_raw = cross_check_raw(successes, raw_dir)
    jsonl_meta["n_raw_checked"] = n_raw

    rows, meta = load_csv(csv_path)
    csv_vids = set(meta)
    if csv_vids != set(variants):
        raise SystemExit(
            f"CSV/jsonl variant_id mismatch: only-csv={sorted(csv_vids-set(variants))[:5]} "
            f"only-jsonl={sorted(set(variants)-csv_vids)[:5]}"
        )
    if EXCLUDE_VARIANT not in meta:
        raise SystemExit(f"{EXCLUDE_VARIANT} missing from CSV")
    if meta[EXCLUDE_VARIANT]["meaning_preserved"].strip() == "yes":
        # still exclude; record the surprise
        print(
            f"NOTE: {EXCLUDE_VARIANT} is marked meaning_preserved=yes but Phase 4 still excludes it.",
            flush=True,
        )

    controls = control_order(rows)
    if len(controls) != N_CONTROLS:
        raise SystemExit(f"expected {N_CONTROLS} controls, got {len(controls)}")

    v0_pattern = {}
    for r in rows:
        if r["variant"] == "0":
            v0_pattern[r["control_id"]] = r["vocab_pattern"]
    if len(v0_pattern) != N_CONTROLS:
        raise SystemExit("expected one v0 vocab_pattern per control")

    var_verdicts = {vid: [by_var[vid][1], by_var[vid][2], by_var[vid][3]] for vid in variants}
    var_majority = {vid: majority(vs) for vid, vs in var_verdicts.items()}
    var_unanimous = {vid: len(set(vs)) == 1 for vid, vs in var_verdicts.items()}

    n_unanimous = sum(1 for u in var_unanimous.values() if u)
    n_noisy = 200 - n_unanimous
    n_split = sum(1 for m in var_majority.values() if m == "split")
    n_two_one = n_noisy - n_split

    census = Counter(rec["verdict"] for rec in successes.values())
    for status in FIVE_WAY:
        if status != "split":
            census.setdefault(status, 0)
    if sum(census.values()) != 600:
        raise SystemExit("census does not sum to 600")

    def flips_for(maj_map: dict[str, str]) -> tuple[list[dict], int]:
        flipped = []
        n39 = 0
        for cid in controls:
            vids = variant_ids_for(cid, rows, exclude=True)
            majs = [maj_map[v] for v in vids]
            is_flip = len(set(majs)) > 1
            rec = {
                "control_id": cid,
                "vocab_pattern": v0_pattern[cid],
                "n_variants_scored": len(vids),
                "variant_ids": vids,
                "majority_verdicts": majs,
                "majority_by_variant": {v.split(".")[-1]: maj_map[v] for v in vids},
                "flips": is_flip,
            }
            if is_flip:
                flipped.append(rec)
            if cid != "SI-4" and len(set(maj_map[v] for v in variant_ids_for(cid, rows, exclude=False))) > 1:
                n39 += 1
        return flipped, n39

    flipped, n39 = flips_for(var_majority)
    n_flipped = len(flipped)

    # vocab 3-way
    vocab_counts = {p: {"n_controls": 0, "n_flipped": 0, "flipped_ids": []} for p in ("vague-qualifier", "specific", "mixed")}
    for cid in controls:
        pat = v0_pattern[cid]
        vids = variant_ids_for(cid, rows, exclude=True)
        is_flip = len({var_majority[v] for v in vids}) > 1
        vocab_counts[pat]["n_controls"] += 1
        if is_flip:
            vocab_counts[pat]["n_flipped"] += 1
            vocab_counts[pat]["flipped_ids"].append(cid)

    qp_ids = [cid for cid in controls if v0_pattern[cid] in ("vague-qualifier", "mixed")]
    sp_ids = [cid for cid in controls if v0_pattern[cid] == "specific"]
    qp_flipped = [cid for cid in qp_ids if len({var_majority[v] for v in variant_ids_for(cid, rows)}) > 1]
    sp_flipped = [cid for cid in sp_ids if len({var_majority[v] for v in variant_ids_for(cid, rows)}) > 1]

    para_n = 0
    para_diff = 0
    para_diff_ids = []
    for r in rows:
        if r["variant"] == "0":
            continue
        if r["variant_id"] == EXCLUDE_VARIANT:
            continue
        if r["meaning_preserved"].strip() != "yes":
            continue
        para_n += 1
        v0_id = f"{r['control_id']}.v0"
        if var_majority[r["variant_id"]] != var_majority[v0_id]:
            para_diff += 1
            para_diff_ids.append(
                {
                    "variant_id": r["variant_id"],
                    "v0_majority": var_majority[v0_id],
                    "paraphrase_majority": var_majority[r["variant_id"]],
                }
            )
    if para_n != 159:
        raise SystemExit(f"expected 159 meaning-preserved paraphrases excluding {EXCLUDE_VARIANT}, got {para_n}")

    # 3-way
    var_verdicts3 = {vid: [map3(s) for s in vs] for vid, vs in var_verdicts.items()}
    var_majority3 = {vid: majority(vs) for vid, vs in var_verdicts3.items()}
    var_unanimous3 = {vid: len(set(vs)) == 1 for vid, vs in var_verdicts3.items()}
    n_unanimous3 = sum(1 for u in var_unanimous3.values() if u)
    n_noisy3 = 200 - n_unanimous3
    n_split3 = sum(1 for m in var_majority3.values() if m == "split")
    flipped3, n39_3 = flips_for(var_majority3)

    vocab3 = {p: {"n_controls": 0, "n_flipped": 0, "flipped_ids": []} for p in ("vague-qualifier", "specific", "mixed")}
    for cid in controls:
        pat = v0_pattern[cid]
        vids = variant_ids_for(cid, rows, exclude=True)
        is_flip = len({var_majority3[v] for v in vids}) > 1
        vocab3[pat]["n_controls"] += 1
        if is_flip:
            vocab3[pat]["n_flipped"] += 1
            vocab3[pat]["flipped_ids"].append(cid)
    qp_flipped3 = [cid for cid in qp_ids if len({var_majority3[v] for v in variant_ids_for(cid, rows)}) > 1]
    sp_flipped3 = [cid for cid in sp_ids if len({var_majority3[v] for v in variant_ids_for(cid, rows)}) > 1]

    para_diff3 = 0
    para_diff_ids3 = []
    for r in rows:
        if r["variant"] == "0" or r["variant_id"] == EXCLUDE_VARIANT:
            continue
        if r["meaning_preserved"].strip() != "yes":
            continue
        v0_id = f"{r['control_id']}.v0"
        if var_majority3[r["variant_id"]] != var_majority3[v0_id]:
            para_diff3 += 1
            para_diff_ids3.append(
                {
                    "variant_id": r["variant_id"],
                    "v0_majority": var_majority3[v0_id],
                    "paraphrase_majority": var_majority3[r["variant_id"]],
                }
            )

    census3 = Counter(map3(rec["verdict"]) for rec in successes.values())

    noisy_variants = []
    for vid in variants:
        if not var_unanimous[vid]:
            noisy_variants.append(
                {
                    "variant_id": vid,
                    "replicas": var_verdicts[vid],
                    "majority": var_majority[vid],
                }
            )
    noisy_variants3 = []
    for vid in variants:
        if not var_unanimous3[vid]:
            noisy_variants3.append(
                {
                    "variant_id": vid,
                    "replicas": var_verdicts3[vid],
                    "majority": var_majority3[vid],
                }
            )

    all_majorities = []
    for cid in controls:
        vids = variant_ids_for(cid, rows, exclude=True)
        all_majorities.append(
            {
                "control_id": cid,
                "vocab_pattern": v0_pattern[cid],
                "n_variants_scored": len(vids),
                "majority_by_variant": {v.split(".")[-1]: var_majority[v] for v in vids},
                "majority_by_variant_3way": {v.split(".")[-1]: var_majority3[v] for v in vids},
                "flips_5way": len({var_majority[v] for v in vids}) > 1,
                "flips_3way": len({var_majority3[v] for v in vids}) > 1,
            }
        )

    tables = {
        "hash": computed_hash,
        "expected_hash": EXPECTED_HASH,
        "hash_ok": True,
        "exclude_variant": EXCLUDE_VARIANT,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "jsonl": jsonl_meta,
        "x": {
            "n_flipped": n_flipped,
            "n_controls": 40,
            "rate": n_flipped / 40,
            "percent": pct_num(n_flipped, 40),
            "label": "5-way majority; SI-4 scored on v0,v2,v3,v4 only",
            "flipped_ids": [r["control_id"] for r in flipped],
        },
        "x_39": {
            "n_flipped": n39,
            "n_controls": 39,
            "rate": n39 / 39,
            "percent": pct_num(n39, 39),
            "label": "5-way majority; SI-4 dropped entirely",
        },
        "y": {
            "status": "pending_phase5",
            "note": "filled after Phase 5 scoring below",
        },
        "noise": {
            "n_variants": 200,
            "n_unanimous": n_unanimous,
            "n_noisy": n_noisy,
            "n_two_one": n_two_one,
            "n_split": n_split,
            "rate": n_noisy / 200,
            "percent": pct_num(n_noisy, 200),
            "noisy_variants": noisy_variants,
        },
        "verdict_census": {
            "n": 600,
            "counts": dict(census),
        },
        "flip_by_vocab_pattern": vocab_counts,
        "qualifier_present_vs_specific": {
            "qualifier_present": {
                "n_controls": len(qp_ids),
                "n_flipped": len(qp_flipped),
                "percent": pct_num(len(qp_flipped), len(qp_ids)),
                "control_ids": qp_ids,
                "flipped_ids": qp_flipped,
            },
            "specific": {
                "n_controls": len(sp_ids),
                "n_flipped": len(sp_flipped),
                "percent": pct_num(len(sp_flipped), len(sp_ids)),
                "control_ids": sp_ids,
                "flipped_ids": sp_flipped,
            },
        },
        "paraphrase_vs_v0": {
            "n_paraphrases": para_n,
            "n_differ": para_diff,
            "rate": para_diff / para_n,
            "percent": pct_num(para_diff, para_n),
            "differing": para_diff_ids,
            "note": "meaning_preserved=yes only; SI-4.v1 skipped",
        },
        "flipped_controls": flipped,
        "all_controls": all_majorities,
        "sensitivity_3way": {
            "map": dict(MAP_3WAY),
            "x": {
                "n_flipped": len(flipped3),
                "n_controls": 40,
                "rate": len(flipped3) / 40,
                "percent": pct_num(len(flipped3), 40),
                "flipped_ids": [r["control_id"] for r in flipped3],
            },
            "x_39": {
                "n_flipped": n39_3,
                "n_controls": 39,
                "rate": n39_3 / 39,
                "percent": pct_num(n39_3, 39),
            },
            "noise": {
                "n_variants": 200,
                "n_unanimous": n_unanimous3,
                "n_noisy": n_noisy3,
                "n_split": n_split3,
                "rate": n_noisy3 / 200,
                "percent": pct_num(n_noisy3, 200),
                "noisy_variants": noisy_variants3,
            },
            "replica_census": {"n": 600, "counts": dict(census3)},
            "flip_by_vocab_pattern": vocab3,
            "qualifier_present_vs_specific": {
                "qualifier_present": {
                    "n_controls": len(qp_ids),
                    "n_flipped": len(qp_flipped3),
                    "percent": pct_num(len(qp_flipped3), len(qp_ids)),
                    "flipped_ids": qp_flipped3,
                },
                "specific": {
                    "n_controls": len(sp_ids),
                    "n_flipped": len(sp_flipped3),
                    "percent": pct_num(len(sp_flipped3), len(sp_ids)),
                    "flipped_ids": sp_flipped3,
                },
            },
            "paraphrase_vs_v0": {
                "n_paraphrases": para_n,
                "n_differ": para_diff3,
                "percent": pct_num(para_diff3, para_n),
                "differing": para_diff_ids3,
            },
            "flipped_controls": flipped3,
        },
        "si4": {
            "excluded_variant": EXCLUDE_VARIANT,
            "scored_variants": variant_ids_for("SI-4", rows, exclude=True),
            "majority_5way": {v.split(".")[-1]: var_majority[v] for v in variant_ids_for("SI-4", rows, exclude=True)},
            "v1_replicas": var_verdicts.get(EXCLUDE_VARIANT),
            "v1_majority": var_majority.get(EXCLUDE_VARIANT),
            "flips": len({var_majority[v] for v in variant_ids_for("SI-4", rows, exclude=True)}) > 1,
        },
    }

    phase5 = score_phase5(root, [r["control_id"] for r in flipped])
    tables["y"] = phase5["y"]
    tables["x2"] = phase5["x2"]
    tables["phase5"] = phase5

    results_md = build_results_md(tables)
    results_path.write_text(results_md, encoding="utf-8")
    tables_path.write_text(json.dumps(tables, indent=2) + "\n", encoding="utf-8")

    print(f"X = {pct(n_flipped, 40)}", flush=True)
    print(f"X_39 = {pct(n39, 39)}", flush=True)
    print(f"noise = {pct(n_noisy, 200)}", flush=True)
    print(f"Y = {pct(phase5['y']['n_reduced'], phase5['y']['n_treated'])}", flush=True)
    print(f"X2 = {pct(phase5['x2']['n_flipped'], phase5['x2']['n_controls'])}", flush=True)
    print(f"phase5_noise = {pct(phase5['noise']['n_noisy'], phase5['noise']['n_variants'])}", flush=True)
    print(f"wrote {results_path}", flush=True)
    print(f"wrote {tables_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
