# Consultant review pack: Section 1, Knee Fundamentals

| Field | Value |
|---|---|
| Section | 1 Knee Fundamentals |
| Pages | 16 |
| Chapters | 1.1 Introduction to the Knee (6), 1.2 Basic Knee Anatomy (10) |
| Tiers on every page | Junior, Patient, Medical Student |
| Priority | High. The architecture places all sixteen in the Foundation phase, months 1 to 3 |
| Style gate | All sixteen pass. Zero failures, zero warnings |
| Evidence verification | **Did not run on any page** |
| Reference lists | **None** |

## How these were produced

Each page was written against a brief generated from the Master Publishing
Architecture, so the scope and, more importantly, the exclusion list came from
the architecture rather than from a writer's judgement. That exclusion list is
what stops Section 1 duplicating Sections 2, 3, 6 and 7.

Agent 2, the fact checker, could not run on any page. The build environment has
no access to PubMed, Cochrane or any source library. Every page is therefore
marked `NOT_RUN_TOOLS_UNAVAILABLE` rather than stubbed as a pass.

## What you are being asked to do

Return approve, amend or reject for each page.

You are doing two jobs on all sixteen: confirming the content, and standing in
for a verification stage that could not run.

**No page carries a single reference.** The substantive claims are listed per
page in `pipeline/runs/<page_id>/draft_v1.handoff.json` under
`claims_needing_verification`, five per page, taken from the deepest tier's key
learning points. Every factual statement in the body needs the same treatment;
those five are where to start.

## Deliberate omissions across the whole section

The pages give **almost no numbers**. Where a figure would normally appear, it
has been left out rather than estimated. The exceptions are definitional ranges
that any textbook would state the same way, for example cartilage thickness and
normal range of movement.

If you want a figure anywhere, please supply the one you would stand behind.

## Specific questions

1. **Pitch of the junior tier.** Every page targets reading age 12 to 14. Is that
   consistently hit, and is anything too simplified to be accurate?
2. **The medical student tier and Section 2.** This is the same boundary question
   raised by the Menisci page and still unanswered. How much structural detail
   may a Fundamentals page carry before it belongs to the Anatomy Academy? Your
   answer applies to all sixteen pages here, not one.
3. **1.1.4 Evolution of the Human Knee.** This page makes comparative and
   evolutionary claims. Is the framing right, and is the statement about sex
   differences in injury risk pitched correctly for a junior reader?
4. **1.1.6 Lifelong Knee Health.** This page states that recreational running is
   not associated with increased knee wear and that supplements have weak
   evidence. Both are claims patients will quote back. Confirm the wording.
5. **1.2.7 Nerves and Blood Supply.** The patient tier says a knee dislocation
   can threaten the blood supply to the leg and is an emergency. Is that framed
   proportionately for a lay reader, or does it alarm without helping?
6. **1.2.10 Growth Plates.** Confirm the statement that the two physes at the
   knee contribute roughly two thirds of lower limb length, and the ages given
   for closure.

## Governance confirmed on all sixteen

- No commercial content. Every brief refuses it, because the junior tier is present.
- No citation markers in junior or patient text.
- Junior tier closes with the standard speak to an adult message.
- Patient tier closes with a when to seek help message.
- No em dashes, no en dashes, British English throughout.
- Each page respects the architecture's exclusion list for its own page id.

## Page list

| Page | Title | Words |
|---|---|---|
| 1.1.1 | What Is the Knee? | 1204 |
| 1.1.2 | Why the Knee Is Important | 959 |
| 1.1.3 | Functions of the Knee | 965 |
| 1.1.4 | Evolution of the Human Knee | 975 |
| 1.1.5 | Common Knee Problems | 915 |
| 1.1.6 | Lifelong Knee Health | 932 |
| 1.2.1 | Bones of the Knee | 1185 |
| 1.2.2 | Articular Cartilage | 1100 |
| 1.2.3 | Menisci | 1598 |
| 1.2.4 | Ligaments | 1165 |
| 1.2.5 | Tendons | 1091 |
| 1.2.6 | Muscles Around the Knee | 1184 |
| 1.2.7 | Nerves and Blood Supply | 1231 |
| 1.2.8 | Synovium | 1102 |
| 1.2.9 | Bursa | 1077 |
| 1.2.10 | Growth Plates | 1216 |

**Total: 17899 words across sixteen pages.**
