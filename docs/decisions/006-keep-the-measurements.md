# Decision 006: keep the measurements, and register every one

| Field | Value |
|---|---|
| Date | 8 October 2026 |
| Decided by | Client, on 8 October 2026 |
| Status | Applied |
| Reverses | Decision 005, part 1, for Section 2 |
| Leaves standing | Decision 003's figure rule for Section 0 |

## The instruction

> Keep the measurements. Don't worry, we will check all measurements. As long as
> they are based on current papers, keep them.

## The part of it that cannot be honoured

The condition cannot be met from the build environment. There is no source
access here and never has been: no PubMed, no Cochrane, no journal, no textbook.
No figure written here is based on a current paper, because no paper can be
retrieved to base it on.

What a figure written here is based on is standard teaching held in memory. That
is a real but weaker thing. It is usually right, it is occasionally out of date,
and it is never attributable.

The instruction stands and the figures are being written. What this decision
does is make the second half of the instruction, "we will check all
measurements", mechanically possible.

## The ruling

### 1. Section 2 may carry figures

Decision 005's blanket ban is lifted for Section 2. Measurements, angles,
dimensions and normal ranges may appear.

### 2. Every figure is registered

Each page with a figure has a register at `pipeline/config/figures/<page_id>.json`
holding one entry per figure:

| Field | What it holds |
|---|---|
| `as_written` | the figure exactly as it appears, "17 mm" |
| `tier` | which tier block it sits in |
| `section` | which body section |
| `claim` | the whole sentence it supports |
| `verification` | `UNVERIFIED_FROM_MEMORY`, `VERIFIED`, `CORRECTED` or `REMOVED` |
| `source` | empty, for the reviewer |

The register is generated from the page by `tools/figures.py --extract`, so
nothing is typed twice and the list cannot fall behind the prose. Extraction
never overwrites a `verification` or a `source` somebody has set. A figure that
is corrected or deleted is marked `REMOVED` and kept, because a record of what
was checked is worth more than a tidy file.

### 3. The gate refuses an unregistered figure

`FIG-002` fails any page whose brief allows figures and that carries one not in
its register, or whose register holds an entry with no claim or an unknown
verification state.

The rule does not judge a figure. It cannot: it has no sources either. What it
guarantees is that no figure reaches the site without appearing on the list
somebody is going to check.

`FIG-001`, the outright ban, survives for Section 0, where the figures are entry
requirements, test scores, fees and deadlines. Those change annually, they are
not in any paper, and no amount of checking fixes them. Decision 003 stands
there unchanged.

### 4. Every page says what its figures are worth

The references note on each Section 2 page now states that every measurement is
written from standard teaching rather than from a retrieved paper, that none has
been checked, and that all of them are registered. A reader at FRCS level is
entitled to know which of those two things they are reading.

## What is on the pages now

Twelve figures across six of the first fifteen pages. That is a deliberately
conservative set: the values that are standard teaching and that a reader would
notice the absence of.

| Page | Figures |
|---|---|
| 2.1.1 | distal femoral valgus, transepicondylar to posterior condylar rotation |
| 2.1.3 | femoral condylar cartilage thickness, medial compartment load share |
| 2.1.5 | trochlear sulcus angle, trochlear cartilage thickness |
| 2.1.6 | anterior cruciate femoral footprint, two dimensions |
| 2.2.1 | posterior tibial slope |
| 2.2.3 | anterior cruciate tibial footprint, two dimensions; posterior cruciate attachment depth below the joint line |

Figures that would normally appear and are still absent, because they are not
values this environment can state with confidence: posterolateral corner origin
coordinates, condylar radii, notch width index, tunnel geometry, and every
threshold that separates normal from abnormal. Those need a source, not a better
memory.

## Known limit of the register

A range written as "5 to 7 degrees" produces one register entry, for the bound
carrying the unit, because a bare small integer cannot be told apart from prose
numbering. The `claim` field holds the whole sentence, so a reviewer sees the
range. The register simply does not hold two rows for it.

## How to check the list

    python3 tools/figures.py --report --unchecked

Set `verification` and `source` in the register as each one is confirmed. Run
`--extract` again after any edit to the prose; it preserves what has been set.
