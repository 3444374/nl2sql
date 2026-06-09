---
name: nl2sql-intensive-reading
description: Use for NL2SQL/SQL+ thesis intensive paper reading in this repository, especially when the user asks to explain, verify, summarize, continue reading, or record notes for opening-report papers under docs/opening. Applies to source verification, PDF reading, key figure extraction, paper-note writing, and mapping each paper to the SQL+ multi-agent repair thesis claims.
---

# NL2SQL Intensive Reading

## Overview

Use this skill to read opening-report papers rigorously and consistently. Each paper should be handled as a verified source, a teachable reading session, and a durable note in `docs/opening/intensive_reading_notes.md`.

When available, also consult `academic-research-suite` for its bibliography/source verification discipline. Apply its core ideas here: verify source existence, prefer authoritative venues, record search/source provenance, distinguish source quality from paper relevance, and avoid unsupported claims.

## Required Workflow

1. Identify the next paper from `docs/opening/intensive_reading_plan.md`.
2. Verify the source before explaining it.
   - Prefer official venue pages and proceedings: ACL Anthology, NeurIPS, ICLR/OpenReview, ICML/PMLR, AAAI, PVLDB/SIGMOD, official publisher pages.
   - Use arXiv only as a fallback or supplementary source when no formal version is available.
   - If an intensive-reading paper is arXiv-only, first search for a formal version. If none exists, replace it with a stronger venue paper covering the same role in the thesis, then update the reading plan and opening-reference documents.
   - If a local PDF is downloaded from arXiv but the paper has a formal proceedings version, replace the local PDF with the formal version and update `docs/opening/papers/README.md`.
   - When replacing an arXiv-heavy paper, synchronize all affected opening materials, including `docs/opening/intensive_reading_plan.md`, `docs/opening/intensive_reading_notes.md`, `docs/opening/papers/README.md`, `docs/opening/venue_strengthened_literature.md`, opening report drafts, and PPT reference lists.
   - Record DOI, venue, official URL, local PDF path, source quality, and verification status.
3. Read the local PDF from `docs/opening/papers/`.
   - Extract metadata, abstract claims, dataset/method details, metrics, tables, limitations, and discussion points.
   - If a local PDF is an arXiv version but a formal proceedings PDF exists, prefer replacing or additionally recording the formal PDF.
4. Add key paper figures only when they clarify the method, benchmark, framework, workflow, or evaluation.
   - Save cropped figures under `docs/opening/paper_figures/`.
   - Use local relative Markdown links such as `![caption](paper_figures/name.png)`.
   - Do not dump whole PDF pages unless the full page is the useful figure.
5. Explain the paper to the user in Chinese while keeping technical terms such as Text-to-SQL, schema linking, execution accuracy, SQL+, and Skill Router in English when useful.
6. Write the durable note to `docs/opening/intensive_reading_notes.md`.
7. Do not write paper-reading progress to `docs/project/project_log.md` or `docs/project/experiment_log.md` unless the user explicitly asks to change project workflow or an actual experiment is run.

## Note Structure

For each paper, use this structure:

```markdown
## N. Short Paper Name

### 0. Source and verification
- Full title:
- Authors:
- Venue:
- DOI / official URL:
- Local PDF:
- Local figures:
- Source quality:
- Verification status:

![optional key figure](paper_figures/...)

### 1. One-sentence positioning
### 2. Problem addressed
### 3. Core method / benchmark design
### 4. Experiments and main results
### 5. Key contributions
### 6. Limitations
### 7. Relation to this thesis
### 8. Opening-defense wording
### 9. Likely advisor questions
### 10. Intensive-reading conclusion
```

## Claim Discipline

- Do not present small local results as broad benchmark scores.
- State current project results precisely when relevant:
  - SQL+ Skill Router + Repair Skills v3: `13/13` on the current known-failure set.
  - Spider smoke test: `20/20` on a supported small Spider dev subset, not full Spider.
- Separate what a paper proves from how this thesis uses it.
- Mark future-work relevance explicitly for BIRD, Spider 2.0, and other large benchmarks if no local experiment has been run.
- Do not keep arXiv-only papers in the 15-paper intensive-reading list when a formal ACL/EMNLP/AAAI/NeurIPS/ICML/ICLR/PVLDB/SIGMOD substitute can serve the same thesis role.

## Figure Extraction

When figures are needed:

1. Render a PDF page with PyMuPDF (`fitz`) if available.
2. Crop the exact figure with PIL.
3. Save only the final cropped figure. Remove intermediate full-page images unless they are intentionally used.
4. Verify the crop with `view_image` before referencing it.

Example naming:

```text
docs/opening/paper_figures/03_spider2_fig1_overview.png
```

## Final Response

After each paper, briefly report:

- Which paper was completed.
- Which notes and figures were updated.
- The one or two claims the user should remember for opening defense.
- The recommended next paper.
