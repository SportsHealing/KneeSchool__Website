# Decision 007: a clinical recommendation needs a name against it

| Field | Value |
|---|---|
| Date | 8 October 2026 |
| Decided by | Client instruction to keep one recommendation, generalised by the build team |
| Status | Applied |
| Applies to | Every page carrying a tier from medical student upwards |

## How this came up

The review pack for chapters 2.5 and 2.6 singled out one sentence as a problem:

> Because the lateral compartment depends on its meniscus for congruence, the
> threshold for difficult preservation surgery should be lower here than
> medially.

That is not anatomy. It is a recommendation about when to operate, written by a
process with no clinical qualification, on a page that states it has not been
reviewed. The pack said it should carry the consultant's name or come off the
site.

The client said keep it.

That is a reasonable answer, and acting on it exposed the real problem: **the
sentence was not unusual.** A scan of the written pages found seventy six
sentences that tell a clinician what to do, across twenty seven pages, including
Section 1 and the anterior cruciate condition page. Picking out one and leaving
seventy five would have been worse than leaving all of them, because it would
imply the rest had been looked at.

## The ruling

### 1. The recommendations stay

They are the useful part of a professional page. An anatomy page that refuses to
say what its anatomy implies is less useful and no safer, because the reader
draws the inference anyway without seeing the reasoning.

### 2. Every one is registered

Each page has a register at `pipeline/config/positions/<page_id>.json` with one
entry per recommendation:

| Field | What it holds |
|---|---|
| `as_written` | the sentence, verbatim |
| `tier` | which tier block it sits in |
| `section` | which body section |
| `detected_as` | imperative, or directed modal |
| `kind` | `CLINICAL_RECOMMENDATION` until a reviewer says otherwise |
| `verification` | `UNSIGNED`, `CONFIRMED`, `AMENDED`, `WITHDRAWN` or `NOT_CLINICAL` |
| `signed_off_by` | empty, for the name |

`tools/positions.py --extract` generates it from the pages. It never overwrites a
verdict, a classification or a name somebody has set. A sentence removed from a
page is marked `WITHDRAWN` rather than deleted, so the record of what was signed
survives.

### 3. The gate warns rather than fails

`POS-001` warns when a professional page carries a recommendation that is not in
its register. It is a warning and not a failure, deliberately: the detector is a
heuristic over imperative openers and directed modals, and a false positive must
not be able to block a page. What it must do is stop the pages and the sign off
list drifting apart.

It over collects on purpose. A false positive costs a reviewer one line in a
register. A false negative leaves unsigned clinical advice on a page read by
somebody who operates.

### 4. Teaching instructions are reclassified, not deleted

"Count the bow ties" and "Place the posterior root by its neighbours" are
instructions to a reader learning anatomy, not directions about patient care.
The reviewer marks those `NOT_CLINICAL`. They stay in the register, because the
judgement that they are not clinical is itself worth recording.

## What this does not do

It does not make the recommendations correct. Nothing here has been verified and
no figure has been checked. What it does is make the set of claims somebody is
being asked to stand behind finite, listed and generated rather than
remembered.

## How to work the list

    python3 tools/positions.py --report --unsigned

Then set `verification` and `signed_off_by` in the register. Re-run `--extract`
after any edit to a page; it preserves what has been set.

## The same shape as decision 006

This is the third register on the build, after the figure register and the
withdrawn word count overrides. The pattern is now explicit: where the build
produces a claim it cannot verify, it does not hide the claim and it does not
drop it. It lists it, states what it is worth, and makes the list generated from
the work rather than compiled by hand.
