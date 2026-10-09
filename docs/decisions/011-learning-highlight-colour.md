# Decision 011: the learning highlight colour

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Declined. The palette is unchanged |
| Source | Chapter 6 of the Master Operations Handbook |
| Supersedes | The same decision's first version, which wired a separate token |

## The question put

> The handbook asks for muted teal as a learning highlight. The stylesheet has
> no teal. Add it, or leave the palette as green, ivory and gold?

The first answer was to use the OmKneeHealth brand colours. The second answer
withdrew it:

> Sorry that's an old Omkneehealth website leave green, ivory and gold

## The ruling

Three colours. Deep forest green, warm ivory, brushed gold. No fourth.

The learning highlight keeps the gold it already used. Chapter 6's muted teal is
declined, not forgotten: it is recorded here so that nobody adds it later
thinking it was an oversight.

## What the handbook asked for, and where that leaves it

Chapter 6 gives five colour directions.

| Direction | State |
|---|---|
| Primary deep forest green | In the stylesheet as `--green-900` to `--green-500` |
| Warm ivory background | `--ivory` and `--ivory-2` |
| Restrained brushed gold accents | `--gold` and `--gold-dark` |
| Muted teal for learning highlights | Declined by this decision |
| Soft grey for structure | `--rule` and `--rule-dark` |

Four of five implemented, the fifth declined by the client. That is the whole of
chapter 6's colour direction answered.

## What was done and then undone

The first version of this decision added a `--learn` token so that one line
could set the learning highlight across the site, and left it holding the gold
value because the brand's hex codes were not available. The ruling makes that
indirection pointless: there is no second colour coming, so a token that always
equals `--gold` is a hop with nothing at the end of it. The key learning points
rules point at `--gold` again and the token is gone.

## On the source that was not reachable

The build environment could not reach `omkneehealth.com`, and the site it could
not reach turns out to have been the wrong one in any case. Both facts point the
same way: a brand colour is not something to infer. Had a plausible teal or a
guessed brand hex been written into the stylesheet, it would now be in 116 pages
and would have had to be found and removed.

## One governance point that no longer arises

The earlier version of this decision raised it: Section 9 of the Operations
Handbook allows no commercial content of any kind on any page carrying the
Junior tier, and all 38 Section 0 pages carry it. Putting a commercial partner's
livery on pages written for school age readers needed a ruling. With the palette
unchanged there is nothing to rule on.
