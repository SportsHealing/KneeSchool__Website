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
| Measurements | **12, all unverified. See decision 006 and the figure register** |
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

## The figures, and what they are worth

The client's instruction on 8 October 2026 was to keep the measurements and to
check them, provided they are based on current papers.

**That last condition is not met and cannot be met from the build environment.**
There is no source access here. Every figure on these pages is written from
standard teaching held in memory, not from a retrieved paper. That is usually
right, occasionally out of date, and never attributable.

So the figures are here, and the machinery around them has been built to make
the checking half of the instruction real. Twelve figures across six of the
fifteen pages, every one registered:

| Page | Figure | Tier |
|---|---|---|
| 2.1.1 | distal femoral valgus, 5 to 7 degrees | FRCS |
| 2.1.1 | transepicondylar to posterior condylar rotation, about 3 degrees | MRCS |
| 2.1.3 | femoral condylar cartilage, 2 to 3 mm | Medical student |
| 2.1.3 | medial compartment load share, about 60 per cent | Medical student |
| 2.1.5 | trochlear sulcus angle, about 138 degrees | Medical student |
| 2.1.5 | trochlear cartilage thickness, about 5 mm | MRCS |
| 2.1.6 | anterior cruciate femoral footprint, about 17 by 9 mm | MRCS |
| 2.2.1 | posterior tibial slope, 7 to 10 degrees | Medical student |
| 2.2.3 | anterior cruciate tibial footprint, about 17 by 11 mm | MRCS |
| 2.2.3 | posterior cruciate attachment, about 1 cm below the joint line | MRCS |

The list to work from is generated, not this table:

    python3 tools/figures.py --report --unchecked

It prints every figure with the tier it sits in and the whole sentence it
supports. Set `verification` and `source` in
`pipeline/config/figures/<page_id>.json` as each is confirmed. A figure you
correct or delete is marked `REMOVED` rather than deleted, so the record of what
was checked survives.

The gate refuses any figure that is not on that list, so it cannot fall behind
the pages.

**What is still absent, and why.** Posterolateral corner origin coordinates,
condylar radii, notch width index, tunnel geometry, and every threshold
separating normal from abnormal. Those are values this environment cannot state
with confidence, and a wrong one would be worse than the gap. They need a
source, not a better memory. Say the word and I will write the sentences with
the figures left blank for you to fill.

## What you are being asked to confirm

1. ~~The no measurements rule.~~ Reversed by the client. The figures are on the
   pages, all twelve unverified, and the register is the list to check them
   against.
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
