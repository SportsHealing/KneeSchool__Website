"""Deterministic style gate for KneeSchool article drafts.

The gate is regex and counting only. No model call. A language model asked to
police its own style will occasionally let something through; a rule will not.

Document conventions this linter expects from Agent 3:

  # Title
  ## Junior            <- tier block, one heading per tier in brief.tiers_required
  ...body...
  ### Key learning points
  - point
  ## Patient
  ...
  ### Frequently asked questions
  **Q.** ...
  ## References
  1. Author A, Author B. Title. Journal. 2024. doi:10.xxxx/yyyy

Tier headings are matched case insensitively against the aliases in TIER_ALIASES.
Everything from the References heading to the end of the document is the
reference list, which is excluded from the body scopes.
"""

import json
import os
import re
import statistics

TIERS = ["junior", "patient", "medical_student", "mrcs", "frcs", "fellowship", "consultant"]

TIER_ALIASES = {
    "junior": ["junior", "junior academy", "school", "school age"],
    "patient": ["patient", "patient academy", "for patients"],
    "medical_student": ["medical student", "student", "student academy", "undergraduate"],
    "mrcs": ["mrcs", "mrcs academy", "core trainee"],
    "frcs": ["frcs", "frcs academy", "frcs (tr and orth)", "frcs tr and orth", "higher trainee"],
    "fellowship": ["fellowship", "fellow", "fellowship academy"],
    "consultant": ["consultant", "consultant masterclass"],
}

REFERENCE_HEADINGS = ["references", "reference list", "sources"]
CROSS_LINK_HEADINGS = ["explore further"]

# Human headings the handbook uses in prose, mapped to the slugs its JSON block
# uses. Anything not listed falls back to slugifying the heading, which covers
# the sections whose prose name and slug already match.
SECTION_ALIASES = {
    "who gets it": "epidemiology",
    "who gets it (epidemiology)": "epidemiology",
    "how it presents": "presentation",
    "before the operation": "before_the_operation",
    "before the operation (work up and consent points)": "before_the_operation",
}

# Sections the handbook restricts to the deeper tiers.
SECTION_TIER_FLOOR = {
    "controversies_and_evidence": "frcs",
    "variations_and_controversies": "fellowship",
}
KLP_HEADINGS = ["key learning points", "key learning point"]
FAQ_HEADINGS = ["frequently asked questions", "faqs", "faq", "common questions"]

ABBREVIATIONS = [
    "e.g.", "i.e.", "vs.", "cf.", "approx.", "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.",
    "Fig.", "no.", "et al.", "St.", "Inc.", "Ltd.",
]

CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)


# ---------------------------------------------------------------- document


