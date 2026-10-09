# -*- coding: utf-8 -*-
"""Shared header and footer for the KneeSchool static pages.

There is no build step on the site itself, so this emits complete standalone
HTML. tools/apply_chrome.py rewrites the header and footer of every page from
here, which is what keeps ten hand written pages in step with each other.

Every path is relative with no leading slash, so the pages work from the
filesystem, from a subdirectory and from a host root alike.

The ribbon is four categories with dropdowns. It carries no JavaScript: the
menus open on hover and on keyboard focus, and at phone width the whole thing
expands into one list behind the Menu checkbox.
"""

import hashlib
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SITE = os.path.join(_ROOT, "pipeline", "config", "site.json")


def site_config():
    with open(_SITE, encoding="utf-8") as fh:
        return json.load(fh)


def canonical_url(published_path):
    """The absolute URL of a page, from its path under the repository root.

    Chapter 14 of the Master Operations Handbook requires a slug on every page
    and the publication gate checks that the canonical link agrees with where
    the file actually sits. Every other path in the chrome is relative, so this
    is the one place the site needs to know its own domain, and the domain comes
    from pipeline/config/site.json rather than from here.
    """
    base = site_config()["base_url"].rstrip("/") + "/"
    path = published_path.replace(os.sep, "/").lstrip("./")
    if path == "index.html":
        return base
    return base + path


def stylesheet_version():
    """A short hash of the stylesheet, used as a query string on its link.

    Without it a browser that has the old stylesheet cached keeps using it
    against the new markup. That failure is worse than no styling at all: the
    dropdown menus have no rule hiding them, so every menu renders open and the
    ribbon collapses into one long row. Changing the URL whenever the file
    changes makes a stale copy impossible.
    """
    path = os.path.join(_ROOT, "assets", "styles.css")
    try:
        with open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:8]
    except IOError:
        return "0"


TIERS = ["junior", "patient", "student", "mrcs", "frcs", "fellowship", "consultant"]

LEVEL_NAMES = {
    "junior": "Junior Academy",
    "patient": "Patient Academy",
    "student": "Student Academy",
    "mrcs": "MRCS Academy",
    "frcs": "FRCS (Tr and Orth) Academy",
    "fellowship": "Fellowship Academy",
    "consultant": "Consultant Masterclass",
}

# (category label, category href, [(item label, item href)])
# hrefs are written relative to the site root and rewritten per page depth.
RIBBON = [
    ("Learn", "index.html#levels", [
        ("Find your level", "index.html#levels"),
    ] + [("%s" % LEVEL_NAMES[t], "levels/%s.html" % t) for t in TIERS]
      # Chapter 0.7 is written for adults, and the only route to it was a page
      # headed Junior Academy. A teacher or coach is not going to look there.
      + [("For teachers and coaches", "junior/ready-made-lesson-plans.html")]),

    ("Reference", "encyclopaedia/index.html", [
        ("The knee encyclopaedia", "encyclopaedia/index.html"),
        ("The Anatomy Academy", "anatomy/index.html"),
        ("Conditions library", "conditions/index.html"),
        ("Whole body factors", "encyclopaedia/whole-body.html"),
    ]),

    ("Practise", "practise/index.html", [
        ("Question bank", "practise/index.html#questions"),
        ("Case library", "practise/index.html#cases"),
        ("Video academy", "practise/index.html#video"),
        ("Knee score centre", "practise/index.html#scores"),
    ]),

    ("About", "about/standards.html", [
        ("How a page reaches this site", "about/standards.html"),
        ("Mapped to the UK training pathway", "about/curriculum.html"),
        # Published pages point readers here when a feature is not available yet.
        ("Build status", "about/status.html"),
        ("Authors and reviewers", "#"),
        ("References and sources", "#"),
        ("Contact", "#"),
    ]),
]


def depth_bar(position, total=7, cls="depth"):
    """position is 1 based: junior is 1, consultant is 7."""
    return ('<span class="%s">' % cls
            + "".join('<i class="on"></i>' if i < position else "<i></i>"
                      for i in range(total))
            + "</span>")


