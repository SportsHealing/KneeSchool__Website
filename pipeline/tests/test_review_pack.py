"""EV-2 has had reviewers and no return path since the build began. The pack
generator is that path, so these tests hold both directions of it: a pack is
generated from the work, and a filled pack is read back into the registers.

The round trip is the part worth testing. A pack that cannot be ingested is a
document, and a document is what the build already had.
"""

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(REPO, "tools"))
import review_pack  # noqa: E402

PACKS = os.path.join(REPO, "docs", "review", "packs")


def run(*args):
    return subprocess.run([sys.executable, os.path.join(REPO, "tools", "review_pack.py")]
                          + list(args), capture_output=True, text=True, cwd=REPO)


class Generation(unittest.TestCase):

    def test_every_chapter_with_a_published_page_has_a_pack(self):
        for chapter in review_pack.chapters_with_pages():
            self.assertTrue(os.path.exists(review_pack.pack_path(chapter)),
                            "no pack for chapter %s" % chapter)

    def test_no_pack_has_drifted_from_the_work(self):
        out = run("--check")
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertNotIn("drifted", out.stdout)

    def test_a_pack_states_the_counts_its_registers_hold(self):
        chapter = "3.3"
        facts = [review_pack.page_facts(p)
                 for p in review_pack.chapter_pages(chapter)]
        unsigned = len([p for f in facts for p in f["positions"]
                        if p["verification"] == "UNSIGNED"])
        unchecked = len([g for f in facts for g in f["figures"]
                         if g["verification"] == "UNVERIFIED_FROM_MEMORY"])
        with open(review_pack.pack_path(chapter), encoding="utf-8") as fh:
            body = fh.read()
        self.assertIn("| Recommendations to sign | %d |" % unsigned, body)
        self.assertIn("| Measurements to check | %d |" % unchecked, body)

    def test_a_pack_says_verification_never_ran(self):
        """Every pack carries the statement, because every page does."""
        for chapter in review_pack.chapters_with_pages():
            with open(review_pack.pack_path(chapter), encoding="utf-8") as fh:
                self.assertIn("did not run on any page", fh.read(), chapter)

    def test_a_row_reference_survives_the_table(self):
        with open(review_pack.pack_path("3.3"), encoding="utf-8") as fh:
            rows = review_pack.parse_rows(fh.read())
        self.assertTrue(rows)
        kinds = {r[1] for r in rows}
        self.assertEqual(kinds, {"P", "F"})
        for page_id, kind, index, _ in rows:
            self.assertTrue(index >= 1)
            self.assertEqual(page_id.count("."), 2)

    def test_a_sentence_containing_a_pipe_cannot_break_a_table(self):
        self.assertNotIn("|", review_pack.cell("a | b").replace("\\|", ""))


