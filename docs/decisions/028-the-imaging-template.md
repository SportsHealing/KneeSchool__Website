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
- **5.19 Magic Angle.** An artefact academy, where Where It Misleads is the
  subject of the chapter rather than its last section.
- **5.20 reporting.** How It Is Acquired reads as how the report is produced.
  This is the loosest fit in the set and is the first thing to revisit.

**Where It Misleads earns its place again, for a different reason.** An imaging
finding fails in patterned, nameable ways: the magic angle effect, truncation
artefact, a pulsation artefact crossing a ligament, fluid in a post operative
bed read as a re-tear. A template with nowhere to put that produces pages that
teach the appearance and omit the thing that makes a radiologist wrong. Chapter
5.19 exists because this site's own people have a programme on exactly that.

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
