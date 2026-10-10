# Decision 020: controversies skip the fellowship tier

| Field | Value |
|---|---|
| Date | 10 October 2026 |
| Decided by | Client, on 10 October 2026 |
| Status | Applied |
| Changes | `section_tier_rules` added to `article_template.json`, SECTION_TIER_FLOOR demoted to a fallback, STRUCT-001 now reads an allow list, 6.1.1 edited, 5 tests |

## The instruction

> Cut fellowship

Answering this, asked after 6.1.1 was read:

> Three tiers carrying controversies on one page: cut FRCS, cut fellowship, or
> leave the overlap because each pitches it differently?

## Why fellowship was the right one to cut

The three tiers were not pitching the same material three ways. They were
repeating it.

FRCS framed the controversy as evidence appraisal, which is what the examination
asks for. The consultant block frames it as a decision, which is decision 018's
job. Fellowship sat between them with a single paragraph that said slope
correction has a place in the revision knee and the threshold is not agreed,
which the consultant block already weighs and the FRCS block already appraises.

Fellowship is advanced practice under the handbook's matrix. Its controversies
belong inside its management and complications sections, where the operation is,
rather than in a survey that repeats the tier below and pre-empts the tier above.

## Nothing was deleted

The cut paragraph carried one thing the rest of the page did not: the name of the
operation. That moved rather than went.

| Was | Now |
|---|---|
| Fellowship controversies: slope correction has a place, threshold not agreed | Gone |
| | Fellowship complications: the operation that reduces slope is an anterior closing wedge osteotomy, and whether it is justified is weighed in the consultant block |
| | Fellowship key learning points: the named operation |
| Consultant: correction adds an osteotomy | Consultant: an anterior closing wedge osteotomy adds its own recovery and complications |

The page went from 2,150 words to 2,167. Cutting a section made it slightly
longer, which is what happens when a survey paragraph is replaced by the fact it
was circling.

## The rule, and a gate that was already half wrong

The handbook restricts Controversies and Evidence to FRCS and above. That was
enforced by `SECTION_TIER_FLOOR`, a dict of section to floor tier hardcoded in
`linter.py`.

A floor cannot express "FRCS and consultant but not fellowship". So the limits
now live in `article_template.json` under `section_tier_rules`, which takes
either an explicit `tiers` allow list or a `from` floor, and
`SECTION_TIER_FLOOR` is demoted to a fallback for the case where the template
loses the block.

Two things follow. An editorial decision about which tier carries which section
is now a change to one configuration file rather than to the linter. And the
restriction is checked rather than described: the condition page type's
`body_sections_rule` said `controversies_and_evidence frcs_and_above_only` in
prose, and nothing read that string.

The gate was run before the page was edited, to confirm it fails the thing it is
supposed to fail:

    STRUCT-001: tier 'fellowship' carries 'controversies_and_evidence',
    which is restricted to frcs and consultant

## Scope

6.1.1 is the only condition page on the site, so this changed one page. It will
apply to every condition page in Section 6, which is 100 or so pages not yet
written, and that is the point of putting it in the template now.
