"""The architecture and the handbook are configuration, not code, and both
arrived after the pipeline was built. These tests hold the join between them.
"""

import collections
import glob
import json
import os
import re
import shutil
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
import crossrefs  # noqa: E402


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
        # Decision 020 turned the floor into an allow list, so the message names
        # the tiers rather than a floor. The rule still fires on the patient tier,
        # which is what this test is for.
        self.assertIn("carries 'controversies_and_evidence'", found)
        self.assertIn("restricted to frcs and consultant", found)


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

    def test_architecture_load_pages_does_not_read_the_outline(self):
        """The original form of this test compared page ids, on the assumption
        that any id outside Sections 1 to 3 could only have come from the
        outline. Decision 024 made that false: pages_4.json supplies Section 4
        with real tiers and a real must_not_cover list, so its ids are now
        legitimately in the brief generator. What must stay true is that no page
        reaching the generator came from the outline file itself."""
        sources = set(p.get("_source_file") for p in architecture.load_pages())
        self.assertNotIn("outline_1_to_15.json", sources)
        self.assertTrue(sources, "the brief generator found no architecture file")
        for name in sources:
            self.assertTrue(name and name.startswith("pages_"), name)

    def test_every_page_the_generator_sees_has_tiers_and_a_boundary_list(self):
        """What the id comparison was actually protecting. A page map file may be
        added for any section, and this is the property that makes it usable."""
        thin = []
        for p in architecture.load_pages():
            if not p.get("tiers_required") or not p.get("must_not_cover"):
                thin.append(str(p["page_id"]))
        self.assertEqual(thin, [])

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


class BiomechanicsTemplate(unittest.TestCase):
    """Decision 014 defined the two Section 3 page types. These hold the join
    between the template, the page type map and the pages built on it."""

    def setUp(self):
        self.tpl = load("article_template.json")
        self.map = load("page_type_map.json")

    def test_both_new_types_have_a_template_of_their_own(self):
        for name in ("biomechanics", "landmark_papers"):
            entry = self.map["page_types"][name]
            self.assertEqual(entry["template"], name)
            self.assertFalse(entry["variant_pending"], name)
            self.assertIn(name, self.tpl["page_types"])

    def test_the_biomechanics_sections_are_the_declared_five(self):
        self.assertEqual(
            self.tpl["page_types"]["biomechanics"]["body_sections"],
            ["the_principle", "at_the_knee", "what_changes_it",
             "how_it_is_measured", "clinical_relevance"])

    def test_every_body_section_slug_has_a_heading(self):
        """A heading derived by guesswork from a slug is how a template drifts."""
        headings = self.tpl["body_section_headings"]
        for name, spec in self.tpl["page_types"].items():
            for slug in spec["body_sections"]:
                self.assertIn(slug, headings, "%s: %s" % (name, slug))

    def test_the_faq_allowance_applies_to_any_band(self):
        """A four tier page with a patient block carries an FAQ block the
        handbook's 800 to 1800 band was not written for."""
        four = ["junior", "patient", "medical_student", "mrcs"]
        got = architecture.scale_for_tiers({"min": 800, "max": 1800}, four)
        self.assertEqual(got["max"], 1800 + architecture.FAQ_ALLOWANCE)
        no_patient = ["medical_student", "mrcs", "frcs"]
        self.assertEqual(
            architecture.scale_for_tiers({"min": 800, "max": 1800}, no_patient)["max"], 1800)

    def test_the_built_chapter_uses_the_new_headings(self):
        with open(os.path.join(ROOT, "runs", "3.1.1", "styled_v1.md"),
                  encoding="utf-8") as fh:
            body = fh.read()
        for heading in ("### The Principle", "### At the Knee", "### How It Is Measured"):
            self.assertIn(heading, body)
        self.assertNotIn("Blood Supply and Innervation", body)


