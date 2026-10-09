"""Publication QA is the fifth QA tier named in chapter 13 of the Master
Operations Handbook. These tests hold its rules against known good and known bad
markup, and hold the live site at zero findings.
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "tools"))
import publication_qa as pq  # noqa: E402
import site_chrome as chrome  # noqa: E402


def page(**over):
    """A minimal page that passes every rule, so a test can break one thing."""
    cfg = chrome.site_config()
    fields = {
        "title": "A Page With A Long Enough Title | KneeSchool",
        "description": ("A description written to sit inside the bounds the "
                        "handbook's chapter 14 implies, ending in a full stop."),
        "canonical": chrome.canonical_url("levels/junior.html"),
        "body": ('<h1>A heading</h1><h2>Another</h2>'
                 '<p>KneeSchool is educational. %s.</p>'
                 '<a href="../index.html">Up</a>'
                 % cfg["medical_safety"]["required_sentence"]),
    }
    fields.update(over)
    html = ('<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width">'
            '<title>%(title)s</title>'
            '<meta name="description" content="%(description)s">'
            '<meta name="theme-color" content="#0E2A21">'
            '<link rel="canonical" href="%(canonical)s">'
            '</head><body>%(body)s</body></html>') % fields
    p = pq.Head()
    p.feed(html)
    return p


class Rules(unittest.TestCase):
    def setUp(self):
        self.cfg = chrome.site_config()
        self.rel = "levels/junior.html"

    def run_rule(self, rule, pg, all_pages=None):
        return rule(self.rel, pg, self.cfg, all_pages or {self.rel: pg})

    def test_a_good_page_passes_every_rule(self):
        pg = page()
        for rid, name, rule in pq.RULES:
            self.assertEqual(self.run_rule(rule, pg), [], rid)

    def test_a_title_without_the_suffix_fails(self):
        out = self.run_rule(pq.pub_001, page(title="A Title Without The Brand"))
        self.assertTrue(any("does not end" in m for m in out), out)

    def test_the_homepage_leads_with_the_brand_instead(self):
        pg = page(title="KneeSchool | One knee, seven depths of understanding",
                  canonical=chrome.canonical_url("index.html"))
        self.assertEqual(pq.pub_001("index.html", pg, self.cfg, {}), [])

    def test_a_short_description_fails(self):
        out = self.run_rule(pq.pub_002, page(description="Too short."))
        self.assertTrue(any("wanted" in m for m in out), out)

    def test_a_description_cut_mid_sentence_fails(self):
        """The earlier renderer truncated the summary to 160 characters, which
        cut words in half. The rule exists to stop that coming back."""
        cut = ("A description of exactly the right length that happens to stop "
               "without any closing punctuation at all because it was cut")
        out = self.run_rule(pq.pub_002, page(description=cut))
        self.assertTrue(any("truncated" in m for m in out), out)

    def test_a_canonical_pointing_elsewhere_fails(self):
        out = self.run_rule(pq.pub_003,
                            page(canonical="https://kneeschool.com/wrong.html"))
        self.assertTrue(any("canonical is" in m for m in out), out)

    def test_two_h1_headings_fail(self):
        pg = page(body='<h1>One</h1><h1>Two</h1>')
        out = self.run_rule(pq.pub_004, pg)
        self.assertTrue(any("2 H1" in m for m in out), out)

    def test_a_skipped_heading_level_fails(self):
        pg = page(body='<h1>One</h1><h3>Three</h3>')
        out = self.run_rule(pq.pub_004, pg)
        self.assertTrue(any("H1 to H3" in m for m in out), out)

    def test_an_image_without_alt_text_fails(self):
        pg = page(body='<h1>One</h1><img src="x.png">')
        self.assertEqual(len(self.run_rule(pq.pub_005, pg)), 1)

    def test_an_empty_alt_attribute_is_not_alt_text(self):
        pg = page(body='<h1>One</h1><img src="x.png" alt="  ">')
        self.assertEqual(len(self.run_rule(pq.pub_005, pg)), 1)

    def test_a_page_without_the_disclaimer_fails(self):
        pg = page(body='<h1>One</h1><p>Nothing about assessment here.</p>')
        self.assertEqual(len(self.run_rule(pq.pub_006, pg)), 1)

    def test_a_missing_theme_colour_is_a_metadata_failure(self):
        pg = page()
        del pg.meta["theme-color"]
        out = self.run_rule(pq.pub_008, pg)
        self.assertTrue(any("theme-color" in m for m in out), out)

    def test_two_pages_sharing_a_title_both_fail_uniqueness(self):
        a, b = page(), page()
        both = {"a.html": a, "b.html": b}
        self.assertTrue(any("title is not unique" in m
                            for m in pq.pub_009("a.html", a, self.cfg, both)))

    def test_every_rule_in_the_table_is_a_callable_with_an_id(self):
        for rid, name, rule in pq.RULES:
            self.assertTrue(rid.startswith("PUB-"), rid)
            self.assertTrue(callable(rule), rid)


class LiveSite(unittest.TestCase):
    def test_the_site_passes_publication_qa(self):
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "publication_qa.py")],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("0 findings", out.stdout)

    def test_the_bounds_are_configuration_not_code(self):
        with open(os.path.join(ROOT, "config", "site.json")) as fh:
            cfg = json.load(fh)
        for key in ("title_min", "title_max", "description_min", "description_max"):
            self.assertIsInstance(cfg["seo"][key], int, key)

    def test_the_canonical_url_of_the_homepage_is_the_bare_domain(self):
        self.assertEqual(chrome.canonical_url("index.html"),
                         chrome.site_config()["base_url"])