class Document(object):
    """A parsed draft: raw text, tier blocks, reference list, body."""

    def __init__(self, text, template=None):
        self.raw = text or ""
        self.template = template or {}
        self.lines = self.raw.split("\n")
        self.sections = self._split_headings()
        self.reference_span = self._find_reference_span()
        self.tier_spans = {}
        self.tier_by_alias = {}
        self.tier_heading_level = {}
        self._find_tier_spans()

    # -- parsing ---------------------------------------------------

    def _split_headings(self):
        """Return [(level, title, start_line, end_line_exclusive)] for every heading."""
        found = []
        in_fence = False
        for i, line in enumerate(self.lines):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
            if m:
                found.append([len(m.group(1)), m.group(2), i, None])
        for idx, item in enumerate(found):
            level = item[0]
            end = len(self.lines)
            for later in found[idx + 1:]:
                if later[0] <= level:
                    end = later[2]
                    break
            item[3] = end
        return [tuple(x) for x in found]

    @staticmethod
    def _normalise(title):
        t = title.lower().strip()
        t = re.sub(r"^tier\s*[:.]?\s*", "", t)
        t = re.sub(r"[^a-z0-9 ()]+", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    def _find_reference_span(self):
        for level, title, start, end in self.sections:
            if self._normalise(title) in REFERENCE_HEADINGS and level <= 2:
                return (start, len(self.lines))
        return None

    def article_section(self, headings):
        """Find a top level (H2) section by normalised heading."""
        for level, title, start, end in self.sections:
            if level <= 2 and self._normalise(title) in headings:
                return (title, start, end)
        return None

    def _find_tier_spans(self):
        """Exact handbook headings first. A loose alias match is still recorded,
        so the tier-scoped rules keep working on a draft that used the wrong
        heading, and STRUCT-001 reports the heading itself as the fault."""
        exact = {}
        for tier, heading in (self.template.get("tier_headings") or {}).items():
            exact[self._normalise(heading)] = tier

        for level, title, start, end in self.sections:
            norm = self._normalise(title)
            tier = exact.get(norm)
            if tier and tier not in self.tier_spans:
                self.tier_spans[tier] = (start, end)
                self.tier_heading_level[tier] = level
                continue
            for alias_tier, aliases in TIER_ALIASES.items():
                if norm in aliases and alias_tier not in self.tier_spans:
                    self.tier_spans[alias_tier] = (start, end)
                    self.tier_heading_level[alias_tier] = level
                    self.tier_by_alias[alias_tier] = title

    # -- views -----------------------------------------------------

    def full_text(self):
        return self.raw

    def body_text(self):
        """Everything except the reference list and fenced code."""
        if self.reference_span:
            text = "\n".join(self.lines[: self.reference_span[0]])
        else:
            text = self.raw
        return CODE_FENCE.sub("", text)

    def reference_text(self):
        if not self.reference_span:
            return ""
        return "\n".join(self.lines[self.reference_span[0]: self.reference_span[1]])

    def tier_text(self, tier):
        span = self.tier_spans.get(tier)
        if not span:
            return ""
        return "\n".join(self.lines[span[0]: span[1]])

    def tiers_present(self):
        return sorted(self.tier_spans.keys())

    def prose_sentences(self):
        text = self.body_text()
        text = re.sub(r"^\s{0,3}#{1,6}\s.*$", "", text, flags=re.MULTILINE)   # headings
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)          # bullets
        text = re.sub(r"\[\d+\]", "", text)                                    # citations
        text = re.sub(r"[*_`]", "", text)
        guard = text
        for abbr in ABBREVIATIONS:
            guard = guard.replace(abbr, abbr.replace(".", "\x00"))
        parts = re.split(r"(?<=[.!?])\s+", guard)
        out = []
        for part in parts:
            part = part.replace("\x00", ".").strip()
            if len(part.split()) >= 3:
                out.append(part)
        return out

    def word_count(self):
        text = re.sub(r"^\s{0,3}#{1,6}\s", "", self.body_text(), flags=re.MULTILINE)
        return len(re.findall(r"[A-Za-z0-9']+", text))

    def subsection_titles_within(self, span):
        titles = []
        for level, title, start, end in self.sections:
            if span[0] < start < span[1]:
                titles.append((self._normalise(title), start, end))
        return titles

    def bullet_count(self, start, end):
        n = 0
        for line in self.lines[start:end]:
            if re.match(r"^\s*(?:[-*+]|\d+\.)\s+\S", line):
                n += 1
        return n


# ---------------------------------------------------------------- helpers


def normalise_title(title):
    return Document._normalise(title)


def context(text, start, end, width=50):
    lo = max(0, start - width)
    hi = min(len(text), end + width)
    return re.sub(r"\s+", " ", text[lo:hi]).strip()


def finding(rule_id, severity, description, matched, ctx, line=None):
    item = {
        "rule_id": rule_id,
        "severity": severity,
        "description": description,
        "matched_text": matched,
        "context": ctx,
    }
    if line is not None:
        item["line"] = line
    return item


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def phrase_pattern(phrase):
    """Word-boundary, case-insensitive pattern that tolerates the trailing comma
    variants in the banned list (for example 'additionally,')."""
    escaped = re.escape(phrase)
    lead = r"(?<![A-Za-z])" if phrase[:1].isalnum() else ""
    trail = r"(?![A-Za-z])" if phrase[-1:].isalnum() else ""
    return re.compile(lead + escaped + trail, re.IGNORECASE)


