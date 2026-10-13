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

    def test_commercial_rule_allows_the_architectures_own_title(self):
        """The architecture names 4.22.7 'Sportshealing Knee Score'.

        The rule banned that page's own title on its own page, and banned the
        correct cross link label on every page pointing at it. A drafter cannot
        reword either without breaking the brief or the link, so both are out of
        scope and prose is not.
        """
        doc = ("# Sportshealing Knee Score\n\nSummary.\n\n## For Patients\n\n"
               "The knee is a hinge joint of the lower limb.\n\n"
               "## Explore Further\n\n- [[4.22.7 | Sportshealing Knee Score]]\n")
        brief = {"tiers_required": ["patient"], "title": "Sportshealing Knee Score",
                 "governance": {"commercial_content_allowed": False}}
        self.assertNotIn("GOV-001", ids(linter.lint(doc, brief)))

    def test_commercial_rule_still_catches_the_term_in_prose(self):
        doc = ("# Sportshealing Knee Score\n\nSummary.\n\n## For Patients\n\n"
               "The Sportshealing clinic scores the knee.\n")
        brief = {"tiers_required": ["patient"], "title": "Sportshealing Knee Score",
                 "governance": {"commercial_content_allowed": False}}
        matched = [f["matched_text"] for f in linter.lint(doc, brief)["findings"]
                   if f["rule_id"] == "GOV-001"]
        self.assertEqual(matched, ["Sportshealing"])

    def test_commercial_rule_still_catches_a_different_title(self):
        """Only the page's own architecture title is out of scope."""
        doc = ("# Something Else\n\nSummary.\n\n## For Patients\n\n"
               "The knee bends.\n\n## Explore Further\n\n- [[1.1.1 | A]]\n")
        brief = {"tiers_required": ["patient"], "title": "Sportshealing Knee Score",
                 "governance": {"commercial_content_allowed": False}}
        self.assertNotIn("GOV-001", ids(linter.lint(doc, brief)))

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


