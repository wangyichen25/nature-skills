---
name: clinical-academic-search
description: Coordinated clinical literature search for clinical medicine, GI, hepatology-adjacent, endoscopy, clinical AI, diagnostic, prognostic, guideline, trial, and implementation questions. Use when the user needs PubMed/MeSH search strategy, ClinicalTrials.gov or FDA source checks, Big Four or GI journal discovery, evidence mapping, guideline/source verification, or reference set triage for clinical research. Default output language is English.
---

# Clinical Academic Search

Use this skill when literature search needs clinical evidence discipline rather than generic paper discovery.

## Default source hierarchy

1. Guidelines, society statements, and official regulatory pages for practice or product status.
2. PubMed/MEDLINE with MeSH and clinical filters for peer-reviewed biomedical evidence.
3. ClinicalTrials.gov for trial registration, status, outcomes, and protocol consistency.
4. Publisher pages, DOI/Crossref, and journal instructions for bibliographic and submission metadata.
5. Broader indexes only as discovery aids, never as sole clinical support.

## Clinical framing

Before searching, state:

- population and setting
- intervention/exposure/index test/model
- comparator or reference standard
- patient-important outcomes and harms
- study type needed: trial, observational, diagnostic accuracy, prediction model, systematic review, guideline, or implementation study
- whether the target is Big Four, GI journals, all PubMed, guidelines, FDA, or mixed evidence

## Search behavior

- Prefer PubMed queries with MeSH plus title/abstract terms.
- For trials, check registration number, protocol/SAP availability, primary outcome, enrollment, and reported results.
- For clinical AI, include reporting and evaluation terms such as external validation, calibration, deployment, workflow, bias, fairness, monitoring, and safety.
- For GI, include endoscopy, colorectal cancer screening, IBD, hepatology-adjacent, pancreaticobiliary, motility, pathology, imaging, and clinic operations terms when relevant.
- Separate evidence-ready findings from promising, investigational, workflow-only, or regulatory-only material.

## Output

Return a compact search log:

```text
Question:
Search scope:
Queries run:
Key sources found:
Evidence gaps:
Suggested next search:
```

## References

Open `references/clinical-search-sources.md` when the task needs source prioritization, reporting guideline selection, or journal-family boundaries.
