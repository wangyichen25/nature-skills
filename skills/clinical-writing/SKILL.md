---
name: clinical-writing
description: Draft, restructure, or plan clinical manuscript sections for NEJM/JAMA/Lancet/BMJ/GI-style research, including titles, structured abstracts, introductions, methods, results, discussions, limitations, clinical implications, cover letters, and reporting-guideline checklists. Use for trials, observational studies, diagnostic/prognostic studies, systematic reviews, guidelines, clinical AI, and AI-in-GI manuscripts. Default output language is English.
---

# Clinical Writing

Use this skill when the user needs clinical manuscript argument construction, not just sentence polishing.

## Intake

Identify:

- target journal or journal family
- study type and reporting guideline
- PICO or equivalent clinical question
- setting, population, eligibility, and generalizability
- intervention/exposure/test/model and comparator/reference standard
- primary and secondary endpoints with time horizon
- effect sizes, uncertainty, harms, missingness, and subgroup results
- protocol/SAP/registry details when applicable
- clinical implication and boundary of the claim

## Default structure

- Abstract: question, design/setting, participants, intervention/exposure/test, main outcomes, results with absolute/relative effects, limitations, conclusion.
- Introduction: clinical problem, evidence gap, why current practice/data are insufficient, study objective.
- Methods: design, setting, participants, outcome definitions, statistical plan, ethics, registry, reporting guideline.
- Results: participant flow, baseline, primary result, secondary/harms, sensitivity/subgroups, missing data.
- Discussion: principal finding, comparison with prior evidence, mechanisms only if supported, clinical meaning, limitations, next steps.

## Guardrails

- Do not invent data, analyses, citations, registry numbers, ethics approvals, or clinical implications.
- Do not upgrade association, diagnostic accuracy, detection, or workflow evidence into patient-outcome benefit.
- For AI, separate model performance, clinical utility, prospective evaluation, and deployed impact.

## References

Open `references/clinical-manuscript-patterns.md` for study-type routing and abstract/discussion patterns.
