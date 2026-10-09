# Finding 001: what the Sections 1 to 15 architecture gives, and what it does not

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Source | `KneeSchool_Sections_1_to_15_Full_Architecture.docx`, received 9 October 2026 |
| Also received | `KneeSchool_Master_Handbook_Table_of_Contents.pdf`, a different document |
| Closes | Build status EV-5, partly |

## What arrived

The compiled page level architecture for Sections 1 to 15. It has been parsed
into two repository configs:

- `pipeline/config/architecture/outline_1_to_15.json`, 1,516 pages and 1,047
  chapters, with page id, title, chapter and part.
- `pipeline/config/section_conventions.json`, each section's declared tiers,
  required subsections and audiences, taken from its own preamble.

`tools/outline.py` queries both.

## The integrity check passed

Sections 1, 2 and 3 appear in both the new document and the Part 1 page map that
has driven every page written so far. All 283 page ids, titles and chapter names
match, with one exception:

| Page | Part 1 | New upload |
|---|---|---|
| 2.12.5 | Dynamic Stabilisers | Dynamic Stabili**z**ers |

Part 1 is correct. UK-001 bans the -ize form in body text, so the page map keeps
the British spelling and the upload has a typographical error. No change made.

**Section 0, the Junior Academy, is absent from the new document.** It covers
Sections 1 to 15 only. The 38 Section 0 pages written to date are governed by
Part 1 and by decisions 002 and 003, and nothing in the new document contradicts
them. Worth confirming that Section 0 is still in the plan.

## What it unblocks

Planning. For the first time there is a named target for every section: what the
chapters are, what the pages in them are called, and how many there are.

It also supplies something decisions 003 and 005 had to invent in its absence:
**a page template per section, stated by the client.** Section 6 declares five
tiers and sixteen required subsections for every condition. Section 10 declares
five tiers. Section 13 declares six. Sections 6, 7, 8, 13, 14 and 15 declare
their required subsections. That is exactly the material that was missing when
Section 0's and Section 2's templates had to be ruled on locally.

## What it does not unblock

**Brief generation for Sections 4 to 15.** The document gives titles. It does not
give, per page:

- `tiers_required`
- `scope` / must cover
- `must_not_cover`
- `deeper_pages`
- `page_type`
- `priority`

The third of those is the one that matters most. The `must_not_cover` list is the
mechanism that stops the same fact being written on three thousand pages, and
`tools/architecture.py` copies it from the architecture rather than letting a
drafter decide. A brief generated without one would be worse than no brief,
because it would look complete.

The outline is therefore deliberately **not** named `pages_*.json`.
`tools/architecture.py` globs that pattern to build briefs, and a test asserts
the outline stays outside it.

| State | Pages |
|---|---|
| Full page map, briefable | 283 |
| Outline only: title, chapter, part | 1,233 |

## The architecture runs out of detail partway through each later section

775 of the 1,047 chapters carry no enumerated pages. The pattern is consistent:
each section from 6 onwards is enumerated to page level for its first part or
two, then drops to chapter titles.

| Section | Chapters | Enumerated to pages |
|---|---|---|
| 6 Conditions Library | 156 | 8 |
| 7 Surgical Academy | 136 | 9 |
| 8 Rehabilitation Academy | 115 | 13 |
| 14 Question Bank | 80 | 4 |
| 15 Video Academy | 100 | 30 |

`python3 tools/outline.py --gaps` lists all 775.

At five pages per chapter the finished plan is of the order of five thousand
pages, which is consistent with Part 1's own per section estimates.

## What this immediately fixed

Every page written so far carries forward links to sections that had no
architecture, written as `[[7.20 | Cruciate reconstruction]]`. The ids came from
Part 1's `deeper_pages` lists and were right. **The labels were invented and 28
of them were wrong.**

`tools/crossrefs.py` now loads the outline, including the 775 chapters with no
pages, so a chapter level link is checked too. All 28 are corrected across 36
pages. Three were worse than mislabelled: the anterior cruciate condition page
linked to PCL, MCL and posterolateral corner injury using page ids inside the
ACL chapter, because Section 6 had no architecture when it was written. Those now
point at 6.9, 6.14 and 6.23.

Before this document arrived, none of those 510 forward links could be checked
against anything.

## The second file is a different document

`KneeSchool_Master_Handbook_Table_of_Contents.pdf` is the contents page of a
**Master Handbook**, not the publishing architecture. Twenty three chapters
covering vision, brand, sitemap, educational pathways, the academies, an
assistant operations manual, commercial integration, SEO, KPIs and a roadmap.

Two things follow.

**The handbook itself is not here.** Only its contents page. Several of its
chapters would answer open questions on the build status page: 19 Assistant
Operations Manual covers source collection and the publication workflow, and 22
KPIs and Governance covers the review process.

**It uses a different numbering system for the same academies.** In the handbook
the Anatomy Academy is chapter 6 and the Conditions Library is chapter 9; in the
publishing architecture they are Sections 2 and 6. Nothing in the repository uses
the handbook numbering, and nothing should start to without a decision, because
"Section 6" would then be ambiguous.
