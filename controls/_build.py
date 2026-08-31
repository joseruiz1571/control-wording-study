#!/usr/bin/env python3
"""Build Phase 2 control_set.csv and sidecar docs from official v0 + paraphrases."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path("/workspace/control-wording-study")
CONTROLS = ROOT / "controls"
V0_PATH = CONTROLS / "_v0_official.json"
META_PATH = CONTROLS / "_meta.json"
CSV_PATH = CONTROLS / "control_set.csv"
SEL_PATH = CONTROLS / "SELECTION.md"
SRC_PATH = CONTROLS / "SOURCE.md"
DEC_PATH = ROOT / "DECISIONS.md"
REP_PATH = ROOT / "phase2-report.md"

ALLOWED_COLLECTORS = {
    "getModelRegistryEntry",
    "getModelCard",
    "getEndpointConfig",
    "getDataCaptureConfig",
    "getModelMonitorSchedules",
    "getKMSConfig",
    "getEndpointNetworkConfig",
    "getEndpointExecutionRole",
    "getCloudTrailEvents",
}
ALLOWED_PATTERNS = {"synthesis", "sufficiency", "correlation"}
ALLOWED_VOCAB = {"vague-qualifier", "specific", "mixed"}
CSV_FIELDS = [
    "control_id",
    "variant_id",
    "variant",
    "family",
    "nist_title",
    "vocab_pattern",
    "ml_reason",
    "mlassure_pattern",
    "collectors",
    "control_text",
    "meaning_preserved",
    "notes",
]

OSCAL_URL = "https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json"
XLSX_URL = "https://csrc.nist.gov/CSRC/media/Publications/sp/800-53/rev-5/final/documents/sp800-53r5-control-catalog.xlsx"
PDF_URL = "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf"

BRACKET = re.compile(r"\[(?:Assignment|Selection)[^\]]*\](?:\])?")
# Nested Selection containing Assignment: match from [Selection or [Assignment to matching close.
def extract_brackets(text: str) -> list[str]:
    """Extract NIST [Assignment: ...] and [Selection: ...] blocks, including nested ones."""
    blocks = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("[Assignment:", i) or text.startswith("[Selection:", i) or text.startswith("[Selection (", i):
            depth = 0
            j = i
            while j < n:
                if text[j] == "[":
                    depth += 1
                elif text[j] == "]":
                    depth -= 1
                    if depth == 0:
                        blocks.append(text[i : j + 1])
                        i = j + 1
                        break
                j += 1
            else:
                break
        else:
            i += 1
    return blocks


def norm_ws(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    parts = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.split("\n")]
    return " ".join(p for p in parts if p)


def family_of(cid: str) -> str:
    return cid.split("-", 1)[0]


def main() -> None:
    v0 = json.loads(V0_PATH.read_text())
    meta = json.loads(META_PATH.read_text())
    assert set(v0) == set(meta), f"id mismatch {set(v0)^set(meta)}"
    # Stable study order (favor AC AU CM RA SA SI, then limited SC/CA)
    order = [
        "AC-3", "AC-2(7)", "AC-5", "AC-6", "AC-6(5)", "AC-6(7)", "AC-6(9)", "AC-6(10)",
        "AU-2", "AU-3", "AU-6", "AU-6(3)", "AU-8", "AU-12", "AU-12(1)",
        "CM-2", "CM-3", "CM-3(1)", "CM-3(2)", "CM-6", "CM-7(1)", "CM-8", "CM-8(1)",
        "RA-3", "RA-7",
        "SA-10", "SA-10(5)", "SA-8(32)", "SA-4(8)", "SA-11",
        "SI-2", "SI-2(2)", "SI-4", "SI-4(2)", "SI-6", "SI-7", "SI-12",
        "SC-28(1)", "SC-7(5)",
        "CA-7",
    ]
    assert set(order) == set(meta) and len(order) == 40

    unsure: dict[tuple[str, int], str] = {}
    # Hand-marked unsure paraphrases (none currently; checker may add)
    rows = []
    issues = []
    for cid in order:
        off = v0[cid]
        md = meta[cid]
        v0_text = norm_ws(off["text"])
        title = off["title"]
        fam = family_of(cid)
        vocab = md["vocab_pattern"]
        pat = md["mlassure_pattern"]
        coll = md["collectors"]
        reason = md["ml_reason"]
        paras = md["paraphrases"]
        assert vocab in ALLOWED_VOCAB, cid
        assert pat in ALLOWED_PATTERNS, cid
        assert len(paras) == 4, cid
        assert all(c in ALLOWED_COLLECTORS for c in coll), (cid, coll)
        assert "[Withdrawn" not in v0_text
        v0_brackets = extract_brackets(v0_text)
        texts = [v0_text] + [norm_ws(p) for p in paras]
        for vi, text in enumerate(texts):
            notes = ""
            if vi == 0:
                notes = "v0: official NIST SP 800-53 Rev 5 statement copied from CSRC control-catalog xlsx (retrieved 2026-08-29); whitespace normalized only"
            else:
                missing = [b for b in v0_brackets if b not in text]
                if missing:
                    issues.append(f"{cid}.v{vi} missing brackets: {missing[:2]}")
                for bad in (" SHALL ", " shall ", " MUST ", " must "):
                    if bad in f" {text} " and bad.lower() not in f" {v0_text} ".lower():
                        issues.append(f"{cid}.v{vi} introduced {bad.strip()}")
                key = (cid, vi)
                if key in unsure:
                    notes = unsure[key]
            rows.append({
                "control_id": cid,
                "variant_id": f"{cid}.v{vi}",
                "variant": vi,
                "family": fam,
                "nist_title": title,
                "vocab_pattern": vocab,
                "ml_reason": reason,
                "mlassure_pattern": pat,
                "collectors": "|".join(coll),
                "control_text": text,
                "meaning_preserved": "",
                "notes": notes,
            })

    if issues:
        raise SystemExit("VALIDATION FAILED\n" + "\n".join(issues))

    # CSV
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # verify round-trip
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        got = list(csv.DictReader(f))
    assert len(got) == 200, len(got)
    assert len({r["variant_id"] for r in got}) == 200
    assert len({r["control_id"] for r in got}) == 40
    by = Counter(r["control_id"] for r in got)
    assert all(v == 5 for v in by.values())
    assert all(r["meaning_preserved"] == "" for r in got)
    for r in got:
        if r["variant"] == "0" or r["variant"] == 0:
            assert norm_ws(v0[r["control_id"]]["text"]) == r["control_text"]

    fam_c = Counter(r["family"] for r in got if r["variant"] == "0")
    vocab_c = Counter(r["vocab_pattern"] for r in got if r["variant"] == "0")
    pat_c = Counter(r["mlassure_pattern"] for r in got if r["variant"] == "0")
    unsure_n = sum(1 for r in got if r["notes"].startswith("unsure:"))

    # SELECTION.md
    sel_lines = [
        "# Phase 2 control selection (40 bases)",
        "",
        "Official NIST SP 800-53 Rev 5 statements (v0) with four meaning-preserving paraphrases each.",
        "All 40 use mlassure patterns `synthesis`, `sufficiency`, or `correlation` only.",
        "SC-28 and SC-7 (deterministic, code-keyed) and attestation controls are excluded.",
        "",
        "## Counts by family",
        "",
    ]
    for fam in ["AC", "AU", "CM", "RA", "SA", "SI", "SC", "CA"]:
        sel_lines.append(f"- **{fam}**: {fam_c.get(fam, 0)}")
    sel_lines += ["", "## Counts by vocab_pattern (tagged on v0, copied to all variants)", ""]
    for k in ["vague-qualifier", "specific", "mixed"]:
        sel_lines.append(f"- **{k}**: {vocab_c.get(k, 0)}")
    sel_lines += ["", "## Counts by mlassure_pattern", ""]
    for k in ["synthesis", "sufficiency", "correlation"]:
        sel_lines.append(f"- **{k}**: {pat_c.get(k, 0)}")
    sel_lines += ["", "## Bases", ""]
    for cid in order:
        md = meta[cid]
        off = v0[cid]
        sel_lines += [
            f"### {cid} — {off['title']}",
            "",
            f"- **vocab_pattern:** {md['vocab_pattern']}",
            f"- **mlassure_pattern:** {md['mlassure_pattern']}",
            f"- **collectors:** {' | '.join(md['collectors'])}",
            f"- **ml_reason:** {md['ml_reason']}",
            "",
        ]
    SEL_PATH.write_text("\n".join(sel_lines), encoding="utf-8")

    SRC_PATH.write_text(
        "\n".join(
            [
                "# Phase 2 catalog source",
                "",
                "## Retrieval",
                "",
                f"- Date: **2026-08-29** (box UTC; user zone America/Chicago).",
                f"- Preferred OSCAL JSON (fetched, SHA-256 `01f37cf90ea99d92242c936cbfbdebcc338eef1f71454e2acac36cc56e9bc062`): {OSCAL_URL}",
                "  - Catalog metadata: title *Electronic (OSCAL) Version of NIST SP 800-53 Rev 5.2.0 Controls and SP 800-53A Rev 5.2.0 Assessment Procedures*; version **5.2.0**; last-modified 2026-05-11T16:01:09Z; oscal-version 1.2.2; uuid `ea7c7688-79c5-463b-a91b-0650f2d98623`.",
                "  - Control statements in this file use `{{ insert: param, ... }}` placeholders, not published assignment prose.",
                f"- CSRC official spreadsheet (fetched; used for v0 prose): {XLSX_URL}",
                "  - Package title: *NIST SP 800-53, Revision 5 Security and Privacy Controls for Information Systems and Organizations*.",
                "  - Spreadsheet description: control catalog (includes errata updates) in spreadsheet format created from OSCAL (XML) file.",
                "  - core.xml modified 2025-02-12T20:39:59Z.",
                "  - Columns used: `Control Identifier`, `Control (or Control Enhancement) Name`, `Control Text`.",
                f"- nvlpubs PDF also fetched as a backup (not used for extraction): {PDF_URL}",
                "",
                "## How v0 was extracted",
                "",
                "- **Base controls** (no parentheses in the ID, e.g. AC-6, AU-3): v0 is the **control statement** from the spreadsheet `Control Text` column, whitespace-normalized (newlines/runs of space collapsed to a single space; no wording change).",
                "- **Enhancements** (parentheses in the ID, e.g. AC-6(9), SC-28(1)): v0 is the **control enhancement statement** from the same `Control Text` column, not the parent control statement, and not discussion/related-controls text.",
                "- `[Assignment: …]` and `[Selection: …]` / `[Selection (one or more): …]` strings are copied as published in the spreadsheet. They were not reconstructed from OSCAL param labels.",
                "- Titles (`nist_title`) are the spreadsheet `Control (or Control Enhancement) Name` values (enhancements use the `Parent | Enhancement` form).",
                "- Withdrawn statements (`[Withdrawn: …]`) were skipped (including SI-6(1), which mlassure's fixture had used as adapted intent).",
                "- v0 is **not** mlassure `fixtures/controls/nist-subset.yaml` `intent` text.",
                "",
                "## Why the spreadsheet rather than rendered OSCAL 5.2.0",
                "",
                "The brief prefers the OSCAL JSON URL. That file was fetched and used to confirm IDs, titles, withdrawn status, and family membership. v0 wording was copied from the CSRC spreadsheet because that file already contains the published assignment-rendered statements. Rendering `{{ insert: param }}` from OSCAL 5.2.0 would have been a reconstruction; a few ODP labels also differ slightly from the spreadsheet (e.g. AC-6(7) *roles and classes* vs *roles or classes of users*). The study needs copied official prose, so the spreadsheet wins for v0.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    dec_add = """
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
"""
    dec = DEC_PATH.read_text(encoding="utf-8")
    if "## Phase 2 — control set" not in dec:
        DEC_PATH.write_text(dec.rstrip() + "\n" + dec_add, encoding="utf-8")

    artifacts = [
        str(CSV_PATH),
        str(SEL_PATH),
        str(SRC_PATH),
        str(DEC_PATH),
        str(REP_PATH),
        str(ROOT / "evidence/model-stale.json"),
    ]
    report = f"""# Control-Wording Variance Study — Phase 2 report

