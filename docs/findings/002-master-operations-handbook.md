# Finding 002: the Master Operations Handbook, and what it settles

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Source | `Knee_school_2.zip`, supplied 9 October 2026 |
| Closes | Build status item EV-8 |
| Related decision | 008, the architecture numbering is canonical |

## What arrived

Eight files. Three of them are new.

| File | Status | Size of text |
|---|---|---|
| `KneeSchool_Master_Operations_Handbook.pdf` | New. 21 chapters and 10 appendices | 25,242 characters |
| `KneeSchool_Master_Playbook_v1.docx` | New. Section headings with placeholder bodies | 6,263 characters |
| `KneeSchool_Master_Playbook.pdf` | New. An earlier, shorter playbook | 4,506 characters |
| `KneeSchool_Operations_Handbook.pdf` | New file, thin content. Saved as `KneeSchool_Complete_Operations_Handbook.pdf` to avoid a name clash | 3,410 characters |
| `KneeSchool_Sections_1_to_15_Full_Architecture.docx` | Byte identical to the copy already in `docs/` | already parsed |
| `KneeSchool_Table_of_Contents.pdf` | Byte identical to `KneeSchool_Master_Handbook_Table_of_Contents.pdf` | already parsed |
| `KneeSchool_Sections_1_to_15_Full_Architecture.pdf` | The same architecture in PDF form | already parsed |
| `KneeSchool_Team_Pack.zip` | Identical to the pack supplied at the start of the build | already parsed |

All four PDFs were produced on 13 June 2026. Every file is now in `docs/`, each
with a plain text extraction beside it.

### Why extraction took four attempts

The Master Operations Handbook does not store its text as text. It stores
hex-encoded glyph ids from seven subset fonts, so a naive extractor returns
nothing readable. The working extractor finds every object, inflates at each
stream offset rather than at each `stream` keyword, because the embedded
TrueType font data itself contains those bytes, parses all seven ToUnicode
character maps, tracks which font is current through each of the 30 content
streams, and maps the glyph ids back to characters.

## The authority question, and its answer

The handbook does not carry a version number or a date in its text. Its PDF was
written on 13 June 2026.

`docs/KneeSchool_Operations_Handbook.md` is version 1.0, dated 22 September
2026, and it carries an explicit authority rule:

> Where this handbook and any other document disagree, this handbook wins. That
> includes KneeSchool_AI_Agent_Prompts.md, the build handover, the brief
> template, and prior playbook drafts.

The Master Operations Handbook predates it by three months. It is therefore one
of the prior drafts that rule names. The Operations Handbook keeps authority on
every point where the two disagree, and the Master Operations Handbook governs
everything the Operations Handbook does not cover, which is most of the
commercial and operational side of the project.

That ordering is a reading of the dates and the rule, not a client instruction.
It is put as a question at the end of this finding.

## What it settles

EV-8 asked for the Master Handbook because its contents page named two chapters
that would answer open questions. Both are now readable.

**Content production SOP, chapter 7.** The sequential workflow is: understand
site structure, select topic, gather sources, organise repository, upload to the
AI workspace, create a content brief, generate a draft, run editorial checks,
verify factual claims, prepare a consultant review pack, complete SEO, publish.
The pipeline here implements all of it except source gathering, verification and
the consultant pack, which are the three stages that have no route from this
build environment.

**Version control.** Four stages are required: draft, checked,
consultant-reviewed, published.

**Production status fields.** Topic ID, Priority, Source status, Draft status,
QA status, Publication status, with named allowed values. The tracker seed
already uses these exact fields and values, because the Operations Handbook
carried them forward.

**Appendix A, the master article tracker.** Thirteen columns: Topic ID, Topic,
Category, Level, Priority, Sources gathered, AI draft, Assistant QA, Evidence
QA, Consultant review, SEO complete, Published, Refresh date. The tracker here
is missing three of them: Category, SEO complete and Refresh date.

**Escalation triggers, chapter 8.** Conflicting evidence, unclear surgical
recommendation, unsupported statistic, patient safety issue, commercial claim,
drug or supplement claim, or any statement that could be read as personal
medical advice. Six of the seven already have machinery here. The seventh,
conflicting evidence, cannot arise without sources.

**Red flags, chapter 13.** Unsupported statistics, overconfident claims,
non-evidence-based supplement claims, incorrect anatomy, wrong examination
interpretation, outdated surgical recommendations, fabricated citations. The
figure register is the response to the first. The position register is the
response to the sixth. CITE-001 and CITE-002 are the response to the last.

## What it confirms without being asked

