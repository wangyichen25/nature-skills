---
name: clinical-response
description: Draft, audit, or revise point-by-point reviewer responses for clinical journals, Big Four submissions, GI journals, trials, observational studies, diagnostic/prognostic manuscripts, and clinical AI papers. Use when the user provides reviewer comments, editor letters, revision notes, or response drafts and needs clinical, statistical, reporting-guideline, ethics, registry, or AI-specific response handling. Default output language is English.
---

# Clinical Reviewer Response

Use this skill to make reviewer responses precise, traceable, and clinically defensible.

## Default stance

- Preserve every reviewer concern and answer it directly.
- Map each response to manuscript text, table, figure, supplement, protocol/SAP, registry, or `AUTHOR_INPUT_NEEDED`.
- Do not invent new analyses, line numbers, ethics approvals, trial registration, results, or subgroup findings.
- When disagreeing, use clinical scope, study design, evidence, or reporting-guideline logic.
- For impossible requests, explain feasibility and add limitations or future-work language when appropriate.

## Clinical response checks

- Protocol/SAP and registry consistency.
- Primary versus secondary endpoint clarity.
- Absolute effects, harms, missingness, multiplicity, and subgroup interpretation.
- Confounding, bias, generalizability, and clinical significance.
- AI external validation, calibration, threshold, workflow, privacy, and monitoring.

## Output

```text
Response strategy summary
Comment-response tracker
Draft point-by-point response letter
Manuscript change checklist
Missing information / risk flags
```

## References

Open `references/clinical-response-patterns.md` for difficult reviewer scenarios and safe response language.
