# Decision 009: which handbook has authority

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Confirmed |
| Closes | Build status item EV-12 |
| Confirms | The FAQ rule and the seven tier spiral, both already built |

## The question put

> Confirm the authority order: the Operations Handbook of 22 September 2026 wins
> on any point of disagreement, and the Master Operations Handbook governs
> everything it does not cover.

Answered yes.

## The order

1. **KneeSchool Operations Handbook**, version 1.0, 22 September 2026. Senior on
   any point of disagreement. It says so itself: "Where this handbook and any
   other document disagree, this handbook wins."
2. **KneeSchool Sections 1 to 15 Full Architecture**, and the Junior Academy
   architecture of 28 August 2026. These own the page map, titles and numbering.
   Decision 008 settles the numbering.
3. **KneeSchool Master Operations Handbook**, 13 June 2026. Governs everything
   the Operations Handbook does not cover, which is most of the commercial and
   operational side: the sitemap, SEO, image and video standards, publication
   QA, KPIs, the roadmap and the integration strategies.
4. **Master Playbook and Master Playbook v1**, 13 June 2026. Historical. Both
   are superseded on every point where a later document speaks, and the v1
   document is a set of headings with placeholder bodies.

## What this settles

**FAQs stay on the patient tier only.** The Master Operations Handbook's
chapters 12 and 14 ask for FAQs on every page. The Operations Handbook
adjudicated it the other way and recorded why: three to five pairs, present
exactly when the patient tier is present, inside the patient tier block. No
other tier carries them. `article_template.json` keeps
`allowed_in_other_tiers: false` and the style gate keeps enforcing it.

The practical effect: a professional-only page, such as a Section 2 surgical
anatomy page, carries no FAQs at all. That is now deliberate and recorded.

**The spiral keeps seven tiers.** The Master Operations Handbook's curriculum
matrix lists six, Patient to Consultant, with no Junior. Master Playbook v1
lists five, Patient to Fellowship, with no Consultant either. Both are June
documents. Section 0 Junior Academy stays, and so does Consultant.

**No rework.** Had the June handbook been senior, roughly 60 pages would have
needed FAQs added and the Junior Academy would have had no place in the
curriculum. Nothing changes.

## Why the dates matter more than the titles

"Master" in a filename is not a statement of authority. The Master Operations
Handbook carries no version number and no date in its text; its PDF was written
on 13 June 2026, as were both playbooks. The Operations Handbook is explicitly
version 1.0 of 22 September 2026 and names "prior playbook drafts" as documents
it supersedes. The June documents are those drafts.

This ordering is now recorded so that the next document to arrive is placed
against it rather than against whichever file was read most recently.
