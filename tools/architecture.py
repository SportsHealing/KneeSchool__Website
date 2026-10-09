#!/usr/bin/env python3
"""Read the Master Publishing Architecture and produce what the pipeline needs.

    python3 tools/architecture.py brief 1.2.3 --out pipeline/config/briefs/1.2.3.json
    python3 tools/architecture.py seed  --out pipeline/config/architecture/tracker_seed.json
    python3 tools/architecture.py show  1.2.3

A brief is not written by hand. The architecture owns which tiers a page serves,
what it must not cover, and which pages own that material instead. That last list
is the whole mechanism that stops the same fact being written across three
thousand pages, so it is copied from the architecture rather than retyped.
"""

import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH_DIR = os.path.join(ROOT, "pipeline", "config", "architecture")
TEMPLATE = os.path.join(ROOT, "pipeline", "config", "article_template.json")
TYPE_MAP = os.path.join(ROOT, "pipeline", "config", "page_type_map.json")


def load_pages():
    pages = []
    for name in sorted(os.listdir(ARCH_DIR)):
        if name.startswith("pages_") and name.endswith(".json"):
            with open(os.path.join(ARCH_DIR, name)) as fh:
                pages.extend(json.load(fh))
    return pages


def load(path):
    with open(path) as fh:
        return json.load(fh)


def page_sort_key(page_id):
    """1.2.10 sorts after 1.2.9, not between 1.2.1 and 1.2.2."""
    out = []
    for part in str(page_id).split("."):
        out.append((0, int(part)) if part.isdigit() else (1, 0, part))
    return out


# The handbook's word ranges assume a page carrying several tiers. A page with
# one tier is not a short version of that page; it is a different object. A
# junior only page padded to eight hundred words stops reading like a junior
# page, which defeats the reading age the same handbook sets. See decision 002.
TIER_WORD_BANDS = {1: (350, 900), 2: (600, 1300)}

# A page carrying the patient tier must also carry an FAQ block of three to five
# questions with answers, which the handbook requires and the drafter cannot
# shorten away. That is structural overhead, not prose, and on a one tier page it
# is a quarter of the whole band. The allowance lets it sit on top rather than
# pushing the body text out. See decision 002, FAQ allowance.
FAQ_ALLOWANCE = 250


OVERRIDES = os.path.join(ROOT, "pipeline", "config", "word_count_overrides.json")


# Section 0 carries no entry requirement, test score, fee or deadline. Those
# change every year, none could be verified, and they are not in any paper, so
# nobody can check them later either. Decision 003 forbids them and FIG-001
# enforces it.
#
# Section 2 is the opposite case. Its figures are measurements, they are in the
# literature, and the client has said to keep them and check them. Decision 006
# reverses decision 005's blanket ban, and FIG-002 requires every figure to be
# registered so the checking list is generated rather than compiled by hand.
NO_FIGURE_SECTIONS = {"0": "decision 003"}


def figures_allowed(page):
    return str(page["section"]["id"]) not in NO_FIGURE_SECTIONS


def band_override(page_id):
    """Decision 005: a declared band for a page the page type band does not fit.

    Returned in preference to the tier scaling, because the reason it exists is
    the page's subject rather than how many tiers it carries.
    """
    if not os.path.exists(OVERRIDES):
        return None
    cfg = load(OVERRIDES)
    entry = (cfg.get("pages") or {}).get(str(page_id))
    if not entry:
        return None
    band = (cfg.get("bands") or {}).get(entry.get("band"))
    return dict(band) if band else None


def scale_for_tiers(defaults, tiers):
    band = TIER_WORD_BANDS.get(len(tiers))
    if not band or not defaults:
        return defaults
    lo, hi = band
    if "patient" in tiers:
        hi += FAQ_ALLOWANCE
    return {"min": lo, "max": hi}


def build_brief(page, merge=None):
    tpl = load(TEMPLATE)
    type_map = load(TYPE_MAP)["page_types"]
    template_name = (type_map.get(page["page_type"]) or {}).get("template")
    defaults = (tpl["page_types"].get(template_name) or {}).get("word_count") or {}
    defaults = band_override(page["page_id"]) \
        or scale_for_tiers(defaults, page["tiers_required"])

    brief = collections.OrderedDict()
    brief["brief_version"] = "1.1"
    brief["page_id"] = page["page_id"]
    brief["title"] = page["title"]
    brief["section"] = page["section"]
    brief["chapter"] = page["chapter"]
    brief["page_type"] = page["page_type"]
    brief["article_template"] = template_name
    brief["generated_from"] = "Master Publishing Architecture, pages_0_to_3.json"
    brief["tiers_required"] = page["tiers_required"]
    brief["scope"] = collections.OrderedDict([
        ("must_cover", [page["scope"]]),
        ("must_not_cover", page["must_not_cover"]),
        ("sibling_pages", page["siblings"]),
        ("deeper_spiral_pages", page["deeper_pages"]),
    ])
    brief["curriculum_tags"] = []
    brief["source_requirements"] = collections.OrderedDict([
        ("kb_topic_filter", page["title"].lower()),
        ("minimum", {"textbook_or_review": 1, "peer_reviewed_for_clinical_claims": True}),
        ("preferred_recency_years", 10),
        ("guidelines_expected", []),
    ])
    klp = tpl["key_learning_points"]
    faq = tpl["faqs"]
    brief["output_requirements"] = collections.OrderedDict([
        ("language", "en-GB"),
        ("format", "markdown"),
        ("key_learning_points_per_tier", {"min": klp["min_bullets"], "max": klp["max_bullets"]}),
        ("faqs_patient_level", {"min": faq["min"], "max": faq["max"]}),
        ("target_word_count", dict(defaults)),
        ("internal_link_placeholders", True),
    ])
    junior = "junior" in page["tiers_required"]
    brief["governance"] = collections.OrderedDict([
        ("commercial_content_allowed", False),
        ("clinical_advice_allowed", False),
        ("junior_tier_present", junior),
        ("figures_allowed", figures_allowed(page)),
    ])
    brief["pipeline"] = collections.OrderedDict([
        ("priority", page["priority"]),
        ("requested_by", "architecture"),
        ("regen_count", 0),
        ("consultant_assigned", None),
    ])

    prior = None
    if merge and os.path.exists(merge):
        try:
            prior = load(merge)
        except ValueError:
            # An unreadable or empty merge target is not a reason to refuse to
            # generate the brief. Fall back to the architecture's values.
            prior = None
    if prior:
        # Hand set values that the architecture does not own are preserved.
        for path in (("output_requirements", "target_word_count"),
                     ("curriculum_tags",), ("tier_notes",),
                     ("source_requirements", "kb_topic_filter")):
            node, target = prior, brief
            ok = True
            for key in path[:-1]:
                node = node.get(key) if isinstance(node, dict) else None
                target = target.get(key)
                if node is None or target is None:
                    ok = False
                    break
            if ok and isinstance(node, dict) and path[-1] in node:
                target[path[-1]] = node[path[-1]]
            elif ok and path[-1] in prior and len(path) == 1:
                brief[path[-1]] = prior[path[-1]]
    return brief


