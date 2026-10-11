---
name: grill-tracker
description: Track an ongoing /grill-me session with another agent by distilling Q&A decisions into single-sentence acceptance criteria in a review document for downstream artifact verification.
---

# Grill Session Tracker

Track an ongoing `/grill-me` (or design interview) session with another agent. When a user is answering interview questions in another thread or tool, this skill records and condenses every decision into an authoritative `review.md` checklist. This provides a concrete ground truth so a downstream reviewing agent can evaluate the generated artifacts against settled user intent rather than performing an abstract review.

---

## Workflow

### 1. Initialize the Review Document
When the session begins, create or reset `review.md` (or a user-specified path) at the workspace root using the standard verification structure:

```markdown
# Review & Verification Guide: <Topic Name>

> **Instructions for Reviewing Agent:**
> Use this document as the ground truth specification to review the generated artifact(s): `<target-file-1.md>`, `<target-file-2.md>`.
> For each criterion below, verify whether the generated document:
> 1. **Covers** the requirement accurately.
> 2. **Misses** or underspecifies the topic.
> 3. **Contradicts** any decisions established during the interview.

---

## Baseline Requirements & Decisions

- [ ] **<Topic/Area>:** <Single concise sentence defining the decision or requirement.>
```

### 2. Incrementally Distill Q&A Pairs
As the user provides questions and answers from the grilling session:
1. **Identify the core decision**: Extract the definitive choice made (option selected, custom nuance, constraint, or correction).
2. **Condense into a single sentence**: Formulate exactly one clear, active, testable sentence stating what the target artifact must contain or comply with.
3. **Format as a checklist item**: Prefix with a bold label indicating the domain area (`- [ ] **Label:** Sentence`).
4. **Append immediately**: Write or replace content in `review.md` after each turn.

### 3. Handle Refinements and Scope Corrections
Users frequently refine, narrow, or reverse previous decisions later in the grilling session:
- **Update in place**: When an answer refines an existing criterion, modify the existing line rather than appending a conflicting rule.
- **Record exclusions explicitly**: If the user excludes a feature (e.g. out of scope for MVP, removed game mechanics, deferred technical schemas), record the exclusion as a concrete non-requirement.
- **Protect user files**: Explicitly mark any personal or user-managed files (e.g. `todo`, personal notes) as protected from agent modification.

### 4. Finalize & Generate Reviewer Handoff Prompt
Once the grilling session reaches the end of its design tree and artifacts are generated:
1. Perform a final consistency check across all checklist items in `review.md`.
2. Output a ready-to-run prompt snippet that the user can pass directly to the reviewing agent.

---

## Distillation Guidelines

- **Single-Sentence Rule**: Every checklist item must be exactly one sentence. If a decision has multiple sub-clauses, join them logically or split into distinct labeled checklist items.
- **Checkable Completion Bounds**: Phrase requirements so a reviewing agent can give a binary yes/no answer (e.g., "Must specify Phase 7" instead of "Should explain when recall stops").
- **Domain vs. Implementation Separation**: Keep domain rules (business logic, invariants, tournament topologies) free of low-level implementation details (database tables, DTO schemas, enum code) unless the user explicitly requests them.
- **Positive Phrasing**: State what the artifact *must* contain or *must omit* directly, rather than vague commentary.

---

## Reviewer Handoff Template

When the session concludes, provide this template to the user:

```markdown
Please review the generated artifacts:
- `<path/to/artifact-1>`
- `<path/to/artifact-2>`

Use `review.md` as your ground-truth specification. For each checklist item in `review.md`:
1. Verify whether the target document accurately covers the requirement.
2. Flag any missing details, discrepancies, or contradictions.
3. Check off the items that pass.
```
