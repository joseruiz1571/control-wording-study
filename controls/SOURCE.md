# Phase 2 catalog source

## Retrieval

- Date: **2026-08-29** (box UTC; user zone America/Chicago).
- Preferred OSCAL JSON (fetched, SHA-256 `01f37cf90ea99d92242c936cbfbdebcc338eef1f71454e2acac36cc56e9bc062`): https://raw.githubusercontent.com/usnistgov/oscal-content/main/nist.gov/SP800-53/rev5/json/NIST_SP-800-53_rev5_catalog.json
  - Catalog metadata: title *Electronic (OSCAL) Version of NIST SP 800-53 Rev 5.2.0 Controls and SP 800-53A Rev 5.2.0 Assessment Procedures*; version **5.2.0**; last-modified 2026-05-11T16:01:09Z; oscal-version 1.2.2; uuid `ea7c7688-79c5-463b-a91b-0650f2d98623`.
  - Control statements in this file use `{{ insert: param, ... }}` placeholders, not published assignment prose.
- CSRC official spreadsheet (fetched; used for v0 prose): https://csrc.nist.gov/CSRC/media/Publications/sp/800-53/rev-5/final/documents/sp800-53r5-control-catalog.xlsx
  - Package title: *NIST SP 800-53, Revision 5 Security and Privacy Controls for Information Systems and Organizations*.
  - Spreadsheet description: control catalog (includes errata updates) in spreadsheet format created from OSCAL (XML) file.
  - core.xml modified 2025-02-12T20:39:59Z.
  - Columns used: `Control Identifier`, `Control (or Control Enhancement) Name`, `Control Text`.
- nvlpubs PDF also fetched as a backup (not used for extraction): https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf

## How v0 was extracted

- **Base controls** (no parentheses in the ID, e.g. AC-6, AU-3): v0 is the **control statement** from the spreadsheet `Control Text` column, whitespace-normalized (newlines/runs of space collapsed to a single space; no wording change).
- **Enhancements** (parentheses in the ID, e.g. AC-6(9), SC-28(1)): v0 is the **control enhancement statement** from the same `Control Text` column, not the parent control statement, and not discussion/related-controls text.
- `[Assignment: …]` and `[Selection: …]` / `[Selection (one or more): …]` strings are copied as published in the spreadsheet. They were not reconstructed from OSCAL param labels.
- Titles (`nist_title`) are the spreadsheet `Control (or Control Enhancement) Name` values (enhancements use the `Parent | Enhancement` form).
- Withdrawn statements (`[Withdrawn: …]`) were skipped (including SI-6(1), which mlassure's fixture had used as adapted intent).
- v0 is **not** mlassure `fixtures/controls/nist-subset.yaml` `intent` text.

## Why the spreadsheet rather than rendered OSCAL 5.2.0

The brief prefers the OSCAL JSON URL. That file was fetched and used to confirm IDs, titles, withdrawn status, and family membership. v0 wording was copied from the CSRC spreadsheet because that file already contains the published assignment-rendered statements. Rendering `{{ insert: param }}` from OSCAL 5.2.0 would have been a reconstruction; a few ODP labels also differ slightly from the spreadsheet (e.g. AC-6(7) *roles and classes* vs *roles or classes of users*). The study needs copied official prose, so the spreadsheet wins for v0.
