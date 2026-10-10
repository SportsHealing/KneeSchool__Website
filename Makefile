# KneeSchool.com
#
#   make verify    every gate, in order, stopping at the first failure
#   make test      the test suite alone
#   make render    rebuild the published pages from the styled markdown
#
# `verify` is what CI runs and what to run before pushing. It exists because the
# gates used to be five separate invocations held in one person's head, so a
# contributor could not know the list, CI could not run it, and "the gates pass"
# rested on somebody saying so. See decision 021.
#
# The content pipeline has its own targets for linting a single draft and for
# the AWS deployment: see pipeline/Makefile.

PYTHON ?= python3

.PHONY: verify test gates render clean

# One recipe line, so the baseline path survives between the steps. It is held
# outside the working tree: a baseline file inside the repository is itself an
# untracked file, which the last step would then report as a change the checks
# made. It did, the first time this target ran.
verify:
	@set -e; \
	baseline=$$(mktemp); \
	trap 'rm -f "$$baseline"' EXIT; \
	$(PYTHON) tools/check_clean.py --write-baseline "$$baseline" >/dev/null; \
	$(MAKE) --no-print-directory test; \
	$(MAKE) --no-print-directory gates; \
	$(PYTHON) tools/check_clean.py --baseline "$$baseline"; \
	echo; \
	echo "all gates passed"

test:
	@echo "== test suite =="
	$(PYTHON) -m unittest discover -s pipeline/tests

# Every target here exits non zero on a finding, so make stops at the first one.
gates:
	@echo "== style gate, every page with a brief and a draft =="
	$(PYTHON) tools/lint_site.py
	@echo "== site checks: links, chrome, fonts, stylesheet =="
	$(PYTHON) tools/check_site.py
	@echo "== publication QA, the fifth gate =="
	$(PYTHON) tools/publication_qa.py
	@echo "== cross link labels =="
	$(PYTHON) tools/crossrefs.py --check
	@echo "== prose references against the architecture =="
	$(PYTHON) tools/crossrefs.py --prose-check
	@echo "== review packs match the registers =="
	$(PYTHON) tools/review_pack.py --check

render:
	$(PYTHON) tools/render_site.py
	$(PYTHON) tools/build_section_index.py 3
	$(PYTHON) tools/build_status.py
	$(PYTHON) tools/apply_chrome.py

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