class ProseReferenceDetector(unittest.TestCase):
    """The prose reference report is what caught four references that pointed at
    a real page about the wrong subject. Chapter 3.4 then quoted a bare decimal
    and the detector read "1.0 to 1.2 times body weight" as two chapter
    references, one of which resolved to a real page. These tests hold the fix
    and the pre-existing miss it uncovered."""

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import crossrefs
        self.refs = lambda t: [r for _, _, r in crossrefs.reference_spans(t)]

    def test_a_measurement_is_not_a_reference(self):
        for text in ("roughly 1.0 to 1.2 times body weight",
                     "about 1.5 times body weight",
                     "a 2.5 mm step off",
                     "1.0 to 1.2 body weight walking",
                     "roughly 25.5 degrees of rotation"):
            self.assertEqual(self.refs(text), [], text)

    def test_a_list_of_references_keeps_every_member(self):
        """The first attempt at the fix dropped the second id in a pair, because
        it looks exactly like the second number in a range. It suppressed 156
        real references."""
        self.assertEqual(self.refs("3.7 and 3.8 cover the cruciates"), ["3.7", "3.8"])
        self.assertEqual(self.refs("3.4.6 and 3.13 cover it"), ["3.4.6", "3.13"])
        self.assertEqual(self.refs("2.5.7 and 2.6.4 cover the roots"), ["2.5.7", "2.6.4"])

    def test_a_reference_ending_a_sentence_is_found(self):
        """The old pattern refused a reference followed by a full stop, so every
        reference that closed a sentence went unchecked. There were 56."""
        self.assertEqual(self.refs("chapters 0.1 and 0.2."), ["0.1", "0.2"])
        self.assertEqual(self.refs("the subject of 2.7.6."), ["2.7.6"])

    def test_a_four_part_id_is_not_reported_as_its_first_three(self):
        self.assertEqual(self.refs("see 5.3.1.1 AP View"), [])

    def test_a_field_strength_is_not_a_reference(self):
        """EV-38. tesla was in neither unit list. This detector read "1.5 tesla"
        as a reference to a chapter 1.5 the architecture does not have, while the
        style gate read the same text as a page id and left the measurement out
        of the figure register. One omitted word, two tools, opposite failures."""
        for text in ("imaging runs at 1.5 tesla",
                     "a 3 tesla scanner",
                     "runs at 1.5 tesla or 3 tesla",
                     "scanners run at 1.5 to 3 tesla"):
            self.assertEqual(self.refs(text), [], text)

    def test_a_reference_before_the_word_tesla_is_still_a_reference(self):
        """The exclusion must need the number to be the thing the unit measures.
        A sentence that happens to mention tesla after a reference is not a
        measurement."""
        self.assertEqual(self.refs("5.2.12 covers the basic principles"), ["5.2.12"])

    def test_an_ordinary_reference_still_resolves(self):
        self.assertEqual(self.refs("3.3.9 covers walking"), ["3.3.9"])
        self.assertEqual(self.refs("3.5 covers contact mechanics"), ["3.5"])

    def test_the_site_has_no_reference_to_a_missing_id(self):
        out = subprocess.run([sys.executable, os.path.join(REPO, "tools", "crossrefs.py"),
                              "--prose-report"], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("0 point at an id the architecture does not have", out.stdout)


class Section5PageMapIsRebuildable(unittest.TestCase):
    """Decision 027. pages_5.json is generated, so it must be regenerable.

    pages_4.json was generated by a script that lived in a scratchpad directory,
    and when the container was reclaimed the script went with it. The committed
    map survived and the thing that made it did not, so nobody can re-derive it
    or check it against the source. tools/extract_section5.py is committed for
    that reason and this test holds the two in step.
    """

    def built(self):
        import importlib
        sys.path.insert(0, os.path.join(REPO, "tools"))
        try:
            mod = importlib.import_module("extract_section5")
            importlib.reload(mod)
            return mod.build()[0]
        finally:
            sys.path.remove(os.path.join(REPO, "tools"))

    def committed(self):
        path = os.path.join(REPO, "pipeline", "config", "architecture",
                            "pages_5.json")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_the_committed_map_matches_a_rebuild_from_the_source(self):
        self.assertEqual(self.committed(), self.built())

    def test_the_section_is_224_pages(self):
        """The outline file says 161, because it recorded the navigational
        headings of chapters 5.2 to 5.5 as pages and dropped the 78 leaves under
        them. 224 also sits inside Part 1's own 250 to 350 estimate."""
        self.assertEqual(len(self.committed()), 224)

    def test_no_page_id_has_four_components(self):
        """Part 1's numbering convention: navigational groupings never appear in
        page ids."""
        for page in self.committed():
            self.assertEqual(len(page["page_id"].split(".")), 3,
                             page["page_id"])

    def test_the_navigational_headings_are_not_pages(self):
        """Chapter 5.3's four sub section headings must not survive as pages.
        5.3.4 exists as a page id, but it is the fourth leaf of the flattened
        chapter and not the old "Osteoarthritis Imaging" heading."""
        titles = {p["page_id"]: p["title"] for p in self.committed()}
        for nav_title in ("X-ray Physics", "Alignment Imaging",
                          "Osteoarthritis Imaging", "Interventional Ultrasound",
                          "MRI Protocols"):
            self.assertNotIn(nav_title, titles.values(), nav_title)

    def test_the_osteoarthritis_chain_lands_on_the_osteoarthritis_pages(self):
        """The spiral map's 5.3.4 meant the sub section. After flattening, 5.3.4
        is Tunnel View, so taking the reference at face value wired the
        osteoarthritis chain to a radiographic view."""
        by_id = {p["page_id"]: p for p in self.committed()}
        self.assertEqual(by_id["5.3.16"]["title"], "Kellgren-Lawrence Grading")
        self.assertIn("6.71", by_id["5.3.16"]["deeper_pages"])
        self.assertNotIn("6.71", by_id["5.3.4"]["deeper_pages"])

    def test_every_page_carries_a_type_the_map_knows(self):
        path = os.path.join(REPO, "pipeline", "config", "page_type_map.json")
        with open(path, encoding="utf-8") as fh:
            known = json.load(fh)["page_types"]
        for page in self.committed():
            self.assertIn(page["page_type"], known, page["page_id"])


class CrossLinksToPagesThatExist(unittest.TestCase):
    """A cross link to a page id that does not exist used to pass every gate.

    The link check exempted every unknown id as a forward link to a section the
    architecture had not mapped yet. That was written when only sections 0 to 3
    were mapped; all sixteen now carry page ids, so the exemption protected
    nothing and hid a typo. 4.19.4 linked [[4.15.11 | The Apprehension Test]]
    when chapter 4.15 ends at 4.15.10, the renderer counted it as one
    unresolved link of six, and nothing failed.
    """

    def run_check(self, runs):
        return subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "crossrefs.py"),
             "--check", "--runs", runs],
            capture_output=True, text=True, cwd=REPO)

    def draft(self, runs, page_id, link):
        os.makedirs(os.path.join(runs, page_id))
        with open(os.path.join(runs, page_id, "draft_v1.md"), "w") as fh:
            fh.write("# T\n\nSummary.\n\n## Explore Further\n\n- %s\n" % link)

    def test_a_link_to_a_page_that_does_not_exist_fails(self):
        with tempfile.TemporaryDirectory() as runs:
            self.draft(runs, "4.19.4", "[[4.15.11 | The Apprehension Test]]")
            out = self.run_check(runs)
            self.assertNotEqual(out.returncode, 0, out.stdout)
            self.assertIn("4.15.11", out.stdout)

    def test_a_link_past_the_last_section_fails_too(self):
        with tempfile.TemporaryDirectory() as runs:
            self.draft(runs, "4.19.4", "[[99.1.1 | A Future Page]]")
            out = self.run_check(runs)
            self.assertNotEqual(out.returncode, 0, out.stdout)

    def test_a_real_link_passes(self):
        with tempfile.TemporaryDirectory() as runs:
            self.draft(runs, "4.19.4", "[[4.15.3 | Patellar Apprehension Test]]")
            out = self.run_check(runs)
            self.assertEqual(out.returncode, 0, out.stdout)

    def test_the_site_has_no_cross_link_to_a_missing_page(self):
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "crossrefs.py"), "--check"],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout)