## What I did

Fetched NIST SP 800-53 Rev 5 OSCAL JSON and the CSRC official control-catalog spreadsheet on 2026-08-29, and copied v0 statements from the spreadsheet (control statement or enhancement statement, whitespace-normalized only). Selected 40 bases the frozen SageMaker fixture can actually inform, using only synthesis, sufficiency, or correlation and the nine existing collectors. Wrote four meaning-preserving paraphrases per base (200 rows), left `meaning_preserved` empty for Jose, and did not modify `evidence/model-stale.json`, spend API money, push, or start Phase 3.

## Artifacts

- `{CSV_PATH}`
- `{SEL_PATH}`
- `{SRC_PATH}`
- `{DEC_PATH}` (Phase 2 section appended)
- `{REP_PATH}` (this file)
- Frozen evidence (unmodified): `{ROOT / "evidence/model-stale.json"}` SHA-256 `bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de`

## Judgment calls

- Excluded SC-28 and SC-7 (and any attestation control) because those paths never let wording change the verdict; included SC-28(1) and SC-7(5) as sufficiency instead.
- Used official catalog prose, not mlassure `intent`; dropped SI-6(1) (withdrawn) and AU-12(3) (official text is not what the fixture can assess).
- Tagged SA-10 as correlation from registry+CloudTrail, not attestation.
- Kept RA-3/SA-8(32) on getModelCard=null because absence can still flip insufficient-evidence vs not-satisfied; rejected PE/PS/RA-5 and other no-signal families.
- Recorded vocab_pattern as {vocab_c.get('vague-qualifier',0)} vague-qualifier / {vocab_c.get('specific',0)} specific / {vocab_c.get('mixed',0)} mixed rather than forcing 14/14/12.

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
"""
    REP_PATH.write_text(report, encoding="utf-8")

    ev = hashlib.sha256((ROOT / "evidence/model-stale.json").read_bytes()).hexdigest()
    print("rows", len(got), "controls", len(by), "unsure", unsure_n)
    print("family", dict(fam_c))
    print("vocab", dict(vocab_c))
    print("pattern", dict(pat_c))
    print("evidence", ev)
    print("csv", CSV_PATH, "bytes", CSV_PATH.stat().st_size)


if __name__ == "__main__":
    main()
