"""The architecture and the handbook are configuration, not code, and both
arrived after the pipeline was built. These tests hold the join between them.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "functions", "style_lint"))
import linter  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "tools"))
import architecture  # noqa: E402


def load(*parts):
    with open(os.path.join(ROOT, "config", *parts)) as fh:
        return json.load(fh)


class PageTypeMap(unittest.TestCase):
    def setUp(self):
        self.map = load("page_type_map.json")["page_types"]
        self.template = load("article_template.json")
        with open(os.path.join(ROOT, "config", "architecture", "pages_0_to_3.json")) as fh:
            self.pages = json.load(fh)

    def test_every_architecture_page_type_is_mapped(self):
        used = set(p["page_type"] for p in self.pages)
        self.assertEqual(used - set(self.map), set())

    def test_every_mapping_targets_a_real_template(self):
        defined = set(self.template["page_types"])
        for name, entry in self.map.items():
            self.assertIn(entry["template"], defined, "%s maps to a template that does not exist" % name)

    def test_resolver_agrees_with_the_map(self):
        for name, entry in self.map.items():
            self.assertEqual(linter.resolve_template(name), entry["template"])

    def test_every_page_id_is_unique(self):
        ids = [p["page_id"] for p in self.pages]
        self.assertEqual(len(ids), len(set(ids)))

    def test_sibling_and_deeper_references_are_well_formed(self):
        for p in self.pages:
            for ref in p["siblings"]:
                self.assertRegex(ref, r"^\d+(\.\d+)*$", "%s has a malformed sibling" % p["page_id"])


class GeneratedBrief(unittest.TestCase):
    """A brief generated from the architecture must pass the validator and the
    structure rule it feeds."""

    @classmethod
    def setUpClass(cls):
        import types
        if "boto3" not in sys.modules:
            m = types.ModuleType("boto3")
            m.client = lambda *a, **k: None
            m.resource = lambda *a, **k: None
            sys.modules["boto3"] = m
        sys.path.insert(0, os.path.join(ROOT, "layers", "common", "python"))

    def generate(self, page_id):
        out = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        out.close()
        subprocess.check_output([sys.executable, os.path.join(REPO, "tools", "architecture.py"),
                                 "brief", page_id, "--out", out.name], cwd=REPO)
        with open(out.name) as fh:
            brief = json.load(fh)
        os.unlink(out.name)
        return brief

    def test_a_generated_brief_validates(self):
        from kneeschool_common import brief as rules
        b = self.generate("1.2.3")
        self.assertIs(rules.validate(b), b)

    def test_a_generated_brief_carries_the_architecture_exclusions(self):
        b = self.generate("1.2.3")
        joined = " ".join(b["scope"]["must_not_cover"])
        self.assertIn("2.5.7", joined)
        self.assertIn("5.6.2", joined)
        self.assertGreaterEqual(len(b["scope"]["must_not_cover"]), 7)

    def test_a_junior_page_forces_the_commercial_ban(self):
        b = self.generate("0.1.1")
        self.assertTrue(b["governance"]["junior_tier_present"])
        self.assertFalse(b["governance"]["commercial_content_allowed"])


class StructureRule(unittest.TestCase):
    """The handbook's rulings, asserted rather than assumed."""

    def setUp(self):
        # A short probe document, so the word count is overridden rather than
        # failing every case for being 41 words long.
        self.brief = {"tiers_required": ["patient"], "page_type": "anatomy",
                      "output_requirements": {"target_word_count": {"min": 0, "max": 100000}}}

    def ids(self, doc):
        return [f["description"] for f in linter.lint(doc, self.brief)["findings"]]

    def body(self, heading="For Patients", extras=""):
        return ("# T\n\nSummary.\n\n## %s\n\n### Structure and Location\n\nThe knee bends.\n\n"
                "### Key Learning Points\n\n- one\n- two\n- three\n\n"
                "### Frequently Asked Questions\n\n**Q.** A?\nYes.\n\n**Q.** B?\nYes.\n\n"
                "**Q.** C?\nYes.\n\nSeek advice if the knee gives way.\n\n"
                "## Explore Further\n\n- [[1.2.1 | Bones]]\n%s" % (heading, extras))

    def test_a_correct_patient_block_passes(self):
        self.assertTrue(linter.lint(self.body(), self.brief)["pass"])

    def test_a_wrong_tier_heading_is_reported(self):
        found = " ".join(self.ids(self.body(heading="Patient")))
        self.assertIn("the handbook requires the exact heading", found)

    def test_a_missing_explore_further_is_reported(self):
        doc = self.body().split("## Explore Further")[0]
        self.assertIn("no 'Explore Further' section", " ".join(self.ids(doc)))

    def test_a_per_tier_reference_list_is_reported(self):
        doc = self.body().replace("### Frequently Asked Questions",
                                  "### References\n\n1. Smith J. Title. 2020.\n\n### Frequently Asked Questions")
        self.assertIn("article level list only", " ".join(self.ids(doc)))

    def test_a_section_out_of_template_order_is_reported(self):
        doc = self.body().replace("### Structure and Location\n\nThe knee bends.",
                                  "### Function\n\nIt bends.\n\n### Structure and Location\n\nThe knee bends.")
        self.assertIn("out of the order", " ".join(self.ids(doc)))

    def test_a_section_outside_the_page_template_is_reported(self):
        doc = self.body().replace("### Structure and Location",
                                  "### Operative Technique")
        self.assertIn("not in the anatomy page template", " ".join(self.ids(doc)))

    def test_controversies_below_frcs_is_reported(self):
        brief = {"tiers_required": ["patient"], "page_type": "condition",
                 "output_requirements": {"target_word_count": {"min": 0, "max": 100000}}}
        doc = ("# T\n\nSummary.\n\n## For Patients\n\n### Definition\n\nA knee problem.\n\n"
               "### Controversies and Evidence\n\nOpinions differ.\n\n"
               "### Key Learning Points\n\n- one\n- two\n- three\n\n"
               "### Frequently Asked Questions\n\n**Q.** A?\nYes.\n\n**Q.** B?\nYes.\n\n"
               "**Q.** C?\nYes.\n\nSeek advice if it gives way.\n\n"
               "## Explore Further\n\n- [[6.1.2 | PCL]]\n")
        found = " ".join(f["description"] for f in linter.lint(doc, brief)["findings"])
        self.assertIn("restricts to frcs and above", found)