class RenderTargetCollisions(unittest.TestCase):
    """Two page ids pointing at the same output file would publish one page and
    silently lose the other, with every gate still passing. Chapter 3.6 came
    within one slug of it, because three of its titles are shared with chapters
    3.4 and 2.7."""

    TARGETS = os.path.join(REPO, "pipeline", "config", "render_targets.json")

    def targets(self):
        with open(self.TARGETS, encoding="utf-8") as fh:
            return json.load(fh)

    def test_no_two_pages_render_to_the_same_file(self):
        seen = {}
        for page_id, t in sorted(self.targets()["pages"].items()):
            out = t["out"]
            self.assertNotIn(out, seen,
                             "%s and %s both render to %s" % (seen.get(out), page_id, out))
            seen[out] = page_id

    def test_the_renderer_refuses_a_collision(self):
        with open(self.TARGETS, encoding="utf-8") as fh:
            original = fh.read()
        cfg = json.loads(original)
        ids = sorted(cfg["pages"])
        cfg["pages"][ids[1]]["out"] = cfg["pages"][ids[0]]["out"]
        try:
            with open(self.TARGETS, "w", encoding="utf-8") as fh:
                json.dump(cfg, fh, indent=2)
            out = subprocess.run(
                [sys.executable, os.path.join(REPO, "tools", "render_site.py")],
                capture_output=True, text=True, cwd=REPO)
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("render targets collide", out.stdout + out.stderr)
        finally:
            with open(self.TARGETS, "w", encoding="utf-8") as fh:
                fh.write(original)


