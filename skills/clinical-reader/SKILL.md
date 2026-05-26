---
name: clinical-reader
description: Build English clinical paper readers and appraisal notes from PDFs, DOIs, abstracts, trial reports, guidelines, systematic reviews, diagnostic/prognostic studies, and AI-in-medicine papers. Use when the user asks to read, appraise, summarize, or extract a clinical paper with source grounding, PICO, endpoints, effect sizes, harms, bias, and practice implications. Default output language is English.
---

# Clinical Reader

Use this skill to read clinical papers as evidence for decisions, teaching, or manuscript planning.

## Default artifact

Create a source-grounded reader with:

- citation and study type
- PICO
- study design and setting
- population and generalizability
- intervention/exposure/test/model and comparator/reference standard
- endpoints with time horizon
- main results with absolute and relative effects
- harms, missingness, subgroup results, and limitations
- reporting guideline fit
- practice implication and what remains uncertain
- source anchors for claims

## Clinical AI/GI checks

- AI: task definition, data split, external validation, calibration, threshold, workflow, bias/fairness, monitoring, privacy, regulatory caveats.
- GI: endoscopy/pathology reference standards, ADR versus PDR, interval cancer or mortality endpoint distinction, surveillance and workflow implications.

## Do not

- Treat a paper summary as clinical guidance.
- Equate detection improvement with cancer mortality reduction.
- Treat retrospective model performance as deployed clinical benefit.

## References

Open `references/clinical-appraisal.md` when judging study quality or selecting reporting guidelines.
