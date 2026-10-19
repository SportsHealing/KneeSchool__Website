# Decision 028: the imaging template, and the accuracy hole it found

| Field | Value |
|---|---|
| Date | 15 October 2026 |
| Decided by | Claude, applied and open to revision |
| Status | Applied. Section 5 built on it |
| Builds on | Decision 014 and decision 023, which invented templates the same way |
| Changes | `imaging` template added, `page_type_map.json` no longer marks it pending, four new body section headings, ACC-001 widened and its scope moved into config |

## Why a decision was needed

Section 5 is 224 pages and there was no `imaging` page type. The type map had no
entry at all, so a Section 5 brief could not be generated.

This is the third time: decision 014 for biomechanics and landmark papers,
decision 023 for examination, now imaging. The pattern is stable enough to name.
A section with its own kind of page needs its own template, and the Operations
Handbook shipped three.

## The template

| Slug | Heading |
|---|---|
| `what_it_shows` | What It Shows |
| `how_it_is_acquired` | How It Is Acquired |
| `what_normal_looks_like` | What Normal Looks Like |
| `what_abnormal_looks_like` | What Abnormal Looks Like |
| `how_good_it_is` | How Good It Is |
| `where_it_misleads` | Where It Misleads |

Rule: ordered subset per tier. `how_good_it_is` already carries a floor of MRCS
in `section_tier_rules`, from decision 023, and that applies here unchanged.

Six sections where examination has five. The extra one is earned: normal and
abnormal appearance are two different teaching jobs on an imaging page, and
collapsing them produces a page that describes a tear without ever having
described the meniscus it is in.

The template has to stretch across four kinds of page and the subset rule is
what lets it:

- **5.2 physics.** "Generation of X-rays" shows, is acquired, and misleads. It
  has no normal or abnormal appearance, so it carries three sections.
- **5.6 to 5.17 findings.** "Radial Tears" carries all six.
- **5.2 artefact pages.** "Artefacts" and "Magic Angle Effect" are pages where
  Where It Misleads is the subject rather than the last section.
- **5.20 reporting.** How It Is Acquired reads as how the report is produced.
  This is the loosest fit in the set and is the first thing to revisit.

**Where It Misleads earns its place again, for a different reason.** An imaging
finding fails in patterned, nameable ways: the magic angle effect, truncation
artefact, a pulsation artefact crossing a ligament, fluid in a post operative
bed read as a re-tear. A template with nowhere to put that produces pages that
teach the appearance and omit the thing that makes a radiologist wrong.

## ACC-001, widened, and a hole it turned out to have

Decision 023 refuses a sensitivity, specificity, predictive value or likelihood
ratio written as a number on an examination page: the comparative standing of
the tests is standard teaching and recalled robustly, the percentage is recalled
alone, and a wrong one looks exactly like a right one.

Imaging carries the identical risk. "Magnetic resonance imaging is 95% sensitive
for a meniscal tear" is the same class of claim as a sensitivity for the
McMurray test. So ACC-001 now applies to both page types.

Two things changed in the course of doing it.

**The scope moved into the config.** The rule named `examination` inside
`linter.py`, so the rule's reach could not be read off `lint_rules.json`. That
is the shape of a bug this repository has already shipped: the condition
template's `body_sections_rule` said `frcs_and_above_only` in prose and nothing
in the code read it. ACC-001 now carries a `page_types` list and the function
reads it.

**The term list was missing the adjectives.** `ACC_TERM` matched sensitivity,
specificity, PPV, NPV, AUC and likelihood ratio. It did not match *sensitive* or
*specific*, so "MRI is 95% sensitive for a meniscal tear" passed the gate.
It would have passed on an examination page too, for the last 227 pages.

The adjective patterns are kept deliberately tight, because *specific* is an
ordinary word and this repository's own reference boilerplate contains the
phrase "a specific sensitivity written from memory". Only a number bound
directly to the adjective counts: `95% sensitive`, or `specific in 90 per cent`.
A test holds both directions, including the boilerplate.

