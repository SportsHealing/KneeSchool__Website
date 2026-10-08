# Decision 003: templates for Section 0 chapters 0.3 to 0.7

| Field | Value |
|---|---|
| Date | 7 October 2026 |
| Decided by | Build team, applied and flagged for confirmation |
| Status | Confirmed. Orders revised 7 October 2026 |
| Applies to | page types careers, study_skills, teacher_resource, assessment |
| Closes | Handbook open question 5, architecture open question 6 |

## The problem

The Operations Handbook defines three article templates: anatomy, condition and
procedure. The architecture gives Section 0 thirty eight pages across seven
chapters and tags twenty seven of them with a page type the handbook never
defines.

| Page type | Pages | Chapters |
|---|---|---|
| careers | 6 | 0.3 |
| study_skills | 11 | 0.4, 0.5 |
| teacher_resource | 6 | 0.1.6, 0.7 |
| assessment | 4 | 0.6 |

Until now `page_type_map.json` pointed all four at the anatomy template and
marked them `variant_pending`. That is unusable in practice. The anatomy
template's first heading is Structure and Location. Forcing it onto 0.4.1
Choosing Subjects would put a heading reading Structure and Location on a page
about picking A levels.

Leaving them unmapped is no better. With no template the style gate cannot check
structure at all, so these would be the only pages on the site written without a
shape anything verifies.

## The ruling

Four templates are defined locally, in `article_template.json` under
`page_types`, with the heading text in `body_section_headings`. They follow the
handbook's own conventions: body sections are an ordered subset per tier, key
learning points are per tier, and the reference list stays at article level.

**careers**

1. What the Work Involves
2. The People Who Do It
3. The Route
4. What It Takes
5. Where to Find Out More

**study_skills**

1. What This Is
2. How It Works
3. How to Prepare
4. Common Mistakes
5. Where to Find Out More

**teacher_resource**

1. Curriculum Links
2. What This Covers
3. How to Use It
4. What to Watch For
5. Where to Find Out More

**assessment**

1. What This Is
2. How to Earn It
3. What It Covers
4. Rules and Fair Play
5. Where to Find Out More

Word bands are 500 to 1200 for the first three and 400 to 1000 for assessment,
then scaled by decision 002 because every one of these pages carries one tier.

## The revision of 7 October 2026

The orders above are the confirmed ones. The first draft of this decision had
four different orders, and the client changed all four. What changed and why:

| Template | Change |
|---|---|
| careers | What the Work Involves moves to the front and What This Is is dropped. Lead with the work, not with a definition |
| study_skills | Why It Matters is dropped. On a page that is a set of instructions it reads as filler |
| teacher_resource | Curriculum Links moves to the front. A teacher checks the mapping before anything else |
| assessment | How to Earn It moves above What It Covers |

The two dropped headings had prose under them on seventeen pages. None of it was
deleted.

- The careers What This Is prose is folded to the front of The People Who Do It.
  The reader now meets the work, then who does it and what it is.
- The study skills Why It Matters prose is folded to the end of What This Is. The
  heading was the objection, not the facts under it.

Both folds are in `emit2.py` as a documented migration map rather than applied by
hand, so they are inspectable and repeatable.

One page departs from its order. 0.7.4 Supporting an Injured Young Athlete is
written for parents, and its Curriculum Links section said "Not applicable".
That is a reasonable fourth section and a terrible first one, so the page omits
it and opens with What This Covers. The template allows an ordered subset, so
this needs no exception.

## The reasoning behind the original orders

Kept for the record. Each was taken from the question a reader of that chapter
arrives with.

- A fourteen year old reading chapter 0.3 wants to know what the job is, who
  does it, how you get there, and what the day is actually like, in that order.
  Reversing it and opening with the examination structure loses them.
- Chapter 0.4 and 0.5 readers are doing a task, not reading about a subject.
  How It Works then How to Prepare then Common Mistakes is the shape of
  instructions, which is what those pages are.
- Chapter 0.7 serves adults planning a lesson or supporting an injured child.
  Curriculum Links sits second because a teacher checks the mapping before
  reading the activity.
- Chapter 0.6 describes awards. What It Covers before How to Earn It, because
  the criteria are the award.

`Where to Find Out More` is last on all four and is not optional on a page that
would otherwise state a requirement. See the next section.

## No unverifiable figures on these pages

Chapters 0.3 to 0.5 invite entry requirements, admissions test scores, fees,
deadlines and competition ratios. Every one of those changes annually, and no
source retrieval was available when these pages were written, so none could be
checked.

The ruling is that these pages carry no entry requirement, test score, fee,
deadline or application statistic. Where a figure would normally go the page
names the body that publishes it and tells the reader to check it there. This
also satisfies the architecture's own instruction on 0.4.3, which excludes test
coaching content and asks for official sources to be signposted.

This started as a content rule rather than a lint rule, which meant it relied on
whoever was drafting remembering it. Decision 005 needed the same rule for
Section 2's measurements, so it is now enforced by the gate: FIG-001 fails any
page whose brief carries `governance.figures_allowed: false`, and every page in
Sections 0 and 2 carries that flag. It is also still listed in each page's
handoff block.

**Confirmed by the client on 7 October 2026.** The rule stands. No entry
requirement, test score, fee, deadline or application statistic goes on a
Section 0 page, and a later reviewer should not add one. Where a figure would
sit, the page names the body that publishes it. This is no longer an open
question and does not need raising again in a review pack.

## Status in the handbook

These four templates are not in Handbook v1.0. They are candidates for v1.1.
`article_template.json` records that under `local_additions_note`, and each new
page type carries `source_of_truth: decision 003`, so a reader of the config can
tell which templates the handbook owns and which this decision does.

If editorial rejects an order, the prose survives. That claim has now been
tested: all four orders were changed on 7 October 2026, seventeen pages lost a
heading, and not one sentence of prose was lost with it. The cost was one
re-emit, one re-render and about ten minutes.
