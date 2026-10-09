# Decision 011: the learning highlight colour

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Wired, value pending |
| Source | Chapter 6 of the Master Operations Handbook |

## The question put

> The handbook asks for muted teal as a learning highlight. The stylesheet has
> no teal. Add it, or leave the palette as green, ivory and gold?

Answered: use the OmKneeHealth brand colours.

## What the handbook specifies

Chapter 6 gives five colour directions: deep forest green, warm ivory
background, restrained brushed gold accents, muted teal for learning highlights,
soft grey for structure. Four were already in the stylesheet. Teal was the
missing one, and the ruling replaces it with the partner brand's colour rather
than adding teal.

## What has been done

The learning highlight is now its own token rather than borrowed gold.

```css
--learn:#C3A046;
--learn-dark:#8F701F;
```

Everything that marks a learning highlight points at it: the key learning points
rule on every article page, and the same rule inside each depth dial panel.
Changing those two lines changes every learning highlight on the site.

## What has not been done

The two lines still hold the gold values. The OmKneeHealth brand hex codes have
not been supplied, and this build environment cannot reach the brand's site to
read them: the network policy refuses the host, so `omkneehealth.com` does not
resolve from here.

A brand colour cannot be guessed. A near miss is worse than the current gold,
because it reads as a mistake rather than as a choice. So the token is in place,
the value is honest about being a placeholder, and the comment in the stylesheet
says so at the point where someone would otherwise assume the gold was the
brand.

## What is needed

The hex codes. Two values if the brand has a primary and a darker variant, one
if it has a single colour.

## One governance point to settle with them

Section 9 of the Operations Handbook is binding: no commercial content of any
kind in any page carrying the Junior tier, no product placement, no supplements,
no clinical service promotion. All 38 Section 0 pages carry that tier.

A colour is not content and no reasonable reading makes a border colour product
placement. But using a commercial partner's brand colour as the site's learning
highlight does put that brand's livery on pages written for school age readers.
The safer form is to apply the brand colour everywhere except pages carrying the
Junior tier, which the stylesheet can do in one rule because `--learn` is a
token and Junior pages are identifiable. That is a question, not an assumption:
nothing has been scoped away.
