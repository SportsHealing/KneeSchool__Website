#!/usr/bin/env python3
"""Render a pipeline article into a site page.

    python3 tools/render_article.py pipeline/runs/1.2.3/styled_v1.md \
        --brief pipeline/config/briefs/1.2.3.json \
        --out encyclopaedia/menisci.html

The input is markdown in the Operations Handbook article template. The output is
a standalone page in the site's own design, with the tier blocks carried by the
depth dial. Every pipeline page renders through here, so they all look alike and
a template change lands everywhere at once.

The hand written pages of the site are not touched by this; they stay hand
written. This is the join between the content factory and the website.
"""

import argparse
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import site_chrome as chrome  # noqa: E402

TEMPLATE_PATH = os.path.join(ROOT, "pipeline", "config", "article_template.json")

# The dial tab is a control, the handbook heading is the content. They are
# allowed to differ: a tab has to fit seven across a phone screen.
TAB_LABELS = {
    "junior": "Junior", "patient": "Patient", "medical_student": "Student",
    "mrcs": "MRCS", "frcs": "FRCS", "fellowship": "Fellow", "consultant": "Consultant",
}


def esc(t):
    return html.escape(t, quote=False)


def inline(text):
    """The small subset of markdown the template actually uses."""
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"<span class='pid'>\1</span>\2", text)
    return text


def blocks(lines):
    """Group body lines into ('p', text) / ('ul', [items]) blocks."""
    out, para, items = [], [], []

    def flush():
        if para:
            out.append(("p", " ".join(para)))
            del para[:]
        if items:
            out.append(("ul", list(items)))
            del items[:]

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        m = re.match(r"^[-*+]\s+(.*)$", stripped)
        if m:
            if para:
                out.append(("p", " ".join(para)))
                del para[:]
            items.append(m.group(1))
        else:
            if items:
                out.append(("ul", list(items)))
                del items[:]
            para.append(stripped)
    flush()
    return out


def render_body(lines, indent="            "):
    parts = []
    for kind, payload in blocks(lines):
        if kind == "p":
            parts.append("%s<p>%s</p>" % (indent, inline(payload)))
        else:
            lis = "".join("<li>%s</li>" % inline(i) for i in payload)
            parts.append("%s<ul>%s</ul>" % (indent, lis))
    return "\n".join(parts)


def parse(md):
    """Split the article into title, summary, tier blocks and article sections."""
    lines = md.split("\n")
    doc = {"title": "", "summary": "", "tiers": [], "sections": {}}
    heads = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.*?)\s*$", line)
        if m:
            heads.append((len(m.group(1)), m.group(2), i))

    for level, title, i in heads:
        if level == 1 and not doc["title"]:
            doc["title"] = title

    # summary is the first non blank line after the H1, before any H2
    h1 = next((i for lvl, t, i in heads if lvl == 1), 0)
    nxt = next((i for lvl, t, i in heads if i > h1), len(lines))
    doc["summary"] = " ".join(l.strip() for l in lines[h1 + 1:nxt] if l.strip())

    with open(TEMPLATE_PATH) as fh:
        tpl = json.load(fh)
    by_heading = dict((v, k) for k, v in tpl["tier_headings"].items())

    h2s = [(t, i) for lvl, t, i in heads if lvl == 2]
    for n, (title, start) in enumerate(h2s):
        end = h2s[n + 1][1] if n + 1 < len(h2s) else len(lines)
        tier = by_heading.get(title)
        if tier:
            subs = [(t, i) for lvl, t, i in heads if lvl == 3 and start < i < end]
            parts = []
            for k, (sub_title, sub_start) in enumerate(subs):
                sub_end = subs[k + 1][1] if k + 1 < len(subs) else end
                parts.append((sub_title, lines[sub_start + 1:sub_end]))
            tail_start = subs[-1][1] if subs else start
            closer = []
            if subs:
                last_end = end
                body = lines[subs[-1][1] + 1:last_end]
                # a trailing paragraph that is not part of the last subsection
                while body and not body[-1].strip():
                    body.pop()
            doc["tiers"].append({"tier": tier, "heading": title, "sections": parts,
                                 "closer": closer, "span": (start, end)})
        else:
            doc["sections"][title] = lines[start + 1:end]
    return doc, tpl