def cmd_brief(args, pages):
    by_id = dict((p["page_id"], p) for p in pages)
    page = by_id.get(args.page_id)
    if not page:
        sys.exit("page %s is not in the architecture" % args.page_id)
    brief = build_brief(page, merge=args.merge or args.out)
    text = json.dumps(brief, indent=2) + "\n"
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
        print("%s written for page %s (%s, %s)"
              % (args.out, page["page_id"], page["page_type"], brief["article_template"]))
    else:
        print(text)


# Appendix A of the Master Operations Handbook sets the tracker columns. Category
# is one of them, and the architecture's own section names supply it. Sections 2
# to 8 match the handbook's chapter 5 taxonomy exactly. Sections 9 to 15 are not
# in that taxonomy but are named as top level areas in its chapter 3 sitemap.
# Sections 0 and 1 are in neither document, which is the Section 0 gap recorded
# in finding 001 showing up again. See finding 002.
TAXONOMY_CATEGORY = {
    "0": "Junior Academy",
    "1": "Foundations",
    "2": "Anatomy",
    "3": "Biomechanics",
    "4": "Clinical Examination",
    "5": "Imaging",
    "6": "Conditions",
    "7": "Surgery",
    "8": "Rehabilitation",
    "9": "Women's Knee Health",
    "10": "Children's Knee Health",
    "11": "Performance",
    "12": "Research",
    "13": "Case Library",
    "14": "Question Bank",
    "15": "Video Library",
}


def cmd_seed(args, pages):
    """Tracker seed, in the queue order the architecture specifies: high pages in
    section order, then medium, then low; lower page id first within a band."""
    bands = {"high": 0, "medium": 1, "low": 2}
    ordered = sorted(pages, key=lambda p: (bands.get(p["priority"], 9),
                                           page_sort_key(p["page_id"])))
    items = []
    for n, p in enumerate(ordered, 1):
        items.append(collections.OrderedDict([
            ("page_id", p["page_id"]),
            ("title", p["title"]),
            ("section", p["section"]["id"]),
            ("chapter", p["chapter"]["id"]),
            ("page_type", p["page_type"]),
            ("category", TAXONOMY_CATEGORY.get(str(p["section"]["id"]), "")),
            ("tiers_required", p["tiers_required"]),
            ("priority", p["priority"]),
            ("queue_position", n),
            ("source_status", "not_started"),
            ("draft_status", "not_started"),
            ("qa_status", "assistant_checked"),
            ("publication_status", "ready"),
            ("seo_complete", False),
            ("refresh_date", None),
            ("curriculum_tags", []),
            ("regen_count", 0),
            ("red_flag_count", 0),
        ]))
    text = json.dumps(items, indent=2) + "\n"
    with open(args.out, "w") as fh:
        fh.write(text)
    counts = collections.Counter(p["priority"] for p in pages)
    print("%s written: %d pages (high %d, medium %d, low %d)"
          % (args.out, len(items), counts["high"], counts["medium"], counts["low"]))
    print("queue head: " + ", ".join(i["page_id"] for i in items[:8]))


def cmd_show(args, pages):
    by_id = dict((p["page_id"], p) for p in pages)
    page = by_id.get(args.page_id)
    if not page:
        sys.exit("page %s is not in the architecture" % args.page_id)
    print(json.dumps(page, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("brief", help="generate a content brief for one page")
    b.add_argument("page_id")
    b.add_argument("--out")
    b.add_argument("--merge", help="existing brief whose hand set values are preserved")

    s = sub.add_parser("seed", help="generate the tracker seed and queue order")
    s.add_argument("--out", required=True)

    w = sub.add_parser("show", help="print one page's architecture entry")
    w.add_argument("page_id")

    args = ap.parse_args()
    pages = load_pages()
    {"brief": cmd_brief, "seed": cmd_seed, "show": cmd_show}[args.cmd](args, pages)


if __name__ == "__main__":
    main()
