"""Publication QA is the fifth QA tier named in chapter 13 of the Master
Operations Handbook. These tests hold its rules against known good and known bad
markup, and hold the live site at zero findings.
"""

import io
import json
import os
import re
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
    # A page that claims to pass every rule has to carry the publication posture
    # too, whichever way site.json has it set.
    fields["robots"] = ("" if cfg.get("discoverable")
                        else '<meta name="robots" content="noindex, nofollow">')
    html = ('<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width">'
            '<title>%(title)s</title>'
            '<meta name="description" content="%(description)s">'
            '<meta name="theme-color" content="#0e2b22">'
            '%(robots)s'
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


class PublicationPosture(unittest.TestCase):
    """Decision 015: the site is published and not publicised. One value in
    site.json drives the page directive and robots.txt, and PUB-010 refuses a
    half flip, because a site where some pages are indexable has no posture."""

    def setUp(self):
        self.cfg = chrome.site_config()
        self.rel = "levels/junior.html"

    def test_the_posture_is_a_deliberate_boolean(self):
        """This used to assert the flag was false, which made it a test of one
        moment rather than of the mechanism. The client set it true on 12 October
        2026 under decision 026, taking responsibility for publishing unreviewed
        material behind the work in progress notice. What must stay true is that
        the value is set deliberately and that everything else agrees with it,
        which the tests below check."""
        self.assertIn(self.cfg.get("discoverable"), (True, False))
        self.assertTrue((self.cfg.get("discoverable_note") or "").strip(),
                        "the switch has no recorded reason")

    def test_every_page_agrees_with_the_switch(self):
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "publication_qa.py")],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout)
        with open(os.path.join(REPO, "index.html"), encoding="utf-8") as fh:
            html = fh.read()
        directive = 'name="robots" content="noindex, nofollow"'
        if self.cfg.get("discoverable"):
            self.assertNotIn(directive, html)
        else:
            self.assertIn(directive, html)

    def test_the_sitemap_agrees_with_the_switch(self):
        """robots.txt has named a sitemap since it was written and the file never
        existed. Harmless while every crawler was disallowed and a 404 for every
        crawler once the site became discoverable."""
        path = os.path.join(REPO, "sitemap.xml")
        if not self.cfg.get("discoverable"):
            self.assertFalse(os.path.exists(path),
                             "a sitemap offered to crawlers that are disallowed")
            return
        self.assertTrue(os.path.exists(path), "robots.txt names a sitemap that is absent")
        with io.open(path, encoding="utf-8") as fh:
            body = fh.read()
        with open(os.path.join(REPO, "pipeline", "config",
                               "published_pages.json")) as fh:
            pages = json.load(fh)
        pages = pages.get("pages", pages)
        missing = []
        for page_id, value in sorted(pages.items()):
            out_path = value if isinstance(value, str) else value.get("out")
            if out_path and ("<loc>%s%s</loc>"
                             % (self.cfg["base_url"], out_path)) not in body:
                missing.append(page_id)
        self.assertEqual(missing, [])

    def test_robots_txt_agrees_with_the_switch(self):
        with open(os.path.join(REPO, "robots.txt"), encoding="utf-8") as fh:
            body = fh.read()
        if self.cfg.get("discoverable"):
            self.assertIn("Allow: /", body)
        else:
            self.assertIn("Disallow: /", body)

    # PUB-010 is tested against explicit configurations rather than the live one,
    # so both postures stay covered whichever one the site is in. These two tests
    # previously used self.cfg and silently changed meaning when the client set
    # discoverable true on 12 October 2026: one stopped exercising the rule and
    # the other asserted a half flip in the direction that was no longer the
    # dangerous one.

    def test_the_rule_catches_a_page_missing_the_directive_when_not_discoverable(self):
        pg = page()
        pg.meta.pop("robots", None)
        out = pq.pub_010(self.rel, pg, dict(self.cfg, discoverable=False), {})
        self.assertTrue(out and out[0].startswith("no robots noindex"), out)

    def test_the_rule_catches_a_stray_directive_when_discoverable(self):
        pg = page()
        pg.meta["robots"] = "noindex, nofollow"
        out = pq.pub_010(self.rel, pg, dict(self.cfg, discoverable=True), {})
        self.assertTrue(out and "but site.json says the site is discoverable" in out[0])

    def test_a_page_with_no_directive_is_fine_when_discoverable(self):
        pg = page()
        pg.meta.pop("robots", None)
        self.assertEqual(pq.pub_010(self.rel, pg, dict(self.cfg, discoverable=True), {}), [])

    def test_a_page_with_the_directive_is_fine_when_not_discoverable(self):
        pg = page()
        pg.meta["robots"] = "noindex, nofollow"
        self.assertEqual(pq.pub_010(self.rel, pg, dict(self.cfg, discoverable=False), {}), [])

    def test_flipping_the_switch_without_applying_chrome_fails_the_gate(self):
        """The half flip is the failure worth catching: site.json and the pages
        disagreeing. The dangerous direction depends on where the site currently
        is, so this flips whichever way is currently inconsistent and expects the
        gate to refuse it."""
        path = os.path.join(ROOT, "config", "site.json")
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        cfg = json.loads(original)
        cfg["discoverable"] = not cfg.get("discoverable")
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(cfg, fh, indent=2)
            out = subprocess.run(
                [sys.executable, os.path.join(REPO, "tools", "publication_qa.py")],
                capture_output=True, text=True, cwd=REPO)
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("PUB-010", out.stdout)
        finally:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(original)


