"""Publication QA is the fifth QA tier named in chapter 13 of the Master
Operations Handbook. These tests hold its rules against known good and known bad
markup, and hold the live site at zero findings.
"""

import collections
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


class DisambiguatedTitlesSeparateThePages(unittest.TestCase):
    """PUB-009 wants a unique title tag per page, and the renderer gets one for a
    colliding page by appending the chapter name, trimmed to fit PUB-001's bound.

    Which words to drop is the whole problem. Dropping from the back loses
    "Examination" from "Patellofemoral Examination", the word that separates it
    from "Patellofemoral Biomechanics". Dropping from the front loses "ACL" from
    "ACL Examination", the word that separates it from "Rotational Instability
    Examination". Chapter 4.15 hit the first and gave two pages the identical
    title tag the disambiguation existed to separate.

    The renderer now ranks a chapter name's words by how many of the other
    colliding chapters contain them and drops the most shared word first. These
    hold both halves of that, and the live site's uniqueness is held by
    PublicationPosture and the publication gate rather than here.
    """

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import render_site
        self.mod = render_site
        self.budget = render_site.title_budget()

    def test_a_shared_opening_word_is_dropped_before_the_distinguishing_one(self):
        a = self.mod.disambiguate("Patellofemoral Arthritis",
                                  "Patellofemoral Examination", self.budget,
                                  ["Patellofemoral Biomechanics"])
        b = self.mod.disambiguate("Patellofemoral Arthritis",
                                  "Patellofemoral Biomechanics", self.budget,
                                  ["Patellofemoral Examination"])
        self.assertNotEqual(a, b)
        self.assertIn("Examination", a)
        self.assertIn("Biomechanics", b)

    def test_a_shared_closing_word_is_dropped_before_the_distinguishing_one(self):
        a = self.mod.disambiguate("Examination Under Anaesthesia",
                                  "ACL Examination", self.budget,
                                  ["Rotational Instability Examination"])
        self.assertIn("ACL", a)

    def test_every_disambiguated_title_fits_the_bound(self):
        for chapter in ("Patellofemoral Examination", "ACL Examination",
                        "Tibiofemoral Contact Mechanics",
                        "Rotational Instability Examination"):
            out = self.mod.disambiguate("Effects of Malalignment", chapter,
                                        self.budget, ["Patellofemoral Biomechanics"])
            self.assertLessEqual(len(out), self.budget, out)


class TheSitemapCountAgreesWithTheSitemap(unittest.TestCase):
    """about/status.html quotes the number of urls in the sitemap, and the
    sitemap is written by a different tool.

    build_status.py used to read sitemap.xml to get the count, so adding a batch
    of pages made the status page quote the previous number until apply_chrome
    had written the sitemap and build_status had run again. Chapter 4.15 failed
    the suite on exactly that. Both now derive the path list from
    site_chrome.sitemap_paths(), and this holds the derived list against the file
    on disk so the two cannot drift apart again.
    """

    def test_the_file_lists_the_paths_the_function_derives(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import site_chrome as chrome
        path = os.path.join(REPO, "sitemap.xml")
        if not chrome.site_config().get("discoverable"):
            self.assertFalse(os.path.exists(path),
                             "a sitemap is offered while the site is not discoverable")
            return
        with io.open(path, encoding="utf-8") as fh:
            body = fh.read()
        self.assertEqual(body.count("<loc>"), len(chrome.sitemap_paths()))
        base = chrome.site_config()["base_url"]
        for rel in chrome.sitemap_paths():
            self.assertIn("<loc>%s%s</loc>" % (base, rel), body)


class TheSitemapCoversEveryPageTheSiteServes(unittest.TestCase):
    """site_chrome.sitemap_paths() used to end with eleven paths typed by hand.

    It listed the homepage, the section indexes and the three about pages, and
    it did not list the seven tier pages under levels/ or
    encyclopaedia/whole-body.html. All eight are linked from the navigation on
    every page of the site, so a reader reached them and a crawler following
    sitemap.xml did not. Nothing failed, because a page missing from a sitemap
    is still served, and the site has been discoverable since decision 026.

    The typed list was a copy of the navigation and drifted from it. The paths
    are now read out of header() and footer(), so a page added to either is in
    the sitemap from that moment. These tests hold both halves: that the
    derivation finds the navigation, and that the result leaves nothing served
    unlisted.
    """

    def served_pages(self):
        """Every html file the site publishes, by path from the repository root."""
        out = set()
        for base, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs
                       if d not in {".git", "pipeline", "docs", "node_modules",
                                    "assets"}]
            for name in files:
                if name.endswith(".html"):
                    out.add(os.path.relpath(os.path.join(base, name), REPO))
        return out

    def test_every_served_page_is_in_the_sitemap(self):
        if not chrome.site_config().get("discoverable"):
            self.skipTest("the site is not discoverable, so there is no sitemap")
        missing = sorted(self.served_pages() - set(chrome.sitemap_paths()))
        self.assertEqual(missing, [], "served and unlisted: %r" % (missing[:8],))

    def test_the_sitemap_lists_nothing_that_is_not_served(self):
        extra = sorted(set(chrome.sitemap_paths()) - self.served_pages())
        self.assertEqual(extra, [], "listed and not served: %r" % (extra[:8],))

    def test_the_navigation_is_where_the_extra_paths_come_from(self):
        """The eight that were missing are the point of the change."""
        nav = set(chrome.nav_targets())
        for rel in ("levels/junior.html", "levels/patient.html",
                    "levels/student.html", "levels/mrcs.html",
                    "levels/frcs.html", "levels/fellowship.html",
                    "levels/consultant.html", "encyclopaedia/whole-body.html"):
            self.assertIn(rel, nav)
            self.assertIn(rel, chrome.sitemap_paths())

    def test_the_derivation_drops_fragments_and_placeholders(self):
        """practise/index.html#cases is one page, and "#" is not a page."""
        nav = chrome.nav_targets()
        self.assertNotIn("#", "".join(nav))
        self.assertIn("practise/index.html", nav)
        for target in nav:
            self.assertFalse(target.startswith(("http", "mailto:")), target)

    def test_a_new_navigation_entry_reaches_the_sitemap(self):
        """The drift this replaced is the thing worth testing, so add a page to
        the ribbon and check it arrives without anything else being edited."""
        original = chrome.RIBBON
        page = os.path.join(REPO, "about", "standards.html")
        try:
            chrome.RIBBON = original + [
                ("Test", "about/standards.html",
                 [("Test entry", "about/standards.html#x")])]
            self.assertIn("about/standards.html", chrome.nav_targets())
            self.assertTrue(os.path.exists(page))
            self.assertIn("about/standards.html", chrome.sitemap_paths())
        finally:
            chrome.RIBBON = original