# ---------------------------------------------------------------- rules


def scope_text(doc, scope, brief=None):
    """Resolve a rule scope string to the text it applies to."""
    if scope in (None, "body_and_headings"):
        return [("document", doc.full_text())]
    if scope == "body":
        return [("body", doc.body_text())]
    if scope and scope.startswith("tier:"):
        out = []
        for tier in scope.split(":", 1)[1].split(","):
            tier = tier.strip()
            text = doc.tier_text(tier)
            if text:
                out.append(("tier:" + tier, text))
        return out
    return [("document", doc.full_text())]


def run_pattern_rule(doc, rule, brief):
    out = []
    pattern = re.compile(rule["pattern"])
    for label, text in scope_text(doc, rule.get("scope"), brief):
        for m in pattern.finditer(text):
            out.append(finding(rule["id"], rule["severity"],
                               rule["description"] + " (" + label + ")",
                               m.group(0), context(text, m.start(), m.end()),
                               line_of(text, m.start())))
    return out


def blank_architecture_titles(text, brief):
    """Blank the lines that carry page titles the architecture fixed.

    Two places on a page hold a title rather than prose: the H1, and the labels
    in the cross link block. Neither is written by the drafter. The architecture
    names every page, and a writer cannot reword a title without breaking the
    brief or the link. Scanning them for house style reports a fault nobody on
    the pipeline is allowed to fix. 0.5.5 "Meet the Researchers" is the case that
    forced this: it trips the "meet the" ban in the H1 of its own page and in the
    cross link block of every page that points at it.

    Lines are replaced with spaces rather than removed, so every other finding
    keeps its line number.
    """
    want = normalise_title((brief or {}).get("title") or "") or None
    out, in_cross = [], False
    for line in text.split("\n"):
        m = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
        if m:
            level, title = len(m.group(1)), normalise_title(m.group(2))
            if level == 1 and want and title == want:
                out.append(" " * len(line))
                continue
            # the cross link block runs from its own heading to the next one
            in_cross = title in CROSS_LINK_HEADINGS
        elif in_cross and WIKILINK.search(line):
            out.append(" " * len(line))
            continue
        out.append(line)
    return "\n".join(out)


def run_phrase_rule(doc, rule, brief):
    out = []
    exclude_refs = rule["id"].startswith("UK-")
    for label, text in scope_text(doc, rule.get("scope"), brief):
        if exclude_refs and label == "document":
            text = doc.body_text()
            label = "body (reference list excluded)"
        if rule.get("excludes_architecture_title"):
            text = blank_architecture_titles(text, brief)
        for phrase in rule.get("banned_phrases", []):
            for m in phrase_pattern(phrase).finditer(text):
                out.append(finding(rule["id"], rule["severity"],
                                   rule["description"] + " (" + label + ")",
                                   m.group(0), context(text, m.start(), m.end()),
                                   line_of(text, m.start())))
    return out


WIKILINK = re.compile(r"\[\[[^\]]+\]\]")
LIST_MARKER = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])(\s)", re.MULTILINE)
HRULE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", re.MULTILINE)
TABLE_RULE = re.compile(r"^\s*\|?[\s:|-]{5,}\|?\s*$", re.MULTILINE)


def rule_dash_002(doc, rule):
    """Space-hyphen-space in prose.

    Markdown structure uses the same character sequence for list markers,
    horizontal rules and table separators. Those are blanked out before the
    configured pattern runs, so the rule catches a parenthetical dash in a
    sentence and leaves valid markup alone.
    """
    text = doc.body_text()
    cleaned = HRULE.sub(lambda m: " " * len(m.group(0)), text)
    cleaned = TABLE_RULE.sub(lambda m: " " * len(m.group(0)), cleaned)
    cleaned = LIST_MARKER.sub(lambda m: m.group(1) + " " * (m.end() - m.start() - len(m.group(1))),
                              cleaned)
    out = []
    for m in re.compile(rule["pattern"]).finditer(cleaned):
        out.append(finding(rule["id"], rule["severity"],
                           rule["description"] + " (body)",
                           m.group(0), context(text, m.start(), m.end()),
                           line_of(text, m.start())))
    return out


