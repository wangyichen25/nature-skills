---
name: clinical-figure
description: Create, revise, or audit clinical research figures and tables for manuscripts, journal clubs, and clinical presentations. Use for CONSORT/STROBE/PRISMA flow diagrams, Kaplan-Meier curves, forest plots, diagnostic accuracy, calibration, ROC/PR curves, decision curves, subgroup plots, trial timelines, harms tables, baseline tables, and clinical AI model evaluation figures. Default output language is English.
---

# Clinical Figure

Use this skill for clinical figures where interpretability and endpoint integrity matter more than decorative style.

## First checks

- Identify study design and the figure's clinical question.
- Define population denominator, time horizon, outcome definition, and comparison.
- Prefer absolute effects, confidence intervals, and denominators over isolated percentages.
- Show harms and missingness when they affect interpretation.
- For AI, include external validation, calibration, decision thresholds, subgroup performance, and workflow safety when available.

## Recommended figure types

- Trial: CONSORT flow, primary endpoint effect plot, Kaplan-Meier, subgroup forest, harms table.
- Observational: cohort flow, adjusted effect forest, covariate balance, missingness table.
- Diagnostic: 2x2 table, ROC/PR curve, calibration, threshold table, decision curve.
- Prediction/AI: development-validation diagram, calibration, discrimination, net benefit, subgroup/fairness, deployment workflow.
- Review/meta-analysis: PRISMA flow, forest, heterogeneity and risk-of-bias summaries.

## Output rules

- Do not infer patient benefit from surrogate, detection, or workflow metrics.
- Label axes with units, time windows, and event definitions.
- Keep editable charts/tables when possible.
- If using Python or R, ask which backend only when the user's files do not make it clear.

## References

Open `references/clinical-figure-patterns.md` for figure routing and QA checks.
