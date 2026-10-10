# Decision 016: the review pack is the return path

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Client, on 10 October 2026 |
| Status | Applied |
| Changes | New tool `tools/review_pack.py`, 25 generated packs, build status EV-2, 12 tests |

## The instruction

> yes generate a review pack

Asked in answer to this, put after chapter 3.3 went up:

> The register now holds 523 unsigned recommendations. At the current rate that
> is roughly 50 per chapter. Would you like me to generate the consultant review
> pack by chapter, so a reviewer gets one chapter at a time rather than a list of
> 523?

## What was wrong with the old packs

There are eight review packs in `docs/review/` and every one was written by hand.
They read well, because a person wrote them, and they have three problems.

They go stale the moment a page changes, and nothing says so. They cover a batch
that made sense on the day rather than a unit of the architecture. And they are
prose, so a reviewer's answer comes back as prose too, which is the half of EV-2
that was never solved: the people existed from 10 October and the route for their
decisions did not.

## What replaced them

`tools/review_pack.py` generates one pack per chapter from the chapter's own
files. Nothing in a pack is typed: the page list comes from
`published_pages.json`, the word counts and the gate result from each page's
`lint_report.json`, the claims from each page's draft handoff, the measurements
from `pipeline/config/figures/`, and the recommendations from
`pipeline/config/positions/`.

That is the same rule the two registers already follow. The list comes from the
work rather than from a person compiling it, so it cannot disagree with the site.

## The part that matters: it reads back

Every row in the measurement and recommendation tables carries a reference, such
as `3.3.1-P1` or `3.3.2-F1`. The reviewer fills a Decision cell and a name, sends
the file back, and:

    python3 tools/review_pack.py --ingest docs/review/packs/chapter-3.3.md

writes each decision into that page's register. A decision survives the next
extraction, which was tested rather than assumed, because the extractor rewrites
a register from the page on every chapter and a signature that did not survive it
would be lost on the next build.

Three properties were chosen deliberately:

**A blank row is not an error.** A reviewer who has read a pack and answered
nothing has done nothing wrong. Ingest reports the blanks and succeeds, and the
blank rows come back in the next generated pack.

**One bad row writes nothing at all.** Registers are loaded, changed in memory,
and written only once every row has been accepted. A typo in row 40 cannot leave
rows 1 to 39 signed and the pack half consumed.

**An amendment carries its wording.** `AMENDED: <new sentence>` or
`CORRECTED: <right value>` puts the replacement in the register's note field, so
whoever edits the page has the reviewer's words rather than a verdict alone.

## What this does not do

It does not edit a page. A confirmed recommendation needs nothing; an amended one
needs the prose changed, and the pack records what to change rather than changing
it. That boundary is deliberate: a tool that rewrote published prose from a table
cell would be the most dangerous thing in this repository.

It also does not verify anything. The pack states on its face that evidence
verification never ran, on every chapter, because that is still true. EV-1 is
untouched.

## Where it leaves EV-2

The mechanism exists and nothing has been signed. 523 recommendations and 254
measurements are outstanding, spread across 25 chapters, and
`python3 tools/review_pack.py --status` prints the breakdown.

The largest single chapter is 3.3 with 85 recommendations. The median is nearer
20. That was the point of cutting by chapter.