def rule_phrase_002(doc, rule):
    """Warn when more than max_allowed_per_article paragraphs open with a
    transition word."""
    pattern = re.compile(rule["pattern"])
    text = doc.body_text()
    hits = list(pattern.finditer(text))
    limit = rule.get("max_allowed_per_article", 2)
    if len(hits) <= limit:
        return []
    out = []
    for m in hits[limit:]:
        out.append(finding(rule["id"], rule["severity"],
                           rule["description"] + " (limit " + str(limit) + ")",
                           m.group(0), context(text, m.start(), m.end()),
                           line_of(text, m.start())))
    return out


THREE_ITEM = re.compile(
    r"\b[^,.;:]{2,40},\s+[^,.;:]{2,40}[,]?\s+(?:and|or)\s+[^,.;:]{2,40}", re.IGNORECASE)


def rule_phrase_003(doc, rule):
    sentences = doc.prose_sentences()
    if len(sentences) < 8:
        return []
    hits = [s for s in sentences if THREE_ITEM.search(s)]
    ratio = float(len(hits)) / len(sentences)
    if ratio <= rule.get("threshold", 0.3):
        return []
    return [finding(rule["id"], rule["severity"],
                    rule["description"],
                    "%d of %d sentences (%.0f%%)" % (len(hits), len(sentences), ratio * 100),
                    " | ".join(s[:70] for s in hits[:3]))]


def rule_phrase_004(doc, rule):
    sentences = doc.prose_sentences()
    if len(sentences) < 8:
        return []
    lengths = [len(s.split()) for s in sentences]
    sd = statistics.pstdev(lengths)
    if sd >= rule.get("threshold", 4):
        return []
    return [finding(rule["id"], rule["severity"],
                    rule["description"],
                    "standard deviation %.1f words over %d sentences" % (sd, len(sentences)),
                    "mean %.1f words" % (sum(lengths) / float(len(lengths))))]


CITE_MARKER = re.compile(r"\[(\d{1,3})\]")
REF_ENTRY = re.compile(r"^\s*(?:\[(\d{1,3})\]|(\d{1,3})[.)])\s+\S", re.MULTILINE)


def rule_cite_001(doc, rule):
    body = doc.body_text()
    refs = doc.reference_text()
    used = set(int(m.group(1)) for m in CITE_MARKER.finditer(body))
    listed = set()
    for m in REF_ENTRY.finditer(refs):
        listed.add(int(m.group(1) or m.group(2)))
    out = []
    if not refs and used:
        out.append(finding(rule["id"], rule["severity"],
                           "Citation markers present but no reference list found",
                           sorted(used).__repr__(), ""))
        return out
    missing = sorted(used - listed)
    orphan = sorted(listed - used)
    if missing:
        out.append(finding(rule["id"], rule["severity"],
                           "In-text markers with no reference entry",
                           ", ".join("[%d]" % n for n in missing), ""))
    if orphan:
        out.append(finding(rule["id"], rule["severity"],
                           "Reference entries never cited in the text",
                           ", ".join(str(n) for n in orphan), ""))
    return out


def rule_cite_002(doc, rule):
    out = []
    for label, text in scope_text(doc, rule.get("scope")):
        for m in CITE_MARKER.finditer(text):
            out.append(finding(rule["id"], rule["severity"],
                               rule["description"] + " (" + label + ")",
                               m.group(0), context(text, m.start(), m.end()),
                               line_of(text, m.start())))
    return out


def slugify(title):
    slug = SECTION_ALIASES.get(title)
    if slug:
        return slug
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", title)).strip("_")


def is_ordered_subset(found, allowed):
    """Every found section must appear in `allowed`, in that order."""
    i = 0
    for item in found:
        while i < len(allowed) and allowed[i] != item:
            i += 1
        if i == len(allowed):
            return False
        i += 1
    return True


