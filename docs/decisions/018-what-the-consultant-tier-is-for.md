# Decision 018: what the consultant tier is for

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Client, on 10 October 2026 |
| Status | Applied |
| Changes | `tier_intent` added to `article_template.json`, consultant blocks on 3.11.9 and 3.1.7 rewritten, 6.1.1 rewritten, POSITION_VERBS extended, 7 tests |

## The instruction

> The consultant tier should really be about decision-making based on a balance
> argument, not necessarily having a strong view one way or another

Given after reading 3.11.9 Contemporary Controversies, the first page in Section 3
to carry a consultant tier.

## What was wrong with the page

3.11.9 set out two positions on lateral augmentation and called both defensible.
That reads as balance and is not. It describes two camps and leaves the reader to
join one, which is a survey of opinion with a decision bolted on the end.

The handbook's Curriculum Matrix gives the consultant tier "Innovation, debates
and expert judgement". The page read "expert judgement" as licence to arbitrate
between camps. The client's reading is narrower and more useful: the consultant
tier is about how a decision gets made when the evidence does not make it.

## The rule

A consultant block must do five things. They are now in
`pipeline/config/article_template.json` under `tier_intent.consultant` so the
generator reads them rather than remembering them.

1. Name the decision. It is rarely the same as the controversy. On 3.11.9 the
   controversy is whether the anterolateral ligament exists; the decision is how
   much extra surgery to add to a reconstruction.
2. Set out what sits on each side, benefit and cost, in the reader's terms.
3. Say what moves the weight, and separate the variables that look decisive from
   the ones that are.
4. Say what the measurements can and cannot settle, including which side of the
   balance is measured worse. On 3.11.9 that is the harm side.
5. Leave the reader able to decide, and able to say why a colleague decided
   otherwise.

Three things are forbidden. Declaring a question settled when it is not.
Advocating a position the evidence does not reach. A survey of disputes with no
decision attached, which is the fellowship tier's job and duplicating it wastes a
tier.

One thing stays permitted. Naming a move as indefensible, where the objection
does not bear on the decision at all. 3.11.9 still says that citing the
anatomical dispute as a reason not to augment weighs nothing, because the
mechanical case never rested on it. That is weighing, not advocacy.

## What the rewrite exposed

The style gate found almost none of the new consultant recommendations. POS-001
detects clinical direction from a list of imperative openers, and the list was
built from directive prose: Assess, Avoid, Prefer, Treat. A balance argument
opens differently, with Weigh, Stage, Correct, Offer, Confirm.

A dry run across every professional page found 163 clinical directions on 101
pages that had never reached the position register. They include "Stage the
corner before any cruciate reconstruction in a knee with lateral findings" and
"Correct varus alignment where it would load a corner reconstruction". Both are
clinical direction, neither was listed, and both have been live for days.

The gap predates this decision. The consultant rewrite only walked into it. The
verb list has been extended, the register re-extracted, and the unsigned total
rises accordingly. That rise is a correction to the count, not new exposure: the
advice was always on the page, it was simply not on the list anybody is being
asked to sign.

## Pages changed

| Page | Was | Now |
|---|---|---|
| 3.11.9 | Two defensible positions on augmentation | The decision is how much to add; benefit, cost, and what moves the weight |
| 3.1.7 | A department should require method and era alongside every figure | What dating every figure buys, what it costs, and when the cost is worth paying |
| 6.1.1 | Four controversies surveyed | The same four, each with the decision it forces and what sits on each side |

Those were the only three pages on the site carrying a consultant tier.

## What is not settled

Whether the fellowship tier needs the same treatment. It currently carries
controversies, which is its job under the matrix, and on several pages it reads
close to the old consultant style. Left as it is until a fellowship block is
read and judged rather than changed on the strength of this one.
