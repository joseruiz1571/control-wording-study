# Phase 5 editing rules (10 flipped controls)

Jose scoped Phase 5 to the **10 controls that flipped** under 5-way majority (X = 10/40 = 25.0%). The qualifier-present vs specific hypothesis was **not** supported on this fixture (specific 8/23 = 34.8%; qualifier-present 2/17 = 11.8%). These rules are therefore **not** a claim that vague qualifiers cause flips. They are editing rules that would have de-ambiguated the 10 statements that actually flipped, drawn from controlled-vocabulary and authority-control practice.

Most of those 10 flips were `not-satisfied` ↔ `partially-satisfied` (one `split`). Only AC-6(9) and AU-8 moved `satisfied`. The hedge-room the rules target is: undefined class membership, compound actions assessed as a single blob, unnamed evidence objects, and unspecified associative links. The rules do **not** add, remove, or weaken requirements, and they do not introduce numbers, roles, or artifacts the official v0 did not already require.

Official v0 is the CSRC spreadsheet `Control Text` copied in `controls/control_set.reviewed.csv` variant 0. Rewrites are traceable to that text. `[Assignment:]` / `[Selection:]` blocks are copied verbatim.

## Sources actually retrieved (2026-08-30)

1. **ANSI/NISO Z39.19-2005 (R2010)** *Guidelines for the Construction, Format, and Management of Monolingual Controlled Vocabularies*. NISO, approved 2005-07-25, reaffirmed 2010-05-13. ISBN 978-1-937522-22-3 / 1-880124-65-3. PDF retrieved from https://groups.niso.org/higherlogic/ws/public/download/12591 . Catalog: https://www.niso.org/publications/ansiniso-z3919-2005-r2010
2. **ISO 25964-1:2011(E)** *Information and documentation — Thesauri and interoperability with other vocabularies — Part 1: Thesauri for information retrieval*. First edition 2011-08-15. Preview retrieved (SIST ISO 25964-1:2013, stated identical to ISO 25964-1:2011) from https://cdn.standards.iteh.ai/samples/53657/ac286b3aea6d447caaf603bce260a2f0/SIST-ISO-25964-1-2013.pdf . ISO catalog: https://www.iso.org/standard/53657.html
3. **IFLA** *Guidelines for Authority Records and References* (GARR), 2nd ed., 2001. UBCIM Publications New Series Vol. 23. PDF retrieved from https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/garr/garr.pdf
4. **IFLA** *Statement of International Cataloguing Principles* (ICP), 2016 edition with minor revisions 2017. The freely retrieved RDA-aligned authority-control source (RDA Toolkit itself was not retrieved). PDF retrieved from https://www.ifla.org/wp-content/uploads/2019/05/assets/cataloguing/icp/icp_2016-en.pdf
5. Clarke, Stella G. Davenport & Marcia Lei Zeng. “From ISO 2788 to ISO 25964: the evolution of thesaurus standards towards interoperability and data modeling.” *Information Standards Quarterly*, quoting ISO 25964-1 §15.2.3. Retrieved from https://www.niso.org/sites/default/files/stories/2017-11/SP_clarke_zeng_isqv24no1.pdf

## The seven rules

### R1 — Preferred-term lock

**Instruction.** For each required action or object, pick one preferred noun or noun phrase from the official v0 (or the control title) and reuse that exact string; do not substitute near-synonyms (log/record/capture/maintain; generate/produce; document/record) in the rewritten base.

**Why this de-ambiguates the flips.** AC-6(9) v0 (“Log the execution of privileged functions”) was majority `satisfied`; paraphrases that swapped Log for Record / Capture / Maintain / is-logged were `partially-satisfied`. Near-synonym scatter is exactly the failure Z39.19 names.

**Citation.** ANSI/NISO Z39.19-2005 (R2010) §5.3.2: “A controlled vocabulary must compensate for the problems caused by synonymy by ensuring that each concept is represented by a single preferred term.” Same principle: §6.6 Selecting the Preferred Form; ISO 25964-1:2011 §6.6 Selection of the preferred form, and §15.2.3 as quoted by Clarke & Zeng: “Each concept in the thesaurus is represented by one preferred term per language, and by any number of non-preferred terms.” IFLA ICP 2016 §5.3.3: “The name preferred as the authorized access point for an entity should be based on the name that identifies the entity in a consistent manner.”

**Before / after (AC-6(9) v0).**

- Before: `Log the execution of privileged functions.`
- After: `Log the execution of privileged functions in a log of privileged-function execution.`

“Log” stays the preferred verb from the official statement and the enhancement title (*Log Use of Privileged Functions*). The object is restated as the premodified noun phrase “privileged-function execution” (Z39.19 §6.4.1.2.1: adjectival noun phrases are the preferred form). No completeness word (“each”, “all”) is added.