# -- FIG-001 ---------------------------------------------------------------

# A pointer to another part of the site, not a quantity. These are written into
# the prose constantly ("3.13 takes that further", "Section 7 owns the argument",
# "decision 005 records why"), so they are removed before the scan rather than
# listed as exceptions one at a time.
UNIT = r"(?:mm|cm|%|per\s?cent|degrees?|mL|ml|kg|MPa|m|N)"
# A page id and a decimal measurement look identical: 5.5 could be chapter 5.5 or
# five and a half degrees. The unit decides, so an id is only stripped when no
# unit follows it. A bare decimal with no unit is read as a page id, because on
# this site that is what it almost always is. Write a unit and the rule fires.
XREF = re.compile(r"\b\d+(?:\.\d+){1,2}\b(?!\s*" + UNIT + r"\b)")
XREF_WORD = re.compile(r"\b(?:section|sections|chapter|chapters|decision|decisions|"
                       r"figure|figures|table|tables)\s+\d+"
                       r"(?:\s*(?:,|and|or|to)\s*\d+)*", re.IGNORECASE)
# The trailing lookahead stops the pattern matching half of a decimal while
# still allowing a quantity to end a sentence. "9 degrees." has to fire.
QUANTITY = re.compile(r"(?<![A-Za-z])(\d+(?:[.,]\d+)?)"
                      r"\s*" + UNIT + r"?"
                      r"(?![A-Za-z0-9]|\.\d)")


def rule_fig_001(doc, rule, brief):
    """Decision 005: no measurement on a page in a section that forbids them.

    Every published description of knee anatomy at this depth is quantitative,
    and none of it could be verified here. A plausible wrong dimension on an FRCS
    page is worse than no dimension, so the gate refuses the figure rather than
    trusting review to catch it.

    List numbering written into prose is allowed, because the alternative is
    spelling out every enumeration. A quantity is not, and there is no way to
    write one without a digit.
    """
    out = []
    allowed = set(str(n) for n in rule.get("allowed_bare_integers") or [])
    text = XREF.sub(" ", XREF_WORD.sub(" ", doc.body_text()))
    for m in QUANTITY.finditer(text):
        token = m.group(0).strip()
        if m.group(1) in allowed and token == m.group(1):
            continue
        out.append(finding(rule["id"], rule["severity"],
                           rule["description"] + " (body)", token,
                           context(text, m.start(), m.end()),
                           line_of(text, m.start())))
    return out


