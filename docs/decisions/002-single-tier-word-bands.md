# Decision 002: word count for a page that carries one tier

| Field | Value |
|---|---|
| Date | 7 October 2026 |
| Decided by | Build team, applied and flagged for confirmation |
| Status | Applied, awaiting editorial confirmation |
| Applies to | Any brief generated from the architecture |

## The problem

The Operations Handbook gives word count ranges per page type. An anatomy page
is 800 to 1800 words. Those ranges were written for a page carrying several
tiers, because every page the handbook had in view carried several.

Section 0 pages carry one tier. The first eleven came out between 400 and 650
words and were failing the gate for being under 800.

Padding them to 800 would have been the wrong fix. A junior page is not a short
version of a three tier page; it is a different object. Taking a 500 word
explainer written for a thirteen year old and stretching it to 800 makes it
worse at the one job the handbook sets for that tier, which is a reading age of
12 to 14.

## The ruling

Word bands scale with the number of tiers the brief requires.

| Tiers | Band |
|---|---|
| 1 | 350 to 900 |
| 2 | 600 to 1300 |
| 3 or more | the handbook's page type default |

The handbook already permits this. Section 3.4 says a brief may override the
default within reason, and the brief value then governs that page.

## Why these numbers

The three tier default of 800 to 1800 works out at roughly 270 to 600 words per
tier. The single tier band of 350 to 900 sits slightly above that, which is
right: a page with one tier carries its own introduction and conclusion rather
than sharing them across three.

## Where it is applied

`tools/architecture.py`, in `scale_for_tiers`. Every brief generated from the
architecture picks it up.

## A trap worth knowing about

Regenerating a brief over an existing file preserves hand set values, including
the word count. That is correct when someone has deliberately overridden it, and
wrong when the generator's own default has changed. Delete the brief first if
you want the new default.

## Open

The Editor in Chief should confirm the bands, or replace them. Handbook open
question 2 already flags the word count defaults as provisional.