**The colour direction, chapter 6.** The handbook specifies deep forest green,
warm ivory background, restrained brushed gold accents, muted teal for learning
highlights, soft grey for structure. The stylesheet was built before this
document was readable and its tokens are `--green-900` through `--green-500`,
`--ivory`, `--gold`, and a soft grey `--rule`. Three of five match. Muted teal
for learning highlights is the one direction not implemented.

**Mobile-first.** Chapter 6 requires every page readable in short vertical
sections. The site has one stylesheet, no JavaScript and a fluid measure.

**Collapsible advanced content.** Chapter 6 asks for it. The depth dial is
exactly that, built with CSS radio inputs and no script.

**Topic selection priority.** Chapter 7 says to prioritise ACL, meniscus,
osteoarthritis, knee pain, MRI, anatomy, examination and rehabilitation. The
pilot page was the ACL condition page and Section 2 began with bone and
meniscal anatomy.

## Medical safety: the requirement is met

Chapter 12 requires:

> Patient-facing pages must explain that information is educational and not a
> substitute for professional assessment.

Every one of the 116 published pages carries this in the footer legal block,
generated by `tools/site_chrome.py`:

> KneeSchool is educational. It does not give individual medical advice and it
> does not replace assessment by a clinician.

The requirement was already satisfied before the handbook was readable. What was
missing is enforcement: nothing stopped the statement being edited out of the
chrome. `tools/check_site.py` now fails the build if any page lacks it.

## Three conflicts, and how they resolve

**1. Six tiers against seven.** The handbook's curriculum matrix lists Patient,
Medical Student, MRCS, FRCS, Fellowship and Consultant. There is no Junior
tier. `KneeSchool_Master_Playbook_v1.docx` is worse: five tiers, Patient to
Fellowship, with no Consultant either.

The Operations Handbook of 22 September 2026 states "the spiral has seven tiers.
Section 0 Junior Academy sits below Patient", and the Junior Academy
architecture document of 28 August 2026 specifies Section 0 in full. Both
postdate the June documents. Seven tiers stand. This is the third document to
omit Section 0 and the second to omit it from a curriculum table, which is worth
noting: the Junior Academy appears to have been added to the project after the
June planning round.

**2. FAQs on every page against FAQs on the patient tier only.** Chapter 12
says each page should have overview, key learning points, main content, FAQs,
references and related pages. Chapter 14 repeats FAQs in its per-page
requirements.

The Operations Handbook adjudicated this explicitly: "FAQs are per article,
carried by the Patient tier. Present exactly when the Patient tier is present."
It records the adjudication as deliberate. `article_template.json` sets
`allowed_in_other_tiers: false` and the style gate enforces it.

The later, explicit adjudication wins. No change. The practical effect is that a
professional-only page, such as a Section 2 surgical anatomy page, carries no
FAQs at all, which is the intended behaviour.

**3. A fifth QA tier.** Chapter 13 lists five: AI generation, assistant
editorial review, source verification, consultant review, publication review.
Publication QA checks formatting, SEO, links, images, alt text, disclaimers,
metadata and page status.

The pipeline has four. The fifth is not a conflict, it is an addition, and it is
the one addition in this document that is wholly buildable from here. Everything
publication QA checks is mechanical. `tools/check_site.py` already does the
links, the structure and, from today, the disclaimer. SEO fields, alt text and
metadata are not yet checked because no page carries them.

## What stays blocked

The handbook does not help with any of it.

- Chapter 9, source acquisition, assumes a library and a person to collect it.
  There is still no source access here, so the Evidence Verifier has still never
  run.
- Chapter 13's consultant QA assumes a consultant with a return path. There is
  still none.
- Per-page scope and `must_not_cover` for sections 4 to 15 are still absent.
  The handbook gives a taxonomy, chapter 5, not a page map. 1,233 pages remain
  outline only.
- The 775 unenumerated chapters in sections 4 to 15 are unaffected.

## What the roadmap says about where the build stands

Chapter 20 sets 100 pages for months 1 to 3 and 250 for months 4 to 6, with
anatomy, biomechanics and imaging as the month 4 to 6 deliverable. The site has
116 pages and is working through anatomy. The build is at the start of the
second phase on the handbook's own schedule.

## Questions

1. Confirm the authority order: the Operations Handbook of 22 September 2026
   wins on any point of disagreement, and the Master Operations Handbook governs
   everything it does not cover. If the June handbook is meant to be the senior
   document instead, the FAQ rule and the tier count both change and roughly 60
   pages need rework.
2. Should publication QA be built as a fifth gate now, checking SEO title, meta
   description, slug and image alt text? No page carries those fields yet, so
   building the gate means adding the fields to the brief first.
3. The handbook asks for muted teal as a learning highlight. The stylesheet has
   no teal. Add it, or leave the palette as green, ivory and gold?
