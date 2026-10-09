# KneeSchool.com

Static front end and content pipeline for KneeSchool, a spiral knee curriculum
that teaches the same topic seven times at increasing depth.

```
index.html          the homepage
assets/styles.css   one shared stylesheet, no build step, no JavaScript
levels/             seven level landing pages, one per tier
conditions/         the conditions library and the ACL article
encyclopaedia/      reference pages, starting with 1.2.3 Menisci
tools/              check_site.py, publication_qa.py, architecture.py, render_article.py
pipeline/           the three agent content pipeline: prompts, config,
                    Lambdas, Step Functions definition, SAM template, tests
pipeline/runs/      pipeline output, one folder per page
docs/               the handbook, the architecture, the handover, the team pack
```

## The three documents that govern everything

1. **Operations Handbook.** The article template, editorial standards and the QA
   manual. Where any document disagrees with it, it wins.
2. **Master Publishing Architecture.** Every page's number, tiers, siblings and,
   most importantly, what it must not cover. That last list is what stops the
   same fact being written across three thousand pages.
3. **lint_rules.json.** The deterministic style gate.

The first two are configuration, not prose to be reinterpreted.
`pipeline/config/article_template.json` is extracted from the handbook and
`pipeline/config/architecture/` from the architecture, so the code reads them
rather than restating them.

## Producing a page

```bash
python3 tools/architecture.py show 1.2.3                     # what the architecture says
python3 tools/architecture.py brief 1.2.3 --out pipeline/config/briefs/1.2.3.json
make -C pipeline lint DRAFT=pipeline/runs/1.2.3/styled_v1.md BRIEF=config/briefs/1.2.3.json
python3 tools/render_article.py pipeline/runs/1.2.3/styled_v1.md \
    --brief pipeline/config/briefs/1.2.3.json --out encyclopaedia/menisci.html
```

## The seven tiers

Junior, Patient, Student, MRCS, FRCS (Tr and Orth), Fellowship, Consultant
Masterclass. Each tier assumes the one below it and adds a layer rather than
repeating it.

## Site

`index.html` has no build step. Open it, or serve the directory:

```bash
python3 -m http.server 8000
```

Check every page at once:

```bash
python3 tools/check_site.py
```

That covers tag balance, `lang`, em and en dashes, space hyphen space, the
banned phrase and UK spelling rules from the pipeline config, the educational
and not a substitute statement required by the handbook, and whether every
relative link and in-page anchor actually resolves. Exit code 1 on any failure.

Then publication QA, the fifth gate:

```bash
python3 tools/publication_qa.py            # failures only
python3 tools/publication_qa.py --report   # every rule on every page
```

Nine rules covering the SEO title, the meta description, the slug and canonical
link, the heading ladder, image alt text, the disclaimer, internal linking,
head metadata, and whether any two pages share a title or a description. Bounds
live in `pipeline/config/site.json`. See `docs/decisions/010-publication-qa-the-fifth-gate.md`.

Then check by eye at 375px, 768px and 1440px. Single page structure check:

```bash
python3 - <<'EOF'
from html.parser import HTMLParser
VOID={'area','base','br','col','embed','hr','img','input','link','meta','source','track','wbr'}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.st=[]; s.err=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.st.append(t)
    def handle_endtag(s,t):
        if not s.st or s.st[-1]!=t: s.err.append((t,s.getpos()))
        else: s.st.pop()
p=P(); txt=open('index.html').read(); p.feed(txt)
print("errors:",p.err,"unclosed:",p.st)
print("dashes:", '—' in txt or '–' in txt)
EOF
```

## Pipeline

```bash
make -C pipeline test     # 68 tests, no AWS account needed
make -C pipeline lint DRAFT=path/to/draft.md
```

See `pipeline/README.md` for the architecture, the deployment steps and the
decisions that are still open.

## House rules

British English. No em dashes and no en dashes. Short sentences, one idea each.
Sentence case headings. Buttons name the action. No unsupported clinical claims
and no invented references. Every clinical page carries the educational
disclaimer and the red flag advice.

Consultant review is mandatory before publication and cannot be bypassed. The
state machine enforces that structurally, and `pipeline/tests/` asserts it.
