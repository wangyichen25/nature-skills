---
name: clinical-citation
description: Clinical citation and reference export workflow for PubMed-grounded evidence, Big Four journals, GI journals, guidelines, clinical trials, diagnostic/prognostic studies, and clinical AI claims. Use when the user asks to find clinical references, map claims to evidence, restrict to NEJM/JAMA/Lancet/BMJ/GI journals, export RIS/ENW/Zotero RDF, or create Vancouver/AMA-style clinical source lists. Default output language is English.
---

# Clinical Citation

Use this skill to turn clinical claims or manuscript passages into defensible citation candidates.

## Default stance

- PubMed discovery comes first for clinical literature.
- Crossref is used to enrich DOI/export metadata when available.
- Candidates are not proof. Mark them as `metadata/abstract-screened` until abstract, full text, guideline text, or trial registry data is checked.
- Prefer direct human clinical evidence over preclinical, mechanistic, or related-population evidence for patient-care claims.

## Scope defaults

Default CLI scope is `big4-gi`. Journal scopes:

- `big4`: NEJM, JAMA/JAMA Network, Lancet family, BMJ family.
- `gi`: GI and hepatology-adjacent clinical journals.
- `big4-gi`: Big Four plus GI journals.
- `major-clinical`: Big Four, GI, and selected major clinical journals.
- `nejm`, `jama`, `lancet`, `bmj`: one family only.

## Evidence labels

Use these labels in reports:

- `direct clinical support`
- `partial clinical support`
- `background or mechanistic support`
- `not suitable for this claim`
- `metadata/abstract-screened only`

## Script

Use `scripts/clinical_citation.py` for reference export:

```bash
python skills/clinical-citation/scripts/clinical_citation.py \
  --claim "AI-assisted colonoscopy increases adenoma detection rate" \
  --scope big4-gi \
  --format ris \
  --with-artifacts
```

## References

Open `references/clinical-journal-scope.md` for journal boundaries and `references/evidence-screening.md` for evidence grading and reporting-guideline routing.
