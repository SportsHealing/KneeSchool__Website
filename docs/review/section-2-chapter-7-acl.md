# Consultant review pack: Section 2, chapter 2.7, the anterior cruciate ligament

| Field | Value |
|---|---|
| Section | 2 Anatomy Academy |
| Chapter | 2.7 ACL, all 12 pages |
| Pages | 12, taking Section 2 to 48 of 79 |
| Tiers | Medical student, MRCS and FRCS on all 12; fellowship on 2.7.6, 2.7.7 and 2.7.12 |
| Style gate | All 12 pass. Zero failures |
| Evidence verification | **Did not run on any page** |
| Measurements | 8 new, all unverified. 32 across Section 2 |
| Clinical positions | 24 new, all unsigned. 100 across the site |
| Words | 17,459 |

## Why this chapter needs the closest reading

It is the chapter a trainee will actually use. Twelve pages on the ligament that
generates more surgery, more argument and more examination questions than
anything else in the knee, and every page is unverified.

Three pages carry the content a reconstruction is planned from:

- **2.7.6 Femoral Footprint**, including the claim that nothing native attaches
  in front of the lateral intercondylar ridge, so a graft placed there is non
  anatomical by definition.
- **2.7.7 Tibial Footprint**, including the instruction to use the posterior part
  of the footprint when in doubt, because anterior error is harder to live with.
- **2.7.12 Surgical Anatomy**, including the claim that scuffing the medial
  femoral condyle through a low medial portal is the commonest iatrogenic injury
  in the operation.

If any of those three is wrong, it is wrong in a place that changes what somebody
does with a drill.

## What the chapter is organised around

One anatomical fact: **one artery, arriving by one route.** The middle genicular
artery reaches the ligament through the posterior capsule and the synovial
sheath, and it supplies both cruciates.

2.7.4 states the consequence plainly: that supply maintains the ligament and
cannot heal a complete mid substance rupture. Everything in Section 7 follows
from it. The pages also use it to frame the current repair interest as an
argument about which subgroup has favourable vascular anatomy, not as a claim
that the anatomy has changed.

A second organising claim, on 2.7.5 and 2.7.10: the ligament is a sensor as well
as a restraint, devascularisation and denervation are the same event, and a
reconstructed knee is sensorily altered probably permanently. 2.7.10 goes further
and says the protective hamstring reflex is the most cited and least settled
mechanism, with a latency that looks too long to prevent injury, and that
feedforward control is the more plausible route. **That is a position worth
checking: it contradicts how the reflex is often taught.**

## Three places I deliberately refused to go further

1. **Bundle function through range.** The architecture excludes it from 2.7.8 and
   2.7.9 by name, so both pages describe the bundles as anatomy and hand the
   behaviour to 3.7.5 and 3.7.6. 2.7.8 says the two cord model predicts that
   reproducing both bundles restores native behaviour and that the evidence has
   not borne that out cleanly. Check that framing.
2. **Tunnel drilling technique.** Excluded from 2.7.6 and 2.7.7 by name. The
   pages say where the footprint is and what bounds a trajectory, and stop.
3. **Material properties.** Tensile strength, modulus and stiffness are owned by
   3.7 and appear nowhere, because no value could be verified.

## The eight new measurements

| Page | Figure |
|---|---|
| 2.7.1 | ligament length 32 to 38 mm; width about 10 mm; mid substance area about 40 square millimetres |
| 2.7.2 | first appearance at about the seventh to eighth week of gestation |
| 2.7.5 | neural elements about 1 per cent of cross sectional area |
| 2.7.6 | femoral footprint about 17 by 9 mm |
| 2.7.7 | tibial footprint about 17 by 11 mm |

The architecture asked 2.7.1 for dimensions explicitly, which is why that page
carries three.

    python3 tools/figures.py --report --unchecked

## The positions list grew faster than the page count

Chapter 2.7 added 12 pages and 24 clinical positions, taking the site total from
76 to 100. That is the pattern worth noting: **a surgical chapter generates
positions faster than it generates pages.** Chapters 2.8 to 2.12 will do the
same.

    python3 tools/positions.py --report --unsigned

## What has not been checked

Nothing. Claims are listed per page in
`pipeline/runs/<page_id>/draft_v1.handoff.json`.

## Where the pages are

`anatomy/acl-*.html`, listed on `anatomy/index.html`, which now shows 48 of 79
pages live.
