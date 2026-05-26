---
name: clinical-paper2ppt
description: Build editable English PPTX journal-club or teaching decks from clinical papers, trials, guidelines, systematic reviews, diagnostic/prognostic studies, clinical AI papers, and GI/endoscopy/hepatology-adjacent research. Use when the user asks for clinical slides, Big Four/GI journal club, paper presentation, evidence appraisal deck, or AI-in-GI presentation. Default output language is English.
---

# Clinical Paper to PPT

Build slide decks around clinical decision quality, not paper section order.

## Default deck spine

1. Clinical question and PICO.
2. Why this matters for patients, clinicians, or workflow.
3. Study design and setting.
4. Population, eligibility, and generalizability.
5. Intervention/exposure/test/model and comparator/reference standard.
6. Primary endpoint and patient-important secondary endpoints.
7. Main result with absolute and relative effects.
8. Harms, missingness, and subgroup findings.
9. Bias, limitations, protocol/registry consistency.
10. Practice implication and what remains uncertain.

## Clinical AI/GI additions

- For AI: model task, training/validation setting, external validation, calibration, threshold, workflow fit, monitoring, bias, privacy, and regulatory status caveats.
- For GI: endoscopy workflow, pathology reference standard, ADR/PDR distinction, surveillance interval implications, hepatology-adjacent context, and clinic operations impact.

## Output

Create an editable `.pptx` with speaker notes, concise slide text, source labels, and a short QA report. Prefer native charts/tables when data are extractable.

## References

Open `references/clinical-deck-patterns.md` for slide archetypes and reporting guideline routing.
