# Decision 024: how Section 4 is built before Part 2 of the architecture arrives

| Field | Value |
|---|---|
| Date | 11 October 2026 |
| Decided by | Claude, under the client's instruction of 11 October 2026: "start section 4" |
| Status | Applied. Open to revision the day Part 2 arrives |
| Changes | New `pipeline/config/architecture/pages_4.json`, 227 pages; `generated_from` now names the file a brief actually came from; three findings recorded |

## The problem

Section 4 could not be started, and the reason was in the repository rather
than in the subject.

`pipeline/config/architecture/pages_0_to_3.json` carries full entries for
Sections 0 to 3: tiers, scope, siblings, deeper pages, must not cover, page
type, priority. That file is generated from the Master Publishing Architecture
**Part 1 of 6**, which says on its own first page that it carries "the full page
map for Sections 0 to 3".

Section 4's page map arrives in Part 2. Part 2 is not in this repository.

What exists for Section 4 is `outline_1_to_15.json`, extracted from a different
document, and its own note says exactly why it cannot be used:

> It is deliberately not named `pages_*.json`, because `tools/architecture.py`
> globs that pattern to build briefs and a brief generated from this file would
> have no tiers and no `must_not_cover` list. The `must_not_cover` list is the
> mechanism that stops the same fact being written on three thousand pages, so a
> brief without one is worse than no brief.

That note was right and it is the reason this decision exists.

## What was wrong with the outline as well

Section 4 is **227 pages, not 198**, and the discrepancy is a real extraction
error rather than a counting dispute.

Chapter 4.2 History Taking is organised in the source as five navigational sub
sections, each with seven or eight four level items beneath it:

```
Section 4.2.1 Presenting Complaint
  4.2.1.1 Pain
  4.2.1.2 Instability
  ...
```

The outline recorded the five **headings** as pages and dropped the 34 **leaves**
beneath them. So chapter 4.2 appeared as five pages when its content is 34.

Part 1 settles the numbering. Section 2 of that document says navigational
groupings "never appear in page ids" and that page ids are section.chapter.page.
So the five headings become no page at all and the 34 leaves are renumbered
4.2.1 to 4.2.34. Section 4 totals 198 minus 5 plus 34, which is 227.

**This probably affects other sections.** The outline covers Sections 1 to 15
and the same extraction produced all of it, so any other section whose source
uses four level ids is undercounted the same way. Recorded as a finding rather
than fixed here, because fixing it means re-reading eleven more sections and
Section 4 is the one being built.

## What this decision supplies, and where each part comes from

| Field | Source |
|---|---|
| `page_id`, `title`, `chapter` | the source architecture's own lines |
| `tiers_required` | Part 1 section 4's own words: "Examination for Medical Student to Fellowship tiers". So medical_student, mrcs, frcs, fellowship on every page |
| `must_not_cover` | Part 1's authority boundaries, applied per chapter |
| `siblings` | computed from the chapter's own page list |
| `scope` | the page's title, stated as a scope sentence |
| `deeper_pages`, `priority` | judgement, flagged below |

The tier set is the part that matters most and it is the part that is not
invented. Part 1 states it for the whole section in one sentence, and that
sentence is quoted above. It gives Section 4 no patient tier, no junior tier and
no consultant tier, which is a stronger claim than it looks: it means no page in
this section carries the balance argument that decision 018 governs, and the
five patient factors do not apply here.

`scope` and `deeper_pages` are the weakest fields. Part 1 gives a one sentence
scope per page for Sections 0 to 3 and gives Section 4 nothing, so a title
restated as a scope sentence is the most this process can honestly supply.
`deeper_pages` is per chapter rather than per page, which is coarser than
Sections 0 to 3 and is why cross linking in this section will need a pass once
Part 2 exists.

## Three findings recorded while doing this

**The page count for eleven other sections is unverified.** As above.

**`generated_from` was a hardcoded string, not a fact.**
`tools/architecture.py` wrote `"Master Publishing Architecture,
pages_0_to_3.json"` into every brief it produced, whatever file the page came
from. It happened to be true for all 322 briefs written so far, because only one such file
existed, and it would have been false on the first Section 4 brief. Fixed to
name the file the page actually came from, so no backfill is needed: every
existing brief's value is correct as written.

**`clinical_advice_allowed` is a governance flag that nothing enforces.** It is
written onto every brief, a test asserts it is present, and no lint rule, tool
or gate reads it. A flag that looks like a control and is not one is worse than
no flag, because it invites the belief that something is being checked. Recorded
rather than removed, because deciding what it should mean for Section 4, which
genuinely owns clinical content, is an editorial question rather than a cleanup.

## What should replace this

Part 2 of the Master Publishing Architecture, which carries Section 4's real page
map: per page scope, per page tiers, per page deeper spiral links and the
priorities Part 1 says arrive there. When it lands, `pages_4.json` is regenerated
from it and the briefs are regenerated from that, and the only things that should
survive are the hand set fields the generator already preserves.

Until then every Section 4 page carries a tier set and a boundary list traceable
to one sentence in Part 1, and the build status says so.
