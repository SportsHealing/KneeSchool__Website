# Decision 013: the peroneal nerve page carries a fellowship tier

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Applied |
| Affects | Page 2.10.6, Common Peroneal Nerve |
| Builds on | Decision 005 part 3, the Section 2 tier pattern |

## The instruction

> Continue and do a special section on common peroneal nerve at risk from
> lateral surgery.

## What the architecture gives the page

Page 2.10.6 is listed with three tiers, medical student to FRCS, and its scope
line reads "Course and surgical proximity of the nerve". The architecture already
frames the page as a surgical proximity page, so the instruction asks for more of
what the page was for rather than for something new.

Two other pages in the same chapter carry a fellowship tier, 2.10.4 and 2.10.7,
and fellowship in Section 2 is approach anatomy everywhere it appears. Surgical
proximity at fellowship depth is approach anatomy. Without the tier, the one page
on the structure most often injured by lateral knee surgery stops at FRCS while
the pages about the ligaments beside it do not.

## What was added

**A tier.** `pipeline/config/tier_overrides.json` is new and holds one entry. The
mechanism mirrors the word count overrides from decision 005: a declared list
rather than a heuristic, each entry carrying a reason about the page's subject
and a decision behind it. Tiers are only ever added, never removed, so the
architecture's list is a floor. `tools/architecture.py` applies it when a brief
is generated, and reorders to the template's tier sequence so a brief cannot end
up with its tiers out of order.

**A word band.** The fellowship tier here is a single Clinical Relevance section
of ten paragraphs, which is the deliverable rather than padding around one. The
handbook's 800 to 1800 band is written for an anatomy page with four or five body
sections per tier; this page has four tiers and an eleventh section on top. A
band of 800 to 2400 is declared for it in `word_count_overrides.json`, and the
page came in at 2,227 words without prose added to fill it.

## What the section covers

Ten paragraphs, all of them approach anatomy:

1. Which operations put the nerve in the field, and the common thread: a fixation
   or passage within two centimetres of a nerve that cannot move.
2. Why it is injured more than its size suggests. It lies on bone at the neck
   with no muscle cover, it is tethered in a fibro-osseous tunnel so it cannot
   slide away from a force, and its blood supply is segmental along its length.
3. Identify rather than avoid, by following the posteromedial border of the
   biceps femoris tendon, and what to do when that landmark has been avulsed.
4. The three injuries. Division is obvious and least common; compression is
   recoverable in proportion to duration; traction is the commonest and the
   quietest, because nothing happens at the time.
5. Position as a tool. Flexion shortens the nerve's path and is available at any
   moment without changing the plan.
6. Mobilisation costs supply, so the shortest mobilisation that protects it is
   the right one, and the trade is explicit.
7. When releasing the tunnel becomes an anatomical question.
8. The recurrent articular branch, usually sacrificed and rarely mentioned.
9. Recording the examination as three findings rather than one.

## The line this page does not cross

The architecture owns nerve injury at 6.26 and its management at 7.49, and
imaging at 5.10.5. The page names all three and hands those subjects on in its
first paragraph, so the section is approach anatomy rather than a chapter on
nerve injury written in the wrong place.

## A defect found while applying this

The brief generator preserves hand set values when it regenerates a brief, and
`target_word_count` was among them. A band declared in the overrides file is
configuration rather than a hand set value, so the first regeneration merged the
old 1800 back over the new 2400 and the gate kept failing a page that was within
its declared band.

`build_brief` now drops `target_word_count` from the preserved set whenever a
band override exists for the page. An override added after a brief exists has to
reach that brief, and it did not.
