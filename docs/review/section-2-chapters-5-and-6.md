# Consultant review pack: Section 2, chapters 2.5 and 2.6

| Field | Value |
|---|---|
| Section | 2 Anatomy Academy |
| Chapters | 2.5 Medial Meniscus (7 pages), 2.6 Lateral Meniscus (6 pages) |
| Pages | 13, taking Section 2 to 36 of 79 |
| Page type | anatomy, on every page |
| Tiers | Medical student, MRCS and FRCS on all 13; fellowship on 2.5.6, 2.5.7, 2.6.2, 2.6.4 and 2.6.6 |
| Style gate | All 13 pass. Zero failures, zero warnings |
| Evidence verification | **Did not run on any page** |
| Measurements | 5 new, all unverified. 24 across Section 2 |
| Words | 17,829 in this batch |

## The claim these two chapters are built on

Every mechanical statement in both chapters rests on one idea: **the meniscus is
a tensioned ring, not a cushion.** Compression of the wedge is converted into
circumferential hoop tension, and the horns transmit that tension into bone.

Everything else follows. A radial tear matters more than a longitudinal one
because it cuts the ring. A root tear behaves like a total meniscectomy because
it unanchors it. Extrusion is a functional finding because a ring that has
stopped carrying tension has stopped working. Repair restores a mechanism rather
than tissue continuity.

If that framing is wrong, or is overstated anywhere, it is worth saying so
before 43 more pages are written on top of it.

## The asymmetry that runs through both chapters

| | Medial | Lateral |
|---|---|---|
| Shape | Open C, broader behind | Nearly closed ring, even width |
| Plateau beneath | Concave | Convex |
| Tethering | Deep collateral and short coronary ligaments | Longer coronary ligaments, no capsule at the hiatus |
| Extra attachments | None | Popliteomeniscal fascicles, meniscofemoral ligaments |
| Behaviour | Loaded in place | Translates with the condyle |
| Tear frequency | Higher | Lower |
| Cost of losing it | Lower | Higher |

The last two rows are the clinically uncomfortable pair, and the pages state the
consequence plainly: the meniscus that tears less often is the one that matters
more, because the lateral compartment has no concavity of its own.

## What you are being asked to confirm

1. **The hoop framing.** Above.
2. **The lateral preservation argument.** 2.6.1 and 2.6.6 both say the threshold
   for difficult preservation surgery should be lower laterally than medially,
   on anatomical rather than evidential grounds. That is a recommendation, and
   it should carry your name or not appear.
3. **Accuracy, on thirteen pages, by someone who operates on menisci.**

## Five pages to read first

**2.5.7 and 2.6.4 Root Attachments.** The two highest consequence pages. Both
state that the anterior root footprint overlaps the anterior cruciate's, and
that a tibial tunnel of useful diameter will take some root fibres. 2.6.4 goes
further: it says an unrecognised lateral posterior root tear is the commonest
reason a technically sound cruciate reconstruction has residual rotational
laxity, and that root inspection should be routine at every reconstruction.
Check both claims.

**2.6.2 Popliteomeniscal Fascicles.** The page on a lesion that is invisible on
imaging. It says an arthroscopy that did not probe lateral meniscal mobility has
not excluded a hypermobile meniscus. Check whether that is too strong.

**2.5.6 Surgical Anatomy.** The fellowship tier argues that releasing the medial
collateral to gain access is a small reversible injury that can save a meniscus,
and that forcing a tight compartment is not an option. Check the framing.

**2.5.3 Vascular Supply.** The page the whole repair decision rests on. It
states that a red zone failure is mechanical and a white zone failure is
biological, and that stability does not substitute for vascularity.

## The five new measurements

| Page | Figure |
|---|---|
| 2.5.1 | medial meniscus covers about 60 per cent of its plateau |
| 2.5.1, 2.5.3 | vascular penetration, peripheral 10 to 30 per cent |
| 2.5.2 | water content about 70 per cent of wet weight |
| 2.6.1 | lateral meniscus covers about 75 per cent of its plateau |

Load share, contact pressure change after meniscectomy, and discoid prevalence
are written in words rather than figures on these pages, because the values I
hold are too uncertain to put a number on. They are the figures most worth
adding once somebody has the sources.

    python3 tools/figures.py --report --unchecked

## What has not been checked

Nothing. Claims are listed per page in
`pipeline/runs/<page_id>/draft_v1.handoff.json`.

## Where the pages are

`anatomy/medial-meniscus-*.html` and `anatomy/lateral-meniscus-*.html`, listed
on `anatomy/index.html`, which now shows 36 of 79 pages live.
