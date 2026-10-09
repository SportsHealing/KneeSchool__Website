"""The architecture and the handbook are configuration, not code, and both
arrived after the pipeline was built. These tests hold the join between them.
"""

import json
import os
import re
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
            # the string carries a revision date as well, so match on the decision
            self.assertIn("decision 003",
                          self.tpl["page_types"][name]["source_of_truth"])


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


class RevisedOrders(unittest.TestCase):
    """The orders confirmed on 7 October 2026. These carry into sections 10 to 15,
    so a silent change to one of them is worth catching."""

    EXPECTED = {
        "careers": ["what_the_work_involves", "the_people_who_do_it", "the_route",
                    "what_it_takes", "where_to_find_out_more"],
        "study_skills": ["what_this_is", "how_it_works", "how_to_prepare",
                         "common_mistakes", "where_to_find_out_more"],
        "teacher_resource": ["curriculum_links", "what_this_covers", "how_to_use_it",
                             "what_to_watch_for", "where_to_find_out_more"],
        "assessment": ["what_this_is", "how_to_earn_it", "what_it_covers",
                       "rules_and_fair_play", "where_to_find_out_more"],
    }

    def test_orders_match_the_confirmed_ones(self):
        tpl = load("article_template.json")
        for name, order in self.EXPECTED.items():
            self.assertEqual(tpl["page_types"][name]["body_sections"], order, name)

    def test_dropped_headings_are_in_no_order(self):
        """What This Is left careers and Why It Matters left study skills. Both
        still exist as headings, because other templates use the first and the
        fold map needs the second resolvable."""
        tpl = load("article_template.json")
        self.assertNotIn("what_this_is", tpl["page_types"]["careers"]["body_sections"])
        for name in self.EXPECTED:
            self.assertNotIn("why_it_matters", tpl["page_types"][name]["body_sections"], name)


