# Decision 004: close chapter 0.6 on the site

| Field | Value |
|---|---|
| Date | 7 October 2026 |
| Decided by | Client |
| Status | Applied |
| Applies to | Section 0 chapter 0.6, Junior Certificates and Challenges |

## The ruling

Chapter 0.6 is closed in the site's navigation. Its one publishable page, 0.6.1
Knee Explorer Certificate, moves to the end of chapter 0.1 on the Junior
Academy syllabus. The other three pages are written and held unpublished.

## Why

The architecture gives chapter 0.6 four pages. Three of them describe features
that do not exist and cannot be built without work nobody has commissioned:

- 0.6.2 Future Surgeon Challenge needs the Section 14 adaptive question bank.
- 0.6.3 School Leaderboards needs accounts, progress tracking, a lawful basis
  for processing children's data, a data protection impact assessment, ICO Age
  Appropriate Design Code compliance, a named safeguarding lead and a
  pre moderation process.
- 0.6.4 Digital Badges needs all of 0.6.3's requirements plus badge artwork.

All three were written and passed the style gate. All three are held, under the
rule that came out of that decision: **a page may say a feature is not ready,
but a page whose only subject is a feature that is not ready does not publish.**

That left a chapter heading with one page under it and three greyed out rows.
A chapter that is three quarters placeholder advertises what the site cannot do
on the page where a new reader is choosing what to read. Closing it is more
honest than leaving the stubs on display.

## What was done

- The 0.6 card is gone from the Junior Academy syllabus.
- The certificate is the last row of chapter 0.1, labelled "covering 0.1 and
  0.2", because that is its actual scope.
- The 0.6 row is gone from the "Where each chapter leads" table.
- The hero's second entry card offered a ten question quiz, which was 0.6.2. It
  now points at the certificate, which exists.
- `levels/junior.html` carries no "coming soon" marker of any kind.

## What was deliberately not done

**The architecture was not edited.** It still lists chapter 0.6 with four pages,
and 0.6.1 still carries `page_id` 0.6.1 and the chapter name "Junior
Certificates and Challenges" in its own page metadata. That is the architecture's
truth and the page's provenance, and rewriting a client source document to match
a navigation decision would be the wrong repair.

So a reader of the certificate page sees a chapter name that is not in the
menu. That is a known and accepted discrepancy, recorded here so it is not later
mistaken for a bug.

**Nothing was deleted.** The three held drafts, their handoffs and their lint
reports are in `pipeline/runs/0.6.2` to `0.6.4`, and `render_targets.json`
records each one's reason under `withheld`.

## How to reopen it

1. Build the feature.
2. Move the page's entry from `withheld` back into `pages` in
   `render_targets.json`.
3. Run `python3 tools/render_site.py`.
4. Restore the 0.6 card and its chapter map row on `levels/junior.html`, and
   move the certificate back.

Steps 2 and 3 are a minute's work. Step 1 is the whole of PG-4 and PG-5 on the
build status page.