class TrackerSeed(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "config", "architecture", "tracker_seed.json")) as fh:
            self.items = json.load(fh)

    def test_one_row_per_architecture_page(self):
        with open(os.path.join(ROOT, "config", "architecture", "pages_0_to_3.json")) as fh:
            self.assertEqual(len(self.items), len(json.load(fh)))

    def test_queue_runs_high_then_medium_then_low(self):
        bands = [{"high": 0, "medium": 1, "low": 2}[i["priority"]] for i in self.items]
        self.assertEqual(bands, sorted(bands))

    def test_queue_positions_are_contiguous(self):
        self.assertEqual([i["queue_position"] for i in self.items],
                         list(range(1, len(self.items) + 1)))

    def test_every_row_starts_unbuilt(self):
        for i in self.items:
            self.assertEqual(i["draft_status"], "not_started")


if __name__ == "__main__":
    unittest.main()


class DecisionZeroZeroThreeTemplates(unittest.TestCase):
    """The four Section 0 templates added by decision 003."""

    NAMES = ("careers", "study_skills", "teacher_resource", "assessment")

    def setUp(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(here, "config", "article_template.json")) as fh:
            self.tpl = json.load(fh)
        with open(os.path.join(here, "config", "page_type_map.json")) as fh:
            self.map = json.load(fh)["page_types"]

    def test_each_type_resolves_to_its_own_template(self):
        for name in self.NAMES:
            self.assertEqual(self.map[name]["template"], name)
            self.assertFalse(self.map[name]["variant_pending"], name)
            self.assertIn(name, self.tpl["page_types"], name)

    def test_every_body_section_has_a_heading(self):
        headings = self.tpl["body_section_headings"]
        for name in self.NAMES:
            for slug in self.tpl["page_types"][name]["body_sections"]:
                self.assertIn(slug, headings, "%s/%s" % (name, slug))

    def test_heading_slugifies_back_to_its_slug(self):
        """The gate slugifies a heading and compares it with the template's list.
        If the two directions disagree, every page of that type fails STRUCT-001."""
        headings = self.tpl["body_section_headings"]
        for slug, heading in headings.items():
            self.assertEqual(linter.slugify(linter.normalise_title(heading)), slug)

    def test_these_types_are_marked_as_not_from_the_handbook(self):
        self.assertIn("decision 003", self.tpl["local_additions_note"].lower())
        for name in self.NAMES:
            self.assertEqual(self.tpl["page_types"][name]["source_of_truth"], "decision 003")


class FaqAllowance(unittest.TestCase):
    """Decision 002 amendment: the patient tier's FAQ block gets its own room."""

    def test_patient_tier_raises_the_maximum(self):
        band = architecture.scale_for_tiers({"min": 500, "max": 1200}, ["junior"])
        self.assertEqual(band, {"min": 350, "max": 900})
        band = architecture.scale_for_tiers({"min": 500, "max": 1200}, ["patient"])
        self.assertEqual(band, {"min": 350, "max": 900 + architecture.FAQ_ALLOWANCE})

    def test_the_minimum_does_not_move(self):
        a = architecture.scale_for_tiers({"min": 500, "max": 1200}, ["junior"])
        b = architecture.scale_for_tiers({"min": 500, "max": 1200}, ["patient"])
        self.assertEqual(a["min"], b["min"])
