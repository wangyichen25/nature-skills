# nejm-skills

Personal Codex skill fork for NEJM-style, high-standard medical research workflows.

This repository began as a fork of [`Yuan1z0825/nature-skills`](https://github.com/Yuan1z0825/nature-skills). It preserves the original `nature-*` skills and adds an English-first `nejm-*` suite for patient-oriented medical research, Big Four journals, GI/endoscopy/hepatology-adjacent work, and AI-in-medicine/GI projects.

## What This Fork Adds

- `nejm-*` skills for medical literature search, citation, data availability, figures/tables, paper-to-PPT, polishing, paper reading, reviewer responses, and manuscript writing.
- PubMed-first citation workflow with Crossref DOI enrichment.
- Big Four and GI journal scopes: NEJM, JAMA/JAMA Network, The Lancet family, BMJ family, Gastroenterology, Gut, AJG, CGH, Gastrointestinal Endoscopy, Endoscopy, Lancet Gastroenterology & Hepatology, Journal of Hepatology, and Hepatology.
- Evidence appraisal defaults: PICO, study design, population/generalizability, endpoints, absolute and relative effects, harms, bias, missingness, multiplicity, protocol/SAP/registry consistency, and practice implications.
- AI-in-medicine checks when relevant: CONSORT-AI, SPIRIT-AI, TRIPOD+AI, external validation, calibration, subgroup fairness, workflow fit, monitoring, privacy, and regulatory caveats.

## Skill Index

### NEJM-Style Medical Research Skills

| Skill | Purpose |
|---|---|
| [`nejm-academic-search`](skills/nejm-academic-search/SKILL.md) | PubMed/MeSH, ClinicalTrials.gov, FDA, guideline, Big Four, and GI evidence search. |
| [`nejm-citation`](skills/nejm-citation/SKILL.md) | PubMed-grounded citation discovery and ENW/RIS/Zotero RDF export. |
| [`nejm-data`](skills/nejm-data/SKILL.md) | Data/code/protocol/SAP/registry/ethics/privacy availability statements. |
| [`nejm-figure`](skills/nejm-figure/SKILL.md) | Medical research figures and tables with endpoint, denominator, uncertainty, and reporting-guideline checks. |
| [`nejm-paper2ppt`](skills/nejm-paper2ppt/SKILL.md) | Editable English journal-club or teaching PPTX decks from medical papers. |
| [`nejm-polishing`](skills/nejm-polishing/SKILL.md) | High-impact medical journal prose polishing with endpoint and claim precision. |
| [`nejm-reader`](skills/nejm-reader/SKILL.md) | Source-grounded medical paper readers and appraisal notes. |
| [`nejm-response`](skills/nejm-response/SKILL.md) | Point-by-point reviewer response drafting for medical journals. |
| [`nejm-writing`](skills/nejm-writing/SKILL.md) | Medical manuscript section drafting and restructuring. |

### Preserved Nature/CNS Skills

The original `nature-*` suite remains available for Nature/CNS-style scientific work:

| Skill | Purpose |
|---|---|
| [`nature-academic-search`](skills/nature-academic-search/SKILL.md) | Literature search, citation verification, and reference management. |
| [`nature-citation`](skills/nature-citation/SKILL.md) | Nature/CNS citation retrieval and export. |
| [`nature-data`](skills/nature-data/SKILL.md) | Nature-style data availability and repository planning. |
| [`nature-figure`](skills/nature-figure/SKILL.md) | Nature-style publication figures. |
| [`nature-paper2ppt`](skills/nature-paper2ppt/SKILL.md) | Paper-to-PPT workflows from the upstream suite. |
| [`nature-polishing`](skills/nature-polishing/SKILL.md) | Nature-style academic prose polishing. |
| [`nature-reader`](skills/nature-reader/SKILL.md) | Full-paper Markdown readers. |
| [`nature-response`](skills/nature-response/SKILL.md) | Reviewer response workflows. |
| [`nature-writing`](skills/nature-writing/SKILL.md) | Nature-style manuscript drafting. |

## Local Codex Installation

Clone the fork:

```bash
git clone https://github.com/wangyichen25/nejm-skills.git
cd nejm-skills
```

Install the NEJM-style skills:

```bash
mkdir -p ~/.codex/skills
for d in skills/nejm-*; do
  ln -sfn "$PWD/$d" ~/.codex/skills/$(basename "$d")
done
```

Install both NEJM-style and Nature-style skills:

```bash
mkdir -p ~/.codex/skills
for d in skills/nejm-* skills/nature-*; do
  ln -sfn "$PWD/$d" ~/.codex/skills/$(basename "$d")
done
```

Restart Codex after changing installed skills so skill metadata is reloaded.

## Citation CLI

The NEJM-style citation script lives at:

```bash
skills/nejm-citation/scripts/nejm_citation.py
```

Example:

```bash
python skills/nejm-citation/scripts/nejm_citation.py \
  --claim "AI-assisted colonoscopy increases adenoma detection rate" \
  --scope big4-gi \
  --format ris \
  --with-artifacts
```

Supported scopes:

```text
big4, jama, nejm, lancet, bmj, gi, big4-gi, major-medical
```

`major-clinical` is kept as a backward-compatible alias for `major-medical`.

## Maintenance Notes

- This fork is optimized for English output.
- Exact word limits, article-type limits, and submission requirements should be checked live from official journal pages during real submission work.
- Citation candidates are conservative: treat them as metadata/abstract-screened until the abstract, full text, guideline text, or trial registry record is checked.
- Upstream remains available as `upstream`; merge selectively when useful.

## License

MIT license, inherited from the upstream repository. See [`LICENSE`](LICENSE).