def _href(target, rel):
    """Rewrite a root relative href for a page sitting `rel` deep."""
    if target.startswith(("http", "mailto:")) or target == "#":
        return target
    if rel == "" and target.startswith("index.html#"):
        return target[len("index.html"):]          # stay on the page
    return rel + target


def head(title, description, rel, extra_meta="", canonical=None):
    return """<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%s</title>
<meta name="description" content="%s">
<meta name="theme-color" content="%s">
%s%s<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Hanken+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="%sassets/styles.css?v=%s">
</head>
<body>
""" % (title, description, site_config()["theme_color"],
       '<link rel="canonical" href="%s">\n' % canonical_url(canonical) if canonical else "",
       extra_meta, rel, stylesheet_version())


def header(rel):
    home = "index.html" if rel == "" else rel + "index.html"
    groups = []
    for n, (label, top_href, items) in enumerate(RIBBON, 1):
        lis = "\n".join(
            '            <li><a href="%s">%s</a></li>' % (_href(h, rel), t)
            for t, h in items)
        groups.append("""        <li class="has-menu">
          <a class="top" href="%s">%s<span class="caret" aria-hidden="true"></span></a>
          <ul class="menu">
%s
          </ul>
        </li>""" % (_href(top_href, rel), label, lis))
    # MyKneeScore ends its nav with a single filled pill, the one action it wants
    # a visitor to take. Here that action is choosing a depth, because every page
    # on this site is written seven times and the reader has to pick one.
    groups.append('        <li><a class="start-link" href="%s">Find your level</a></li>'
                  % _href("index.html#levels", rel))
    return """<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="%s"><b>Knee</b><span>School</span></a>
    <input class="nav-toggle" type="checkbox" id="navtoggle" aria-label="Show navigation">
    <label class="burger" for="navtoggle">Menu</label>
    <nav class="nav" aria-label="Main">
      <ul>
%s
      </ul>
    </nav>
  </div>
</header>
""" % (home, "\n".join(groups))


def footer(rel):
    learn = "\n".join(
        '          <li><a href="%slevels/%s.html">%s</a></li>' % (rel, t, LEVEL_NAMES[t])
        for t in TIERS)
    return """<footer class="site-foot" id="about">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <h3>Learn</h3>
        <ul>
%s
        </ul>
      </div>
      <div>
        <h3>Reference</h3>
        <ul>
          <li><a href="%sencyclopaedia/index.html">The knee encyclopaedia</a></li>
          <li><a href="%sconditions/index.html">Conditions library</a></li>
          <li><a href="%sencyclopaedia/whole-body.html">Whole body factors</a></li>
          <li><a href="%spractise/index.html">Practise and test</a></li>
        </ul>
      </div>
      <div>
        <h3>Clinical care</h3>
        <ul>
          <li><a href="https://www.chinmaygupte.com/">Consultant clinic</a></li>
          <li><a href="#">Imaging and injections</a></li>
          <li><a href="#">Rehabilitation programmes</a></li>
          <li><a href="#">Braces and recovery products</a></li>
        </ul>
      </div>
      <div>
        <h3>About</h3>
        <ul>
          <li><a href="%sabout/standards.html">How a page reaches this site</a></li>
          <li><a href="%sabout/curriculum.html">Mapped to the UK training pathway</a></li>
          <li><a href="%slevels/junior.html">For teachers and coaches</a></li>
          <li><a href="#">Authors and reviewers</a></li>
          <li><a href="#">Contact</a></li>
        </ul>
      </div>
    </div>
    <div class="legal">
      <p>KneeSchool is educational. It does not give individual medical advice and it does not replace assessment by a clinician. Seek urgent care for a hot, swollen knee with fever, a knee that cannot bear weight after injury, or new numbness in the leg.</p>
      <p>Content written for school age learners carries no advertising and no product placement.</p>
      <p>&copy; 2026 KneeSchool. All rights reserved.</p>
    </div>
  </div>
</footer>

</body>
</html>
""" % (learn, rel, rel, rel, rel, rel, rel, rel)


def crumb(items):
    """items is [(label, href_or_None)]; the last one carries no link."""
    parts = []
    for label, href in items:
        parts.append('<a href="%s">%s</a>' % (href, label) if href else label)
    return '<p class="crumb">' + '<span>/</span>'.join(parts) + '</p>'