class EveryPageIsReachableByClicking(unittest.TestCase):
    """A page nobody can navigate to is not published, whatever the index says.

    Section 4's 65 pages passed every gate on this site and were unreachable from
    the homepage, because the Clinical Examination Academy was never added to the
    ribbon and nothing outside its own directory linked to it. They formed an
    island: every page had an inbound link, so an orphan check found nothing, and
    no path led into the island from anywhere a visitor starts.

    The client found it by asking to see the pages. No gate did.
    """

    @staticmethod
    def _links(path, here):
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            html = fh.read()
        out = set()
        for m in re.finditer(r'href="([^"#?]+\.html)"', html):
            target = os.path.normpath(os.path.join(here, m.group(1)))
            out.add(target.replace(os.sep, "/"))
        return out

    def _graph(self):
        adjacency = {}
        for root, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs
                       if d not in (".git", "pipeline", "docs", "node_modules")]
            for name in files:
                if not name.endswith(".html"):
                    continue
                full = os.path.join(root, name)
                page = os.path.relpath(full, REPO).replace(os.sep, "/")
                adjacency[page] = self._links(full, os.path.dirname(page))
        return adjacency

    def test_every_published_page_is_reachable_from_the_homepage(self):
        adjacency = self._graph()
        self.assertIn("index.html", adjacency, "no homepage to start from")

        seen, stack = {"index.html"}, ["index.html"]
        while stack:
            for target in adjacency.get(stack.pop(), ()):
                if target not in seen:
                    seen.add(target)
                    stack.append(target)

        with open(os.path.join(REPO, "pipeline", "config",
                               "published_pages.json")) as fh:
            published = json.load(fh)
        pages = published.get("pages", published)

        unreachable = []
        for page_id, value in sorted(pages.items()):
            out = value if isinstance(value, str) else value.get("out")
            if out and out not in seen:
                unreachable.append("%s (%s)" % (page_id, out))
        self.assertEqual(unreachable, [])