def rule_struct_001(doc, rule, brief, template):
    """Structure against the handbook template and the brief.

    The handbook is the source of truth for shape; the brief says which tiers
    and, where it chooses to, overrides the word count. Everything checked here
    is regenerated from the handbook's machine-readable block rather than
    restated, so the rule and the handbook cannot drift apart.
    """
    out = []
    sev = rule["severity"]
    desc = rule["description"]

    def fail(msg, matched=""):
        out.append(finding(rule["id"], sev, desc + ": " + msg, matched, ""))

    tier_order = template.get("tier_order") or TIERS
    headings = template.get("tier_headings") or {}
    klp_cfg = template.get("key_learning_points") or {}
    faq_cfg = template.get("faqs") or {}
    closers = template.get("tier_closers") or {}
    page_types = template.get("page_types") or {}
    cross = template.get("cross_links") or {}

    required = brief.get("tiers_required") or []
    rank = dict((t, i) for i, t in enumerate(tier_order))

    # -- tier blocks present, correctly headed, in ascending order -----------
    for tier in required:
        if tier not in doc.tier_spans:
            fail("no content block found for tier '%s' (expected heading '%s')"
                 % (tier, headings.get(tier, tier)), tier)
        elif tier in doc.tier_by_alias:
            fail("tier '%s' is headed '%s'; the handbook requires the exact heading '%s'"
                 % (tier, doc.tier_by_alias[tier], headings.get(tier, tier)), tier)

    extra = [t for t in doc.tier_spans if t not in required]
    for tier in extra:
        fail("tier block '%s' is present but the brief does not require it" % tier, tier)

    present = [t for t in tier_order if t in doc.tier_spans]
    ordered = sorted(present, key=lambda t: doc.tier_spans[t][0])
    if present != ordered:
        fail("tier blocks are out of order; the handbook fixes ascending tier order",
             " then ".join(ordered))

    # -- per tier: key learning points, body sections, closers ---------------
    klp_heading = normalise_title(klp_cfg.get("heading", "Key Learning Points"))
    faq_heading = normalise_title(faq_cfg.get("heading", "Frequently Asked Questions"))
    lo, hi = klp_cfg.get("min_bullets"), klp_cfg.get("max_bullets")

    page_type = brief.get("page_type")
    # The architecture's fine grained type maps onto one of the handbook's three
    # templates. A page_type with no template is a configuration gap, not a
    # drafting error, so it is reported as such.
    template_name = resolve_template(page_type)
    spec = page_types.get(template_name) or {}
    allowed_sections = spec.get("body_sections") or []

    for tier in required:
        span = doc.tier_spans.get(tier)
        if not span:
            continue
        subs = doc.subsection_titles_within(span)

        klp = [(t, a, b) for t, a, b in subs if t == klp_heading]
        if not klp:
            fail("tier '%s' has no '%s' block" % (tier, klp_cfg.get("heading")), tier)
        else:
            n = doc.bullet_count(klp[0][1] + 1, klp[0][2])
            if lo is not None and n < lo:
                fail("tier '%s' has %d key learning points, minimum %d" % (tier, n, lo), tier)
            elif hi is not None and n > hi:
                fail("tier '%s' has %d key learning points, maximum %d" % (tier, n, hi), tier)

        # FAQs belong to one tier only
        has_faq = [t for t, a, b in subs if t == faq_heading]
        if has_faq and tier != faq_cfg.get("location", "patient_tier_block").split("_")[0]:
            fail("tier '%s' carries an FAQ block; the handbook allows FAQs only in the "
                 "patient tier" % tier, tier)

        # Decision 001: a page told to exclude region level anatomy detail may not
        # carry a dissection level section in its professional tiers.
        depth = load_depth_rules()
        block = depth.get("forbidden_sections_when_excluded") or {}
        phrase = (block.get("exclusion_phrase") or "").lower()
        excluded = " ".join(brief.get("scope", {}).get("must_not_cover") or []).lower()
        if phrase and phrase in excluded and tier in (block.get("restricted_tiers") or []):
            exempt = set(
                (e.get("page_id"), e.get("section"))
                for e in depth.get("exemptions") or [])
            for banned in block.get("sections") or []:
                if normalise_title(banned) in [t for t, a, b in subs]:
                    if (brief.get("page_id"), banned) in exempt:
                        continue
                    fail("tier '%s' carries a '%s' section. %s See decision 001."
                         % (tier, banned, block.get("reason", "")), tier)

        # a reference list inside a tier block is forbidden
        for t, a, b in subs:
            if t in REFERENCE_HEADINGS:
                fail("tier '%s' carries its own reference list; the handbook allows one "
                     "article level list only" % tier, tier)

        # body sections must be an ordered subset of the page type's list
        if allowed_sections:
            body = [slugify(t) for t, a, b in subs
                    if t not in (klp_heading, faq_heading) and t not in REFERENCE_HEADINGS]
            unknown = [x for x in body if x not in allowed_sections]
            if unknown:
                fail("tier '%s' has section(s) not in the %s page template: %s"
                     % (tier, template_name, ", ".join(unknown)), tier)
            elif not is_ordered_subset(body, allowed_sections):
                fail("tier '%s' body sections are out of the order the %s template fixes"
                     % (tier, template_name), tier)
            for slug in body:
                floor = SECTION_TIER_FLOOR.get(slug)
                if floor and rank.get(tier, 0) < rank.get(floor, 0):
                    fail("tier '%s' carries '%s', which the handbook restricts to %s and "
                         "above" % (tier, slug, floor), tier)

        # tier closers
        closer = closers.get(tier) or {}
        text = doc.tier_text(tier)
        message = closer.get("message")
        if message and page_type in (closer.get("not_required_for_page_types") or []):
            # The handbook attaches this message to symptom or injury content.
            # These page types carry none. See decision 003.
            message = None
        if message:
            # Compare with whitespace collapsed. A draft wraps its paragraphs, so
            # the closing message almost never sits on a single line.
            flat = re.sub(r"\s+", " ", text).lower()
            want = re.sub(r"\s+", " ", message).rstrip(".").lower()
            if want not in flat:
                fail("tier '%s' does not carry the standard closing message" % tier, tier)
        if closer.get("when_to_seek_help_message_required"):
            # Any plain pointer to a clinician counts. The handbook asks for a
            # when to seek help message, not for one particular wording.
            if not re.search(r"\bseek\b|\burgent\b|emergency|999|"
                             r"\b(see|tell|speak to|contact|consult|ask)\b[^.]{0,40}"
                             r"\b(doctor|clinician|gp|physiotherapist|nurse|specialist|"
                             r"surgeon|parent|teacher|coach|professional)\b|"
                             r"\b(get|have)\b[^.]{0,30}\b(checked|assessed|looked at|seen)\b",
                             text, re.IGNORECASE):
                fail("tier '%s' has no when to seek help message" % tier, tier)

    # -- patient FAQ count ---------------------------------------------------
    if faq_cfg and faq_cfg.get("required_when") == "patient_tier_present" \
            and "patient" in required:
        span = doc.tier_spans.get("patient")
        block = None
        if span:
            for title, a, b in doc.subsection_titles_within(span):
                if title == faq_heading:
                    block = (a, b)
                    break
        if block is None:
            fail("patient tier has no '%s' block" % faq_cfg.get("heading"))
        else:
            n = len(re.findall(r"^\s*(?:\*\*Q|Q[.:]|####\s)", "\n".join(
                doc.lines[block[0] + 1: block[1]]), re.MULTILINE))
            if faq_cfg.get("min") is not None and n < faq_cfg["min"]:
                fail("patient FAQ block has %d questions, minimum %d" % (n, faq_cfg["min"]))
            elif faq_cfg.get("max") is not None and n > faq_cfg["max"]:
                fail("patient FAQ block has %d questions, maximum %d" % (n, faq_cfg["max"]))

    # -- article level sections ---------------------------------------------
    if cross.get("heading"):
        if doc.article_section([normalise_title(cross["heading"])]) is None:
            fail("no '%s' section" % cross["heading"])

    if doc.reference_span is None and CITE_MARKER.search(doc.body_text()):
        fail("citation markers are used but there is no article level reference list")

    # -- word count: the brief overrides the page type default ---------------
    wc = (brief.get("output_requirements") or {}).get("target_word_count") \
        or spec.get("word_count") or {}
    n = doc.word_count()
    if wc.get("min") is not None and n < wc["min"]:
        fail("word count %d below the minimum %d" % (n, wc["min"]))
    elif wc.get("max") is not None and n > wc["max"]:
        fail("word count %d above the maximum %d" % (n, wc["max"]))

    if page_type and not spec:
        fail("brief names page_type '%s', which resolves to template '%s'; the handbook "
             "defines no such template" % (page_type, template_name), page_type)
    if not page_type:
        fail("brief does not name a page_type, so body section order cannot be checked")

    return out


