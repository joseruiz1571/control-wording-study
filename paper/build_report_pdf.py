#!/usr/bin/env python3
"""Build the Control-Wording Variance Study PDF report (private draft).

Usage:
    /workspace/.venv-pdf/bin/python build_report_pdf.py

Output:
    control-wording-variance-report.pdf  (same directory as this script)
"""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

OUT_DIR = Path(__file__).resolve().parent
OUT_PDF = OUT_DIR / "control-wording-variance-report.pdf"

# Typography
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# Palette (clean technical report — not Mileva branding)
CHARCOAL = (28, 32, 38)
CHARCOAL_MID = (45, 52, 62)
INK = (28, 32, 38)
MUTED = (90, 98, 110)
RULE = (200, 205, 212)
ACCENT = (55, 90, 120)
LIGHT_BG = (245, 247, 250)
WHITE = (255, 255, 255)
FINDING_MARK = (55, 90, 120)

SHORT_TITLE = "Control-Wording Variance Study"
EVIDENCE_HASH = (
    "bded936ec0b5c1c46c091d73e23952e5503e8e2dfe213acdba69711fc50e12de"
)


class ReportPDF(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=22)
        self.add_font("Sans", "", FONT_REG)
        self.add_font("Sans", "B", FONT_BOLD)
        self.add_font("Serif", "", FONT_SERIF)
        self.add_font("Serif", "B", FONT_SERIF_BOLD)
        self.add_font("Mono", "", FONT_MONO)
        self._suppress_footer = False
        self.set_margins(18, 18, 18)

    def header(self) -> None:
        return

    def footer(self) -> None:
        if self._suppress_footer:
            return
        self.set_y(-14)
        self.set_draw_color(*RULE)
        self.set_line_width(0.2)
        self.line(18, self.get_y(), 192, self.get_y())
        self.set_y(-12)
        self.set_font("Sans", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 5, SHORT_TITLE, align="L")
        self.set_x(18)
        self.cell(0, 5, str(self.page_no()), align="R")

    # --- helpers ---

    def section_heading(self, text: str) -> None:
        self.ln(3)
        self.set_font("Sans", "B", 14)
        self.set_text_color(*INK)
        self.multi_cell(0, 7, text.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.6)
        y = self.get_y() + 0.5
        self.line(18, y, 55, y)
        self.ln(5)

    def subheading(self, text: str) -> None:
        self.ln(2)
        self.set_font("Sans", "B", 11)
        self.set_text_color(*INK)
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.5)

    def body(self, text: str, size: float = 9.5, leading: float = 4.8) -> None:
        self.set_font("Sans", "", size)
        self.set_text_color(*INK)
        self.multi_cell(0, leading, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.5)

    def bullet(self, text: str, indent: float = 4, marker: str = "•") -> None:
        self.set_font("Sans", "", 9.5)
        self.set_text_color(*INK)
        x0 = self.l_margin
        self.set_x(x0 + indent)
        # marker
        self.set_font("Sans", "B", 9.5)
        self.cell(5, 4.8, marker)
        self.set_font("Sans", "", 9.5)
        w = self.w - self.r_margin - (x0 + indent + 5)
        self.multi_cell(w, 4.8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(0.8)

    def finding_bullet(self, letter: str, text: str) -> None:
        self.set_font("Sans", "B", 9.5)
        self.set_text_color(*FINDING_MARK)
        x0 = self.l_margin
        self.set_x(x0 + 2)
        mark = f"[{letter}]"
        self.cell(10, 4.8, mark)
        self.set_font("Sans", "", 9.5)
        self.set_text_color(*INK)
        w = self.w - self.r_margin - (x0 + 2 + 10)
        self.multi_cell(w, 4.8, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.2)

    def labeled_block(self, label: str, text: str) -> None:
        self.set_font("Sans", "B", 9.5)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 5, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.body(text)

    def ensure_space(self, mm: float) -> None:
        if self.get_y() + mm > self.h - self.b_margin:
            self.add_page()

    def simple_table(
        self,
        headers: list[str],
        rows: list[list[str]],
        col_widths: list[float] | None = None,
    ) -> None:
        n = len(headers)
        usable = self.w - self.l_margin - self.r_margin
        if col_widths is None:
            col_widths = [usable / n] * n
        row_h = 5.5

        def draw_row(cells: list[str], header: bool = False) -> None:
            # estimate height from tallest cell
            heights = []
            for i, cell in enumerate(cells):
                self.set_font("Sans", "B" if header else "", 8)
                lines = self.multi_cell(
                    col_widths[i], 4.2, cell, dry_run=True, output="LINES"
                )
                heights.append(max(row_h, 4.2 * len(lines) + 1.5))
            h = max(heights)
            self.ensure_space(h + 1)
            x_start = self.l_margin
            y_start = self.get_y()
            if header:
                self.set_fill_color(*CHARCOAL_MID)
                self.set_text_color(*WHITE)
                self.set_font("Sans", "B", 8)
            else:
                self.set_fill_color(*LIGHT_BG)
                self.set_text_color(*INK)
                self.set_font("Sans", "", 8)
            x = x_start
            for i, cell in enumerate(cells):
                self.set_xy(x, y_start)
                self.rect(x, y_start, col_widths[i], h, style="F" if header else "")
                if not header:
                    self.set_draw_color(*RULE)
                    self.set_line_width(0.15)
                    self.rect(x, y_start, col_widths[i], h, style="D")
                self.set_xy(x + 1.2, y_start + 0.8)
                self.multi_cell(col_widths[i] - 2.4, 4.2, cell)
                x += col_widths[i]
            self.set_y(y_start + h)

        draw_row(headers, header=True)
        for r in rows:
            draw_row(r, header=False)
        self.ln(3)

    def kv_row(self, key: str, value: str) -> None:
        self.set_font("Sans", "B", 9)
        self.set_text_color(*MUTED)
        self.cell(42, 5.2, key)
        self.set_font("Sans", "", 9)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.2, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build() -> Path:
    pdf = ReportPDF()

    # =====================================================================
    # COVER
    # =====================================================================
    pdf._suppress_footer = True
    pdf.add_page()
    # full-bleed charcoal
    pdf.set_fill_color(*CHARCOAL)
    pdf.rect(0, 0, 210, 297, style="F")

    # thin accent rule near top
    pdf.set_fill_color(*ACCENT)
    pdf.rect(18, 28, 40, 1.2, style="F")

    pdf.set_xy(18, 42)
    pdf.set_font("Sans", "", 9)
    pdf.set_text_color(160, 170, 185)
    pdf.cell(0, 5, "PRIVATE STUDY DRAFT  ·  STUDY ARCHIVE  ·  NOT PUBLISHED")

    pdf.set_xy(18, 58)
    pdf.set_font("Serif", "B", 26)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(
        174,
        11,
        "Same Control,\nDifferent Verdict",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_xy(18, pdf.get_y() + 6)
    pdf.set_font("Sans", "", 12)
    pdf.set_text_color(190, 198, 210)
    pdf.multi_cell(
        174,
        6.5,
        "Measuring How Control Wording Changes\n"
        "Automated AI Compliance Assessments",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.set_xy(18, pdf.get_y() + 10)
    pdf.set_draw_color(70, 80, 95)
    pdf.set_line_width(0.3)
    pdf.line(18, pdf.get_y(), 90, pdf.get_y())

    pdf.set_xy(18, pdf.get_y() + 8)
    pdf.set_font("Sans", "B", 11)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 6, "Jose Ruiz-Vazquez")

    pdf.set_xy(18, pdf.get_y() + 8)
    pdf.set_font("Sans", "", 9.5)
    pdf.set_text_color(170, 180, 195)
    pdf.multi_cell(
        174,
        5,
        "Control-Wording Variance Study\n"
        "Private study draft — August–September 2026\n"
        "PDF dated September 2026",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    # bottom band
    pdf.set_fill_color(*CHARCOAL_MID)
    pdf.rect(0, 260, 210, 37, style="F")
    pdf.set_xy(18, 268)
    pdf.set_font("Sans", "", 8.5)
    pdf.set_text_color(180, 188, 200)
    pdf.multi_cell(
        174,
        4.5,
        "Assessment tool: mlassure  ·  Model: claude-sonnet-4-6 (temperature 0)\n"
        "40 NIST SP 800-53 Rev 5 controls  ·  Frozen SageMaker-shaped evidence fixture\n"
        "This document is a private study archive. It has not been published.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    # =====================================================================
    # EXECUTIVE SUMMARY
    # =====================================================================
    pdf._suppress_footer = False
    pdf.add_page()
    pdf.section_heading("Executive Summary")

    pdf.subheading("Problem")
    pdf.body(
        "Organizations increasingly use large language models to assess whether AI "
        "systems satisfy security and governance controls such as those in NIST SP "
        "800-53 Revision 5. Those controls are written in English. English admits "
        "synonyms, sentence restructuring, and near-equivalent phrasing that a human "
        "reviewer can accept as meaning-preserving. If an automated assessor changes "
        "its verdict when only the control string changes — evidence held fixed — then "
        "control wording is doing security-relevant work. This study measures how often "
        "that happens, tests a pre-registered qualifier hypothesis, and asks whether a "
        "cataloging-style rewrite reduces wording-driven flips on the controls that moved."
    )

    pdf.subheading("Our objectives were to")
    pdf.bullet(
        "Measure wording variance (X): the share of controls whose 5-way majority "
        "verdict flips across meaning-preserving paraphrases of the official statement, "
        "on one frozen evidence fixture."
    )
    pdf.bullet(
        "Test the qualifier hypothesis: whether qualifier-present controls "
        "(vague-qualifier + mixed) flip more often than specific controls."
    )
    pdf.bullet(
        "Test a vocabulary-control rewrite (Y / X2): apply seven editing rules drawn "
        "from thesaurus and authority-control practice to the flipped set only, and "
        "measure reduction in flip rate without adding, removing, or weakening requirements."
    )

    pdf.subheading("Methodology overview")
    pdf.labeled_block(
        "Part 1 — Control set and paraphrases",
        "Forty official NIST SP 800-53 Rev 5 statements (CSRC spreadsheet Control Text) "
        "were selected for applicability to an inspectable ML system. Each control has "
        "five variants: official v0 plus four human-reviewed, meaning-preserving "
        "paraphrases. SI-4.v1 remains unmarked and is excluded from that control’s "
        "scored variant set.",
    )
    pdf.labeled_block(
        "Part 2 — Assessment runs and scoring",
        "Every assessment used one frozen mlassure SageMaker-shaped fixture "
        f"(SHA-256 {EVIDENCE_HASH}). Assessments were produced by mlassure with local "
        "unpushed logging patches. Model claude-sonnet-4-6, temperature 0, three "
        "replicas per variant, native 5-way verdicts. Primary X uses majority flip "
        "across scored variants; a 3-way OSCAL fail-closed map is reported as sensitivity.",
    )
    pdf.labeled_block(
        "Part 3 — Cataloging rewrite on the flipped set",
        "Seven rules from ANSI/NISO Z39.19, ISO 25964, IFLA GARR, and IFLA ICP were "
        "applied only to the ten controls that flipped. After human review (47 yes / "
        "3 unsure excluded), 141 successful reruns measured Y (flip-rate reduction on "
        "those ten) and X2 (remaining flips on the original 40-control denominator).",
    )

    pdf.subheading("Key findings")
    pdf.finding_bullet(
        "A",
        "X = 10/40 = 25.0%. Ten controls change 5-way majority verdict under "
        "meaning-preserving paraphrase (AC-6(9), AU-8, CM-2, CM-3, CM-3(1), CM-3(2), "
        "CM-8(1), SA-10, SA-4(8), SI-2). Model noise at temperature 0: 32/200 = 16.0% "
        "of variants not unanimous. Paraphrase-vs-v0: 22/159 = 13.8%.",
    )
    pdf.finding_bullet(
        "B",
        "The qualifier hypothesis is not supported. Qualifier-present flipped "
        "2/17 = 11.8%; specific flipped 8/23 = 34.8%; vague-qualifier alone flipped "
        "0/4. Specific controls flipped more often in this set.",
    )
    pdf.finding_bullet(
        "C",
        "Under 3-way OSCAL fail-closed mapping, X = 2/40 = 5.0% (AC-6(9) and AU-8 "
        "only). Most 5-way flips are not-satisfied ↔ partially-satisfied and collapse "
        "under fail-closed mapping.",
    )
    pdf.finding_bullet(
        "D",
        "Preferred-term rewrite on the flipped ten: Y = 70% reduction (3/10 still "
        "flip: AU-8, CM-2, CM-3). X2 = 3/40 = 7.5%. Rewritten-set noise: "
        "19/47 = 40.4% — higher than Phase 3; reported beside Y, not folded into it.",
    )

    pdf.subheading("Recommendations (preview)")
    pdf.bullet("Pin the official catalog statement; do not silently substitute adapted intent.")
    pdf.bullet(
        "Prefer preferred-term / vocabulary-control rewrite over qualifier-stripping; "
        "qualifier-stripping was not indicated by this data."
    )
    pdf.bullet("Persist native 5-way verdicts beside any OSCAL 3-way collapse.")
    pdf.bullet("Report replica noise with X; treat control-text digest as a sibling to the evidence hash.")

    pdf.subheading("Conclusion")
    pdf.body(
        "On this frozen fixture, with one model at temperature 0, control wording moved "
        "the 5-way majority on a quarter of a 40-control set. That is enough to treat "
        "wording as a security-relevant attribute of an automated assessment. The "
        "mechanism is not the one hypothesized: specific controls flipped more than "
        "qualifier-present controls. A cataloging-style rewrite reduced majority flips "
        "on the treated ten without claiming that library science solved compliance, "
        "and without lobbying for catalog change. Results are bounded by one fixture, "
        "one model, forty controls, and unpushed assessment patches."
    )

    # =====================================================================
    # PROJECT INFORMATION
    # =====================================================================
    pdf.add_page()
    pdf.section_heading("Project Information")

    pdf.kv_row("Title", "Same Control, Different Verdict: Measuring How Control Wording Changes Automated AI Compliance Assessments")
    pdf.kv_row("Author", "Jose Ruiz-Vazquez")
    pdf.kv_row("Study period", "August 2026 (assessment runs); PDF dated September 2026")
    pdf.kv_row("Status", "Private study draft / study archive — not published")
    pdf.kv_row("Assessment tool", "mlassure (github.com/joseruiz1571/mlassure), with local unpushed logging patches")
    pdf.kv_row("Archive", "Private study archive; local patches and run logs are not published with this draft")
    pdf.kv_row("Model", "claude-sonnet-4-6, temperature 0, three replicas per variant")
    pdf.kv_row("Control source", "NIST SP 800-53 Rev 5 — CSRC spreadsheet Control Text (official v0)")
    pdf.kv_row("Evidence", f"One frozen SageMaker-shaped mlassure fixture; SHA-256 {EVIDENCE_HASH}")
    pdf.ln(2)
    pdf.body(
        "No external funding is claimed for this study. This document does not "
        "constitute a product endorsement, a NIST recommendation, or a published "
        "research article. Official NIST control text is a U.S. government work.",
        size=9,
    )

    # =====================================================================
    # METHODOLOGY
    # =====================================================================
    pdf.add_page()
    pdf.section_heading("Methodology")

    pdf.subheading("Part 1 — Control set and paraphrases")
    pdf.body(
        "Objective. Construct a human-reviewed set of meaning-preserving paraphrases "
        "of official NIST SP 800-53 Rev 5 statements so that wording can be varied "
        "while requirements stay fixed."
    )
    pdf.body(
        "Data. Forty controls were selected because they apply to a machine-learning "
        "system an automated assessor can inspect (families AC, AU, CM, RA, SA, SI, "
        "SC, CA). Deterministic and attestation-only controls were excluded: their "
        "verdicts are not produced by reading intent, so wording cannot change them. "
        "Official v0 wording is the CSRC spreadsheet Control Text, not adapted fixture "
        "intents and not reconstructed OSCAL parameter inserts. Assignment and Selection "
        "blocks are copied verbatim."
    )
    pdf.body(
        "Each control has five versions (v0 plus four paraphrases). Paraphrases change "
        "vocabulary and sentence structure only; they do not add SHALL/MUST, numbers, "
        "or roles absent from v0. Human review marked 199 rows meaning-preserved yes. "
        "SI-4.v1 was rewritten after review and remains unmarked; it is excluded from "
        "SI-4’s scored variant set for X, for vocab-pattern flip tables, and for "
        "paraphrase-vs-v0. SI-4 is therefore scored on four variants (v0, v2, v3, v4). "
        "Vocab tags on v0: 4 vague-qualifier, 23 specific, 13 mixed. The hypothesis cut "
        "is qualifier-present (vague-qualifier + mixed = 17) versus specific (23)."
    )

    pdf.subheading("Part 2 — Assessment runs and scoring")
    pdf.body(
        "Objective. Hold evidence fixed and measure how often majority verdicts change "
        "when only the control string changes."
    )
    pdf.body(
        f"Frozen evidence. One mlassure SageMaker-shaped fixture "
        f"(churn-predictor-v1 style), SHA-256 {EVIDENCE_HASH}. Chosen for mixed "
        "satisfied and not-satisfied conditions so wording has room to flip. It is not "
        "an mltrack bundle; mlassure cannot consume mltrack bundles. The hash was "
        "re-verified at scoring and is unchanged through Phase 5."
    )
    pdf.body(
        "Assessor. Assessments were produced by mlassure with local logging patches "
        "that remain unpushed. Control wording is supplied as ControlItem.intent. "
        "Verdicts are five-way: satisfied, partially-satisfied, not-satisfied, "
        "not-applicable, insufficient-evidence. Model: claude-sonnet-4-6. Temperature: "
        "0 on every successful replica."
    )
    pdf.body(
        "Replicas and census. Each variant was assessed three times. Scoring uses the "
        "last successful jsonl record per variant_id + replica; failed credit-crash "
        "rows are ignored. Result: 600 unique successful replicas (200 variants × 3). "
        "Census: 454 not-satisfied, 132 partially-satisfied, 10 satisfied, "
        "4 insufficient-evidence (0 not-applicable)."
    )
    pdf.body(
        "Scoring rules. Majority is the unique status with count ≥ 2 among three "
        "replicas; a 1-1-1 triple is labeled split. A control flips when its scored "
        "variant majority verdicts are not all identical. Primary X = flipped controls "
        "/ 40 (SI-4 contributes with four scored variants). Paraphrase-vs-v0 counts "
        "meaning-preserved paraphrases whose majority differs from that control’s v0 "
        "majority (denominator 159 after excluding SI-4.v1)."
    )
    pdf.body(
        "3-way sensitivity map (OSCAL fail-closed), applied per replica then "
        "re-majored: satisfied → satisfied; not-satisfied → not-satisfied; "
        "insufficient-evidence → undetermined; partially-satisfied → not-satisfied; "
        "not-applicable → not-satisfied. This map is a labeled sensitivity, not the "
        "primary outcome."
    )

    pdf.subheading("Part 3 — Cataloging rewrite on the flipped set")
    pdf.body(
        "Objective. Ask whether vocabulary-control editing reduces flip rate on the "
        "controls that already moved — without adding, removing, or weakening "
        "requirements, and without injecting fixture artifact names into control text."
    )
    pdf.body(
        "Seven editing rules (R1–R7) were drawn from sources actually retrieved: "
        "ANSI/NISO Z39.19-2005 (R2010), ISO 25964-1:2011, IFLA GARR (2nd ed., 2001), "
        "and IFLA ICP (2016). Rules address preferred terms, named count-noun evidence "
        "objects already present in the control, factoring of compound actions, scoped "
        "class terms, closed OR-selections, explicit associative links, and discrete "
        "authorized headings for lettered clauses. Assignment and Selection blocks are "
        "copied verbatim."
    )
    pdf.body(
        "Scope. Rules were applied only to the ten flipped controls, not to all forty. "
        "Human review of 50 rewritten rows: 47 yes, 3 unsure "
        "(AC-6(9).r4, AU-8.r4, CM-2.r4). Unsure rows are excluded. Remaining "
        "47 variants × 3 replicas = 141 successful assessments (temperature 0, same "
        "model, same frozen hash)."
    )
    pdf.body(
        "Y = (10 − n_flipped_after) / 10, the reduction in flip rate on the treated "
        "ten. Before rewrite, all ten flipped. X2 = n_flipped_after / 40, counting "
        "the 30 untreated controls as still non-flipping."
    )

    # =====================================================================
    # FINDINGS
    # =====================================================================
    pdf.add_page()
    pdf.section_heading("Findings")

    pdf.subheading("Primary wording variance (X)")
    pdf.body(
        "X = 10/40 = 25.0% under 5-way majority scoring (SI-4 scored on four variants). "
        "Dropping SI-4 entirely yields X_39 = 10/39 = 25.6%; SI-4 itself does not flip "
        "(four × not-satisfied). The ten flipped controls are: AC-6(9), AU-8, CM-2, "
        "CM-3, CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), SI-2."
    )
    pdf.body(
        "Paraphrase-versus-v0: 22 of 159 meaning-preserved paraphrases (13.8%) differ "
        "from that control’s v0 majority. All 22 sit inside the ten flipped controls."
    )

    pdf.subheading("Replica noise")
    pdf.body(
        "Even at temperature 0, 32/200 = 16.0% of variants were not unanimous across "
        "three replicas (31 two-one majorities; 1 three-way split on CM-2.v4). Noise is "
        "reported with X because majority scoring does not erase replica disagreement."
    )

    pdf.subheading("Qualifier hypothesis — not supported")
    pdf.body(
        "The study expected qualifier-present controls to flip more often than specific "
        "controls. The completed table goes the other way. This result is reported "
        "honestly; the hypothesis is not supported."
    )
    pdf.simple_table(
        ["Cut", "n controls", "n flipped", "Flip rate"],
        [
            ["vague-qualifier", "4", "0", "0/4 = 0.0%"],
            ["mixed", "13", "2", "2/13 = 15.4%"],
            ["specific", "23", "8", "8/23 = 34.8%"],
            ["qualifier-present (vague + mixed)", "17", "2", "2/17 = 11.8%"],
        ],
        col_widths=[72, 28, 28, 46],
    )
    pdf.body(
        "Vague-qualifier alone (AC-6, RA-7, SA-8(32), SI-12) flipped 0/4. Mixed flips "
        "were CM-2 and SA-4(8). Specific controls flipped more often than "
        "qualifier-present controls in this 40-control set. This paper does not claim "
        "the hypothesis was confirmed, qualified, or directionally right — and it does "
        "not claim that vague controls are the problem."
    )

    pdf.subheading("Three-way OSCAL sensitivity")
    pdf.body(
        "After fail-closed mapping, 3-way X = 2/40 = 5.0%. Only AC-6(9) and AU-8 move "
        "satisfied ↔ not-satisfied. Most 5-way flips are not-satisfied ↔ "
        "partially-satisfied (plus one split); those collapse under the map. 3-way "
        "noise is 9/200 = 4.5%; 3-way paraphrase-vs-v0 is 6/159 = 3.8%. If a downstream "
        "program treats partially-satisfied as “not met,” eight of the ten 5-way flips "
        "are operationally silent. Primary X keeps the five-way enum the tool emits."
    )

    pdf.subheading("Rewrite results (Y and X2)")
    pdf.body(
        "Before rewrite, all ten treated controls flipped. After rewrite and exclusion "
        "of three unsure paraphrases, three still flip: AU-8, CM-2, and CM-3. Seven no "
        "longer flip: AC-6(9), CM-3(1), CM-3(2), CM-8(1), SA-10, SA-4(8), and SI-2."
    )
    pdf.simple_table(
        ["Metric", "Value"],
        [
            ["Y (flip-rate reduction on treated 10)", "70%  (10/10 → 3/10)"],
            ["X2 (remaining flips / original 40)", "3/40 = 7.5%"],
            ["Still flipping after rewrite", "AU-8, CM-2, CM-3"],
            ["Rewritten-set noise", "19/47 = 40.4%"],
            ["Phase 5 successful runs", "141 (47 variants × 3)"],
        ],
        col_widths=[90, 84],
    )
    pdf.body(
        "Phase 5 replica census (141): 90 not-satisfied, 40 partially-satisfied, "
        "8 satisfied, 3 insufficient-evidence. Rewritten-set noise (40.4%) is higher "
        "than Phase 3 noise (16.0%). Y is a reduction in majority-verdict wording "
        "variance; the noise rate is reported beside it, not folded into it. Y is not "
        "“the model became more stable.”"
    )

    # =====================================================================
    # LIMITATIONS AND FUTURE WORK
    # =====================================================================
    pdf.add_page()
    pdf.section_heading("Limitations and Future Work")

    pdf.subheading("Binding limitations")
    pdf.bullet(
        "One frozen evidence fixture. Results are not a claim about other inventories, "
        "production systems, or evidence shapes."
    )
    pdf.bullet(
        "One model (claude-sonnet-4-6) at temperature 0. Temperature 0 does not imply "
        "determinism; 16.0% Phase 3 noise is the measurement."
    )
    pdf.bullet(
        "Forty controls. Results are not a ranking of NIST families and are not a "
        "catalog rewrite proposal."
    )
    pdf.bullet(
        "SI-4.v1 hole: unmarked and excluded from SI-4’s scored variant set. The four "
        "scored SI-4 variants already agree (no flip), so the hole does not change X."
    )
    pdf.bullet(
        "Three rewritten paraphrases marked unsure and excluded "
        "(AC-6(9).r4, AU-8.r4, CM-2.r4), so those three controls are scored on four "
        "rewritten variants rather than five."
    )
    pdf.bullet(
        "mlassure logging patches are local and unpushed. Reproducing live assessment "
        "requires a patched clone and an API key; table rebuild from frozen logs does not."
    )
    pdf.body(
        "This study does not lobby NIST, does not claim library science solved "
        "compliance, and does not claim that vague controls are the problem. The "
        "qualifier hypothesis was not supported; recommendations follow the data."
    )

    pdf.subheading("Future work licensed by this data")
    pdf.bullet(
        "Second model on the same frozen fixture and control set, to separate "
        "assessor-specific wording sensitivity from fixture-specific effects."
    )
    pdf.bullet(
        "Second evidence fixture with a different mix of satisfied / not-satisfied "
        "conditions, holding control variants fixed."
    )
    pdf.bullet(
        "Persist a control-text digest in the assessment artifact as a sibling to the "
        "evidence hash, so wording provenance is auditable beside evidence provenance."
    )
    pdf.bullet(
        "Residual analysis on AU-8, CM-2, and CM-3 — the three controls that still "
        "flip after preferred-term rewrite — without expanding scope to untreated controls."
    )
    pdf.body(
        "Out of scope: employee-frame narratives, NIST lobbying, catalog-wide rewrite "
        "claims, and any assertion that qualifier-stripping is the remedy. Those are "
        "refused because the data do not license them."
    )

    # =====================================================================
    # RECOMMENDATIONS
    # =====================================================================
    pdf.add_page()
    pdf.section_heading("Recommendations")

    pdf.body(
        "These recommendations are scoped to automated LLM assessment pipelines that "
        "read control text. They are operational hygiene for wording provenance and "
        "scoring transparency, not a call to rewrite the NIST catalog."
    )

    pdf.subheading("1. Pin the official statement")
    pdf.body(
        "Treat the official catalog Control Text as the pinned input. Do not silently "
        "substitute a vendor’s adapted intent for the catalog statement when measuring "
        "or reporting compliance. If adapted wording is used, record it as a distinct "
        "artifact with its own digest."
    )

    pdf.subheading("2. Prefer preferred-term rewrite over qualifier-stripping")
    pdf.body(
        "Where control authors or assessment designers edit wording for machine "
        "readability, prefer vocabulary-control practice: one preferred term per "
        "required action or object; named count-noun artifacts already present in the "
        "control; factored compound actions; closed selections; explicit associative "
        "links. Do not assume that stripping vague qualifiers will stabilize automated "
        "verdicts — it was not indicated here, because qualifier-tagged controls were "
        "not the ones that flipped."
    )

    pdf.subheading("3. Persist 5-way verdicts beside OSCAL")
    pdf.body(
        "Keep the native five-way enum the assessor emits, and map to OSCAL’s "
        "fail-closed three-way only as an explicit downstream view. Collapsing "
        "partially-satisfied before measuring wording variance hides the majority of "
        "flips observed in this study (3-way X = 2/40 vs 5-way X = 10/40)."
    )

    pdf.subheading("4. Report noise with X")
    pdf.body(
        "Publish replica disagreement beside the flip rate. Majority scoring does not "
        "erase temperature-0 noise (16.0% in Phase 3; 40.4% on the rewritten set). "
        "Readers need both numbers to interpret stability claims."
    )

    pdf.subheading("5. Treat control-text digest as sibling to evidence hash")
    pdf.body(
        "Assessment artifacts should record a digest of the exact control string "
        "assessed, alongside the evidence hash. Wording provenance and evidence "
        "provenance are parallel integrity concerns when an LLM is the reader."
    )

    pdf.ln(6)
    pdf.set_draw_color(*RULE)
    pdf.set_line_width(0.3)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Sans", "", 8.5)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(
        0,
        4.5,
        "End of report. Private study draft — Jose Ruiz-Vazquez — August–September 2026. "
        "Not published. Frozen evidence SHA-256 "
        f"{EVIDENCE_HASH}.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    pdf.output(str(OUT_PDF))
    return OUT_PDF


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