---

### R2 — Name the implied evidence object as a count noun

**Instruction.** When v0 requires logging, documenting, inventorying, planning, time-stamping, or retaining records, name the product as a countable artifact **already implied by the verb or already present as a noun in the control** (a log, the inventory of system components, the plan, time stamps, records of configuration-controlled changes). Do not introduce a fixture collector name, a new document type, or an artifact the official text did not already require.

**Why this de-ambiguates the flips.** Several of the 10 leave the assessor to guess whether “log” / “document” / “plan” / “inventory” is a process or a retrievable object. Naming the object reduces hedge-room between “some logging exists” (`partially-satisfied`) and “the required record is present.” AC-6(9), AU-8, CM-2, CM-8(1), and SA-4(8) all have this shape.

**Citation.** ANSI/NISO Z39.19-2005 (R2010) §6.4.1.1 Verbal Nouns: “Activities should be represented by nouns or gerunds” (e.g. *distillation* rather than *distill*). §6.5.1 Count Nouns: names of objects subject to “How many?” should be expressed so they can be counted. IFLA GARR 2nd ed. §0.2: “Authorised heading. The uniform controlled heading for an entity.” ISO 25964-1:2011 §2.11 concept = “unit of thought”; §2.12 controlled vocabulary: “each representing a concept.”

**Before / after (CM-8(1) v0).**

- Before: `Update the inventory of system components as part of component installations, removals, and system updates.`
- After: `Update the inventory of system components when any of the following occur: component installations; component removals; and system updates.`

“The inventory of system components” was already the authorised heading for the evidence object. The rewrite keeps that heading and stops treating “inventory” as an uncountable process folded into “as part of.”

Also applied on AC-6(9) (the log), AU-8 (time stamps for audit records), CM-2 (baseline configuration), SA-4(8) (the plan).

---

### R3 — Factor compound actions into separately assessable clauses

**Instruction.** When v0 joins two or more distinct actions with “and” (test, validate, and document; identify, report, and correct; develop, document, and maintain; document, manage, and control), split them into lettered clauses or semicolon-separated conjuncts so each action is independently assessable. Keep every conjunct. Do not drop, merge, or weaken any of them.

**Why this de-ambiguates the flips.** Eight of ten flips sit in `not-satisfied` ↔ `partially-satisfied`. A compound AND-list is the natural place for an assessor to score “some of these are done” as partial. Factoring does not change the requirement (all conjuncts still required); it removes the blob.

**Citation.** ISO 25964-1:2011 §2.9 compound term: “term that can be split morphologically into separate components”; §2.8 compound equivalence: one term/concept represented by two or more in another context; §7 Complex concepts, especially §7.4 How to split a complex concept and §8.5 Representation of complex concepts by a combination of terms. ANSI/NISO Z39.19-2005 (R2010) §7.6 Criteria for Determining When Compound Terms Should be Split, and §7.6.2.2 Transitive Action: split when the focus is an action modified by its object (e.g. *offices + management* rather than *office management*). §6.3.1: “Each term included in a controlled vocabulary should represent a single concept (or unit of thought).”

**Before / after (CM-3(2) v0).**

- Before: `Test, validate, and document changes to the system before finalizing the implementation of the changes.`
- After: `a. Test changes to the system before finalizing the implementation of the changes; b. Validate changes to the system before finalizing the implementation of the changes; and c. Document changes to the system before finalizing the implementation of the changes.`

Same three actions, same timing constraint, now separately assessable. Also applied on CM-2 (develop / document / maintain), CM-3 (determine vs document; monitor vs review; coordinate vs oversight), CM-3(1) (notify vs request approval), SA-10 (document / manage / control integrity; document changes vs document impacts; track vs report), SI-2 (identify / report / correct; test for effectiveness vs test for side effects), CM-8(1) (installations / removals / system updates as separate triggers).

---

### R4 — Scope the class term with the control’s own words

**Instruction.** When a class has no membership test in v0 (privileged functions, system flaws, types of changes), attach a preferred-term restatement or parenthetical drawn **only** from words already in the statement or its NIST title. Do not add a definition, role, or membership criterion NIST did not write.

**Why this de-ambiguates the flips.** AC-6(9)’s “privileged functions” and SI-2’s “system flaws” leave the assessor to guess the class. A scope restriction that invents membership would change intent; a preferred-form restatement that uses the control’s own words does not.