def condition_met(expr, brief):
    """Evaluate the small set of conditional_on expressions the config uses."""
    if not expr:
        return True
    m = re.match(r"^\s*brief\.([A-Za-z0-9_.]+)\s*==\s*(true|false)\s*$", expr)
    if not m:
        return True
    node = brief
    for part in m.group(1).split("."):
        if not isinstance(node, dict):
            return False
        node = node.get(part)
    return bool(node) is (m.group(2) == "true")


# ---------------------------------------------------------------- entry point


def load_rules(path=None):
    """Find lint_rules.json. In Lambda the config is packaged next to this file;
    in the repo it lives under pipeline/config/. LINT_RULES_PATH overrides both."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        path,
        os.environ.get("LINT_RULES_PATH"),
        os.path.join(here, "lint_rules.json"),
        os.path.join(here, "..", "..", "config", "lint_rules.json"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            with open(candidate, "r") as fh:
                return json.load(fh)
    raise IOError("lint_rules.json not found; set LINT_RULES_PATH")


def load_page_type_map(path=None):
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in [path, os.environ.get("PAGE_TYPE_MAP_PATH"),
                      os.path.join(here, "page_type_map.json"),
                      os.path.join(here, "..", "..", "config", "page_type_map.json")]:
        if candidate and os.path.exists(candidate):
            with open(candidate) as fh:
                return json.load(fh).get("page_types") or {}
    return {}


def resolve_template(page_type):
    if not page_type:
        return None
    mapped = load_page_type_map().get(page_type)
    if mapped:
        return mapped.get("template")
    return page_type


def load_depth_rules(path=None):
    """Decision 001: how deep a Fundamentals page may go.

    The architecture excludes region level anatomy detail from these pages
    without saying where the line falls. The ruling places it, and this is the
    machine form so a future page cannot breach it quietly.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in [path, os.environ.get("DEPTH_RULES_PATH"),
                      os.path.join(here, "depth_rules.json"),
                      os.path.join(here, "..", "..", "config", "depth_rules.json")]:
        if candidate and os.path.exists(candidate):
            with open(candidate) as fh:
                return json.load(fh)
    return {}


