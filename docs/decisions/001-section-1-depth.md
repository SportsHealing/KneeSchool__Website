# Decision 001: how deep a Fundamentals page may go

| Field | Value |
|---|---|
| Date | 7 October 2026 |
| Decided by | Editor |
| Status | Adopted |
| Applies to | Every page whose brief excludes "Region level anatomy detail" |

## The question

The Master Publishing Architecture tells a Section 1 page to exclude "region
level anatomy detail, owned per structure by Section 2". It does not say where
that line falls.

Section 1 has one page called Ligaments covering all four. Section 2 has twelve
pages on the anterior cruciate ligament alone. Both could reasonably claim the
attachment points, the named blood supply and the layered structure.

## The ruling

**Split by tier.** The junior and patient tiers belong to Section 1 without
qualification. The medical student tier is where the overlap sits, and it is
trimmed to function and clinical meaning.

A Section 1 medical student tier **may** carry:

- what the structure is and roughly where it sits
- what it does
- why that matters clinically
- the name of a deeper page that owns the detail

It **may not** carry:

- precise bony attachment points, origins or insertions
- named individual arteries or nerve branches
- named sub-layers, bundles, fascicles or zones of a structure
- a dissection level account of what lies next to what

## Why this and not the alternatives

Keeping the named detail would have made Section 2 largely a repeat of Section 1
at seventy nine pages of cost. Removing it from every tier would have left the
medical student tier too thin to be worth opening.

Splitting by tier keeps Section 1 genuinely useful to its two larger audiences
and leaves Section 2 with a job to do.

## Practical effect

In practice this removes two section headings from a Section 1 page: Relations,
and Blood Supply and Innervation. Both are region level structural detail by
definition.

**Exemption.** Page 1.2.7 Nerves and Blood Supply keeps its Blood Supply and
Innervation section, because that is the page's subject. It stays in outline:
named territories rather than named branches, and no surgical anatomy, which the
architecture assigns to 2.10.6 and Section 7.

## Enforcement

Recorded in machine readable form at `pipeline/config/depth_rules.json` and
checked by STRUCT-001, so a future page cannot breach it quietly. The exemption
list lives in that file, and adding to it is a deliberate act with a reason
attached.

## What changed when it was applied

Five pages were trimmed: 1.2.1, 1.2.3, 1.2.4, 1.2.5 and 1.2.6 lost named
attachments and named vessels from the medical student tier. 1.2.7 was reduced
to outline. The junior and patient tiers were not touched on any page.
