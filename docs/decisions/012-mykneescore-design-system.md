# Decision 012: adopt the MyKneeScore design system

| Field | Value |
|---|---|
| Date | 9 October 2026 |
| Decided by | Client, on 9 October 2026 |
| Status | Applied |
| Source | `SportsHealing/mykneescore` at commit `4ce92e0`, `mykneescore.com` |
| Supersedes | Decision 011, which left the palette as it was |

## The instruction

> Edit all of the UI and colors on the site to match the UI and design of
> mykneescore.com. Check the mykneescore repo on GitHub for this. Read and
> analyze the code and then execute the changes to make the UI the same.

## What was read

The repository is a static site with no build step, the same shape as this one.
The design system lives in two places that agree with each other: the `:root`
block repeated in `index.html` and `anatomy.html`, and
`advanced/assets/advanced.css`, whose first line says its tokens mirror the
homepage.

`tools/checks/house-style.py` was read as well. It encodes eight rules, each one
grown from a named incident rather than from a checklist, and one of them has
been adopted here along with the colours.

## The tokens, ported exactly

| Token | Value | What it replaced here |
|---|---|---|
| `--green-deep` | `#0e2b22` | `--green-900` `#0E2A21` |
| `--green-ink` | `#16382d` | `--green-800` `#123428` |
| `--green-soft` | `#23503f` | `--green-700` `#174336` |
| `--sage` | `#7c9284` | new; takes the role `--green-500` had |
| `--gold` | `#b58f47` | `--gold` `#C3A046` |
| `--gold-pale` | `#e6d5ac` | new; the gold that reads on dark green |
| `--ivory` | `#faf7ef` | `--ivory` `#F5F1E6` |
| `--paper` | `#f3efe3` | `--ivory-2` `#EAE3D2` |
| `--text` | `#22312a` | `--ink` `#16221D` |
| `--muted` | `#45564c` | `--ink-soft` `#41504A` |
| `--line` | `rgba(22,56,45,.16)` | `--rule` |
| `--warn` | `#8c4a2f` | new |

Their RGB triplet convention came with them, so an alpha variant of a colour
needs no second copy of its value.

## The typefaces

Cormorant Garamond for display, Hanken Grotesk for body. That is the largest
single change on the site: the body text was a serif, Source Serif 4, and is now
a sans.

One concern, stated and then set aside. MyKneeScore is a five minute
questionnaire; this site is long-form reading, and a serif is the conventional
choice for that. Their body settings carry it well enough: 1 to 1.125rem on a
1.65 line height is a comfortable measure, and the display face stays a serif, so
every heading still reads as it did. The instruction was to make the UI the same
and the UI is now the same.

## The components

| Element | What it is now |
|---|---|
| Header | Sticky, deep green, pale gold hairline, wordmark in the body face with `School` in pale gold |
| Nav | Ivory links, gold underline on hover, ending in a filled pale gold pill |
| Buttons | Pills. Gold filled, or ghost with a translucent ivory border |
| Hero | Deep green under a radial gold wash at 85% -10%, their exact gradient |
| Cards | White, hairline border, 3px gold top edge or 3px sage left edge, 12 to 16px radius, lift and shadow on hover |
| Lists | Gold dot bullets in place of rules and dashes |
| Labels | 0.78rem, 600 weight, 0.18em tracking, uppercase |
| Depth dial | Pill tabs; the chosen one fills pale gold on deep green, their selected-option style |
| Tables | Uppercase hairline headers, hairline row rules |
| Footer | Deep green, pale gold links |
| Focus | 3px gold outline, 3px offset, theirs exactly |

## The one rule adopted with the colours

Their check names this their highest value CSS rule:

> no colour literals outside `:root`, incident: 69 literals found 2026-10-03

`tools/check_site.py` now fails the build on any colour literal in the
stylesheet outside its `:root` block, or in any page. One exception is allowed
and is named in the code: the `theme-color` meta tag, because an HTML attribute
cannot read a custom property. That value now lives in
`pipeline/config/site.json` and `tools/apply_chrome.py` refreshes it on every
page, so it cannot drift either.

## One deliberate difference

Their eyebrow labels are `--gold` on `--ivory`, which is about 3.2:1 and below
the 4.5:1 that WCAG AA asks of text that size. This site carries the same labels
on pages written for school age readers, so small gold text on a light
background uses `--gold-ink` `#8a6a2f` instead, which passes. Everything else,
including every use of gold on deep green, is their value.

That is the only colour on the site that is not theirs, and it is here because
of who reads this site rather than because of a preference.

## A defect the port exposed

The status note on every page was styled for a dark background: ivory text on a
translucent ivory panel. Every page but one carries it inside a dark hero or a
dark band, so it read correctly. The Anatomy Academy index was the exception,
and its note had been near invisible ivory on ivory since the page was built.
Nothing marked it, because the light variant existed in the stylesheet and no
page used it.

The default is now the light variant and a dark context switches it, which makes
the common case the safe one rather than the other way round.

## What was checked

- 122 pages, 0 site check failures, 0 publication QA findings
- No horizontal overflow and no page errors at 375px or 1440px on the homepage,
  a level page, an article, the anatomy index and the standards page
- Computed styles confirm the body face, the display face, the ivory background
  and the deep green header on every page sampled
- The status note reads correctly in both contexts, confirmed from computed
  styles on an article page, a level page and a library index
- 156 tests green, including seven new ones that hold the token values, the two
  typefaces, and the colour literal rule, the last proved by planting a literal
  in a real page and requiring the real checker to fail