class OutlineIsNotABriefSource(unittest.TestCase):
    """The Sections 1 to 15 outline carries titles and nothing else. A brief built
    from it would have no tiers and no must_not_cover list, and the must_not_cover
    list is what stops the same fact being written on three thousand pages. See
    docs/findings/001."""

    def setUp(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.arch_dir = os.path.join(here, "config", "architecture")
        with open(os.path.join(self.arch_dir, "outline_1_to_15.json")) as fh:
            self.outline = json.load(fh)

    def test_the_outline_is_not_matched_by_the_page_map_glob(self):
        names = [n for n in os.listdir(self.arch_dir)
                 if n.startswith("pages_") and n.endswith(".json")]
        self.assertNotIn("outline_1_to_15.json", names)

    def test_architecture_load_pages_does_not_see_it(self):
        ids = set(str(p["page_id"]) for p in architecture.load_pages())
        outline_only = [p["page_id"] for p in self.outline["pages"]
                        if p["section"]["id"] not in ("1", "2", "3")]
        self.assertTrue(outline_only)
        self.assertEqual([p for p in outline_only if p in ids], [],
                         "an outline only page reached the brief generator")

    def test_sections_1_to_3_agree_with_the_page_map(self):
        """The one known exception is 2.12.5, where the upload has a US spelling
        and the page map has the British one. UK-001 bans the -ize form."""
        mapped = dict((str(p["page_id"]), p) for p in architecture.load_pages())
        mismatched = []
        for p in self.outline["pages"]:
            if p["section"]["id"] not in ("1", "2", "3"):
                continue
            other = mapped.get(p["page_id"])
            self.assertIsNotNone(other, "%s missing from the page map" % p["page_id"])
            if other["title"].strip() != p["title"].strip():
                mismatched.append(p["page_id"])
        self.assertEqual(mismatched, ["2.12.5"])

    def test_every_chapter_is_carried_including_the_empty_ones(self):
        """775 chapters have no enumerated pages. They are still link targets, so
        crossrefs needs their names."""
        chapters = self.outline["chapters"]
        self.assertGreater(len(chapters), len(set(
            p["chapter"]["id"] for p in self.outline["pages"])))
        empty = [c for c in chapters if c["pages_enumerated"] == 0]
        self.assertGreater(len(empty), 700)


class SectionConventions(unittest.TestCase):
    """Each later section's preamble declares its own tiers and subsections. That
    is a client supplied page template, and it is what decisions 003 and 005 had
    to invent in its absence."""

    def setUp(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(here, "config", "section_conventions.json")) as fh:
            self.conv = json.load(fh)["sections"]

    def test_every_section_one_to_fifteen_is_present(self):
        self.assertEqual(sorted(self.conv, key=int), [str(i) for i in range(1, 16)])

    def test_the_conditions_library_declares_five_tiers_and_sixteen_sections(self):
        s = self.conv["6"]
        self.assertEqual(len(s["tiers_declared"]), 5)
        self.assertEqual(len(s["required_sections_declared"]), 16)

    def test_a_declared_list_keeps_its_trigger_sentence(self):
        """Classification is a heuristic, so the sentence it was based on stays
        in the file and can be checked."""
        for sid, s in self.conv.items():
            for group in s.get("declared") or []:
                self.assertTrue(group["trigger"].endswith(":"), sid)
                self.assertTrue(group["items"], sid)


class MedicalSafetyStatement(unittest.TestCase):
    """Chapter 12 of the Master Operations Handbook requires patient-facing
    pages to say the content is educational and not a substitute for
    professional assessment. The site answers it in the footer on every page.
    The site has no build step, so the footer is copied into each file and
    nothing but a check stops it drifting out of one of them. See finding 002."""

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import check_site
        self.check_site = check_site

    def test_the_required_sentence_is_the_one_the_chrome_writes(self):
        import site_chrome
        self.assertIn(self.check_site.MEDICAL_SAFETY.lower(),
                      site_chrome.footer("").lower())

    def test_a_page_missing_the_statement_fails_the_site_check(self):
        """Run the real checker over a copy of the site with the statement
        removed from one page, and require a failure naming that page."""
        page = os.path.join(REPO, "about", "standards.html")
        with open(page, encoding="utf-8") as fh:
            original = fh.read()
        self.assertIn("replace assessment by a clinician", original)
        damaged = original.replace(
            "It does not give individual medical advice and it does not "
            "replace assessment by a clinician.", "")
        self.assertNotEqual(original, damaged)
        try:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(damaged)
            out = subprocess.run(
                [sys.executable, os.path.join(REPO, "tools", "check_site.py")],
                capture_output=True, text=True, cwd=REPO)
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("about/standards.html: no educational and not a "
                          "substitute statement", out.stdout)
        finally:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(original)


class TrackerColumns(unittest.TestCase):
    """Appendix A of the Master Operations Handbook sets thirteen tracker
    columns. Finding 002 found three of them missing. These hold the join."""

    def setUp(self):
        with open(os.path.join(ROOT, "config", "architecture",
                               "tracker_seed.json")) as fh:
            self.seed = json.load(fh)

    def test_every_appendix_a_column_has_a_field(self):
        wanted = ("page_id", "title", "category", "tiers_required", "priority",
                  "source_status", "draft_status", "qa_status",
                  "publication_status", "seo_complete", "refresh_date")
        for row in self.seed:
            for field in wanted:
                self.assertIn(field, row, row["page_id"])

    def test_every_section_has_a_taxonomy_category(self):
        for row in self.seed:
            self.assertTrue(row["category"], row["page_id"])

    def test_the_category_map_covers_every_section_in_the_outline(self):
        with open(os.path.join(ROOT, "config", "architecture",
                               "outline_1_to_15.json")) as fh:
            outline = json.load(fh)
        sections = set(str(p["section"]["id"]) for p in outline["pages"])
        self.assertTrue(sections <= set(architecture.TAXONOMY_CATEGORY))

    def test_sections_two_to_eight_match_the_handbook_taxonomy(self):
        """Chapter 5 of the handbook names these seven categories; the
        architecture's own section names are the same seven words."""
        self.assertEqual(
            [architecture.TAXONOMY_CATEGORY[str(n)] for n in range(2, 9)],
            ["Anatomy", "Biomechanics", "Clinical Examination", "Imaging",
             "Conditions", "Surgery", "Rehabilitation"])


class TierOverrides(unittest.TestCase):
    """Decision 013: a tier added to a page beyond the architecture's own list.
    Additive only, in the template's order, and never silent."""

    def setUp(self):
        with open(os.path.join(ROOT, "config", "tier_overrides.json")) as fh:
            self.cfg = json.load(fh)

    def test_every_entry_adds_and_never_removes(self):
        for pid, entry in self.cfg["pages"].items():
            self.assertTrue(entry.get("add"), pid)
            self.assertNotIn("remove", entry, pid)

    def test_every_entry_carries_a_reason(self):
        for pid, entry in self.cfg["pages"].items():
            self.assertTrue(len(entry.get("reason", "")) > 40, pid)

    def test_the_override_is_applied_in_template_tier_order(self):
        order = load("article_template.json")["tier_order"]
        got = architecture.tier_override("2.10.6", ["medical_student", "mrcs", "frcs"])
        self.assertEqual(got, [t for t in order if t in set(got)])
        self.assertIn("fellowship", got)

    def test_a_page_with_no_entry_is_untouched(self):
        tiers = ["medical_student", "mrcs"]
        self.assertEqual(architecture.tier_override("2.10.1", tiers), tiers)

    def test_the_brief_carries_the_added_tier(self):
        with open(os.path.join(ROOT, "config", "briefs", "2.10.6.json")) as fh:
            self.assertIn("fellowship", json.load(fh)["tiers_required"])


class DeclaredBandWinsOverMerge(unittest.TestCase):
    """A band in word_count_overrides.json is config, not a hand set value, so
    regenerating a brief must not merge the old number back over it. That is how
    decision 013's page kept failing a gate it was inside."""

    def test_the_overridden_page_carries_its_declared_band(self):
        with open(os.path.join(ROOT, "config", "word_count_overrides.json")) as fh:
            cfg = json.load(fh)
        entry = cfg["pages"]["2.10.6"]
        band = cfg["bands"][entry["band"]]
        with open(os.path.join(ROOT, "config", "briefs", "2.10.6.json")) as fh:
            brief = json.load(fh)
        self.assertEqual(brief["output_requirements"]["target_word_count"], band)

    def test_regenerating_over_an_existing_brief_keeps_the_declared_band(self):
        with open(os.path.join(ROOT, "config", "briefs", "2.10.6.json")) as fh:
            before = fh.read()
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "architecture.py"), "brief",
             "2.10.6", "--out", os.path.join(ROOT, "config", "briefs", "2.10.6.json")],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        with open(os.path.join(ROOT, "config", "briefs", "2.10.6.json")) as fh:
            after = json.load(fh)
        self.assertEqual(after["output_requirements"]["target_word_count"]["max"], 2400)
        with open(os.path.join(ROOT, "config", "briefs", "2.10.6.json"), "w") as fh:
            fh.write(before)