**Citation.** ANSI/NISO Z39.19-2005 (R2010) §5.3.1: “A controlled vocabulary must compensate for the problems caused by ambiguity by ensuring that each term has one and only one meaning.” §6.2.2 Scope Notes: a scope note is used “to restrict or expand the application of a term” and “should state the chosen meaning of a term.” §6.2.1 Homographs: a qualifier “specifies the domain of meaning to which the term belongs” and “is part of the term.” ISO 25964-1:2011 §5 Concepts and their scope in a thesaurus, §5.2 Scope notes. IFLA ICP 2016 §5.3.4.5 Distinguishing among Names: “If necessary, to distinguish an entity from others of the same name, further identifying characteristics should be included as part of the authorized access point” — using characteristics already belonging to the entity, not new ones.

**Before / after (AC-6(9) v0, class term).**

- Before: `…the execution of privileged functions.`
- After: `…the execution of privileged functions in a log of privileged-function execution.`

“Privileged-function execution” is the same class as “execution of privileged functions,” restated as the preferred premodified noun phrase. No new membership test.

---

### R5 — State OR-alternatives as a closed selection

**Instruction.** When v0 offers alternatives joined by “or,” state them as a closed selection of which **one or more** must hold. Do not turn “or” into “and.” Do not add a numbered threshold the original did not have. Keep every alternative.

**Why this de-ambiguates the flips.** AU-8 v0/v1/v4 were `partially-satisfied` and v2/v3 `satisfied` on the same UTC / fixed-offset / include-offset chain. An unpunctuated “A, B, or C” is easy to read as “some of this time-representation is present.” A closed selection makes the one-or-more reading explicit. CM-8(1)’s “installations, removals, and system updates” is the AND dual: a closed list of triggers.

**Citation.** ANSI/NISO Z39.19-2005 (R2010) §8.4.1.1 Relationships Between Overlapping Sibling Terms: sibling terms with overlapping meanings “can be precisely defined (so they do not form an equivalence set)” and must be distinguished, not collapsed. §5.4.1 List is the controlled-vocabulary form for an enumerated set of terms. ISO 25964-1:2011 §2.1 array: “group of sibling concepts”; §10.2 The hierarchical relationship. IFLA ICP 2016 §2.8 Consistency and standardization: “Descriptions and construction of access points should be standardized as far as possible to enable consistency.”

**Before / after (AU-8 v0 clause b).**

- Before: `…time stamps for audit records that meet [Assignment: organization-defined granularity of time measurement] and that use Coordinated Universal Time, have a fixed local time offset from Coordinated Universal Time, or that include the local time offset as part of the time stamp.`
- After: `…those time stamps for audit records such that the time stamps meet [Assignment: organization-defined granularity of time measurement] and satisfy one or more of the following: use Coordinated Universal Time; have a fixed local time offset from Coordinated Universal Time; include the local time offset as part of the time stamp.`

The `[Assignment:]` block is unchanged. The three time-representation options remain alternatives (one or more), not a new AND.

---

### R6 — Name both ends of an associative hedge

**Instruction.** Replace floating relational hedges (“consistent with,” “as part of,” “when required due to”) with an explicit correspondence **between two objects already in the control**. Keep the relation; do not invent a new object, frequency, or actor. Do not drop the hedge (it is a requirement).

**Why this de-ambiguates the flips.** SA-4(8) (“consistent with the continuous monitoring program”) and CM-2 (“When required due to [circumstances]”) and CM-8(1) (“as part of”) are associative links with one end unnamed or both ends fused. Assessors can treat the relation as optional color rather than a checkable correspondence, which is the `partially-satisfied` hedge.

**Citation.** ANSI/NISO Z39.19-2005 (R2010) §8.4 Associative Relationships: associations that are “neither equivalent nor hierarchical, yet the terms are semantically or conceptually associated to such an extent that the link between them should be made explicit”; “it is important to make explicit the nature of the relationship between terms linked in this way and to avoid subjective judgments as much as possible.” ISO 25964-1:2011 §2.2 associative relationship: “relationship between a pair of concepts that are not related hierarchically but share a strong semantic connection”; §10.3 The associative relationship. IFLA GARR 2nd ed. §1.4 See also reference tracing area: related authorised headings are recorded so the relationship is explicit, not inferred.

**Before / after (SA-4(8) v0).**

- Before: `Require the developer of the system, system component, or system service to produce a plan for continuous monitoring of control effectiveness that is consistent with the continuous monitoring program of the organization.`
- After: `Require the developer of the system, system component, or system service to produce a plan for continuous monitoring of control effectiveness; that plan is consistent with the continuous monitoring program of the organization.`

“Plan” and “continuous monitoring program of the organization” become two named entities with the original “consistent with” relation still required. No new plan type.

**Before / after (CM-2 v0 clause b.2).**

- Before: `2. When required due to [Assignment: organization-defined circumstances];`
- After: `2. When [Assignment: organization-defined circumstances] require a review and update;`

The assignment block is unchanged. Both ends (circumstances → the review-and-update that clause b already requires) are named.

