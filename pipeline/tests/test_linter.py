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
