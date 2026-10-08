# Consultant review pack: Section 2, chapters 2.1 and 2.2

| Field | Value |
|---|---|
| Section | 2 Anatomy Academy |
| Chapters | 2.1 Femur (9 pages), 2.2 Tibia (6 pages) |
| Pages | 15 of the 79 in Section 2 |
| Page type | anatomy, on every page |
| Tiers | Medical student, MRCS and FRCS on all 15; fellowship on 2.1.7 and 2.2.6 |
| Style gate | All 15 pass. Zero failures, zero warnings |
| Evidence verification | **Did not run on any page** |
| Reference lists | **None** |
| Measurements | **None, deliberately. See decision 005** |
| Words | 20,976 |

## Read this part first

This is the first section of the site written entirely for professionals. Every
page before it had a junior or patient tier that a lay reader could stop at.
These have none. The shallowest thing on any of these pages is pitched at a
medical student, and the deepest at a fellow planning an approach.

Nothing on them has been verified. Source retrieval has never been available in
the build environment, so not one anatomical statement has been checked against
a text. On a junior page that is uncomfortable. On a page describing the
relationship between the posterior cruciate attachment and the popliteal artery,
it needs saying plainly: **this is unverified content written for people who
operate.**

## The decision that shapes every page

**These pages carry no measurements.** No footprint dimension, no posterior
slope in degrees, no sulcus angle, no distance from a landmark, no normal range.

Anatomy at this depth is normally quantitative, and candidates revise exactly
those numbers. They are absent because none could be verified, and because a
plausible wrong dimension on an FRCS page is worse than no dimension: it gets
repeated in an answer and not caught.

Where a number would sit, the page gives the relationship instead. Larger than,
posterior to, proximal and posterior to, converging on.

Three pages say so in their own text, because they are the ones where it costs
the reader most:

- **2.2.3 Tibial Spine.** Every published description of these footprints is
  quantitative. The page says so in its FRCS tier.
- **2.1.6 Femoral Attachments of Ligaments.** The page is a map with no
  coordinates, and says that in as many words.
- **2.2.6 Surgical Anatomy.** Every published safe zone around the proximal
  tibia is a distance from a landmark.

This is now enforced by the style gate rather than by drafting discipline.
FIG-001 fails any page whose brief forbids figures, and the rule covers Section
0 as well, which is where the same ruling was first made.

## What you are being asked to confirm

1. **The no measurements rule.** Decision 005. Confirm it, or reverse it, in
   which case the figures need adding with a dated source against each and that
   cannot be done from here.
2. **The tier pattern.** Medical student gets Structure, Relations, Function and
   Clinical Relevance. MRCS adds Blood Supply and Innervation. FRCS drops to
   Relations, Function and Clinical Relevance and is written as constraint on a
   decision. Fellowship is Clinical Relevance only, approach anatomy with
   technique excluded. Decision 005 sets this out in full.
3. **Accuracy, on 15 pages, by someone who operates.** This is the real ask.

## Five pages to read first

**2.2.3 Tibial Spine.** The highest consequence page in the batch. It states
that capsule alone separates the posterior cruciate attachment from the
popliteal artery and that flexion does not reliably change that. If that
sentence is wrong or overstated, it is the first thing to fix.

**2.1.7 and 2.2.6 Surgical Anatomy.** The two fellowship pages. Both describe
approaches as anatomy and both deliberately stop short of technique. Check that
the line holds, and that nothing on them reads as operative instruction.

**2.1.6 Femoral Attachments of Ligaments.** Every attachment on the distal femur
in one place, ordered so the set can be found from two landmarks. The ordering
claims are the checkable part: adductor magnus highest, superficial collateral
lowest, medial patellofemoral ligament between them; and laterally the
collateral origin proximal and posterior to the popliteus origin.

**2.1.9 Biomechanical Relevance.** The page closest to the boundary with Section
3. The architecture excludes biomechanics beyond orientation, so everything here
is qualitative and hands over to 3.13. Check it has not crossed.

## What has not been checked

Nothing. The claims are listed per page in
`pipeline/runs/<page_id>/draft_v1.handoff.json` under
`claims_needing_verification`, four or five per page, taken from the deepest
tier's key learning points. Every other anatomical statement in the body needs
the same treatment.

## Where the pages are

Published under `anatomy/`, named `<chapter>-<page>.html`, because Section 2
reuses page titles across chapters: Gross Anatomy appears five times in the
section and Surgical Anatomy five times.

`anatomy/index.html` is the chapter index. It is generated from the architecture
and the published page list, so it shows all 79 pages with the 15 written ones
as links and the rest as coming soon. It will stay correct as further chapters
land without anyone editing it.

The Anatomy Academy is reachable from the Reference menu.