class PositionRegister(unittest.TestCase):
    """POS-001, from decision 007. A sentence telling a clinician what to do is
    registered for sign off. Warn severity, because the detector is a heuristic and
    a false positive must not be able to block a page."""

    def brief(self, tiers=("mrcs",)):
        return {"page_id": "2.9.9", "title": "Test Page", "page_type": "anatomy",
                "tiers_required": list(tiers),
                "governance": {"figures_allowed": True},
                "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}

    def page(self, sentence, tier="MRCS Level"):
        return ("# Test Page\n\nA summary.\n\n## %s\n\n"
                "### Structure and Location\n\n" % tier + sentence + "\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## Explore Further\n\n- [[2.1.1 | Gross Anatomy]]\n\n"
                "## References\n\nNothing is cited.\n")

    def fired(self, sentence, register=None, tiers=("mrcs",), tier="MRCS Level"):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            if register is not None:
                with open(os.path.join(d, "2.9.9.json"), "w") as fh:
                    json.dump({"page_id": "2.9.9", "positions": register}, fh)
            os.environ["POSITION_REGISTRY_DIR"] = d
            try:
                report = linter.lint(self.page(sentence, tier), self.brief(tiers))
            finally:
                os.environ.pop("POSITION_REGISTRY_DIR", None)
        return [f for f in report["findings"] if f["rule_id"] == "POS-001"]

    def test_an_unregistered_imperative_warns(self):
        out = self.fired("Document dorsiflexion before and after any lateral procedure.")
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["severity"], "warn")

    def test_an_imperative_after_a_leading_clause_warns(self):
        self.assertTrue(self.fired(
            "In a young patient with instability, prefer the procedure that preserves bone."))

    def test_a_directed_modal_warns(self):
        self.assertTrue(self.fired(
            "For posterolateral access the nerve should be identified, not estimated."))

    def test_a_registered_position_does_not_warn(self):
        sentence = "Document dorsiflexion before and after any lateral procedure."
        self.assertEqual(self.fired(sentence, [{"as_written": sentence}]), [])

    def test_whitespace_differences_do_not_matter(self):
        sentence = "Document dorsiflexion before and after any lateral procedure."
        self.assertEqual(
            self.fired(sentence, [{"as_written": "Document  dorsiflexion before and after "
                                                 "any lateral procedure."}]), [])

    def test_plain_description_does_not_warn(self):
        self.assertEqual(self.fired(
            "The popliteal artery lies on the capsule behind the distal femur."), [])

    def test_a_note_about_the_build_registers_does_not_warn(self):
        self.assertEqual(self.fired(
            "Decision 006 records why, and a reviewer should add them to the register."), [])

    def test_a_page_with_no_professional_tier_is_out_of_scope(self):
        """A junior page gives no clinical direction to a clinician."""
        self.assertEqual(self.fired("Assess the knee before any sport.",
                                    tiers=("junior",), tier="For Young Learners"), [])

    def test_it_never_fails_a_page(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            os.environ["POSITION_REGISTRY_DIR"] = d
            try:
                report = linter.lint(
                    self.page("Document dorsiflexion before and after any procedure."),
                    self.brief())
            finally:
                os.environ.pop("POSITION_REGISTRY_DIR", None)
        self.assertTrue(report["pass"], "POS-001 must not be able to block a page")

    def test_every_written_professional_page_is_fully_registered(self):
        import glob
        checked = 0
        for path in sorted(glob.glob(os.path.join(ROOT, "runs", "*", "styled_v1.md"))):
            page_id = os.path.basename(os.path.dirname(path))
            brief_path = os.path.join(ROOT, "config", "briefs", page_id + ".json")
            if not os.path.exists(brief_path):
                continue
            with open(brief_path) as fh:
                brief = json.load(fh)
            if not set(brief.get("tiers_required") or []) & set(linter.PROFESSIONAL_TIERS):
                continue
            with open(path) as fh:
                report = linter.lint(fh.read(), brief)
            hits = [f["matched_text"] for f in report["findings"] if f["rule_id"] == "POS-001"]
            self.assertEqual(hits, [], "%s: unregistered position %s" % (page_id, hits))
            checked += 1
        self.assertTrue(checked, "no professional pages found")


class BalanceVerbs(unittest.TestCase):
    """Decision 018. The consultant tier is a balance argument, and a balance
    argument opens with a different verb from a directive one. POS-001's opener
    list was built from directive prose and caught almost none of it. A dry run
    across every professional page found 163 clinical directions that had never
    reached the register, so the gap was not specific to the consultant tier."""

    def opens(self, sentence):
        return bool(linter.POSITION_OPENER.search(sentence))

    def test_weighing_verbs_are_detected(self):
        for sentence in [
                "Weigh the stiffness risk of early combined surgery against the laxity risk.",
                "Stage the corner before any cruciate reconstruction in a knee with lateral findings.",
                "Correct varus alignment where it would load a corner reconstruction.",
                "Offer a cane in the opposite hand for medial compartment pain.",
                "Confirm the femoral point radiographically whichever attachment is used.",
                "Grade by the opening and the endpoint rather than by the pain.",
                "Compare thickness with the contralateral knee where a study is available.",
                "Decide repairability from whether the tension path can be restored.",
                "Add a lateral procedure where the grade or the population indicates it.",
                "Reserve the osteotomy for the knee that has already failed once.",
                "Defer the decision until the slope has been measured.",
                "Limit the construct to what the tunnels will take.",
        ]:
            self.assertTrue(self.opens(sentence), sentence)

    def test_a_leading_clause_still_works_with_the_new_verbs(self):
        self.assertTrue(self.opens(
            "In revision, grade the tibial bone and the tunnel position preoperatively."))

    def test_the_verb_must_open_the_sentence(self):
        # Anchored, as before: a weighing verb used mid sentence is description.
        self.assertFalse(self.opens(
            "The surgeon will weigh the stiffness risk against the laxity risk."))
        self.assertFalse(self.opens(
            "Most departments correct alignment at the same sitting."))


class ConsultantTierIntent(unittest.TestCase):
    """Decision 018 put the tier intents in the template so the generator reads
    them instead of remembering them. The template is the source of truth, so the
    test is against the file and not against a copy of the rule."""

    def setUp(self):
        with open(os.path.join(ROOT, "config", "article_template.json")) as fh:
            self.template = json.load(fh)

    def test_every_tier_has_an_intent(self):
        intent = self.template["tier_intent"]
        for tier in self.template["tier_order"]:
            self.assertIn(tier, intent, tier)

    def test_the_intent_block_adds_no_tier_of_its_own(self):
        extra = set(self.template["tier_intent"]) - set(self.template["tier_order"]) - {"source"}
        self.assertEqual(extra, set())

    def test_the_consultant_intent_carries_the_rule(self):
        c = self.template["tier_intent"]["consultant"]
        self.assertEqual(len(c["required"]), 6)
        self.assertEqual(len(c["forbidden"]), 3)
        self.assertIn("balance argument", c["objective"])
        self.assertIn("permitted", c)

    def test_the_decision_is_recorded(self):
        path = os.path.join(os.path.dirname(ROOT), "docs", "decisions",
                            "018-what-the-consultant-tier-is-for.md")
        self.assertTrue(os.path.exists(path), path)


class PatientFactors(unittest.TestCase):
    """DEC-001, from decision 019. A consultant block that frames a clinical
    decision names all five patient factors. Warn severity, because keyword
    matching can be satisfied by a passing mention: the rule catches the
    omission, not the treatment."""

    FIVE = ("Age and physiology, where healing and tissue quality sit. "
            "Medical comorbidities, because diabetes and smoking change operative risk. "
            "The demands the patient puts on the knee, which is occupation and sport. "
            "Psychological state, because fear of reinjury governs what the knee is used for. "
            "The patient's own ideas, concerns and expectations.")

    def brief(self, tiers=("frcs", "consultant")):
        return {"page_id": "9.9.9", "title": "Test Page", "page_type": "biomechanics",
                "tiers_required": list(tiers),
                "governance": {"figures_allowed": True},
                "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}

    def page(self, consultant_body):
        return ("# Test Page\n\nA summary.\n\n"
                "## FRCS Level\n\n### The Principle\n\nSomething mechanical happens here.\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## Consultant Perspective\n\n### Clinical Relevance\n\n"
                + consultant_body + "\n\n"
                "### Key Learning Points\n\n- One.\n- Two.\n- Three.\n\n"
                "## Explore Further\n\n- [[2.1.1 | Gross Anatomy]]\n\n"
                "## References\n\nNothing is cited.\n")

    def missing(self, consultant_body, tiers=("frcs", "consultant")):
        report = linter.lint(self.page(consultant_body), self.brief(tiers))
        return sorted(f["matched_text"] for f in report["findings"]
                      if f["rule_id"] == "DEC-001")

    def test_a_directive_block_naming_none_of_them_warns_five_times(self):
        out = self.missing("Weigh the construct against the osteotomy in every revision knee.")
        self.assertEqual(len(out), 5)

    def test_the_findings_warn_rather_than_fail(self):
        report = linter.lint(
            self.page("Weigh the construct against the osteotomy in every revision knee."),
            self.brief())
        sev = {f["severity"] for f in report["findings"] if f["rule_id"] == "DEC-001"}
        self.assertEqual(sev, {"warn"})
        self.assertTrue(report["pass"])

    def test_a_block_naming_all_five_is_clean(self):
        body = "Weigh the construct against the osteotomy. " + self.FIVE
        self.assertEqual(self.missing(body), [])

    def test_one_absent_factor_is_named(self):
        body = ("Weigh the construct against the osteotomy. "
                "Age and physiology, where healing sits. "
                "The demands the patient puts on the knee, which is occupation and sport. "
                "Psychological state, because fear of reinjury governs use. "
                "The patient's own ideas, concerns and expectations.")
        self.assertEqual(self.missing(body), ["comorbidities"])

    def test_a_block_with_no_clinical_direction_is_out_of_scope(self):
        # 3.1.7's consultant block weighs a teaching decision. There is no patient
        # in it, and the rule leaves it alone without an exemption list.
        body = ("The decision a department faces is how much caveat to attach to a number "
                "before the caveat becomes the lesson. What moves the weight is whether the "
                "figure is load bearing.")
        self.assertEqual(self.missing(body), [])

    def test_a_page_without_a_consultant_tier_is_out_of_scope(self):
        body = "Weigh the construct against the osteotomy in every revision knee."
        self.assertEqual(self.missing(body, tiers=("frcs", "fellowship")), [])

    def test_the_factors_come_from_the_template(self):
        with open(os.path.join(ROOT, "config", "article_template.json")) as fh:
            cfg = json.load(fh)["decision_factors"]
        keys = [f["key"] for f in cfg["factors"]]
        self.assertEqual(keys, ["age_and_physiology", "comorbidities", "knee_demand",
                                "psychological_state", "ideas_concerns_expectations"])
        for factor in cfg["factors"]:
            self.assertTrue(factor["keywords"], factor["key"])

    def test_consultation_verbs_are_clinical_direction(self):
        for sentence in [
                "Take all five explicitly rather than by impression, and counsel against them.",
                "Counsel honestly about what the operation will and will not deliver.",
                "Elicit the patient's expectations before offering the augmentation.",
                "Record the demands the patient puts on the knee before choosing.",
        ]:
            self.assertTrue(linter.POSITION_OPENER.search(sentence), sentence)


class EveryConsultantBlockOnTheSite(unittest.TestCase):
    """Decisions 018 and 019 against the real pages rather than fixtures. There
    are three consultant blocks on the site and all three are checked."""

    def test_no_consultant_block_is_missing_a_patient_factor(self):
        checked = 0
        for page_id in sorted(os.listdir(os.path.join(ROOT, "runs"))):
            brief_path = os.path.join(ROOT, "config", "briefs", "%s.json" % page_id)
            page_path = os.path.join(ROOT, "runs", page_id, "styled_v1.md")
            if not (os.path.exists(brief_path) and os.path.exists(page_path)):
                continue
            with open(brief_path) as fh:
                brief = json.load(fh)
            if "consultant" not in (brief.get("tiers_required") or []):
                continue
            with open(page_path) as fh:
                report = linter.lint(fh.read(), brief)
            absent = [f["matched_text"] for f in report["findings"]
                      if f["rule_id"] == "DEC-001"]
            self.assertEqual(absent, [], "%s: %s" % (page_id, absent))
            checked += 1
        self.assertTrue(checked, "no consultant blocks found")


class SectionTierRules(unittest.TestCase):
    """Decision 020. Which tiers may carry a body section now comes from the
    template, as either an explicit allow list or a floor. It was a dict
    hardcoded in linter.py holding only floors, and a floor cannot express
    'FRCS and consultant but not fellowship'."""

    def setUp(self):
        with open(os.path.join(ROOT, "config", "article_template.json")) as fh:
            self.template = json.load(fh)
        self.order = self.template["tier_order"]

    def allowed(self, slug):
        return linter.section_tiers_allowed(slug, self.template, self.order)

    def test_controversies_skip_fellowship(self):
        self.assertEqual(self.allowed("controversies_and_evidence"),
                         {"frcs", "consultant"})

    def test_a_floor_still_expands_upwards(self):
        self.assertEqual(self.allowed("variations_and_controversies"),
                         {"fellowship", "consultant"})

    def test_an_unlisted_section_has_no_limit(self):
        self.assertIsNone(self.allowed("management_overview"))

    def test_the_fallback_holds_without_the_template_block(self):
        # If the template ever loses section_tier_rules the gate must not go
        # quiet. The fallback is the handbook's original floor.
        bare = {"tier_order": self.order}
        self.assertEqual(
            linter.section_tiers_allowed("controversies_and_evidence", bare, self.order),
            {"frcs", "fellowship", "consultant"})

    def test_the_condition_page_rule_points_at_the_config(self):
        rule = self.template["page_types"]["condition"]["body_sections_rule"]
        self.assertIn("section_tier_rules", rule)


class AbsentIsNotFalse(unittest.TestCase):
    """A conditional rule applies only when the brief states the condition.

    FIG-001 is conditional on `figures_allowed == false`, and the evaluator read
    a missing key as false. Seventeen briefs had never said anything about
    figures, having been generated before the generator set the key, so they
    silently acquired a rule written for Section 0's fees and entry
    requirements. One of them, 1.1.3, carries flexion angles and sat published
    with eight failures that no per chapter run ever looked at. Worse, FIG-002 is
    conditional on the same key being true, so those measurements were in
    neither gate and in no register. Decision 021."""

    def brief(self, governance):
        return {"page_id": "9.9.9", "title": "T", "page_type": "anatomy",
                "tiers_required": ["mrcs"], "governance": governance,
                "output_requirements": {"target_word_count": {"min": 1, "max": 9000}}}

    def test_an_absent_key_satisfies_neither_polarity(self):
        b = self.brief({})
        self.assertFalse(linter.condition_met("brief.governance.figures_allowed == false", b))
        self.assertFalse(linter.condition_met("brief.governance.figures_allowed == true", b))

    def test_an_explicit_false_still_matches(self):
        b = self.brief({"figures_allowed": False})
        self.assertTrue(linter.condition_met("brief.governance.figures_allowed == false", b))
        self.assertFalse(linter.condition_met("brief.governance.figures_allowed == true", b))

    def test_an_explicit_true_still_matches(self):
        b = self.brief({"figures_allowed": True})
        self.assertTrue(linter.condition_met("brief.governance.figures_allowed == true", b))
        self.assertFalse(linter.condition_met("brief.governance.figures_allowed == false", b))

    def test_a_null_is_treated_as_absent(self):
        b = self.brief({"figures_allowed": None})
        self.assertFalse(linter.condition_met("brief.governance.figures_allowed == false", b))
        self.assertFalse(linter.condition_met("brief.governance.figures_allowed == true", b))

    def test_a_missing_parent_does_not_match(self):
        self.assertFalse(linter.condition_met(
            "brief.governance.figures_allowed == false", {"page_id": "9.9.9"}))

    def test_no_condition_always_applies(self):
        self.assertTrue(linter.condition_met(None, {}))
        self.assertTrue(linter.condition_met("", {}))


class EveryBriefDeclaresItsGovernance(unittest.TestCase):
    """The fix above stops a silent brief acquiring a rule. This stops a brief
    being silent, which is the fault one layer down: the seventeen were stale
    rather than deliberate, and nothing noticed for days."""

    REQUIRED = ("commercial_content_allowed", "clinical_advice_allowed",
                "junior_tier_present", "figures_allowed")

    def test_every_brief_states_every_governance_key(self):
        briefs = os.path.join(ROOT, "config", "briefs")
        missing = []
        for name in sorted(os.listdir(briefs)):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(briefs, name)) as fh:
                gov = json.load(fh).get("governance") or {}
            for key in self.REQUIRED:
                if key not in gov or gov[key] is None:
                    missing.append("%s: %s" % (name[:-5], key))
        self.assertEqual(missing, [])


class FabricableCitationDetail(unittest.TestCase):
    """ATTR-001, decision 022. The rule that stands in for source access.

    A landmark papers page may name the author a study is taught under and the
    decade. The year, the journal, the volume, the page, the DOI and the et al
    form are the parts that get invented, and they are refused at the gate.
    """

    BRIEF = {"page_id": "3.17.1", "page_type": "landmark_papers",
             "tiers_required": ["frcs", "fellowship", "consultant"]}

    def fire(self, text, brief=None):
        rule = next(r for r in linter.load_rules()["rules"] if r["id"] == "ATTR-001")
        doc = linter.Document(text, linter.load_article_template())
        return linter.rule_attr_001(doc, rule, brief or self.BRIEF)

    def test_a_decade_is_allowed(self):
        self.assertEqual(self.fire("Girgis and colleagues described it in the 1970s."), [])

    def test_an_exact_year_is_refused(self):
        found = self.fire("Girgis and colleagues described it in 1975.")
        self.assertEqual(len(found), 1)
        self.assertIn("an exact year", found[0]["description"])

    def test_et_al_is_refused(self):
        self.assertTrue(self.fire("Girgis et al described the bundles."))

    def test_a_journal_abbreviation_is_refused(self):
        self.assertTrue(self.fire("The work appeared in Am J Sports Med."))

    def test_a_volume_and_page_is_refused(self):
        self.assertTrue(self.fire("See 58(2):159 for the series."))

    def test_a_doi_is_refused(self):
        self.assertTrue(self.fire("Available at doi:10.1000/example."))

    def test_the_reference_note_is_in_scope(self):
        """A citation hidden in the reference note is the failure the rule exists
        for, so the scan covers the whole document rather than the body."""
        text = "# A page\n\nSummary.\n\n## References\n\nSee the 1975 paper.\n"
        self.assertTrue(self.fire(text))

    def test_other_page_types_keep_their_dates(self):
        """3.1.7 Historical Development is a page of real years. Scoping by page
        type is what lets this rule exist without an exemption list."""
        brief = dict(self.BRIEF, page_type="biomechanics")
        self.assertEqual(self.fire("The first rig was built in 1975.", brief), [])


class AttributionsAreRegistered(unittest.TestCase):
    """ATTR-002 and the detector behind it, decision 022."""

    def names(self, text):
        return linter.attributed_names(text)

    def test_a_single_surname(self):
        self.assertEqual(self.names("Noyes measured the failure load."), ["Noyes"])

    def test_a_pair(self):
        self.assertEqual(self.names("Race and Amis tested the construct."),
                         ["Race and Amis"])

    def test_a_comma_list_is_one_attribution(self):
        """The first version of this detector split on whitespace and lost the
        whole phrase, so 'Butler, Noyes and Grood' registered as nothing."""
        self.assertEqual(self.names("Butler, Noyes and Grood ran the study."),
                         ["Butler, Noyes and Grood"])

    def test_and_colleagues(self):
        self.assertEqual(self.names("Girgis and colleagues described the bundles."),
                         ["Girgis and colleagues"])

    def test_the_work_of_form(self):
        self.assertEqual(self.names("The work of Markolf measured force directly."),
                         ["Markolf"])

    def test_a_name_with_an_internal_capital(self):
        """[A-Z][a-z]{2,} could not match McMurray, so 4.24.3 attributed the test
        to him in its own first sentence and the register recorded nothing. The
        same shape had been losing LaPrade from three pages of chapter 3.17 since
        that chapter was published."""
        self.assertEqual(self.names("McMurray described the manoeuvre."),
                         ["McMurray"])
        self.assertEqual(self.names("Galway and MacIntosh described it."),
                         ["Galway and MacIntosh"])
        self.assertEqual(self.names("LaPrade and colleagues sectioned the corner."),
                         ["LaPrade and colleagues"])

    def test_a_hyphenated_name(self):
        self.assertEqual(self.names("Barber-Westin and Noyes reported the battery."),
                         ["Barber-Westin and Noyes"])

    def test_a_name_with_an_apostrophe(self):
        """3.17.8 recorded 'Connor' for 'Goodfellow and O'Connor', which is a
        miss and a mangling in one entry."""
        self.assertEqual(self.names("Goodfellow and O'Connor described the motion."),
                         ["Goodfellow and O'Connor"])

    def test_a_subject_that_is_not_a_person(self):
        self.assertEqual(self.names("Cadaveric work showed the restraint."), [])

    def test_a_capitalised_common_noun_opener_is_not_an_author(self):
        """Chapter 4.24 produced three of these in one chapter: Patient reported
        instruments, Translation measured alone, Symmetry measured against a
        changed limb. Each registered as an author."""
        self.assertEqual(self.names("Patient reported instruments were developed."), [])
        self.assertEqual(self.names("Symmetry measured against a limb misleads."), [])
        self.assertEqual(self.names("Translation measured alone was demoted."), [])

    def test_an_imperative_opener_is_not_an_author(self):
        """'Treat quantified positions as targets' registered as a study by
        somebody called Treat on the first extraction of 3.17.4. The openers come
        from POS-001's verb list so the two cannot drift apart."""
        self.assertEqual(self.names("Treat quantified positions as targets."), [])
        self.assertEqual(self.names("Read measured laxity with its angle."), [])

    def test_the_register_satisfies_the_rule(self):
        rule = next(r for r in linter.load_rules()["rules"] if r["id"] == "ATTR-002")
        text = "# A page\n\n## FRCS Level\n\n### What Was Done\n\nNoyes measured it.\n"
        doc = linter.Document(text, linter.load_article_template())
        brief = {"page_id": "no-such-page", "page_type": "landmark_papers"}
        self.assertTrue(linter.rule_attr_002(doc, rule, brief))


class EveryLandmarkPageOnTheSite(unittest.TestCase):
    """Decision 022 against the real pages rather than fixtures.

    The chapter names roughly fifty studies. One fabricable detail anywhere in it
    is the handbook's critical failure, so this runs the gate over every landmark
    papers page that exists.
    """

    def pages(self):
        for page_id in sorted(os.listdir(os.path.join(ROOT, "runs"))):
            brief_path = os.path.join(ROOT, "config", "briefs", "%s.json" % page_id)
            page_path = os.path.join(ROOT, "runs", page_id, "styled_v1.md")
            if not (os.path.exists(brief_path) and os.path.exists(page_path)):
                continue
            with open(brief_path) as fh:
                brief = json.load(fh)
            if brief.get("page_type") != "landmark_papers":
                continue
            with open(page_path) as fh:
                yield page_id, brief, fh.read()

    def test_no_page_carries_a_fabricable_citation_detail(self):
        checked, bad = 0, []
        for page_id, brief, text in self.pages():
            report = linter.lint(text, brief)
            bad += ["%s: %s" % (page_id, f["matched_text"]) for f in report["findings"]
                    if f["rule_id"] == "ATTR-001"]
            checked += 1
        self.assertEqual(bad, [])
        self.assertTrue(checked, "no landmark papers pages found")

    def test_every_attribution_is_in_a_register(self):
        unregistered = []
        for page_id, brief, text in self.pages():
            report = linter.lint(text, brief)
            unregistered += ["%s: %s" % (page_id, f["matched_text"])
                             for f in report["findings"] if f["rule_id"] == "ATTR-002"]
        self.assertEqual(unregistered, [])