class SeoTitleBudget(unittest.TestCase):
    """A colliding page carries its chapter name in the title tag so chapter 14's
    uniqueness rule is satisfied. The suffix had no length budget, so chapter 13's
    length rule could be broken by the fix for chapter 14's. Chapter 3.12 found
    it: "Effects of Malalignment, Tibiofemoral Contact Mechanics | KneeSchool" is
    68 characters against a bound of 60."""

    def setUp(self):
        sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "tools"))
        import render_site
        self.render_site = render_site
        with open(os.path.join(ROOT, "config", "site.json")) as fh:
            self.site = json.load(fh)

    def test_the_budget_leaves_room_for_the_site_suffix(self):
        self.assertEqual(
            self.render_site.title_budget(),
            self.site["seo"]["title_max"] - len(self.site["title_suffix"]))

    def test_a_long_chapter_name_is_trimmed_to_fit(self):
        out = self.render_site.disambiguate(
            "Effects of Malalignment", "Tibiofemoral Contact Mechanics", 47)
        self.assertLessEqual(len(out), 47)
        self.assertEqual(out, "Effects of Malalignment, Tibiofemoral Contact")

    def test_trimming_keeps_the_distinguishing_word(self):
        # The point of the suffix is to separate the two pages. "Tibiofemoral"
        # and "Patellofemoral" are the words that do that, and both survive.
        a = self.render_site.disambiguate(
            "Contact Pressures", "Tibiofemoral Contact Mechanics", 47)
        b = self.render_site.disambiguate(
            "Contact Pressures", "Patellofemoral Biomechanics", 47)
        self.assertIn("Tibiofemoral", a)
        self.assertIn("Patellofemoral", b)
        self.assertNotEqual(a, b)

    def test_a_short_chapter_name_is_left_alone(self):
        self.assertEqual(
            self.render_site.disambiguate("Trochlea", "Patellofemoral Anatomy", 47),
            "Trochlea, Patellofemoral Anatomy")

    def test_a_first_word_that_cannot_fit_is_left_whole(self):
        # Better a reported finding than a mangled title.
        out = self.render_site.disambiguate("A Very Long Page Title Indeed",
                                            "Incompressible", 20)
        self.assertEqual(out, "A Very Long Page Title Indeed, Incompressible")

    def test_every_published_title_is_within_bounds(self):
        import re
        root = os.path.dirname(ROOT)
        lo, hi = self.site["seo"]["title_min"], self.site["seo"]["title_max"]
        with open(os.path.join(ROOT, "config", "render_targets.json")) as fh:
            pages = json.load(fh)["pages"]
        checked = 0
        for page_id, target in sorted(pages.items()):
            path = os.path.join(root, target["out"])
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                m = re.search(r"<title>(.*?)</title>", fh.read(), re.S)
            self.assertTrue(m, target["out"])
            title = m.group(1).strip()
            self.assertTrue(lo <= len(title) <= hi,
                            "%s: title is %d characters: %r"
                            % (page_id, len(title), title))
            checked += 1
        self.assertTrue(checked, "no rendered pages found")

    def test_no_two_published_pages_share_a_title(self):
        import re
        root = os.path.dirname(ROOT)
        with open(os.path.join(ROOT, "config", "render_targets.json")) as fh:
            pages = json.load(fh)["pages"]
        seen = {}
        for page_id, target in sorted(pages.items()):
            path = os.path.join(root, target["out"])
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                m = re.search(r"<title>(.*?)</title>", fh.read(), re.S)
            title = m.group(1).strip()
            self.assertNotIn(title, seen,
                             "%s and %s share the title %r"
                             % (seen.get(title), page_id, title))
            seen[title] = page_id