class HeldPagesAreNotCountedAsComingSoon(unittest.TestCase):
    """A page the client decided against is not a page that is coming soon.

    Written for chapter 5.19, the Magic Angle MRI Academy, held on 15 October
    2026. Before it, the Imaging Academy index read "8 of 224 pages are
    published; the rest are written in syllabus order", which promised ten pages
    that were never coming, and the chapter would have sat at nought of ten for
    ever.

    The client released 5.19 on 19 October 2026 and three of these tests failed,
    because they named that chapter instead of the rule. They now read the
    withheld block and check the arithmetic against whatever it holds, which at
    present is the three Section 0 pages held on 7 October. The mechanism is
    what matters and it is still live.
    """

    def setUp(self):
        self.root = os.path.dirname(ROOT)
        with open(os.path.join(ROOT, "config", "render_targets.json"),
                  encoding="utf-8") as fh:
            self.targets = json.load(fh)

    def test_the_withheld_block_is_not_empty_and_names_real_pages(self):
        """Something is held, and every held id is a page the architecture has.

        This replaced a test that asserted the ten ids of chapter 5.19. That
        chapter was released, so the assertion was about one client decision
        rather than about the withheld mechanism.
        """
        withheld = self.targets.get("withheld") or {}
        self.assertTrue(withheld, "the withheld block is empty")
        known = set()
        arch = os.path.join(ROOT, "config", "architecture")
        for name in sorted(os.listdir(arch)):
            if not name.endswith(".json"):
                continue
            with open(os.path.join(arch, name), encoding="utf-8") as fh:
                data = json.load(fh)
            items = data if isinstance(data, list) else data.get("pages", [])
            if isinstance(items, dict):
                items = list(items.values())
            for p in items:
                if isinstance(p, dict) and "page_id" in p:
                    known.add(p["page_id"])
        for page_id in withheld:
            self.assertIn(page_id, known, "held id is not in the architecture")

    def test_a_held_page_is_not_also_a_render_target(self):
        """An entry in both would publish a page the client declined."""
        both = set(self.targets["pages"]) & set(self.targets.get("withheld") or {})
        self.assertEqual(both, set())

    def test_every_held_entry_says_why(self):
        for page_id, entry in (self.targets.get("withheld") or {}).items():
            self.assertTrue(entry.get("reason"), page_id)
            self.assertTrue(entry.get("title"), page_id)

    def test_a_held_entry_claiming_a_draft_has_one(self):
        """The Section 0 holds were written before they were held and point at
        their draft. Chapter 5.19's were never written and say so, so the two
        kinds must not be confused."""
        for page_id, entry in (self.targets.get("withheld") or {}).items():
            if entry.get("written") is False:
                self.assertNotIn("draft", entry, page_id)
            else:
                draft = entry.get("draft")
                self.assertTrue(draft, page_id)
                self.assertTrue(os.path.exists(os.path.join(self.root, draft)),
                                "%s: %s" % (page_id, draft))

    def test_the_index_excludes_held_pages_from_its_total(self):
        """The denominator on a section index is designed minus held.

        The previous version of this test asserted the Imaging Academy's two
        literal numbers, 214 published of 224 designed, which were correct only
        while chapter 5.19 was held. It now computes the arithmetic, so it holds
        whichever pages are held and in whichever section.
        """
        withheld = set(self.targets.get("withheld") or {})
        arch = os.path.join(ROOT, "config", "architecture")
        designed = collections.Counter()
        held = collections.Counter()
        # The generator counts only the pages_*.json files, so this does too.
        # Counting outline_1_to_15.json as well made Section 2 come out at 237
        # designed pages against an index that says 79.
        for name in sorted(os.listdir(arch)):
            if not (name.startswith("pages_") and name.endswith(".json")):
                continue
            with open(os.path.join(arch, name), encoding="utf-8") as fh:
                for p in json.load(fh):
                    sid = str(p["page_id"]).split(".")[0]
                    designed[sid] += 1
                    if p["page_id"] in withheld:
                        held[sid] += 1
        checked = 0
        for sid, folder in (("2", "anatomy"), ("3", "biomechanics"),
                            ("4", "examination"), ("5", "imaging")):
            path = os.path.join(self.root, folder, "index.html")
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as fh:
                page = fh.read()
            total = designed[sid] - held[sid]
            self.assertTrue(
                ("of %d pages are published" % total) in page
                or ("All %d pages are published" % total) in page,
                "%s does not count %d pages" % (folder, total))
            if held[sid]:
                self.assertIn("are designed and are not being published", page)
                self.assertNotIn("of %d pages are published" % designed[sid], page)
            else:
                self.assertNotIn("are designed and are not being published", page)
            checked += 1
        self.assertTrue(checked, "no section index is built")