def render_tier(block, tpl):
    """One dial panel. Key learning points and FAQs get their own treatment."""
    klp = tpl["key_learning_points"]["heading"]
    faq = tpl["faqs"]["heading"]
    closer_msg = ((tpl.get("tier_closers") or {}).get(block["tier"]) or {}).get("message")

    parts = []
    for title, body in block["sections"]:
        if title == klp:
            parts.append('            <div class="klp">\n              <h4>%s</h4>\n%s\n            </div>'
                         % (esc(title), render_body(body, "              ")))
        elif title == faq:
            parts.append('            <div class="faq">\n              <h4>%s</h4>\n%s\n            </div>'
                         % (esc(title), render_body(body, "              ")))
        else:
            parts.append("            <h4>%s</h4>\n%s" % (esc(title), render_body(body)))

    # the standard closing message is lifted out of the flow and marked
    rendered = "\n".join(parts)
    if closer_msg:
        target = "<p>%s</p>" % inline(closer_msg)
        if target in rendered:
            rendered = rendered.replace(target, '<p class="closer">%s</p>' % inline(closer_msg))
    return rendered


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown")
    ap.add_argument("--brief", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--status", default="Editorial draft. Not evidence verified. Not consultant reviewed. Not for clinical use.")
    ap.add_argument("--parent", help='breadcrumb parent as "Label|href"; defaults to the brief section pointing at the homepage encyclopaedia')
    args = ap.parse_args()

    with open(args.markdown) as fh:
        doc, tpl = parse(fh.read())
    with open(args.brief) as fh:
        brief = json.load(fh)

    rel = "../" if "/" in args.out else ""
    order = tpl["tier_order"]
    tiers = sorted(doc["tiers"], key=lambda b: order.index(b["tier"]))

    inputs = "\n".join(
        '        <input type="radio" name="depth" id="t%d"%s>' % (i, " checked" if i == 0 else "")
        for i in range(len(tiers)))
    tabs = "\n".join('          <label for="t%d">%s</label>' % (i, TAB_LABELS[b["tier"]])
                     for i, b in enumerate(tiers))
    panels = "\n".join(
        '          <div class="dial-panel p%d">\n            <h3>%s</h3>\n%s\n          </div>'
        % (i, esc(b["heading"]), render_tier(b, tpl))
        for i, b in enumerate(tiers))

    # dial selectors are generated because the tier count varies by page
    css = []
    for i in range(len(tiers)):
        css.append("#t%d:checked ~ .dial-tabs label[for=t%d]{color:var(--ivory);border-top-color:var(--gold)}" % (i, i))
        css.append("#t%d:checked ~ .dial-body .p%d{display:block}" % (i, i))
        css.append("#t%d:focus-visible ~ .dial-tabs label[for=t%d]{outline:2px solid var(--gold);outline-offset:2px}" % (i, i))
    dial_css = "<style>\n.dial-tabs{grid-template-columns:repeat(%d,1fr)}\n%s\n</style>" % (
        len(tiers), "\n".join(css))

    if args.parent:
        label, _, href = args.parent.partition("|")
        parent = (label, href)
    else:
        parent = (brief.get("section", {}).get("name", "Encyclopaedia"),
                  rel + "encyclopaedia/index.html")

    explore = doc["sections"].get(tpl["cross_links"]["heading"], [])
    items = []
    for line in explore:
        m = re.match(r"^\s*[-*+]\s+\[\[([^|\]]+)\|([^\]]+)\]\]\s*$", line)
        if m:
            items.append('        <li><span class="pid">%s</span><span class="pending">%s</span></li>'
                         % (esc(m.group(1).strip()), esc(m.group(2).strip())))
    refs = doc["sections"].get("References", [])

    page = chrome.head("%s | KneeSchool" % doc["title"], doc["summary"][:160], rel)
    page += dial_css + "\n"
    page += chrome.header(rel)
    page += """
<main id="top">

  <section class="page-hero">
    <div class="wrap">
      %s
      <div class="hero-split">
        <div>
          <h1>%s</h1>
          <p class="who">Page %s &middot; %s &middot; %s page</p>
          <p class="lede">%s</p>
        </div>
        <div>
          <div class="status"><b>Pipeline status.</b> %s</div>
        </div>
      </div>
    </div>
  </section>

  <section class="band dark">
    <div class="wrap">
      <div class="sec-head">
        <h2>The same topic at %d depths</h2>
        <p class="lede">Each tier deepens the one below it and never repeats it. Choose the level you want.</p>
      </div>
      <div class="dial dial-article">
        <div class="dial-head">
          <h2>%s</h2>
          <small>Choose a depth</small>
        </div>
%s
        <div class="dial-tabs">
%s
        </div>
        <div class="dial-body">
%s
        </div>
      </div>
    </div>
  </section>

  <section class="band wrap">
    <div class="sec-head">
      <h2>%s</h2>
      <p class="lede">Where this topic came from and where it goes next in the spiral.</p>
    </div>
    <ul class="explore">
%s
    </ul>
  </section>

  <section class="band wrap" style="padding-top:0">
    <div class="sec-head">
      <h2>References</h2>
    </div>
    <div class="prose refs">
%s
    </div>
    <p class="safety"><b>Safety.</b> KneeSchool is educational and does not give individual medical advice. Seek urgent assessment for a knee that cannot bear weight after an injury, a hot swollen knee with a fever, or new numbness, weakness or coldness in the leg or foot.</p>
  </section>

</main>

""" % (chrome.crumb([("KneeSchool", rel + "index.html"),
                     parent,
                     (doc["title"], None)]),
       esc(doc["title"]), esc(brief.get("page_id", "")),
       esc(brief.get("chapter", {}).get("name", "")), esc(brief.get("page_type", "")),
       esc(doc["summary"]), esc(args.status),
       len(tiers), esc(doc["title"]), inputs, tabs, panels,
       esc(tpl["cross_links"]["heading"]),
       "\n".join(items), render_body(refs, "      "))
    page += chrome.footer(rel)

    with open(args.out, "w") as fh:
        fh.write(page)
    print("%s written, %d tiers, %d cross links" % (args.out, len(tiers), len(items)))


if __name__ == "__main__":
    main()