def load_article_template(path=None):
    """The handbook's machine-readable article template. It is the source of
    truth for structure; STRUCT-001 reads it rather than restating it."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        path,
        os.environ.get("ARTICLE_TEMPLATE_PATH"),
        os.path.join(here, "article_template.json"),
        os.path.join(here, "..", "..", "config", "article_template.json"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            with open(candidate, "r") as fh:
                return json.load(fh)
    return {}


def lint(text, brief=None, rules=None, template=None):
    """Return a lint report dict. pass is False if any 'fail' rule fired."""
    brief = brief or {}
    rules = rules or load_rules()
    template = load_article_template() if template is None else template
    doc = Document(text, template)
    findings = []

    for rule in rules.get("rules", []):
        rid = rule["id"]
        if not condition_met(rule.get("conditional_on"), brief):
            continue
        if rid == "DASH-002":
            findings += rule_dash_002(doc, rule)
        elif rid == "PHRASE-002":
            findings += rule_phrase_002(doc, rule)
        elif rid == "PHRASE-003":
            findings += rule_phrase_003(doc, rule)
        elif rid == "PHRASE-004":
            findings += rule_phrase_004(doc, rule)
        elif rid == "CITE-001":
            findings += rule_cite_001(doc, rule)
        elif rid == "CITE-002":
            findings += rule_cite_002(doc, rule)
        elif rid == "FIG-001":
            findings += rule_fig_001(doc, rule, brief)
        elif rid == "STRUCT-001":
            findings += rule_struct_001(doc, rule, brief, template)
        elif rule.get("banned_phrases"):
            findings += run_phrase_rule(doc, rule, brief)
        elif rule.get("pattern"):
            findings += run_pattern_rule(doc, rule, brief)

    fails = [f for f in findings if f["severity"] == "fail"]
    warns = [f for f in findings if f["severity"] == "warn"]
    return {
        "lint_version": rules.get("lint_version"),
        "pass": len(fails) == 0,
        "fail_count": len(fails),
        "warn_count": len(warns),
        "findings": findings,
        "article_template_version": template.get("article_template_version"),
        "document": {
            "word_count": doc.word_count(),
            "tiers_present": doc.tiers_present(),
            "has_reference_list": doc.reference_span is not None,
            "sentence_count": len(doc.prose_sentences()),
            "page_type": brief.get("page_type"),
        },
    }


def autofix_quotes(text):
    """QUOTE-001 autofix: normalise curly quotation marks to straight."""
    for bad, good in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')):
        text = text.replace(bad, good)
    return text
