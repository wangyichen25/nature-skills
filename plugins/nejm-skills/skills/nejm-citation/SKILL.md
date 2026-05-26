---
name: nejm-citation
description: NEJM-style citation and reference export workflow for PubMed-grounded medical evidence, Big Four journals, GI journals, guidelines, trials, diagnostic/prognostic studies, and AI-in-medicine/GI claims. Use when the user asks to find patient-care references, map claims to evidence, restrict to NEJM/JAMA/Lancet/BMJ/GI journals, export RIS/ENW/Zotero RDF, or create Vancouver/AMA-style medical source lists. Default output language is English.
---

# NEJM-Style Citation

Use this skill to turn patient-care claims or manuscript passages into NEJM-style defensible citation candidates.

## Default stance

- PubMed discovery comes first for patient-oriented medical literature.
- Crossref is used to enrich DOI/export metadata when available.
- Candidates are not proof. Mark them as `metadata/abstract-screened` until abstract, full text, guideline text, or trial registry data is checked.
- Prefer direct human patient-care evidence over preclinical, mechanistic, or related-population evidence for patient-care claims.

## Scope defaults

Default CLI scope is `big4-gi`. Journal scopes:

- `big4`: NEJM, JAMA/JAMA Network, Lancet family, BMJ family.
- `gi`: GI and hepatology-adjacent clinical journals.
- `big4-gi`: Big Four plus GI journals.
- `major-medical`: Big Four, GI, and selected major medical journals.
- `major-clinical`: compatibility alias for `major-medical`.
- `nejm`, `jama`, `lancet`, `bmj`: one family only.

## Evidence labels

Use these labels in reports:

- `direct patient-care support`
- `partial patient-care support`
- `background or mechanistic support`
- `not suitable for this claim`
- `metadata/abstract-screened only`

## Script

Use `scripts/nejm_citation.py` for reference export:

```bash
python skills/nejm-citation/scripts/nejm_citation.py \
  --claim "AI-assisted colonoscopy increases adenoma detection rate" \
  --scope big4-gi \
  --format ris \
  --with-artifacts
```

## References

Open `references/nejm-journal-scope.md` for journal boundaries and `references/evidence-screening.md` for evidence grading and reporting-guideline routing.
