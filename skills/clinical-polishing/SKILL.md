---
name: clinical-polishing
description: Polish, tighten, or restructure clinical manuscript prose for NEJM/JAMA/Lancet/BMJ/GI-style clinical research, including abstracts, introductions, methods, results, discussions, limitations, titles, cover letters, and plain-language clinical summaries. Use when the user wants clinical journal prose, evidence-aware wording, clinical endpoint precision, or AI/GI manuscript polishing. Default output language is English.
---

# Clinical Polishing

Polish clinical writing by strengthening claim precision, not by making prose sound more impressive.

## Default checks

- Preserve PICO, study design, endpoint definitions, time horizon, denominators, and uncertainty.
- Use absolute effects and harms when available.
- Avoid causal wording for observational or retrospective evidence.
- Avoid patient-benefit claims from surrogate, detection, diagnostic accuracy, or workflow-only outcomes.
- For AI, separate model performance from clinical utility and deployed patient benefit.
- Keep limitations concrete: selection, confounding, spectrum bias, missingness, follow-up, generalizability, drift, and workflow fit.

## Output

Return:

```text
Polished version:
[text]

Clinical edits made:
- [high-signal changes]

Claims to verify:
- [only if needed]
```

## References

Open `references/clinical-prose-guardrails.md` for claim language and abstract/discussion patterns.