---

### R7 — Discrete authorised headings for lettered clauses; lock organization-defined parameters

**Instruction.** Keep every lettered or numbered clause of a multi-part control as its own authorised heading. Do not collapse a–g into one blob. Copy every `[Assignment:]` and `[Selection:]` block verbatim — those strings are the preferred form of the organization-defined frequency, role, time period, mechanism, or element. Do not paraphrase them.

**Why this de-ambiguates the flips.** CM-3, SA-10, SI-2, CM-2, AU-8, and CM-3(1) are long AND-chains. Phase 2 paraphrases that reordered or lightly synonymized a clause sometimes flipped while the others did not. Treating each clause as a separate authorised heading, and freezing the assignment strings, reduces that surface without changing NIST’s organization-defined parameters.

**Citation.** IFLA GARR 2nd ed. §0.2: “Authorised heading. The uniform controlled heading for an entity.” §1.1 Authority heading area: “The heading for the authority record is the authorised heading established by the cataloguing agency.” IFLA ICP 2016 §5.1.1: “Controlled access points should be provided for the authorized and variant forms of names”; §5.3: “The authorized access point for the name of an entity should be recorded as authority data along with identifiers for the entity and variant forms of name”; §5.3.1: “Authorized access points must be constructed following a standard.” ANSI/NISO Z39.19-2005 (R2010) §6.6: variant forms are entry terms; the preferred form is recorded in the term record. ISO 25964-1:2011 §6.6 Selection of the preferred form.

**Before / after (CM-3 v0 clauses a and f, representative).**

- Before a: `Determine and document the types of changes to the system that are configuration-controlled;`
- After a: `Determine the types of changes to the system that are configuration-controlled, and document those types;`
- Before f: `Monitor and review activities associated with configuration-controlled changes to the system;`
- After f: `Monitor activities associated with configuration-controlled changes to the system, and review those activities;`

Clause e’s `[Assignment: organization-defined time period]` and clause g’s `[Assignment: organization-defined configuration change control element]` / `[Selection (one or more): …]` are copied verbatim in the rewritten base and in every paraphrase.

---

## Rule application on the 10 rewritten bases

| control_id | vocab_pattern (retagged on r0) | rewrite_rules_applied | What changed vs official v0 |
| --- | --- | --- | --- |
| AC-6(9) | specific | R1\|R2\|R4 | Preferred term “log”; named log of privileged-function execution |
| AU-8 | specific | R2\|R5\|R7 | Named time stamps; UTC/offset options as closed one-or-more selection; Assignment locked |
| CM-2 | mixed | R2\|R3\|R6\|R7 | Split develop/document/maintain; named baseline configuration; “when required due to” → circumstances require review and update |
| CM-3 | specific | R3\|R7 | Split determine/document, monitor/review, coordinate/oversight; Assignments/Selection locked |
| CM-3(1) | specific | R3\|R7 | Split notify vs request approval; Assignments locked |
| CM-3(2) | specific | R3 | Split test / validate / document; same “before finalizing” on each |
| CM-8(1) | specific | R2\|R3\|R5\|R6 | Named inventory; closed trigger list; “as part of” → when any of the following occur |
| SA-10 | specific | R3\|R7 | Split document/manage/control integrity; document changes vs impacts; track vs report; Selection/Assignments locked |
| SA-4(8) | mixed | R2\|R6 | Named plan vs program; “consistent with” kept as the correspondence |
| SI-2 | specific | R3\|R7 | Split identify/report/correct; test for effectiveness vs test for side effects; Assignment locked |

vocab_pattern is retagged on rewritten r0 using the Phase 2 rule (vague-qualifier / specific / mixed). The two mixed controls stay mixed because R6 **keeps** “consistent with” (SA-4(8)) and the circumstances-require hedge (CM-2) rather than deleting them. The eight specifics stay specific: they name an artifact, frequency, or role and do not pick up a new close qualifier.

## What the rules deliberately do not do

- They do **not** treat vague-qualifier wording as the cause of these flips (the 4 vague-qualifier controls in the 40 did not flip).
- They do **not** inject CloudTrail, the model registry, monitors, or other fixture artifacts into the control text. Fixture artifacts may be named as a recording place only if v0 already required a frequency or actor; none of these 10 rewrites needed that exception.
- They do **not** add SHALL/MUST, numeric thresholds, or roles absent from official v0.
- They do **not** change NIST organization-defined parameters.

Paraphrases r1–r4 of each rewritten base follow the Phase 2 paraphrase rules (vocab/structure only; Assignment/Selection blocks verbatim; no added/removed requirements; mark unsure rather than weaken). None of the 40 paraphrases is marked unsure. `meaning_preserved` is left empty for Jose.
