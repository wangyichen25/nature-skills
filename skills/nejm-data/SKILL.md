---
name: nejm-data
description: Prepare, audit, or revise NEJM-style medical Data Availability, code availability, trial protocol/SAP availability, registry, ethics, consent, privacy, and deidentified participant-data sharing statements for medical journals. Use for NEJM/JAMA/Lancet/BMJ/GI manuscripts, trials, observational studies, registries, AI-in-medicine studies, and human-subject datasets. Default output language is English.
---

# NEJM-Style Data Availability

Use this skill to make clinical research data statements transparent, ethical, and journal-ready.

## Default checks

- Identify whether the study uses individual participant data, images/video, pathology, EHR, claims, registry, device, or model data.
- State registry numbers, protocol/SAP availability, data dictionary availability, and analysis-code availability when applicable.
- Separate deidentified participant-level data, aggregate data, model weights, code, source data, and restricted third-party data.
- For privacy limits, name the restriction and access route; do not hide behind vague "available on request" wording.
- For AI work, address training data access limits, external validation data, model/code availability, inference environment, and monitoring data.

## Output

```text
Data and code availability
[ready-to-paste statement]

Clinical transparency checklist
- Registry:
- Protocol/SAP:
- Data dictionary:
- Participant-level data:
- Code/model:
- Access restrictions:

Missing information
- [specific missing items or None]
```

## References

Open `references/nejm-data-principles.md` when trial, AI, privacy, or registry details matter.