class ChromeIsIdempotent(unittest.TestCase):
    """Rendering twice must not change anything the first render produced.

    The build notice was added above the header, and apply_chrome's pattern
    matched the header alone, so each render prepended another copy. Three had
    accumulated on the homepage before anyone looked, and the clean tree check
    in `make verify` was the thing that would eventually have caught it. This
    is the third idempotency bug in this repository, after the figure register
    and the position register, so it earns a test rather than a fix.
    """

    def test_one_notice_per_page(self):
        bad = []
        for root, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs
                       if d not in (".git", "pipeline", "docs", "node_modules")]
            for name in files:
                if not name.endswith(".html"):
                    continue
                full = os.path.join(root, name)
                with io.open(full, encoding="utf-8", errors="replace") as fh:
                    count = fh.read().count('class="build-notice"')
                if count != 1:
                    bad.append("%s: %d" % (os.path.relpath(full, REPO), count))
        self.assertEqual(sorted(bad), [])

    def test_applying_chrome_again_changes_nothing(self):
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "apply_chrome.py"), "--check"],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout)


class EveryPageCarriesTheBuildNotice(unittest.TestCase):
    """The client asked on 12 October 2026 for every produced page to be visible
    with a disclaimer saying the site is in progress. A disclaimer that is on most
    pages is not a disclaimer, so this checks all of them."""

    def test_the_notice_is_on_every_page(self):
        missing = []
        for root, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs
                       if d not in (".git", "pipeline", "docs", "node_modules")]
            for name in files:
                if not name.endswith(".html"):
                    continue
                full = os.path.join(root, name)
                with io.open(full, encoding="utf-8", errors="replace") as fh:
                    if "build-notice" not in fh.read():
                        missing.append(os.path.relpath(full, REPO))
        self.assertEqual(sorted(missing), [])


class TheBuildStatusPageAgreesWithTheRegisters(unittest.TestCase):
    """about/status.html quotes the register totals, and those numbers used to be
    typed into docs/build_status.json.

    By the time chapter 4.11 was written the page was telling a reader there were
    448 unchecked measurements against a register holding 462, that 32 chapters
    carried unsigned recommendations when 37 did, and that the largest was 3.7
    when it was 4.2. Nobody introduced any of that. The prose was right when it
    was written and the registers moved underneath it, which is the same failure
    the figure register itself was built to end.

    The numbers now come from the registers through {{token}} substitution, so
    this holds the substitution rather than the numbers: no token survives into
    the page, every token the data file uses is one the tool knows, and the
    totals the page prints are the totals the registers hold.
    """

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import build_status
        self.mod = build_status
        with io.open(os.path.join(REPO, "about", "status.html"),
                     encoding="utf-8") as fh:
            self.page = fh.read()
        with io.open(os.path.join(REPO, "docs", "build_status.json"),
                     encoding="utf-8") as fh:
            self.data = fh.read()

    def test_no_token_reaches_the_page(self):
        self.assertEqual(self.mod.TOKEN.findall(self.page), [])

    def test_every_token_in_the_data_file_is_one_the_tool_fills(self):
        known = set(self.mod.register_counts())
        used = set(self.mod.TOKEN.findall(self.data))
        self.assertTrue(used, "the data file no longer uses any register token")
        self.assertEqual(sorted(used - known), [])

    def test_the_page_prints_the_sentences_the_registers_make(self):
        """Every tokenised sentence, filled in, appears on the page.

        Checking that the page contains the string "462" somewhere is not this
        test: the first version of it did, and it passed against a page that said
        448 unchecked measurements, because 462 happened to appear in another
        sentence. Each tokenised sentence is filled and looked for whole.
        """
        import html
        counts = self.mod.register_counts()
        data = json.loads(self.data)
        missing = []
        for group in data["groups"]:
            for item in group["items"]:
                for field, value in item.items():
                    if not isinstance(value, str):
                        continue
                    if not self.mod.TOKEN.search(value):
                        continue
                    want = html.escape(self.mod.fill(value, counts), quote=False)
                    if want not in self.page:
                        missing.append("%s %s" % (item.get("ref"), field))
        self.assertEqual(sorted(missing), [])