class TheRenderTargetRebuildsEverySectionIndex(unittest.TestCase):
    """EV-36. `make render` is the documented way to rebuild the published
    pages, and its recipe read `build_section_index.py 3` from the time Section
    3 was the newest section. That tool rebuilds every section when given no
    argument and only the named ones otherwise, so the target silently left the
    anatomy, examination and imaging indexes stale for months.

    Nothing failed, because the indexes were also rebuilt by hand on each
    content push. The defect would surface as a section index that does not
    list a page the site publishes, which the reachability test above catches
    one push later rather than at the point the wrong command ran.

    This holds the recipe itself. A section id in that line is the bug.
    """

    @classmethod
    def setUpClass(cls):
        cls.root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        with open(os.path.join(cls.root, "Makefile"), encoding="utf-8") as fh:
            cls.makefile = fh.read()

    def recipe_lines(self):
        """The render target's recipe, which is the tab indented block."""
        body = self.makefile.split("\nrender:\n", 1)
        self.assertEqual(len(body), 2, "the Makefile has no render target")
        lines = []
        for line in body[1].splitlines():
            if not line.startswith("\t"):
                break
            lines.append(line.strip())
        return lines

    def test_the_render_target_exists_and_has_a_recipe(self):
        self.assertTrue(self.recipe_lines())

    def test_the_section_index_is_rebuilt_with_no_section_argument(self):
        calls = [l for l in self.recipe_lines() if "build_section_index" in l]
        self.assertEqual(len(calls), 1, self.recipe_lines())
        trailing = calls[0].split("build_section_index.py", 1)[1].strip()
        self.assertEqual(trailing, "",
                         "make render would rebuild only section(s) %r" % trailing)

    def test_the_render_target_still_builds_the_status_page_and_chrome(self):
        """Fixing the argument must not drop the other two steps, which is the
        obvious way to break this while making the test pass."""
        joined = "\n".join(self.recipe_lines())
        for tool in ("render_site.py", "build_section_index.py",
                     "build_status.py", "apply_chrome.py"):
            self.assertIn(tool, joined)

    def test_the_status_page_is_built_after_the_section_indexes(self):
        """build_status.py counts published pages, so it reads what the index
        step has just written."""
        lines = self.recipe_lines()
        order = [i for i, l in enumerate(lines)
                 if "build_section_index.py" in l or "build_status.py" in l]
        self.assertEqual(len(order), 2)
        self.assertIn("build_section_index.py", lines[order[0]])
        self.assertIn("build_status.py", lines[order[1]])

    def test_the_chrome_is_applied_last(self):
        """apply_chrome.py rewrites the chrome of pages the earlier steps wrote,
        the status page among them, so it cannot run before them."""
        lines = self.recipe_lines()
        chrome = [i for i, l in enumerate(lines) if "apply_chrome.py" in l]
        self.assertEqual(len(chrome), 1)
        self.assertEqual(chrome[0], len(lines) - 1, lines)
