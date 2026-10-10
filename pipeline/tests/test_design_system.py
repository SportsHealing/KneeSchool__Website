"""The design system is MyKneeScore's, ported from SportsHealing/mykneescore at
commit 4ce92e0. These tests hold the port: the token values, the two typefaces,
and the one house rule adopted with them, that no colour literal appears outside
the stylesheet's :root block. See docs/decisions/012-mykneescore-design-system.md.
"""

import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
CSS = os.path.join(REPO, "assets", "styles.css")

# Copied from advanced/assets/advanced.css in the mykneescore repository. A test
# that restates the source is the only way a port can be checked without the
# source present, so the values are written out rather than fetched.
MYKNEESCORE_TOKENS = {
    "--green-deep": "#0e2b22",
    "--green-ink": "#16382d",
    "--green-soft": "#23503f",
    "--sage": "#7c9284",
    "--gold": "#b58f47",
    "--gold-pale": "#e6d5ac",
    "--ivory": "#faf7ef",
    "--paper": "#f3efe3",
    "--text": "#22312a",
    "--muted": "#45564c",
    "--warn": "#8c4a2f",
}


def css():
    with open(CSS, encoding="utf-8") as fh:
        return fh.read()


def root_block(src):
    m = re.search(r":root\s*\{.*?\n\}", src, re.DOTALL)
    assert m, "no :root block"
    return m.group(0)


class Tokens(unittest.TestCase):
    def test_every_mykneescore_token_is_declared_with_its_value(self):
        block = root_block(css())
        for name, value in MYKNEESCORE_TOKENS.items():
            self.assertIn("%s:%s" % (name, value), block.replace(" ", ""), name)

    def test_the_typefaces_are_theirs(self):
        block = root_block(css())
        self.assertIn("Cormorant Garamond", block)
        self.assertIn("Hanken Grotesk", block)

    def test_the_font_link_loads_both_families(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import site_chrome
        head = site_chrome.head("T", "d", "")
        self.assertIn("Cormorant+Garamond", head)
        self.assertIn("Hanken+Grotesk", head)

    def test_the_theme_colour_is_the_deep_green_token(self):
        with open(os.path.join(ROOT, "config", "site.json")) as fh:
            self.assertEqual(json.load(fh)["theme_color"],
                             MYKNEESCORE_TOKENS["--green-deep"])


class NoColourLiterals(unittest.TestCase):
    """Their house style check calls this their highest value CSS rule."""

    def test_the_stylesheet_has_no_literal_outside_root(self):
        src = css()
        stripped = src.replace(root_block(src), "")
        hits = re.findall(r"#[0-9a-fA-F]{3,8}\b|rgba?\([0-9][^)]*\)", stripped)
        self.assertEqual(hits, [], "literals outside :root")

    def test_the_site_check_fails_on_a_planted_literal(self):
        """Plant one in a real page, run the real checker, require a failure."""
        page = os.path.join(REPO, "about", "standards.html")
        with open(page, encoding="utf-8") as fh:
            original = fh.read()
        damaged = original.replace("</head>", '<style>.x{color:#ff0000}</style>\n</head>', 1)
        self.assertNotEqual(original, damaged)
        try:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(damaged)
            out = subprocess.run(
                [sys.executable, os.path.join(REPO, "tools", "check_site.py")],
                capture_output=True, text=True, cwd=REPO)
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("colour literal", out.stdout)
        finally:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(original)

    def test_the_theme_colour_meta_is_the_one_allowed_literal(self):
        """An HTML attribute cannot read a custom property, so that one stays."""
        out = subprocess.run(
            [sys.executable, os.path.join(REPO, "tools", "check_site.py")],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(out.returncode, 0, out.stdout)
        with open(os.path.join(REPO, "index.html"), encoding="utf-8") as fh:
            self.assertIn('name="theme-color"', fh.read())


class WebFonts(unittest.TestCase):
    """The port changed the typefaces and fourteen pages kept fetching the old
    pair. Nothing failed, because a page that cannot load its font falls back
    quietly, so the site verified clean while its most visited pages rendered in
    Georgia and Helvetica. These tests hold the fix."""

    def setUp(self):
        sys.path.insert(0, os.path.join(REPO, "tools"))
        import site_chrome
        self.chrome = site_chrome
        with open(CSS, encoding="utf-8") as fh:
            self.css = fh.read()

    def families(self, text):
        return sorted(set(re.findall(r"family=([A-Za-z+]+)", text)))

    def test_the_font_block_has_one_definition(self):
        """apply_chrome and the renderer both read site_chrome.FONT_LINKS."""
        self.assertTrue(hasattr(self.chrome, "FONT_LINKS"))
        for name in ("apply_chrome.py", "check_site.py"):
            with open(os.path.join(REPO, "tools", name), encoding="utf-8") as fh:
                self.assertIn("FONT_LINKS", fh.read(), name)

    def test_the_fetched_families_are_the_ones_the_stylesheet_names(self):
        fetched = self.families(self.chrome.FONT_LINKS)
        self.assertEqual(fetched, ["Cormorant+Garamond", "Hanken+Grotesk"])
        for token, family in (("--display", "Cormorant Garamond"),
                              ("--body", "Hanken Grotesk")):
            m = re.search(re.escape(token) + r":\s*\"([^\"]+)\"", self.css)
            self.assertIsNotNone(m, token)
            self.assertEqual(m.group(1), family)

    def test_every_page_fetches_the_same_two(self):
        want = self.families(self.chrome.FONT_LINKS)
        for base, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs
                       if d not in {".git", "pipeline", "docs", "node_modules", "assets"}]
            for name in sorted(files):
                if not name.endswith(".html"):
                    continue
                path = os.path.join(base, name)
                with open(path, encoding="utf-8") as fh:
                    got = self.families(fh.read())
                self.assertEqual(got, want, os.path.relpath(path, REPO))

    def test_check_site_refuses_a_page_that_fetches_the_wrong_pair(self):
        path = os.path.join(REPO, "index.html")
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(original.replace("family=Cormorant+Garamond", "family=Newsreader"))
            out = subprocess.run(
                [sys.executable, os.path.join(REPO, "tools", "check_site.py")],
                capture_output=True, text=True, cwd=REPO)
            self.assertEqual(out.returncode, 1, out.stdout)
            self.assertIn("fetches web fonts", out.stdout)
        finally:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(original)


if __name__ == "__main__":
    unittest.main()