## Cost

The template is unvalidated. No editorial authority has confirmed its six
sections, exactly as none confirmed examination's five, and a reviewer should
know that the shape of every Section 5 page is this process's invention rather
than the handbook's instruction.

The reporting chapter is the weakest fit and will probably want its own type.
Recording that now is cheaper than discovering it at page 200.

## Amendment, 15 October 2026

The client has decided not to publish chapter 5.19, the Magic Angle MRI Academy.
Its ten pages were never written and are recorded in the `withheld` block of
`render_targets.json` rather than removed from the architecture, because the
architecture records what the site is designed to contain and this is a
publishing decision rather than an architectural one. Section 5 is 224 pages
designed and 214 to be written.

The template is unaffected. The magic angle effect remains in the site as 5.2.20,
a page of standard MRI physics in the physics chapter, and the five references
chapter 5.1 made to the academy were repointed at 5.2.19 Artefacts, 5.2.20 Magic
Angle Effect and 5.18.4 UTE Imaging.

## Amendment, 19 October 2026: the hold is reversed

The client instructed that chapter 5.19 be published. The ten pages have been
written and are render targets. The `withheld` block now holds only the three
Section 0 pages it held before 15 October. Section 5 is 224 pages designed and
203 of them published.

Three consequences are worth recording, because the hold left traces.

**5.2.20 said the hold was permanent.** Its fellowship block carried a sentence
stating that the academy would not be published and that the physics page was
therefore the site's whole treatment of the effect. That sentence was true when
written and false the moment this amendment was made, so it has been replaced by
one pointing at 5.19.1. This is the second time a page has recorded a client
decision in its own prose and then had to be corrected when the decision moved.
A page that states a publishing decision becomes stale when the decision does,
and there is no gate for that.

**The withheld gate stays.** The gate added for EV-41 refuses a reference from a
published page into a held page. Releasing ten of the thirteen held pages does
not weaken it, and the three Section 0 holds keep it live.

**The references repointed on 15 October have been repointed back.** The prose
references and cross links that pointed into 5.19 were moved to 5.1.8, 5.11.1,
5.21.8 and 5.2.20 when the chapter was held, by 513d9d4 for chapter 5.1 and by
4e0dfa0 for the rest. The client asked for them back on 19 October, so 39
paragraphs across nine pages were returned to their pre-hold text: 5.1.6, 5.1.8,
5.12.6 and 5.18.1 to 5.18.6. The chapter now carries 33 inbound prose references
and 9 inbound cross links.

The restoration was done paragraph by paragraph rather than by rewriting
sentences. For each file the two commits touched, the script took the text before
the commit and the text after, paired the blocks that differed, kept only the
pairs whose before side named a page in 5.19, and swapped the after side back.
Anything that had changed since would have been reported and left alone; nothing
had. Doing it that way matters because the repointing had reworded the
surrounding sentences to match each substitute page's title, so a page id swap
alone would have left prose that named the wrong subject.

One of the moves had pointed at 5.21.8 Future Directions, which is designed and
unwritten, so restoring it also removed a cross link into a page that does not
exist yet.

## What 5.19.8 does not contain

Chapter 5.19's eighth page is titled Imperial Magic Angle Programme. Its subject
is a named research programme at a named institution, which makes it the only
page in Section 5 whose content would be a claim about a real organisation.

This environment has no source access, and the handbook's rule is that a missing
reference is acceptable while an invented one is a critical failure. An
investigator, a date, a grant, a trial name or a result written from memory falls
on the wrong side of that rule. The page therefore names none of them.

What it carries instead is the structure such a programme would have and the
questions a reader should ask of it, with the first paragraph stating plainly
that the emptiness is a decision rather than an oversight. The alternatives were
to invent content, which the handbook forbids, or to hold one page of a chapter
the client asked to be published, which is not this process's call to make.

The page is the first item a reviewer with source access should reach for in this
chapter.