class Ingest(unittest.TestCase):
    """The registers are real files, so each test restores what it touched."""

    def setUp(self):
        self.touched = {}
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        for path, original in self.touched.items():
            with io.open(path, "w", encoding="utf-8") as fh:
                fh.write(original)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def keep(self, path):
        with open(path, encoding="utf-8") as fh:
            self.touched[path] = fh.read()

    def filled(self, chapter, replacements):
        with open(review_pack.pack_path(chapter), encoding="utf-8") as fh:
            body = fh.read()
        for old, new in replacements:
            self.assertIn(old, body)
            body = body.replace(old, new)
        path = os.path.join(self.tmp, "filled.md")
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        return path

    def row(self, chapter, ref):
        with open(review_pack.pack_path(chapter), encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("| %s |" % ref):
                    return line.rstrip("\n")
        self.fail("no row %s in chapter %s" % (ref, chapter))

    def test_a_confirmed_recommendation_reaches_its_register(self):
        reg = os.path.join(REPO, "pipeline", "config", "positions", "3.3.1.json")
        self.keep(reg)
        line = self.row("3.3", "3.3.1-P1")
        path = self.filled("3.3", [(line, line[:-4] + " CONFIRMED | Miss B Surgeon |")])
        out = run("--ingest", path)
        self.assertEqual(out.returncode, 0, out.stdout)
        with open(reg, encoding="utf-8") as fh:
            entry = json.load(fh)["positions"][0]
        self.assertEqual(entry["verification"], "CONFIRMED")
        self.assertEqual(entry["signed_off_by"], "Miss B Surgeon")

    def test_a_corrected_figure_keeps_the_replacement_wording(self):
        reg = os.path.join(REPO, "pipeline", "config", "figures", "3.3.2.json")
        self.keep(reg)
        line = self.row("3.3", "3.3.2-F1")
        path = self.filled("3.3", [(line, line[:-4] + " CORRECTED: read 0 to 25 | A textbook |")])
        out = run("--ingest", path)
        self.assertEqual(out.returncode, 0, out.stdout)
        with open(reg, encoding="utf-8") as fh:
            entry = json.load(fh)["figures"][0]
        self.assertEqual(entry["verification"], "CORRECTED")
        self.assertEqual(entry["source"], "A textbook")
        self.assertEqual(entry["note"], "read 0 to 25")

    def test_an_unfilled_pack_changes_nothing_and_is_not_an_error(self):
        """A reviewer who has read a pack and answered nothing yet has done
        nothing wrong, so ingesting it reports the blanks and succeeds."""
        reg = os.path.join(REPO, "pipeline", "config", "positions", "3.3.1.json")
        with open(reg, encoding="utf-8") as fh:
            before = fh.read()
        out = run("--ingest", review_pack.pack_path("3.3"))
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("0 decision(s) written", out.stdout)
        self.assertIn("row(s) still blank", out.stdout)
        with open(reg, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), before)

    def test_a_file_with_no_referenced_rows_is_refused(self):
        path = os.path.join(self.tmp, "notapack.md")
        with io.open(path, "w", encoding="utf-8") as fh:
            fh.write("# Notes\n\n| Page | Title |\n|---|---|\n| 3.3.1 | Kinematics |\n")
        out = run("--ingest", path)
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("no referenced rows found", out.stdout)

    def test_an_unknown_decision_writes_nothing_at_all(self):
        """One bad row must not leave a half signed register behind."""
        reg = os.path.join(REPO, "pipeline", "config", "positions", "3.3.1.json")
        self.keep(reg)
        good = self.row("3.3", "3.3.1-P1")
        bad = self.row("3.3", "3.3.1-P2")
        path = self.filled("3.3", [(good, good[:-4] + " CONFIRMED | Miss B Surgeon |"),
                                   (bad, bad[:-4] + " LOOKS FINE | Miss B Surgeon |")])
        out = run("--ingest", path)
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("nothing written", out.stdout)
        with open(reg, encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["positions"][0]["verification"], "UNSIGNED")

    def test_a_decision_survives_re_extraction(self):
        """The extractor rewrites a register from the page on every chapter, so a
        signature that does not survive it would be lost on the next build."""
        reg = os.path.join(REPO, "pipeline", "config", "positions", "3.3.1.json")
        self.keep(reg)
        line = self.row("3.3", "3.3.1-P1")
        path = self.filled("3.3", [(line, line[:-4] + " CONFIRMED | Miss B Surgeon |")])
        self.assertEqual(run("--ingest", path).returncode, 0)
        subprocess.check_call([sys.executable, os.path.join(REPO, "tools", "positions.py"),
                               "--extract"], cwd=REPO, stdout=subprocess.DEVNULL)
        with open(reg, encoding="utf-8") as fh:
            entry = json.load(fh)["positions"][0]
        self.assertEqual(entry["verification"], "CONFIRMED")
        self.assertEqual(entry["signed_off_by"], "Miss B Surgeon")


if __name__ == "__main__":
    unittest.main()
