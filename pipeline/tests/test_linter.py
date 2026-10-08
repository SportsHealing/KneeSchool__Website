"""Tests for the deterministic style gate.

Run from the repository root:  python3 -m unittest discover -s pipeline/tests -v
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "functions", "style_lint"))
sys.path.insert(0, os.path.join(ROOT, "functions"))

import linter  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
with open(os.path.join(ROOT, "config", "briefs", "1.2.3.json")) as _fh:
    BRIEF = json.load(_fh)

# The clean case is the real pilot article, not a fixture written to pass. If the
# gate and the pilot ever disagree, one of them is wrong and the suite says so.
PILOT = os.path.join(ROOT, "runs", "1.2.3", "styled_v1.md")


def read(name):
    with open(os.path.join(FIXTURES, name)) as fh:
        return fh.read()


def read_pilot():
    with open(PILOT) as fh:
        return fh.read()


def ids(report):
    return set(f["rule_id"] for f in report["findings"])


def ids_at(report, severity):
    return set(f["rule_id"] for f in report["findings"] if f["severity"] == severity)


class CleanDraft(unittest.TestCase):
    def setUp(self):
        self.report = linter.lint(read_pilot(), BRIEF)

    def test_passes(self):
        self.assertTrue(self.report["pass"],
                        "unexpected failures: %s" % json.dumps(
                            [f for f in self.report["findings"] if f["severity"] == "fail"],
                            indent=2))

    def test_no_fail_severity_findings(self):
        self.assertEqual(ids_at(self.report, "fail"), set())

    def test_tiers_detected(self):
        self.assertEqual(self.report["document"]["tiers_present"],
                         ["junior", "medical_student", "patient"])

    def test_tiers_use_the_exact_handbook_headings(self):
        doc = linter.Document(read_pilot(), linter.load_article_template())
        self.assertEqual(doc.tier_by_alias, {},
                         "a tier was matched by alias, so its heading is not the handbook's")

    def test_reference_list_found(self):
        self.assertTrue(self.report["document"]["has_reference_list"])

    def test_runs_against_the_handbook_template(self):
        self.assertEqual(self.report["article_template_version"], "1.0")


class DirtyDraft(unittest.TestCase):
    def setUp(self):
        self.report = linter.lint(read("dirty_1.2.3.md"), BRIEF)

    def test_fails(self):
        self.assertFalse(self.report["pass"])

    def test_catches_em_dash(self):
        self.assertIn("DASH-001", ids(self.report))

    def test_catches_banned_phrases(self):
        self.assertIn("PHRASE-001", ids(self.report))
        matched = set(f["matched_text"].lower() for f in self.report["findings"]
                      if f["rule_id"] == "PHRASE-001")
        for phrase in ("delve", "it is important to note", "plays a crucial role",
                       "in today's world"):
            self.assertIn(phrase, matched)

    def test_catches_us_spellings(self):
        matched = set(f["matched_text"].lower() for f in self.report["findings"]
                      if f["rule_id"] == "UK-001")
        for word in ("fiber", "center", "randomized", "aging"):
            self.assertIn(word, matched)

    def test_catches_citation_mismatch(self):
        self.assertIn("CITE-001", ids(self.report))

    def test_catches_citation_in_junior_tier(self):
        self.assertIn("CITE-002", ids(self.report))

    def test_catches_commercial_content(self):
        matched = set(f["matched_text"].lower() for f in self.report["findings"]
                      if f["rule_id"] == "GOV-001")
        self.assertTrue({"omkneehealth", "buy", "discount"} <= matched, matched)

    def test_catches_advice_pattern_in_junior_tier(self):
        self.assertIn("GOV-002", ids(self.report))

    def test_catches_structure_gaps(self):
        struct = [f for f in self.report["findings"] if f["rule_id"] == "STRUCT-001"]
        self.assertTrue(struct)
        text = " ".join(f["description"] for f in struct)
        self.assertIn("key learning points", text)


class ScopeRules(unittest.TestCase):
    def test_uk_rule_ignores_reference_list(self):
        doc = ("# T\n\nSummary.\n\n## For Patients\n\nThe knee is a hinge joint of the lower limb.\n\n"
               "### Key learning points\n\n- one\n- two\n- three\n\n"
               "### Frequently asked questions\n\n**Q.** A?\nYes.\n\n**Q.** B?\nYes.\n\n"
               "**Q.** C?\nYes.\n\n"
               "## References\n\n1. Smith J. A randomized controlled trial of color vision. 2020.\n")
        report = linter.lint(doc, {"tiers_required": ["patient"]})
        self.assertNotIn("UK-001", ids(report))

    def test_uk_rule_catches_body(self):
        doc = "# T\n\nSummary.\n\n## For Patients\n\nA randomized trial of the center.\n"
        report = linter.lint(doc, {"tiers_required": ["patient"]})
        self.assertIn("UK-001", ids(report))

    def test_commercial_rule_skipped_when_allowed(self):
        doc = "# T\n\nSummary.\n\n## For Patients\n\nYou can buy a brace.\n"
        brief = {"tiers_required": ["patient"],
                 "governance": {"commercial_content_allowed": True}}
        self.assertNotIn("GOV-001", ids(linter.lint(doc, brief)))

    def test_commercial_rule_applied_when_not_allowed(self):
        doc = "# T\n\nSummary.\n\n## For Patients\n\nYou can buy a brace.\n"
        brief = {"tiers_required": ["patient"],
                 "governance": {"commercial_content_allowed": False}}
        self.assertIn("GOV-001", ids(linter.lint(doc, brief)))

    def test_space_hyphen_space_is_a_failure(self):
        doc = "# T\n\nSummary.\n\n## For Patients\n\nThe knee - a hinge joint - bends.\n"
        self.assertIn("DASH-002", ids(linter.lint(doc, {"tiers_required": ["patient"]})))

    def test_hyphenated_word_is_not_flagged(self):
        doc = "# T\n\nSummary.\n\n## For Patients\n\nOsgood-Schlatter disease settles with time.\n"
        report = linter.lint(doc, {"tiers_required": ["patient"]})
        self.assertNotIn("DASH-002", ids(report))
        self.assertNotIn("DASH-001", ids(report))

    def test_markdown_bullets_are_not_flagged_as_dashes(self):
        doc = ("# T\n\nSummary.\n\n## For Patients\n\nThe knee bends.\n\n"
               "### Key learning points\n\n- one\n- two\n- three\n\n"
               "| a | b |\n| --- | --- |\n| 1 | 2 |\n\n---\n\n1. first\n2. second\n")
        self.assertNotIn("DASH-002", ids(linter.lint(doc, {"tiers_required": ["patient"]})))

    def test_imaging_does_not_trip_the_aging_ban(self):
        doc = "# T\n\nSummary.\n\n## For Patients\n\nImaging of the knee is straightforward.\n"
        self.assertNotIn("UK-001", ids(linter.lint(doc, {"tiers_required": ["patient"]})))


class Autofix(unittest.TestCase):
    def test_curly_quotes_normalised(self):
        self.assertEqual(linter.autofix_quotes(u"the ‘knee’ and “joint”"),
                         "the 'knee' and \"joint\"")


if __name__ == "__main__":
    unittest.main()


class ArchitectureTitleExclusion(unittest.TestCase):
    """0.5.5 is called Meet the Researchers, and "meet the" is a banned phrase.

    The architecture fixes page titles. A title nobody on the pipeline is allowed
    to reword must not be reported as a style fault, in its own H1 or in the cross
    link block of every page that points at it. Prose is still scanned.
    """

    BRIEF = {"title": "Meet the Researchers", "page_type": "study_skills",
             "tiers_required": ["junior"]}

    def ran(self, text):
        return linter.lint(text, self.BRIEF)

    def test_the_h1_is_not_scanned(self):
        doc = "# Meet the Researchers\n\nSome prose about research groups.\n"
        self.assertNotIn("PHRASE-001", ids(self.ran(doc)))

    def test_a_cross_link_label_is_not_scanned(self):
        doc = ("# Something Else\n\nProse.\n\n## Explore Further\n\n"
               "- [[0.5.5 | Meet the Researchers]]\n")
        self.assertNotIn("PHRASE-001", ids(self.ran(doc)))

    def test_the_phrase_in_prose_is_still_caught(self):
        doc = "# Meet the Researchers\n\nMeet the team behind the study.\n"
        self.assertIn("PHRASE-001", ids(self.ran(doc)))

    def test_a_different_h1_is_still_scanned(self):
        doc = "# Meet the Surgeons\n\nProse.\n"
        self.assertIn("PHRASE-001", ids(self.ran(doc)))

    def test_a_link_outside_the_cross_link_block_is_still_scanned(self):
        doc = "# Something Else\n\nSee [[0.5.5 | Meet the Researchers]] for profiles.\n"
        self.assertIn("PHRASE-001", ids(self.ran(doc)))


class JuniorCloserByPageType(unittest.TestCase):
    """The speak to an adult message attaches to symptom content, not to every
    junior page. A careers page has nothing for the reader to report. See
    decision 003."""

    PAGE = ("# Choosing Subjects\n\n"
            "A summary line for the page.\n\n"
            "## For Young Learners\n\n"
            "### What This Is\n\n"
            "Medical schools set their own entry requirements.\n\n"
            "### Key Learning Points\n\n"
            "- One point.\n- Two points.\n- Three points.\n\n"
            "## Explore Further\n\n- [[0.4.2 | Work Experience and Volunteering]]\n\n"
            "## References\n\nNothing is cited.\n")

    def closer_findings(self, page_type):
        brief = {"title": "Choosing Subjects", "page_type": page_type,
                 "tiers_required": ["junior"],
                 "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}
        report = linter.lint(self.PAGE, brief)
        return [f for f in report["findings"]
                if f["rule_id"] == "STRUCT-001" and "closing message" in f["description"]]

    def test_exempt_page_type_does_not_need_the_message(self):
        for page_type in ("careers", "study_skills", "teacher_resource", "assessment"):
            self.assertEqual(self.closer_findings(page_type), [], page_type)

    def test_a_junior_explainer_still_needs_it(self):
        self.assertEqual(len(self.closer_findings("junior_explainer")), 1)


class NoFiguresRule(unittest.TestCase):
    """FIG-001, from decisions 003 and 005. The rule has to catch a measurement and
    has to leave the cross references this site's prose is full of alone."""

    def brief(self, allowed=False):
        return {"title": "Distal Femur", "page_type": "anatomy",
                "tiers_required": ["medical_student"],
                "governance": {"figures_allowed": allowed},
                "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}

    def page(self, sentence):
        return ("# Distal Femur\n\nA summary line.\n\n## For Medical Students\n\n"
                "### Structure and Location\n\n" + sentence + "\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## Explore Further\n\n- [[2.1.1 | Gross Anatomy]]\n\n"
                "## References\n\nNothing is cited. Smith 2019 would be a reference.\n")

    def fired(self, sentence, allowed=False):
        report = linter.lint(self.page(sentence), self.brief(allowed))
        return [f["matched_text"] for f in report["findings"] if f["rule_id"] == "FIG-001"]

    def test_a_measurement_fails(self):
        self.assertTrue(self.fired("The footprint is 17 mm across."))
        self.assertTrue(self.fired("Slope averages 9 degrees."))
        self.assertTrue(self.fired("Around 70% of load passes medially."))
        self.assertTrue(self.fired("The angle is 5.5 degrees."))

    def test_a_page_id_does_not_fail(self):
        self.assertEqual(self.fired("3.13 takes that further, and 2.10.6 owns the nerve."), [])

    def test_a_section_or_decision_reference_does_not_fail(self):
        self.assertEqual(self.fired("Section 7 owns technique and decision 005 the figures."), [])
        self.assertEqual(self.fired("Sections 6 and 7 own the argument."), [])

    def test_prose_list_numbering_does_not_fail(self):
        self.assertEqual(self.fired("Three features matter. 1 shape. 2 size. 3 position."), [])

    def test_a_number_above_the_allowed_integers_fails(self):
        self.assertTrue(self.fired("There are 17 named attachments."))

    def test_a_reference_year_does_not_fail(self):
        """The reference list is outside the body scope, so a citation year is safe."""
        self.assertEqual(self.fired("No figure appears in this sentence."), [])

    def test_the_rule_is_off_when_the_brief_allows_figures(self):
        """Decision 006 lifted the ban for Section 2. FIG-001 still guards Section 0,
        where the figures are entry requirements and no amount of checking fixes them."""
        self.assertEqual(self.fired("The footprint is 17 mm across.", allowed=True), [])

    def test_every_written_section_2_page_passes_it(self):
        """The rule was added after the pages were written. If it disagrees with them,
        one of the two is wrong and this says so."""
        import glob
        pages = sorted(glob.glob(os.path.join(ROOT, "runs", "2.*", "styled_v1.md")))
        self.assertTrue(pages, "no Section 2 pages found")
        for path in pages:
            page_id = os.path.basename(os.path.dirname(path))
            with open(os.path.join(ROOT, "config", "briefs", page_id + ".json")) as fh:
                brief = json.load(fh)
            with open(path) as fh:
                report = linter.lint(fh.read(), brief)
            hits = [f["matched_text"] for f in report["findings"] if f["rule_id"] == "FIG-001"]
            self.assertEqual(hits, [], "%s carries a figure: %s" % (page_id, hits))


class FigureRegister(unittest.TestCase):
    """FIG-002, from decision 006. A figure may be written and must be registered,
    because the client has undertaken to check every one and the list has to be
    generated rather than remembered."""

    BRIEF = {"page_id": "2.9.9", "title": "Test Page", "page_type": "anatomy",
             "tiers_required": ["medical_student"],
             "governance": {"figures_allowed": True},
             "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}

    def page(self, sentence):
        return ("# Test Page\n\nA summary line.\n\n## For Medical Students\n\n"
                "### Structure and Location\n\n" + sentence + "\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## Explore Further\n\n- [[2.1.1 | Gross Anatomy]]\n\n"
                "## References\n\nNothing is cited.\n")

    def run_with(self, sentence, register):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            if register is not None:
                with open(os.path.join(d, "2.9.9.json"), "w") as fh:
                    json.dump({"page_id": "2.9.9", "figures": register}, fh)
            os.environ["FIGURE_REGISTRY_DIR"] = d
            try:
                report = linter.lint(self.page(sentence), self.BRIEF)
            finally:
                os.environ.pop("FIGURE_REGISTRY_DIR", None)
        return [f["description"] for f in report["findings"] if f["rule_id"] == "FIG-002"]

    def entry(self, as_written, **kw):
        e = {"as_written": as_written, "claim": "A sentence.",
             "verification": "UNVERIFIED_FROM_MEMORY"}
        e.update(kw)
        return e

    def test_a_registered_figure_passes(self):
        self.assertEqual(
            self.run_with("The footprint is 17 mm across.", [self.entry("17 mm")]), [])

    def test_an_unregistered_figure_fails(self):
        out = self.run_with("The footprint is 17 mm across.", [])
        self.assertTrue(any("not in the page register" in m for m in out))

    def test_a_page_with_figures_and_no_register_fails(self):
        out = self.run_with("The footprint is 17 mm across.", None)
        self.assertTrue(any("no register" in m for m in out))

    def test_a_page_with_no_figures_needs_no_register(self):
        self.assertEqual(self.run_with("Nothing is measured here.", None), [])

    def test_spacing_does_not_matter(self):
        self.assertEqual(
            self.run_with("The footprint is 17 mm across.", [self.entry("17mm")]), [])

    def test_an_entry_with_no_claim_fails(self):
        out = self.run_with("The footprint is 17 mm across.",
                            [self.entry("17 mm", claim="")])
        self.assertTrue(any("no claim recorded" in m for m in out))

    def test_an_unknown_verification_state_fails(self):
        out = self.run_with("The footprint is 17 mm across.",
                            [self.entry("17 mm", verification="probably fine")])
        self.assertTrue(any("verification state" in m for m in out))

    def test_a_register_entry_the_page_lost_fails_unless_marked_removed(self):
        out = self.run_with("The footprint is 17 mm across.",
                            [self.entry("17 mm"), self.entry("9 mm")])
        self.assertTrue(any("does not carry it" in m for m in out))
        self.assertEqual(
            self.run_with("The footprint is 17 mm across.",
                          [self.entry("17 mm"),
                           self.entry("9 mm", verification="REMOVED")]), [])

    def test_every_written_page_with_figures_has_a_complete_register(self):
        import glob
        checked = 0
        for path in sorted(glob.glob(os.path.join(ROOT, "runs", "*", "styled_v1.md"))):
            page_id = os.path.basename(os.path.dirname(path))
            brief_path = os.path.join(ROOT, "config", "briefs", page_id + ".json")
            if not os.path.exists(brief_path):
                continue
            with open(brief_path) as fh:
                brief = json.load(fh)
            if not (brief.get("governance") or {}).get("figures_allowed"):
                continue
            with open(path) as fh:
                report = linter.lint(fh.read(), brief)
            hits = [f["description"] for f in report["findings"] if f["rule_id"] == "FIG-002"]
            self.assertEqual(hits, [], "%s: %s" % (page_id, hits))
            checked += 1
        self.assertTrue(checked, "no pages with figures allowed were found")


class FigureExtractorEdgeCases(unittest.TestCase):
    """The extractor shared by FIG-001 and FIG-002 has to tell a quantity from the
    cross references this site's prose is full of. These are the cases that have
    actually gone wrong."""

    BRIEF = {"page_id": "2.9.9", "title": "Test Page", "page_type": "anatomy",
             "tiers_required": ["medical_student"],
             "governance": {"figures_allowed": False},
             "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}

    def figures(self, sentence):
        page = ("# Test Page\n\nA summary.\n\n## For Medical Students\n\n"
                "### Structure and Location\n\n" + sentence + "\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## Explore Further\n\n- [[2.1.1 | Gross Anatomy]]\n\n"
                "## References\n\nNothing is cited.\n")
        report = linter.lint(page, self.BRIEF)
        return [f["matched_text"] for f in report["findings"] if f["rule_id"] == "FIG-001"]

    def test_a_section_list_does_not_swallow_a_following_page_id(self):
        """'Section 6 and 7.49' used to leave '.49' behind, and 49 was then read
        as a quantity."""
        self.assertEqual(
            self.figures("Management belongs to Section 6 and 7.49 owns the surgical side."),
            [])

    def test_a_section_list_still_passes_on_its_own(self):
        self.assertEqual(self.figures("Sections 6 and 7 own the argument."), [])

    def test_a_page_id_after_a_chapter_list_is_still_a_page_id(self):
        self.assertEqual(self.figures("Chapters 1, 2 and 3 lead to 10.35 eventually."), [])

    def test_a_quantity_after_a_section_reference_still_fires(self):
        self.assertTrue(self.figures("Section 7 owns it, and the slope is 9 degrees."))


class RangesAndRepeats(unittest.TestCase):
    """A range is one figure and a repeated figure is one thing to check. Both were
    wrong in the first register and both are extractor behaviour, so they are
    tested here rather than in the tool."""

    RULE = {"id": "FIG-001", "severity": "fail", "description": "d",
            "allowed_bare_integers": list(range(1, 11))}

    def extract(self, sentence):
        page = ("# Test\n\nA summary.\n\n## For Medical Students\n\n"
                "### Structure and Location\n\n" + sentence + "\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## References\n\nNothing.\n")
        doc = linter.Document(page, linter.load_article_template())
        return [t for t, a, b, c in linter.body_figures(doc, self.RULE)]

    def test_a_range_is_one_figure(self):
        self.assertEqual(self.extract("Engagement is at 20 to 30 degrees."),
                         ["20 to 30 degrees"])

    def test_a_range_with_single_digit_bounds_is_one_figure(self):
        """'5 to 7 degrees' used to register only '7 degrees', because 5 is an
        allowed bare integer. A lone bound tells a reviewer nothing."""
        self.assertEqual(self.extract("Valgus is 5 to 7 degrees."), ["5 to 7 degrees"])

    def test_two_separate_figures_are_not_merged_into_a_range(self):
        self.assertEqual(
            self.extract("About 14 degrees in men and 17 degrees in women."),
            ["14 degrees", "17 degrees"])

    def test_figures_come_back_in_document_order(self):
        self.assertEqual(
            self.extract("First 17 mm, then 20 to 30 degrees, then 60 per cent."),
            ["17 mm", "20 to 30 degrees", "60 per cent"])

    def test_a_repeated_figure_is_reported_at_each_occurrence(self):
        """The gate wants both line numbers; the register deduplicates."""
        self.assertEqual(self.extract("It is 17 mm. Again, 17 mm."), ["17 mm", "17 mm"])
