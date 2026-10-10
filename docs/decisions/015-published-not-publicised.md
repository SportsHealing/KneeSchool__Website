# Decision 015: published, not publicised

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Client, on 10 October 2026 |
| Status | Applied |
| Changes | Build status items EV-2 and EV-15 |

## The instruction

> Don't worry, we have consultants lined up. We're not going to publicise the
> website until it's verified but it can be published.

Two things, and both change the record.

## Consultants exist now

EV-2 has said since the build began that consultant review has no return path.
That was true of the mechanism and it is no longer true of the people. The
reviewers are lined up; what is still missing is the route by which a decision
comes back into the pipeline, which is a smaller problem than having nobody to
ask.

The item is reworded rather than closed. 382 clinical recommendations and 171
measurements are waiting, across 74 and 53 pages, and nothing has been signed
yet.

## Published and not publicised are different states, and the site did not know it

The site can go live. It will not be promoted until it is verified.

A live site that search engines index is publicised, whatever anyone intended.
A crawler finds it, indexes it, and a patient searching for knee pain lands on a
page that says at the top that it has not been evidence verified or consultant
reviewed. The intention was not to show it to them yet.

Worse, that step is not cleanly reversible. A page can stay in a search index
and in caches after it is removed from the site, so the decision to be
discoverable is much easier to make than to unmake.

So the site now carries the distinction rather than relying on nobody linking
to it.

## What was done

One value in `pipeline/config/site.json`:

```json
"discoverable": false
```

From that, two things:

- every page carries `<meta name="robots" content="noindex, nofollow">`
- `robots.txt` disallows every crawler, with a comment saying why

`tools/apply_chrome.py` applies both, as it already does for the theme colour
and the canonical link, so neither can drift page by page.

**Flipping it is one line and one command.** Set `discoverable` to true, run
`python3 tools/apply_chrome.py`, and all 155 pages and `robots.txt` change
together. Nothing else has to be remembered.

## The failure that was worth guarding

The dangerous state is not either posture. It is the half flip: a config that
says discoverable and pages that still say noindex, or the reverse. A site where
some pages are indexable and some are not has no posture, and the indexable half
is the half that publicises it.

`PUB-010` in the publication gate refuses that. Flipping the switch without
re-applying the chrome fails all 155 pages, which is what a test proves by doing
exactly that.

## What has not changed

Every page still carries its pipeline status note at the top: editorial draft,
evidence verification did not run, not consultant reviewed, not for clinical
use. Those stay until the thing they describe changes, and they are not affected
by this decision.

The footer's educational and not a substitute statement stays too, on every
page, under decision 010's rule.

## Questions

1. Confirm the reading: published means the pages may be live at
   kneeschool.com, and not publicised means not indexed, not linked from
   elsewhere and not announced. If live was meant to wait as well, say so and
   nothing is lost.
2. When verification is done, who flips the switch? It is one line, and it is
   the kind of line worth having a named owner for.