class ProseReferences(unittest.TestCase):
    """A bare reference in prose can name a real chapter and still be the wrong
    one. Seven were wrong across chapters 2.8 to 2.10 before anyone looked, and
    nothing caught them because every id was valid. The report makes the list
    readable; these tests hold the report and the seven corrections."""

    def report(self):
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "crossrefs.py"), "--prose-report"],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout

    def test_no_prose_reference_points_at_a_missing_id(self):
        self.assertIn("0 point at an id the architecture does not have", self.report())

    def test_the_examination_references_name_the_right_chapters(self):
        """Posterior cruciate to PCL Examination, medial to Medial Knee
        Examination, lateral to Lateral Knee Examination."""
        wanted = {"2.8.1": "4.11", "2.9.1": "4.12", "2.9.3": "4.12", "2.9.4": "4.12",
                  "2.10.1": "4.13", "2.10.2": "4.13", "2.10.3": "4.13"}
        for page_id, ref in wanted.items():
            path = os.path.join(ROOT, "runs", page_id, "styled_v1.md")
            with open(path, encoding="utf-8") as fh:
                body = fh.read()
            found = re.findall(r"(?<![\w.])(4\.\d{1,2})(?![\w.])", body)
            self.assertTrue(found, "%s has no section 4 reference" % page_id)
            self.assertEqual(set(found), {ref}, page_id)

    def test_the_report_names_a_page_and_its_references(self):
        text = self.report()
        self.assertIn("2.10.6", text)
        self.assertIn("Peroneal Nerve", text)
