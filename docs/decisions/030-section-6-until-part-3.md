# Decision 030: Section 6's page map, and the one page nothing governed

**Date:** 31 October 2026
**Status:** Applied
**Precedents:** decisions 024 and 027, the same gap two sections earlier.

## What Part 1 says Section 6 is

> **Section 6: Conditions Library** (estimated 500 to 700 pages). The clinical
> core, chapters 6.1 to 6.156 across Parts A to T: ACL disorders (6.1 to 6.8),
> PCL (6.9 to 6.13), medial (6.14 to 6.20) ...

and its roadmap table puts Section 6's page map in the **Part 3 instalment**,
which is not in this repository.

## What the source actually enumerates

The source architecture lists 156 chapters across 20 parts. It gives numbered
sub pages for chapters 6.1 to 6.8 only, which is Part A, ACL disorders. That is
37 pages. Every chapter from 6.9 to 6.156 is a bare chapter line with nothing
beneath it.

That is not a defect in the source. Part 1's own conventions say it:

> A chapter listed in the source architecture without numbered sub pages (common
> from Section 6 onwards) publishes as a single page carrying the chapter id.

So Section 5's trick does not transfer. That map was derivable because its
chapters had leaves to flatten. Most of Section 6's have none.

## What this decision builds

`tools/extract_section6.py` builds the 37 pages the source enumerates and
refuses the other 148 chapters. It prints what it skipped, with the count, on
every run, so the gap is visible rather than discoverable.

Building every bare chapter as a single page would give 185, which is a floor
rather than a map, and those ids would carry two components where every
published page on this site carries three. Neither is this process's call.

The extractor is committed for the reason decision 027 committed Section 5's: a
map whose maker is gone cannot be re-derived or checked. A test holds the two in
step.

**What the extractor supplies and how weak each derivation is:**

- **Titles and chapter structure.** From the source, verbatim. Strong.
- **Deeper spiral pages.** From Part 1's own spiral linkage map, which states
  that the step after 6.1 to 6.8 is 7.20 to 7.31, and that 6.6 also sits in the
  women's knee health row. Strong, and derived rather than judged.
- **Tier set.** Seven tiers. The source states none. Its own overview says every
  condition should carry Patient, Medical Student, MRCS, FRCS and Fellowship
  versions; Junior and Consultant are added to reach the site's seven, matching
  the one Section 6 page that already existed. **This is the weak derivation,
  and it is the same one decisions 024 and 027 record.**
- **Scope sentence.** The title restated with a clause chosen per chapter. The
  most this process can honestly supply without Part 3.
- **Must not cover.** The section boundaries, which are stated in Part 1.

## The page nothing governed

`conditions/acl.html` was written in this repository's first commit, before any
page map existed, as the worked example of a seven tier condition article.
`about/standards.html` points at it as "See it applied" and six tier landing
pages link it as "ACL injury".

It held the id **6.1.1**, and it was the only render target in the site with no
entry in any `pages_*.json`. Nothing noticed, because no gate compared the two
lists.

The source's 6.1.1 is "What is the ACL?", a narrower chapter opener. The two are
different pages and could not share an id, so:

- the showcase page moved to **6.1.0**, which sorts ahead of the chapter and is
  clearly outside the source's numbering,
- it is declared in a new `unmapped` block in `render_targets.json`, carrying its
  reason and the decision still owed on it,
- and `NoRenderTargetIsUngoverned` now fails on any render target that is in no
  map and not declared.

The `unmapped` block is the same mechanism as `withheld`, pointing the other
way. `withheld` declares a page that exists and is not published; `unmapped`
declares a page that is published and is in no map. Both turn a silent gap into
a stated one.

**What is still owed on it.** Once chapters 6.1 to 6.8 are written they cover
its ground, and the choice is then to retire it and point its nine inbound links
at 6.1.1, or to keep it as the section's overview page and give it an id the
architecture recognises. Not this process's call, and recorded in the block
rather than left to be rediscovered.

## What the site already promised

189 references from 94 published pages point into Section 6, across 56 distinct
targets spanning 6.1 to 6.154. Only 42 of them land in the eight chapters this
decision maps. The other 147 point at chapters with no page map at all.

They render honestly: an unresolved cross link comes out as a `pending` span
carrying the page id, not a dead link. 124 exist site wide. The site is visibly
incomplete, which is what it should be while it is.

## Cost

Chapter 6.1 is written, five pages, and the remaining 32 pages of Part A are
not. The section around them is mapped at 8 chapters of 156.

A reader reaching `conditions/` sees five new pages against a library the
architecture estimates at 500 to 700. The conditions index is hand maintained
and was edited to link them; Section 6 is deliberately **not** added to
`section_indexes.json`, because the generator would publish "5 of 37 pages are
published" and 37 is not what Section 6 is. That line can be generated once the
map is real.

Part 3 is what moves this. Until it arrives, Section 6 is 37 pages designed and
148 chapters unmapped, and every page of it says the tier set is an editorial
default.