if __name__ == "__main__":
    unittest.main()


class VerifyTargetIsTheOnlyList(unittest.TestCase):
    """The gates are one command, and the one command is what CI runs.

    They used to be five separate invocations held in one person's head, so a
    contributor could not know the list and CI could not run it. Two commands
    meant to agree and written out separately drift, so the workflow runs
    `make verify` rather than restating the steps. Decision 021."""

    def setUp(self):
        self.root = os.path.dirname(ROOT)
        with open(os.path.join(self.root, "Makefile"), encoding="utf-8") as fh:
            self.makefile = fh.read()
        path = os.path.join(self.root, ".github", "workflows", "verify.yml")
        self.assertTrue(os.path.exists(path), "no CI workflow")
        with open(path, encoding="utf-8") as fh:
            self.workflow = fh.read()

    def test_the_workflow_runs_the_make_target(self):
        self.assertIn("make verify", self.workflow)

    def test_the_workflow_does_not_restate_the_gates(self):
        # If a gate is run from the workflow it can fall out of step with the
        # Makefile. Comments may name one, and the status line at the end may
        # run review_pack and figures, because neither is a gate.
        live = "\n".join(line for line in self.workflow.splitlines()
                         if not line.lstrip().startswith("#"))
        for tool in ("lint_site.py", "check_site.py", "publication_qa.py",
                     "crossrefs.py", "check_clean.py"):
            self.assertNotIn(tool, live, tool)

    def test_verify_ends_by_checking_the_tree(self):
        self.assertIn("check_clean.py --baseline", self.makefile)

    def test_every_gate_in_the_target_exists(self):
        import re
        for match in re.finditer(r"tools/(\w+\.py)", self.makefile):
            path = os.path.join(self.root, "tools", match.group(1))
            self.assertTrue(os.path.exists(path), match.group(1))

    def test_the_readme_names_the_one_command(self):
        with open(os.path.join(self.root, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        self.assertIn("make verify", readme)
        # The count the README quoted went stale for days. If it names a number
        # of tests, it has to be this suite's number.
        match = __import__("re").search(r"(\d+) tests", readme)
        if match:
            loader = unittest.TestLoader()
            suite = loader.discover(os.path.join(ROOT, "tests"))
            self.assertEqual(int(match.group(1)), suite.countTestCases())


class ACollidingTitleInsideOneChapterKeepsItsGrouping(unittest.TestCase):
    """EV-37. The renderer gives a page whose title collides with another's a
    title tag carrying its chapter name, which works because a collision had
    always been between chapters: five pages called Surgical Anatomy, one per
    structure.

    Chapter 5.2 broke that. The source gives it a Radiation Dose page under the
    X-ray Physics heading (5.2.1.3) and another under CT Physics (5.2.4.3), and
    decision 027's flattening renumbered them 5.2.3 and 5.2.24 inside one
    chapter. Two pages, one title, one chapter name to tell them apart with. The
    renderer would have refused to render the section, which is the right
    failure and no use to anybody, and the information that separated them was
    in the source and had been thrown away.

    So the extractor keeps the heading as chapter.nav_group and the renderer
    prefers it when the chapter name cannot separate. This holds the invariant
    the renderer depends on: wherever one chapter carries a title twice, every
    one of those pages has a grouping, and the groupings differ.

    Found before chapter 5.2 was written rather than by the render failing,
    which is the only reason it is not also a wasted writing pass.
    """

    @classmethod
    def setUpClass(cls):
        cls.pages = []
        for path in sorted(glob.glob(os.path.join(
                REPO, "pipeline", "config", "architecture", "pages_*.json"))):
            with open(path, encoding="utf-8") as fh:
                cls.pages.extend(json.load(fh))

    def collisions(self):
        """Every (chapter id, title) the architecture uses more than once."""
        seen = collections.defaultdict(list)
        for page in self.pages:
            seen[(page["chapter"]["id"], page["title"])].append(page)
        return dict((k, v) for k, v in seen.items() if len(v) > 1)

    def test_the_known_collision_is_still_the_only_one(self):
        """If a second appears, this test is how it gets noticed."""
        self.assertEqual(sorted(self.collisions()),
                         [("5.2", "Radiation Dose")])

    def test_every_colliding_page_carries_a_grouping(self):
        for (chapter, title), pages in self.collisions().items():
            for page in pages:
                self.assertTrue(
                    page["chapter"].get("nav_group"),
                    "%s (%s in %s) has no nav_group to be told apart by"
                    % (page["page_id"], title, chapter))

    def test_the_groupings_of_a_colliding_set_differ(self):
        for (chapter, title), pages in self.collisions().items():
            groups = [p["chapter"].get("nav_group") for p in pages]
            self.assertEqual(len(set(groups)), len(groups),
                             "%s in %s: %r" % (title, chapter, groups))

    def test_the_two_radiation_dose_pages_name_their_modality(self):
        """Named explicitly, because this pair is the reason the field exists."""
        groups = dict((p["page_id"], p["chapter"].get("nav_group"))
                      for p in self.pages if p["title"] == "Radiation Dose")
        self.assertEqual(groups, {"5.2.3": "X-ray Physics",
                                  "5.2.24": "CT Physics"})

    def test_a_grouping_is_only_on_a_flattened_chapter(self):
        """Chapters 5.2 to 5.5 were flattened and carry groupings. A chapter the
        source numbered flat has no heading to record, and inventing one would
        make the field untrustworthy where it matters."""
        flattened = {"5.2", "5.3", "5.4", "5.5"}
        for page in self.pages:
            if page["section"]["id"] != "5":
                continue
            has = bool(page["chapter"].get("nav_group"))
            self.assertEqual(has, page["chapter"]["id"] in flattened,
                             "%s: nav_group %r" % (page["page_id"],
                                                   page["chapter"].get("nav_group")))

    def test_the_grouping_reaches_the_brief(self):
        """The renderer reads it from the brief, not from the architecture, so a
        brief that drops the field silently restores the bug."""
        path = os.path.join(REPO, "pipeline", "config", "briefs", "5.2.24.json")
        if not os.path.exists(path):
            self.skipTest("5.2.24 has no brief yet")
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["chapter"].get("nav_group"),
                             "CT Physics")


class NoPublishedPagePointsAtAHeldPage(unittest.TestCase):
    """EV-41. render_targets.json holds pages back at the client's instruction,
    and a held page is not coming soon: chapter 5.19 was held on 15 October 2026
    because the Magic Angle MRI Academy will not be published at all. Nothing
    checked whether a published page still pointed at one. Chapter 5.18 was then
    written leaning on 5.19 for its central claim, and shipped 34 prose
    references and 8 cross links into pages no reader will ever open, with every
    gate green. Twelve such references already existed before that chapter.
    """

    def setUp(self):
        with open(os.path.join(REPO, "pipeline", "config",
                               "render_targets.json")) as fh:
            self.targets = json.load(fh)

    def test_the_withheld_block_is_a_dict_of_page_ids(self):
        withheld = self.targets.get("withheld") or {}
        self.assertIsInstance(withheld, dict)
        for page_id in withheld:
            self.assertRegex(page_id, r"^\d+\.\d+\.\d+$")

    def test_a_held_page_is_never_also_a_render_target(self):
        held = set(self.targets.get("withheld") or {})
        published = set(self.targets.get("pages") or {})
        self.assertEqual(held & published, set())

    def test_no_published_page_references_a_held_page(self):
        found = crossrefs.withheld_references(
            os.path.join(REPO, "pipeline", "runs"), listing=False)
        self.assertEqual(found, [], "references into a held page: %r" % (found[:8],))

    def test_the_check_reads_what_is_published_not_the_draft(self):
        # EV-42. Every check in crossrefs.py read draft_v1.md while the site
        # publishes the file the render target names. For thirteen pages the two
        # differ, so 5.1.8's four references into the held chapter were in its
        # published text and not in its draft, and the gate called it clean.
        sources = crossrefs.render_sources()
        self.assertTrue(sources)
        self.assertEqual(set(sources.values()), {"styled_v1.md"})

    def test_the_gate_catches_a_reference_it_is_given(self):
        # The fixture used to name 5.19.9 because that chapter was held. The
        # client released it on 19 October 2026 and this test failed, which is
        # the test naming a page rather than the behaviour. It now takes
        # whichever page is held, so releasing one does not break the gate's
        # own test.
        held, _ = crossrefs.withheld_and_published()
        self.assertTrue(held, "nothing is held, so the gate cannot be exercised")
        target = sorted(held)[0]
        runs = tempfile.mkdtemp()
        os.makedirs(os.path.join(runs, "9.9.9"))
        with open(os.path.join(runs, "9.9.9", "styled_v1.md"), "w") as fh:
            fh.write("# X\n\nBody. %s covers the held subject.\n" % target)
        try:
            sources = crossrefs.render_sources()
            text = crossrefs.source_text(runs, "9.9.9", sources)
            self.assertIn(target, text)
        finally:
            shutil.rmtree(runs)

    def test_the_makefile_runs_the_withheld_gate(self):
        with open(os.path.join(REPO, "Makefile")) as fh:
            mk = fh.read()
        self.assertIn("crossrefs.py --withheld-check", mk)
        # and it runs inside `gates`, not in some unreferenced target
        gates = mk.split("gates:", 1)[1].split("\n\n", 1)[0]
        self.assertIn("--withheld-check", gates)



class TheReportingTemplate(unittest.TestCase):
    """Decision 029. Chapter 5.20's subject is the report, not an image.

    It was written against the imaging template, whose six sections had to be
    read as questions about a report: "What Normal Looks Like" meant what a good
    report looks like, and "What Abnormal Looks Like" meant a poor one. Those two
    headings collide with their own meaning everywhere else in Section 5, where
    normal and abnormal describe a knee. The chapter papered over it with a
    paragraph on 5.20.1 telling the reader how to read the headings, which is a
    translation note standing in for a template.

    Decision 028 recorded at the time that this chapter was the loosest fit in
    the set and would probably want its own type. This is that type.

    The content did not move. The pages were already written to these six
    questions, so the change is the headings, the page_type and the join.
    """

    IDS = ["5.20.%d" % n for n in range(1, 9)]

    def template(self):
        path = os.path.join(ROOT, "config", "article_template.json")
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_the_template_exists_and_keeps_the_six_questions(self):
        spec = self.template()["page_types"].get("reporting")
        self.assertIsNotNone(spec, "no reporting template")
        self.assertEqual(spec["body_sections"], [
            "what_the_report_is_for", "how_the_report_is_built",
            "what_a_good_one_looks_like", "what_a_poor_one_looks_like",
            "how_good_it_is", "where_it_misleads"])

    def test_every_section_has_a_heading(self):
        """A section key with no heading renders as its own key."""
        t = self.template()
        heads = t["body_section_headings"]
        for key in t["page_types"]["reporting"]["body_sections"]:
            self.assertIn(key, heads, key)

    def test_the_two_reused_sections_are_the_two_that_fitted(self):
        """how_good_it_is and where_it_misleads carried over unchanged, so the
        MRCS floor in section_tier_rules still reaches this template."""
        t = self.template()
        shared = set(t["page_types"]["reporting"]["body_sections"]) \
            & set(t["page_types"]["imaging"]["body_sections"])
        self.assertEqual(shared, {"how_good_it_is", "where_it_misleads"})
        self.assertEqual(t["section_tier_rules"]["how_good_it_is"]["from"], "mrcs")

    def test_the_page_type_joins_onto_the_template(self):
        path = os.path.join(ROOT, "config", "page_type_map.json")
        with open(path, encoding="utf-8") as fh:
            m = json.load(fh)
        self.assertIn("reporting", m["templates"])
        self.assertEqual(m["page_types"]["reporting"]["template"], "reporting")
        self.assertFalse(m["page_types"]["reporting"]["variant_pending"])

    def test_the_architecture_gives_the_chapter_the_new_type(self):
        path = os.path.join(ROOT, "config", "architecture", "pages_5.json")
        with open(path, encoding="utf-8") as fh:
            pages = json.load(fh)
        by_id = {p["page_id"]: p for p in pages}
        for page_id in self.IDS:
            self.assertEqual(by_id[page_id]["page_type"], "reporting", page_id)
        # and nothing else moved with it
        others = {p["page_type"] for p in pages
                  if not p["page_id"].startswith("5.20.")}
        self.assertEqual(others, {"imaging", "landmark_papers"})

    def test_the_accuracy_ban_still_covers_these_pages(self):
        """ACC-001 named examination and imaging. A page type split that drops a
        chapter out of a content rule is the kind of regression this change could
        have shipped quietly, because every gate would still have been green."""
        path = os.path.join(ROOT, "config", "lint_rules.json")
        with open(path, encoding="utf-8") as fh:
            rules = json.load(fh)["rules"]
        acc = [r for r in rules if r["id"] == "ACC-001"][0]
        self.assertIn("reporting", acc["page_types"])
        self.assertIn("imaging", acc["page_types"])
        self.assertIn("examination", acc["page_types"])

    def test_the_briefs_and_the_pages_agree_with_the_architecture(self):
        for page_id in self.IDS:
            brief = os.path.join(ROOT, "config", "briefs", "%s.json" % page_id)
            with open(brief, encoding="utf-8") as fh:
                b = json.load(fh)
            self.assertEqual(b["page_type"], "reporting", page_id)
            self.assertEqual(b["article_template"], "reporting", page_id)

    def test_no_reporting_page_still_carries_an_imaging_heading(self):
        """The rename had to reach all three stage files of all eight pages, and
        the site publishes styled_v1.md rather than the draft."""
        gone = ("### What Normal Looks Like", "### What Abnormal Looks Like",
                "### What It Shows", "### How It Is Acquired")
        for page_id in self.IDS:
            for stage in ("draft_v1.md", "verified_v1.md", "styled_v1.md"):
                path = os.path.join(ROOT, "runs", page_id, stage)
                if not os.path.exists(path):
                    continue
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                for heading in gone:
                    self.assertNotIn(heading, text,
                                     "%s/%s keeps %r" % (page_id, stage, heading))

    def test_the_translation_note_is_gone(self):
        """5.20.1 told the reader how to read the headings. The headings say it."""
        path = os.path.join(ROOT, "runs", "5.20.1", "styled_v1.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        self.assertNotIn("the six template headings are read as questions", text)
