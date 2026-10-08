# Decision 005: how deep Section 2 goes, and why it carries no numbers

| Field | Value |
|---|---|
| Date | 8 October 2026 |
| Decided by | Build team, applied and flagged for confirmation |
| Status | Applied, awaiting editorial confirmation |
| Applies to | Section 2 Anatomy Academy, all 79 pages |

## The problem

Section 2 is 79 pages of regional anatomy, every one of them carrying the
medical student, MRCS and FRCS tiers, and 21 of them carrying fellowship as
well. It is the first section on this site written entirely for professionals.

Two things about it do not work under the existing rules.

### Numbers

Anatomy at this depth normally carries measurements. Posterior tibial slope in
degrees. Trochlear sulcus angle. Anterior cruciate ligament footprint
dimensions. Distances from a landmark to an attachment. The angle of the
distal femoral cut. Candidates revise those numbers for FRCS, and a page that
omits them looks incomplete to the reader who needs them most.

Evidence verification has never run on this site. No source retrieval has been
available at any point. A measurement written from memory would be unverifiable,
and at FRCS and fellowship level a plausible wrong number is worse than no
number: it is the kind of error that gets repeated in an answer and not caught.

### Word counts

The handbook sets 800 to 1800 words for an anatomy page. That fits 2.1.2 Distal
Femur.

It does not fit 2.2.4 Gerdy's Tubercle. The architecture excludes pathology,
operative technique, imaging interpretation and biomechanics from these pages,
all of which are owned elsewhere. What is left of Gerdy's tubercle after those
exclusions is a location, two attachments, a set of relations and its use as a
landmark. Three tiers of that does not reach 800 words, and the only way to get
there is padding, which is what decision 002 was written to prevent.

## The ruling

### 1. No figures in Section 2

No page in Section 2 carries a measurement, an angle, a dimension, a distance,
a normal range, a percentage or an incidence figure. Anatomy is described in
relative terms, which is how it is actually taught at the table: larger than,
posterior to, converging on, broader at its base.

Where a number would normally sit, the page names the structure's relationship
instead, and the claim is listed in the page's handoff block so a reviewer with
sources can add the figure with a date against it.

This is an extension of decision 003's rule from Section 0's education
structures to Section 2's clinical anatomy. It matters more here. A wrong
figure on a page about choosing A levels wastes somebody's afternoon. A wrong
figure on a page about the trochlea could end up in an operation.

**It is enforced by the gate, not by review.** Decision 003's version of this
rule was a drafting instruction, which is another way of saying it was a hope.
FIG-001 in `lint_rules.json` now fails any page whose brief carries
`governance.figures_allowed: false`, and `tools/architecture.py` sets that flag
for every page in Sections 0 and 2. Both rulings are therefore the same
mechanism, and neither depends on a drafter remembering it.

Two things the rule has to get right, and the tests hold both. Page ids,
section references and decision references are removed before the scan, because
this site's prose is full of them. And a page id is indistinguishable from a
decimal measurement, since 5.5 could be chapter 5.5 or five and a half degrees,
so a unit decides: an id is only ignored when no unit follows it. A bare decimal
with no unit reads as a page id. Write the unit and the rule fires.

Three of these pages have the exclusion in the architecture already: 2.2.5
excludes TT-TG measurement method, 2.1.5 excludes dysplasia classification, and
2.4.2's variants are described rather than classified. This ruling makes the
same treatment uniform across the section rather than page by page.

### 2. A band for narrow structure pages

Where the architecture scopes a page to a single bony landmark or a single named
structure with no independent neurovascular supply, the band is 450 to 1100
rather than 800 to 1800.

The pages this applies to are listed in
`pipeline/config/word_count_overrides.json`, each with its reason, and
`tools/architecture.py` applies it when the brief is generated. It is a declared
list rather than a heuristic, because no heuristic distinguishes a narrow
structure from a narrow description of a wide one.

An entry on that list is a prediction about a page nobody has written yet, so it
is checked once the page exists. Two were wrong on the first batch. 2.2.3 Tibial
Spine came out at 1219 words and 2.2.4 Gerdy's Tubercle at 1133, both of
substantive anatomy rather than padding: the spine carries both cruciates and
all four meniscal roots, and the tubercle carries a disputed capsular structure
that needs describing carefully. Both overrides were withdrawn and the handbook's
own band applies to them.

Withdrawn entries stay in the file rather than being deleted. A record of what
the prediction got wrong is more useful than a clean list, and it is the reason
the rule is now explicitly "declare, write, then check".

### 3. The tier pattern

Every Section 2 page uses the handbook's anatomy template. What changes between
tiers is which body sections are present and at what depth.

| Tier | Sections | What it is for |
|---|---|---|
| Medical student | Structure and Location, Relations, Function, Clinical Relevance | Naming and orientation. What it is, where it sits, what it does |
| MRCS | Structure and Location, Relations, Blood Supply and Innervation, Function, Clinical Relevance | The viva answer. Named relations, named supply, named landmarks |
| FRCS | Relations, Function, Clinical Relevance | Why the anatomy constrains a decision, with the decision itself left to Sections 6 and 7 |
| Fellowship | Clinical Relevance | Approach anatomy and structures at risk. Not technique, which Section 7 owns |

Blood Supply and Innervation appears at MRCS and above only. At medical student
level it is naming without purpose; at MRCS it is a question that gets asked.

Decision 001 forbids Relations and Blood Supply and Innervation on pages whose
brief excludes region level anatomy detail. Section 2 is the section that owns
that detail, its briefs carry no such exclusion, and the gate therefore permits
both here. That is the rule working as intended rather than an exception to it.

## What this costs

A Section 2 page is a complete description of a structure with no number in it.
A reviewer will notice. The handoff block for every page says so explicitly, and
says which claims a figure would normally attach to.

If editorial wants the figures, they are addable page by page without rewriting
anything: each is a sentence gaining a clause. What cannot be done is adding
them from here.
